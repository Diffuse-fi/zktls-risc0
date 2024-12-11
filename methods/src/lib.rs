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

//! Generated crate containing the image ID and ELF binary of the build guest.
include!(concat!(env!("OUT_DIR"), "/methods.rs"));

pub mod guest_data_structs;

#[cfg(test)]
mod tests {
    use alloy_primitives::U256;
    use alloy_sol_types::SolValue;
    use risc0_zkvm::{default_executor, ExecutorEnv};
    use super::guest_data_structs::GuestInputType;
    use super::guest_data_structs::GuestOutputType;

    #[test]
    // hardcoded pairs
    fn proves_even_number() {
        let data_str = r#"
        {
            "ETHBTC": {
                "price": 0.03548,
                "closeTime": 1730908508815
            },
            "BTCUSDT": {
                "price": 74385.99,
                "closeTime": 1730908510474
            },
            "ETHUSDT": {
                "price": 2639.83,
                "closeTime": 1730908509646
            },
            "ETHUSDC": {
                "price": 2641.76,
                "closeTime": 1730908508905
            },
            "SOLUSDT": {
                "price": 229.56,
                "closeTime": 1733934827
            }
        }"#
        .to_string();


        // hardcoded pairs
        let guest_input = GuestInputType {
            json_string: String::from(data_str),
            currency_pairs: vec![
                String::from("ETHBTC"),
                String::from("BTCUSDT"),
                String::from("ETHUSDT"),
                String::from("ETHUSDC"),
                String::from("SOLUSDT")
            ],
        };


        let env = ExecutorEnv::builder()
            .write(&guest_input)
            .unwrap()
            .build()
            .unwrap();

        // NOTE: Use the executor to run tests without proving.
        let session_info = match default_executor().execute(env, super::JSON_PARSER_ELF) {
            Ok(info) => info,
            Err(e) => panic!("Execution failed with error: {:?}", e),
        };


        // hardcoded pairs
        let res: GuestOutputType = <GuestOutputType>::abi_decode(&session_info.journal.bytes, true).unwrap();
        assert_eq!("ETHBTC", res[0].0);
        assert_eq!(3548, res[0].1);
        assert_eq!(1730908508815, res[0].2);

        assert_eq!("BTCUSDT", res[1].0);
        assert_eq!(7438599000, res[1].1);
        assert_eq!(1730908510474, res[1].2);

        assert_eq!("ETHUSDT", res[2].0);
        assert_eq!(263983000, res[2].1);
        assert_eq!(1730908509646, res[2].2);

        assert_eq!("ETHUSDC", res[3].0);
        assert_eq!(264176000, res[3].1);
        assert_eq!(1730908508905, res[3].2);

        assert_eq!("SOLUSDT", res[4].0);
        assert_eq!(22956000, res[4].1);
        assert_eq!(1733934827, res[4].2);

    }

    #[test]
    #[should_panic(expected = "called `Result::unwrap()` on an `Err` value: Guest panicked: called `Result::unwrap()` on an `Err` value: DeserializeUnexpectedEnd")]
    fn rejects_odd_number() {
        let data_str = r#"Hello, world!"#
        .to_string();

        let env = ExecutorEnv::builder()
            .write(&data_str)
            .unwrap()
            .build()
            .unwrap();

        // NOTE: Use the executor to run tests without proving.
        default_executor().execute(env, super::JSON_PARSER_ELF).unwrap();

    }
}
