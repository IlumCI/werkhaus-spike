// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

/// Stand-in for a template instance: the parameters a model chose, fixed at
/// deploy. Phase 0 attests this bytecode; Phase 1 replaces it with the real
/// staking-rewards template.
contract StakingConfig {
    uint256 public immutable lockSeconds;
    uint256 public immutable cooldownSeconds;
    uint256 public immutable minStake;

    error Invalid();

    constructor(uint256 lockDays, uint256 cooldownHours, uint256 minStakeTokens) {
        if (lockDays > 365 || cooldownHours > 168 || minStakeTokens == 0) revert Invalid();
        lockSeconds = lockDays * 1 days;
        cooldownSeconds = cooldownHours * 1 hours;
        minStake = minStakeTokens * 1 ether;
    }
}
