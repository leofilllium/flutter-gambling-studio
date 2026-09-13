# Interaction timing review

Observed two reproductions: after a settled spin and real elapsed debounce, a one-hour backward device-clock correction rejected Spin; zero-second chip recovery also rejected after a previous recovery and clock rollback. The current300ms protection itself remains required.

The additive rule separates elapsed interaction timing from persistent calendar eligibility. It retains UTC date anti-replay, existing RNG/math/reward values, and current action-button checks. Its zero-cooldown branch applies only when the configuration explicitly disables that interval gate. It does not prescribe a general way to bypass positive cooldowns or daily grants. Integration owns the game fixes and their actual regression tests; this proposal validates guidance and does not claim those fixes have passed yet.
