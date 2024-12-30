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
//
// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.8.20;

import {IRiscZeroVerifier} from "risc0/IRiscZeroVerifier.sol";
import {IAutomataDcapAttestationFee} from "./IAutomataDcapAttestationFee.sol";
import "./DataFeedStorage.sol";
import "./PairDataStruct.sol";
import {ImageID} from "./ImageID.sol"; // auto-generated contract after running `cargo build`.

/// @title A starter application using RISC Zero.
/// @notice This basic application holds a number, guaranteed to be even.
/// @dev This contract demonstrates one pattern for offloading the computation of an expensive
///      or difficult to implement function to a RISC Zero guest running on the zkVM.

contract DataFeedFeeder {
    /// @notice RISC Zero verifier contract address.
    IRiscZeroVerifier public immutable risc0_verifier;
    /// @notice Automata Intel SGX quote verifier contract address.
    IAutomataDcapAttestationFee public immutable sgx_quote_verifier;

    /// @notice Image ID of the only zkVM binary to accept verification from.
    ///         The image ID is similar to the address of a smart contract.
    ///         It uniquely represents the logic of that guest program,
    ///         ensuring that only proofs generated from a pre-defined guest program
    ///         (in this case, checking if a number is even) are considered valid.

    bytes32 public constant imageId = ImageID.JSON_PARSER_ID;
    mapping (string => DataFeedStorage) dataFeedStorages;
    uint constant PAIRS_AMOUNT = 5; // hardcoded pairs

    /// @notice Initialize the contract, binding it to a specified RISC Zero verifier.
    constructor(
        IRiscZeroVerifier _risc0_verifier,
        IAutomataDcapAttestationFee _sgx_quote_verifier,
        string[PAIRS_AMOUNT] memory /* array size must be fixed in memory */ pair_names
    ) {
        risc0_verifier = _risc0_verifier;
        sgx_quote_verifier = _sgx_quote_verifier;

        for (uint i = 0; i < pair_names.length; i++) {
            dataFeedStorages[pair_names[i]] = new DataFeedStorage(pair_names[i], 8 /* TODO hardcoded*/);
        }
    }

    /// @notice Set btc and eth prices with exact timestamp. Requires a RISC Zero proof that numbers are extracted from json.
    // TODO: maybe its possible to pass array of custom structs, but not obvious
    function set(
        string[PAIRS_AMOUNT] memory pair_names,
        uint64[PAIRS_AMOUNT] memory prices,
        uint64[PAIRS_AMOUNT] memory timestamps,
        bytes memory sgx_quote,
        bytes calldata seal
    ) external payable {
        // payable: sgx_quote_verifier collects fee, but it is 0 on sepolia, so now it will work with msg.value = 0

        // verify sgx_quote
        (bool success, bytes memory output) = sgx_quote_verifier.verifyAndAttestOnChain{value: msg.value}(sgx_quote);
        if (!success) {
            // fail returns bytes(error_string)
            // success returns custom output type:
            // https://github.com/automata-network/automata-dcap-attestation/blob/b49a9f296a5e0cd8b1f076ec541b1239199cadd2/contracts/verifiers/V3QuoteVerifier.sol#L154
            require(success, string(output));
        }

        // extract hashed json from quote
        require(sgx_quote.length >= 368 + 32, "SGX quote too short");
        bytes memory hashed_json = new bytes(32);
        for (uint i = 0; i < 32; i++) {
            // ugly, but will switch to quote verification inside the zkVM, so ok for now
            hashed_json[i] = sgx_quote[368 + i];
        }

        // Construct the expected journal data. Verify will fail if journal does not match.
        PairDataStruct[PAIRS_AMOUNT] memory pairs_data;
        for (uint i = 0; i < PAIRS_AMOUNT; i++) {
            pairs_data[i] = PairDataStruct(pair_names[i], prices[i], timestamps[i]);
        }
        bytes memory pairs_data_abi = abi.encode(pairs_data);
        bytes memory journal = abi.encodePacked(pairs_data_abi, hashed_json);

        // verify zk proof
        risc0_verifier.verify(seal, imageId, sha256(journal));

        // send round data to storage contracts
        for (uint i = 0; i < pairs_data.length; i++) {
            PairDataStruct memory  _current_pair_data = pairs_data[i];
            uint64 _price = _current_pair_data.price;
            uint64 _timestamp = _current_pair_data.timestamp;
            string memory _pair_name = _current_pair_data.pair_name;
            dataFeedStorages[_pair_name].setNewRound(_price, _timestamp);
        }
    }

    function getPairStorageAddress(string memory pair_name) external view returns (address) {
        address result = address(dataFeedStorages[pair_name]);
        require(result != address(0), "There is no data for requested pair");
        return result;
    }
}
