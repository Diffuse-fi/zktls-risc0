// Copyright 2024 RISC Zero, Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// This application demonstrates how to send an off-chain proof request
// to the Bonsai proving service and publish the received proofs directly
// to your deployed app contract.

use alloy::{
    network::EthereumWallet, providers::ProviderBuilder, signers::local::PrivateKeySigner,
    sol_types::SolValue,
};
// use alloy_primitives::{Address, U256};
use alloy_primitives::Address;
use anyhow::{Context, Result};
use clap::Parser;
use methods::JSON_PARSER_ELF;
use methods::guest_data_structs::{GuestInputType, GuestOutputType};
use risc0_ethereum_contracts::encode_seal;
use risc0_zkvm::{default_prover, ExecutorEnv, ProverOpts, VerifierContext};
use url::Url;
use std::fs;
use std::path::Path;

// `IDataFeedFeeder` interface automatically generated via the alloy `sol!` macro.
alloy::sol!(
    #[sol(rpc, all_derives)]
    "../contracts/IDataFeedFeeder.sol"
);

/// Arguments of the publisher CLI.
#[derive(Parser, Debug)]
#[clap(author, version, about, long_about = None)]
struct Args {
    /// Ethereum chain ID
    #[clap(long)]
    chain_id: u64,

    /// Ethereum Node endpoint.
    #[clap(long, env)]
    eth_wallet_private_key: PrivateKeySigner,

    /// Ethereum Node endpoint.
    #[clap(long)]
    rpc_url: Url,

    /// Application's contract address on Ethereum
    #[clap(long)]
    contract: Address,
}

fn main() -> Result<()> {
    env_logger::init();
    // Parse CLI Arguments: The application starts by parsing command-line arguments provided by the user.
    let args = Args::parse();

    // Create an alloy provider for that private key and URL.
    let wallet = EthereumWallet::from(args.eth_wallet_private_key);
    let provider = ProviderBuilder::new()
        .with_recommended_fillers()
        .wallet(wallet)
        .on_http(args.rpc_url);


    let data_storage_path = Path::new("data/");

    let mut max_number = 0;

    if data_storage_path.is_dir() {
        for entry in fs::read_dir(data_storage_path)? {
            let entry = entry?;
            if let Some(folder_name) = entry.file_name().to_str() {
                if let Ok(number) = folder_name.parse::<u32>() {
                    if number > max_number {
                        max_number = number;
                    }
                }
            }
        }
    }

    let max_folder_path = data_storage_path.join(format!("{}", max_number));
    let seal_path = max_folder_path.join("seal.bin");
    let journal_path = max_folder_path.join("journal.bin");
    let json_path = max_folder_path.join("prover_input.json");

    let already_proven = seal_path.exists() && journal_path.exists();

    if !already_proven {
        let json_string = fs::read_to_string(json_path).expect("Unable to read file");

        let guest_input = GuestInputType {
            json_string: String::from(json_string),
            currency_pairs: vec![String::from("ETHBTC"), String::from("BTCUSDT"), String::from("ETHUSDT"), String::from("ETHUSDC")],
        };

        let env = ExecutorEnv::builder().write(&guest_input).unwrap().build()?;

        let receipt = default_prover()
            .prove_with_ctx(
                env,
                &VerifierContext::default(),
                JSON_PARSER_ELF,
                &ProverOpts::groth16(),
            )?
            .receipt;

        // Encode the seal with the selector.
        let seal = encode_seal(&receipt)?;

        // Extract the journal from the receipt.
        let journal = receipt.journal.bytes.clone();

        fs::write(seal_path.clone(), &seal)?;
        fs::write(journal_path.clone(), &journal)?;
    }

    let seal = fs::read(seal_path.clone())?;
    let journal = fs::read(journal_path.clone())?;

    // Decode Journal: Upon receiving the proof, the application decodes the journal to extract
    // the verified numbers. This ensures that the numbers being submitted to the blockchain match
    // the numbers that were verified off-chain.
    let guest_output: GuestOutputType = <GuestOutputType>::abi_decode(&journal, true).context("decoding journal data")?;

    const ARRAY_REPEAT_VALUE: std::string::String = String::new();
    let mut pair_names = [ARRAY_REPEAT_VALUE; 4];
    let mut prices = [0u64; 4];
    let mut timestamps = [0u64; 4];

    for (i, (first, second, third)) in guest_output.into_iter().enumerate() {
        pair_names[i] = first;
        prices[i] = second;
        timestamps[i] = third;
        println!("pair {}. name: {}, price: {}, timestamp:{}", i, pair_names[i], prices[i], timestamps[i]);
    }


    // Construct function call: Using the IDataFeedFeeder interface, the application constructs
    // the ABI-encoded function call for the set function of the DataFeedFeeder contract.
    // This call includes the verified numbers, the post-state digest, and the seal (proof).
    let contract = IDataFeedFeeder::new(args.contract, provider);
    let call_builder = contract.set(pair_names, prices, timestamps, seal.into());

    // Initialize the async runtime environment to handle the transaction sending.
    let runtime = tokio::runtime::Runtime::new()?;

    // Send transaction: Finally, send the transaction to the Ethereum blockchain,
    // effectively calling the set function of the DataFeedFeeder contract with the verified number and proof.
    let pending_tx = runtime.block_on(call_builder.send())?;
    runtime.block_on(pending_tx.get_receipt())?;

    Ok(())
}
