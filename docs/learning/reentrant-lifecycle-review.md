# Reentrant lifecycle guidance review

A real Flutter regression probe demonstrated both notifier disposal during notification and mutation of the controller Set during iteration. The second controller missed its update. The proposed addition targets the existing lifecycle section and explicitly distinguishes those two mechanics within the same reentrant-release cause.

Immediate inactive marking and timer cancellation retain the current disposal safety guarantees; only notifier teardown waits for notification completion. Stable iteration prevents callback mutation from invalidating the traversal, while inactive checks prevent subsequent work on released entries. The two-subscriber regression describes observable behavior, not a specific implementation. No change to outcome RNG, math, balances, reward policy or permission scope. Game integration owns the actual fix and maintained tests; this proposal is a guidance correction awaiting human review.
