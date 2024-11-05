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
use alloy_primitives::{Address, U256};
use anyhow::{Context, Result};
use clap::Parser;
use methods::IS_EVEN_ELF;
use risc0_ethereum_contracts::encode_seal;
use risc0_zkvm::{default_prover, ExecutorEnv, ProverOpts, VerifierContext};
use url::Url;
use std::fs;

// `IEvenNumber` interface automatically generated via the alloy `sol!` macro.
alloy::sol!(
    #[sol(rpc, all_derives)]
    "../contracts/IEvenNumber.sol"
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

    /// Path to json
    #[clap(long)]
    json_path: String,
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

    // path to json file where information about prices is stored
    let json_path = args.json_path;
    let data = fs::read_to_string(json_path).expect("Unable to read file");
    let env = ExecutorEnv::builder().write(&data).unwrap().build()?;

    let receipt = default_prover()
        .prove_with_ctx(
            env,
            &VerifierContext::default(),
            IS_EVEN_ELF,
            &ProverOpts::groth16(),
        )?
        .receipt;

    // Encode the seal with the selector.
    let seal = encode_seal(&receipt)?;

    // Extract the journal from the receipt.
    let journal = receipt.journal.bytes.clone();

    // Decode Journal: Upon receiving the proof, the application decodes the journal to extract
    // the verified numbers. This ensures that the numbers being submitted to the blockchain match
    // the numbers that were verified off-chain.
    let (btc_price, eth_price, timestamp): (U256, U256, U256) = <(U256, U256, U256)>::abi_decode(&journal, true).context("decoding journal data")?;

    // Construct function call: Using the IEvenNumber interface, the application constructs
    // the ABI-encoded function call for the set function of the EvenNumber contract.
    // This call includes the verified numbers, the post-state digest, and the seal (proof).
    let contract = IEvenNumber::new(args.contract, provider);
    let call_builder = contract.set(btc_price, eth_price, timestamp, seal.into());

    // Initialize the async runtime environment to handle the transaction sending.
    let runtime = tokio::runtime::Runtime::new()?;

    // Send transaction: Finally, send the transaction to the Ethereum blockchain,
    // effectively calling the set function of the EvenNumber contract with the verified number and proof.
    let pending_tx = runtime.block_on(call_builder.send())?;
    runtime.block_on(pending_tx.get_receipt())?;

    Ok(())
}
