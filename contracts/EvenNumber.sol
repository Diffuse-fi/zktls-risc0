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
import {ImageID} from "./ImageID.sol"; // auto-generated contract after running `cargo build`.

/// @title A starter application using RISC Zero.
/// @notice This basic application holds a number, guaranteed to be even.
/// @dev This contract demonstrates one pattern for offloading the computation of an expensive
///      or difficult to implement function to a RISC Zero guest running on the zkVM.
contract EvenNumber {
    /// @notice RISC Zero verifier contract address.
    IRiscZeroVerifier public immutable verifier;
    /// @notice Image ID of the only zkVM binary to accept verification from.
    ///         The image ID is similar to the address of a smart contract.
    ///         It uniquely represents the logic of that guest program,
    ///         ensuring that only proofs generated from a pre-defined guest program
    ///         (in this case, checking if a number is even) are considered valid.
    bytes32 public constant imageId = ImageID.IS_EVEN_ID;

    /// @notice A numbers that are guaranteed, by the RISC Zero zkVM, to be extracted from a json file.
    ///         Can be set by calling the `set` function.
    mapping(uint256 => uint256) public btc_price;
    mapping(uint256 => uint256) public eth_price;

    /// @notice Initialize the contract, binding it to a specified RISC Zero verifier.
    constructor(IRiscZeroVerifier _verifier) {
        verifier = _verifier;
    }

    /// @notice Set btc and eth prices with exact timestamp. Requires a RISC Zero proof that numbers are extracted from json.
    function set(uint256 _btc_price, uint256 _eth_price, uint256 _timestamp, bytes calldata seal) public {
        // Construct the expected journal data. Verify will fail if journal does not match.
        bytes memory journal = abi.encode(_btc_price, _eth_price, _timestamp);
        verifier.verify(seal, imageId, sha256(journal));

        btc_price[_timestamp] = _btc_price;
        eth_price[_timestamp] = _eth_price;
    }

    /// @notice Returns the prices at requested timestamp.
    function get(uint256 timestamp) public view returns (uint256, uint256) {
        return (btc_price[timestamp], eth_price[timestamp]);
    }
}
