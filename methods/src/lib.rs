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

    #[test]
    fn proves_even_number() {
        let data_str = r#"
        {
            "BTC":{"price":"1234"},
            "ETH":{"price":"5678"},
            "serverTime":"90"
        }"#
        .to_string();

        let env = ExecutorEnv::builder()
            .write(&data_str)
            .unwrap()
            .build()
            .unwrap();

        // NOTE: Use the executor to run tests without proving.
        let session_info = match default_executor().execute(env, super::IS_EVEN_ELF) {
            Ok(info) => info,
            Err(e) => panic!("Execution failed with error: {:?}", e),
        };

        let (btc_price, eth_price, timestamp): (U256, U256, U256) = <(U256, U256, U256)>::abi_decode(&session_info.journal.bytes, true).unwrap();
        assert_eq!(btc_price, U256::from(1234));
        assert_eq!(eth_price, U256::from(5678));
        assert_eq!(timestamp, U256::from(90));
    }

    // #[test]
    // #[should_panic(expected = "number is not even")]
    // fn rejects_odd_number() {
    //     let odd_number = U256::from(75);
    //     let odd_number_2 = U256::from(75);

    //     let encoded_numbers = (odd_number, odd_number_2).abi_encode();

    //     let env = ExecutorEnv::builder()
    //         .write_slice(&encoded_numbers)
    //         .build()
    //         .unwrap();

    //     // NOTE: Use the executor to run tests without proving.
    //     default_executor().execute(env, super::IS_EVEN_ELF).unwrap();
    // }
}
