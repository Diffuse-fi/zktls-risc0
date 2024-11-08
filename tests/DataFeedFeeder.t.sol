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
import {Elf} from "./Elf.sol"; // auto-generated contract after running `cargo build`.

contract DataFeedFeederTest is RiscZeroCheats, Test {
    DataFeedFeeder public dataFeedFeeder;

    // function setUp() public {
    //     IRiscZeroVerifier verifier = deployRiscZeroVerifier();
    //     dataFeedFeeder = new DataFeedFeeder(verifier);
    //     (uint256 btc_price, uint256 eth_price) = dataFeedFeeder.get(0);
    //     assertEq(btc_price, 0);
    //     assertEq(eth_price, 0);
    // }

    // function test_SetEven() public {
    //     uint256 number = 1234;
    //     uint256 number_2 = 5678;
    //     (bytes memory journal, bytes memory seal) = prove(Elf.JSON_PARSER_PATH, abi.encode(number, number_2));


    //     (uint256 decoded_x, uint256 decoded_y) = abi.decode(journal, (uint256, uint256));
    //     dataFeedFeeder.set(decoded_x, decoded_y, seal);

    //     (uint256 btc_price_get, uint256 eth_price_get, uint256 timestamp_get) = dataFeedFeeder.get();
    //     assertEq(x, number);
    //     assertEq(y, number_2);
    // }

    // function test_SetZero() public {
    //     uint256 number = 0;
    //     uint256 number_2 = 0;
    //     (bytes memory journal, bytes memory seal) = prove(Elf.JSON_PARSER_PATH, abi.encode(number, number_2));

    //     (uint256 decoded_x, uint256 decoded_y) = abi.decode(journal, (uint256, uint256));
    //     dataFeedFeeder.set(decoded_x, decoded_y, seal);

    //     (uint256 x, uint256 y) = dataFeedFeeder.get();
    //     assertEq(x, number);
    //     assertEq(y, number_2);
    // }
}
