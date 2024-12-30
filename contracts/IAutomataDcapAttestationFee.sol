//SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

/// @title Automata's sgx_quote verifier.
/// @notice Takes sgx quote and returns bool result reason for fail / custom data type for success.
/// @dev custom data type:
/// https://github.com/automata-network/automata-dcap-attestation/blob/b49a9f296a5e0cd8b1f076ec541b1239199cadd2/contracts/verifiers/V3QuoteVerifier.sol#L154

interface IAutomataDcapAttestationFee {
    function verifyAndAttestOnChain(bytes calldata rawQuote) external payable returns (bool, bytes memory);
}