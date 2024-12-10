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

import {RiscZeroCheats} from "risc0/test/RiscZeroCheats.sol";
import {console2} from "forge-std/console2.sol";
import {Test} from "forge-std/Test.sol";
import {IRiscZeroVerifier} from "risc0/IRiscZeroVerifier.sol";
import {DataFeedFeeder} from "../contracts/DataFeedFeeder.sol";
import {DataFeedStorage} from "../contracts/DataFeedStorage.sol";
import {Elf} from "./Elf.sol"; // auto-generated contract after running `cargo build`.

contract DataFeedFeederTest is RiscZeroCheats, Test {
    DataFeedFeeder public dataFeedFeeder;

    function test_DataFeedStorage_decimals() public {
        DataFeedStorage dataFeedStorage = new DataFeedStorage("asdf", 10);
        assertEq(dataFeedStorage.decimals(), 10);
    }

    function test_DataFeedStorage_description() public {
        DataFeedStorage dataFeedStorage = new DataFeedStorage("asdf", 10);
        assertEq(dataFeedStorage.description(), "asdf");
    }

    function test_DataFeedStorage_latestRound() public {
        DataFeedStorage dataFeedStorage = new DataFeedStorage("asdf", 10);
        dataFeedStorage.setNewRound(11111, 22222);
        assertEq(dataFeedStorage.latestRound(), 0);
    }

    function test_DataFeedStorage_latesAnswer() public {
        DataFeedStorage dataFeedStorage = new DataFeedStorage("asdf", 10);
        dataFeedStorage.setNewRound(11111, 22222);
        assertEq(dataFeedStorage.latestAnswer(), 11111);
    }

    function test_DataFeedStorage_latestRoundData() public {
        DataFeedStorage dataFeedStorage = new DataFeedStorage("asdf", 10);
        dataFeedStorage.setNewRound(11111, 22222);
        (uint80 roundId, uint256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound) =
            dataFeedStorage.latestRoundData();

        assertEq(roundId, 0);
        assertEq(answer, 11111);
        assertEq(startedAt, 22222);
        assertEq(updatedAt, 22222);
        assertEq(answeredInRound, 0);
    }

    function test_DataFeedStorage_fail_latestRound() public {
        DataFeedStorage dataFeedStorage = new DataFeedStorage("asdf", 10);
        // Expecting revert before calling a function that should fail
        vm.expectRevert("there has been no rounds yet");
        dataFeedStorage.latestRound();
    }

    function test_DataFeedStorage_fail_latestRoundData() public {
        DataFeedStorage dataFeedStorage = new DataFeedStorage("asdf", 10);
        // Expecting revert before calling a function that should fail
        vm.expectRevert("there has been no rounds yet");
        dataFeedStorage.latestRoundData();
    }
}
