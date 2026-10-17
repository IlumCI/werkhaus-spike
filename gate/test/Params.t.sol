// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import {Test} from "forge-std/Test.sol";
import {StakingConfig} from "../src/StakingConfig.sol";

/// The gate a model's output must pass: the template deploys with these
/// parameters, and a rule the schema cannot express holds.
contract ParamsTest is Test {
    function test_candidate_deploys() public {
        string memory json = vm.readFile(vm.envString("PARAMS"));
        uint256 lockDays = vm.parseJsonUint(json, ".lock_days");
        uint256 cooldownHours = vm.parseJsonUint(json, ".cooldown_hours");
        uint256 minStake = vm.parseJsonUint(json, ".min_stake_tokens");

        StakingConfig c = new StakingConfig(lockDays, cooldownHours, minStake);

        // Demo rule beyond the schema: a cooldown never outlasts a nonzero lock.
        if (lockDays > 0) assertLe(c.cooldownSeconds(), c.lockSeconds(), "cooldown longer than the lock");
    }
}
