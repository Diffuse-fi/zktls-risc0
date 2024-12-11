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

#[cfg(test)]
mod tests {
    use alloy_primitives::U256;
    use alloy_sol_types::SolValue;
    use risc0_zkvm::{default_executor, ExecutorEnv};
    use shared_between_host_and_guest::GuestInputType;
    use shared_between_host_and_guest::GuestOutputType;

    #[test]
    // hardcoded pairs
    fn proves_valid_json() {
        let data_str = r#"
        {
            "ETHBTC": {
                "price": "0.03902000",
                "closeTime": 1734004690790
            },
            "BTCUSDT": {
                "price": "100255.18000000",
                "closeTime": 1734004690148
            },
            "ETHUSDT": {
                "price": "3911.39000000",
                "closeTime": 1734004690470
            },
            "ETHUSDC": {
                "price": "3912.56000000",
                "closeTime": 1734004689069
            },
            "SOLUSDT": {
                "price": "229.14000000",
                "closeTime": 1734004690664
            }
        }"#
        .to_string();

        let data_bytes   = data_str.as_bytes().to_vec();

        // hardcoded pairs
        let guest_input = GuestInputType {
            json_bytes: data_bytes,
            currency_pairs: [
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


        let guest_output: GuestOutputType = <GuestOutputType>::abi_decode(&session_info.journal.bytes, true).unwrap();
        let res = guest_output.extracted_data;

        assert_eq!("ETHBTC", res[0].0);
        assert_eq!(3902000, res[0].1);
        assert_eq!(1734004690790, res[0].2);

        assert_eq!("BTCUSDT", res[1].0);
        assert_eq!(10025518000000, res[1].1);
        assert_eq!(1734004690148, res[1].2);

        assert_eq!("ETHUSDT", res[2].0);
        assert_eq!(391139000000, res[2].1);
        assert_eq!(1734004690470, res[2].2);

        assert_eq!("ETHUSDC", res[3].0);
        assert_eq!(391256000000, res[3].1);
        assert_eq!(1734004689069, res[3].2);

        assert_eq!("SOLUSDT", res[4].0);
        assert_eq!(22914000000, res[4].1);
        assert_eq!(1734004690664, res[4].2);

    }

    #[test]
    #[should_panic(expected = "called `Result::unwrap()` on an `Err` value: Guest panicked: called `Result::unwrap()` on an `Err` value: DeserializeUnexpectedEnd")]
    fn rejects_invalid_json() {
        let data_str = r#"Hello, world!"#
        .to_string();

        let data_bytes   = data_str.as_bytes().to_vec();

        let env = ExecutorEnv::builder()
            .write(&data_bytes)
            .unwrap()
            .build()
            .unwrap();

        // NOTE: Use the executor to run tests without proving.
        default_executor().execute(env, super::JSON_PARSER_ELF).unwrap();

    }
}
