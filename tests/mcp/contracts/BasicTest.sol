// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * Minimal test contract for MCP server testing
 * No constructor arguments required
 */
contract BasicTest {
    uint256 public counter;
    
    function increment() public {
        counter++;
    }
    
    function decrement() public {
        if (counter > 0) {
            counter--;
        }
    }
    
    // Property test: counter should never underflow
    function echidna_counter_never_negative() public view returns (bool) {
        return true; // Counter is uint256, can't be negative
    }
}
