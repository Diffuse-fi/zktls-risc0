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

// use alloy_primitives::U256;
use alloy_sol_types::SolValue;
use risc0_zkvm::guest::env;
use json::{parse, JsonValue};

fn extract_pair_data<'a>(json_data: &'a JsonValue, pair_name: &'a String) -> (&'a String, u64, u64) {

    let price_str = json_data[pair_name]["price"].to_string();

    let integer_and_fractional: Vec<&str> = price_str.split('.').collect();

    if integer_and_fractional.len() != 2 {
        eprintln!("Error: 'price' value for {} is {}, unable to parse as float", pair_name, price_str);
        panic!("price is not float number!");
    }

    let integer: u64 = integer_and_fractional[0].parse().expect("Failed to parse integer part");
    let fractional: u64 = integer_and_fractional[1].parse().expect("Failed to parse integer part");

    let mut price: u64 = integer * 100000;
    let decimal_points: u32 = integer_and_fractional[1].chars().count().try_into().unwrap();
    assert!(decimal_points <= 5, "price decimal points <= 5 are hardcoded"); // TODO 5 hardcoded

    price += fractional * 10u64.pow(5 - decimal_points);


    let timestamp = match json_data[pair_name]["closeTime"].as_u64() {
        Some(value) => value,
        None => {
            eprintln!("Error: 'closeTime' value for {} pair is not a valid u64 or is missing", pair_name);
            panic!("Failed to parse timestamp");
        }
    };

    (pair_name, price, timestamp)
}

fn main() {

    // TODO declared identical to methods/src/guest_input_struct.rs because was failing to import for too long
    #[derive(serde::Deserialize)]
    pub struct GuestInputType {
        pub json_string: String,
        pub currency_pairs: Vec<String>,
    }

    // Read the input data for this application.
    let input: GuestInputType = env::read();
    let json_string: String = input.json_string;
    let json_data = parse(&json_string).unwrap();

    let placeholder_str = "".to_string();
    let mut results: [(&String, u64, u64); 4] = [(&placeholder_str, 0u64, 0u64); 4];
    for i in 0..4 {
        results[i] = extract_pair_data(&json_data, &input.currency_pairs[i]);
    }


    // Commit the journal that will be received by the application contract.
    // Journal is encoded using Solidity ABI for easy decoding in the app contract.

    let encoded_journal = results.abi_encode();
    env::commit_slice(&encoded_journal.as_slice());
}
