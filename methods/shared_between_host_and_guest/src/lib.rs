// Copyright 2024 Diffuse
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

use alloy_sol_types::{SolValue, SolType};
use anyhow::{Context, Result};

use serde::{Serialize, Deserialize};

// hardcoded pairs
pub const PAIRS_AMOUNT: usize = 5;
pub type PairDataType = (String, u64, u64);
pub type ParsedDataType = [PairDataType; PAIRS_AMOUNT];

#[derive(Serialize, Deserialize)]
pub struct GuestOutputStruct {
    pub extracted_data: ParsedDataType,
    pub hashed_json: [u8; 32],
}

impl GuestOutputStruct {
    pub fn abi_decode(encoded: &[u8], validate: bool) -> anyhow::Result<Self> {
        let extracted_data_len = encoded.len() - 32;

        let extracted_data = <ParsedDataType>::abi_decode(&encoded[..extracted_data_len], validate)
            .context("decoding journal data")?;

        let hashed_json: [u8; 32] = encoded[extracted_data_len..]
            .try_into()
            .map_err(|_| anyhow::anyhow!("Failed to decode hashed_json"))?;
        Ok(GuestOutputStruct {
            extracted_data,
            hashed_json,
        })
    }
}

#[derive(Serialize, Deserialize)]
pub struct GuestInputStruct {
    pub json_bytes: Vec<u8>,
    pub currency_pairs:[String; PAIRS_AMOUNT]
}

pub type GuestInputType = GuestInputStruct;
pub type GuestOutputType = GuestOutputStruct;