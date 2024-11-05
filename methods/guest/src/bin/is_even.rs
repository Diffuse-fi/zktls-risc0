// Copyright 2023 RISC Zero, Inc.
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

use std::io::Read;

use alloy_primitives::U256;
use alloy_sol_types::SolValue;
use risc0_zkvm::guest::env;
use json::parse;


fn main() {
    // Read the input data for this application.
    let data: String = env::read();
    let data = parse(&data).unwrap();

    // TODO: using strings here, real json will contain float, EVM uses uint256, need to do something with conversions
    let btc_price_str = data["BTC"]["price"].to_string();
    let btc_price_u32: u32 = match btc_price_str.parse::<u32>() {
        Ok(num) => num,
        Err(e) => {
            eprintln!("Failed to parse BTC price: {}", e);
            eprintln!("btc_price_str: {}", btc_price_str);
            eprintln!("data: {}", data);
            return;
        }
    };

    let eth_price_str = data["ETH"]["price"].to_string();
    let eth_price_u32: u32 = match eth_price_str.parse::<u32>() {
        Ok(num) => num,
        Err(e) => {
            eprintln!("Failed to parse eth price: {}", e);
            eprintln!("btc_price_str: {}", eth_price_str);
            eprintln!("data: {}", data);
            return;
        }
    };


    let timestamp_str = data["serverTime"].to_string();
    let timestamp_u32: u32 = match timestamp_str.parse::<u32>() {
        Ok(num) => num,
        Err(e) => {
            eprintln!("Failed to parse timestamp: {}", e);
            eprintln!("serverTime: {}", timestamp_str);
            eprintln!("data: {}", data);

            return;
        }
    };

    // Commit the journal that will be received by the application contract.
    // Journal is encoded using Solidity ABI for easy decoding in the app contract.
    let u256_number = U256::from(btc_price_u32);

    let encoded_journal = (u256_number, eth_price_u32, timestamp_u32).abi_encode();
    env::commit_slice(&encoded_journal.as_slice());
}
