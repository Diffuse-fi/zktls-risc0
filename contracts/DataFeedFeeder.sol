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
import "./DataFeedStorage.sol";
import "./PairDataStruct.sol";
// import {ImageID} from "./ImageID.sol"; // auto-generated contract after running `cargo build`.
import {ImageID} from "./ImageID_manually_generated.sol"; // TODO: remove github CI crutch

/// @title A starter application using RISC Zero.
/// @notice This basic application holds a number, guaranteed to be even.
/// @dev This contract demonstrates one pattern for offloading the computation of an expensive
///      or difficult to implement function to a RISC Zero guest running on the zkVM.

contract DataFeedFeeder {
    /// @notice RISC Zero verifier contract address.
    IRiscZeroVerifier public immutable verifier;
    /// @notice Image ID of the only zkVM binary to accept verification from.
    ///         The image ID is similar to the address of a smart contract.
    ///         It uniquely represents the logic of that guest program,
    ///         ensuring that only proofs generated from a pre-defined guest program
    ///         (in this case, checking if a number is even) are considered valid.

    bytes32 public constant imageId = ImageID.JSON_PARSER_ID;
    mapping (string => DataFeedStorage) dataFeedStorages;
    uint constant PAIRS_AMOUNT = 4;

    /// @notice Initialize the contract, binding it to a specified RISC Zero verifier.
    constructor(IRiscZeroVerifier _verifier, string[PAIRS_AMOUNT] memory /* array size must be fixed in memory */ pair_names) {
        verifier = _verifier;

        for (uint i = 0; i < pair_names.length; i++) {
            dataFeedStorages[pair_names[i]] = new DataFeedStorage(pair_names[i], 5 /* TODO hardcoded*/);
        }
    }

    /// @notice Set btc and eth prices with exact timestamp. Requires a RISC Zero proof that numbers are extracted from json.
    // TODO: maybe its possible to pass array of custom structs, but not obvious
    function set(
        string[PAIRS_AMOUNT] memory pair_names,
        uint64[PAIRS_AMOUNT] memory prices,
        uint64[PAIRS_AMOUNT] memory timestamps,
        bytes calldata seal
    ) public {
        // Construct the expected journal data. Verify will fail if journal does not match.
        PairDataStruct[PAIRS_AMOUNT] memory pairs_data;
        for (uint i = 0; i < PAIRS_AMOUNT; i++) {
            pairs_data[i] = PairDataStruct(pair_names[i], prices[i], timestamps[i]);
        }
        bytes memory journal = abi.encode(pairs_data);
        verifier.verify(seal, imageId, sha256(journal));

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
