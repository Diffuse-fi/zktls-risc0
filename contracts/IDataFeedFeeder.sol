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

import "./DataFeedStorage.sol";

/// @title A starter application using RISC Zero.
/// @notice This basic application holds btc and eth prices, extracted from json.
/// @dev This contract demonstrates one pattern for offloading the computation of an expensive
///      or difficult to implement function to a RISC Zero guest running on the zkVM.
interface IDataFeedFeeder {
    /// @notice Set btc and eth price to store on the contract. Requires a RISC Zero proof that they are extracted from json.
    function set(
        string[5] memory pair_names,
        uint64[5] memory prices,
        uint64[5] memory timestamps,
        bytes memory sgx_quote,
        bytes calldata seal
    ) external;
}
