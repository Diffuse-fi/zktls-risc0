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
use shared_between_host_and_guest::{GuestInputType, ParsedDataType, PairDataType};
use std::array;
use tiny_keccak::Keccak;
use tiny_keccak::Hasher;


fn extract_pair_data(json_data: &JsonValue, pair_name: &String) -> PairDataType {
    let price_str = json_data[pair_name]["price"].to_string();

    let integer_and_fractional: Vec<&str> = price_str.split('.').collect();

    if integer_and_fractional.len() != 2 {
        eprintln!("Error: 'price' value for {} is {}, unable to parse as float", pair_name, price_str);
        panic!("price is not float number!");
    }

    let integer: u64 = integer_and_fractional[0].parse().expect("Failed to parse integer part");
    let fractional: u64 = integer_and_fractional[1].parse().expect("Failed to parse fractional part");

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

    (pair_name.clone(), price, timestamp)
}

fn main() {

    // Read the input data for this application.
    let input: GuestInputType = env::read();
    let json_bytes: Vec<u8> = input.json_bytes;
    let json_string = String::from_utf8_lossy(&json_bytes);
    let json_data = parse(&json_string).unwrap();

    let mut hasher = Keccak::v256();
    hasher.update(&json_bytes);
    let mut hashed_json = [0u8; 32];
    hasher.finalize(&mut hashed_json);


    let extracted_data: ParsedDataType = array::from_fn(|i| {
        extract_pair_data(&json_data, &input.currency_pairs[i])
    });

    // Commit the journal that will be received by the application contract.
    // Journal is encoded using Solidity ABI for easy decoding in the app contract.

    let mut encoded_journal = Vec::new();
    encoded_journal.extend_from_slice(&extracted_data.abi_encode());
    encoded_journal.extend_from_slice(&hashed_json);




    // let encoded_journal = results.abi_encode();
    env::commit_slice(&encoded_journal.as_slice());
}
