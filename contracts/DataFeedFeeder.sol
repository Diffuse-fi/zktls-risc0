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

import {IAutomataDcapAttestationFee} from "./IAutomataDcapAttestationFee.sol";
import "./DataFeedStorage.sol";

/// @title A starter application using RISC Zero.
/// @notice This basic application holds a number, guaranteed to be even.
/// @dev This contract demonstrates one pattern for offloading the computation of an expensive
///      or difficult to implement function to a RISC Zero guest running on the zkVM.

contract DataFeedFeeder {
    /// @notice Automata Intel SGX quote verifier contract address.
    IAutomataDcapAttestationFee public immutable sgx_quote_verifier;

    /// @notice Image ID of the only zkVM binary to accept verification from.
    ///         The image ID is similar to the address of a smart contract.
    ///         It uniquely represents the logic of that guest program,
    ///         ensuring that only proofs generated from a pre-defined guest program
    ///         (in this case, checking if a number is even) are considered valid.

    mapping (string => DataFeedStorage) dataFeedStorages;
    uint constant PAIRS_AMOUNT = 5; // hardcoded pairs

    /// @notice Initialize the contract, binding it to a specified RISC Zero verifier.
    constructor(
        IAutomataDcapAttestationFee _sgx_quote_verifier,
        string[PAIRS_AMOUNT] memory /* array size must be fixed in memory */ pair_names
    ) {
        sgx_quote_verifier = _sgx_quote_verifier;

        for (uint i = 0; i < pair_names.length; i++) {
            dataFeedStorages[pair_names[i]] = new DataFeedStorage(pair_names[i], 8 /* TODO hardcoded*/);
        }
    }

    /// @notice Set btc and eth prices with exact timestamp. Requires a RISC Zero proof that numbers are extracted from json.
    // TODO: maybe its possible to pass array of custom structs, but not obvious
    function set(
        string[PAIRS_AMOUNT] calldata pair_names,
        uint256[PAIRS_AMOUNT] calldata prices,
        uint256[PAIRS_AMOUNT] calldata timestamps,
        bytes calldata sgx_verification_journal,
        bytes calldata sgx_verification_seal
    ) external payable {
        // payable: sgx_quote_verifier collects fee, but it is 0 on sepolia, so now it will work with msg.value = 0

        // verify sgx_quote
        (bool success, bytes memory output) = sgx_quote_verifier.verifyAndAttestWithZKProof{value: msg.value}(sgx_verification_journal, 1, sgx_verification_seal);
        if (!success) {
            // fail returns bytes(error_string)
            // success returns custom output type:
            // https://github.com/automata-network/automata-dcap-attestation/blob/b49a9f296a5e0cd8b1f076ec541b1239199cadd2/contracts/verifiers/V3QuoteVerifier.sol#L154
            // require(success, string(output)); // found one or more collaterals mismatch
        }

        bytes32[] memory hashes = new bytes32[](PAIRS_AMOUNT * 3);

        for (uint256 i = 0; i < PAIRS_AMOUNT; i++) {
            hashes[i*3] = keccak256(abi.encodePacked(pair_names[i]));
            hashes[i*3 + 1] = keccak256(abi.encodePacked(prices[i]));
            hashes[i*3 + 2] = keccak256(abi.encodePacked(timestamps[i]));
        }
        bytes memory concatenated;

        for (uint256 i = 0; i < hashes.length; i++) {
            concatenated = abi.encodePacked(concatenated, hashes[i]);
        }

        bytes32 hashed_input_data = keccak256(concatenated);

        // extract hashed json from quote
        require(sgx_verification_journal.length >= 335 + 32, "SGX quote too short");
        bytes memory data_hash_from_sgx = new bytes(32);
        for (uint i = 0; i < 32; i++) {
            // ugly, but will switch to quote verification inside the zkVM, so ok for now
            data_hash_from_sgx[i] = sgx_verification_journal[335 + i];
        }

        require(hashed_input_data ==bytes32(data_hash_from_sgx), "hashed_input_data != data_hash_from_sgx");

        // send round data to storage contracts
        for (uint i = 0; i < pair_names.length; i++) {
            dataFeedStorages[pair_names[i]].setNewRound(prices[i], timestamps[i]);
        }
    }

    function getPairStorageAddress(string memory pair_name) external view returns (address) {
        address result = address(dataFeedStorages[pair_name]);
        require(result != address(0), "There is no data for requested pair");
        return result;
    }
}
