# Background guard validation
Reproduction: two inventories contain identical full path/line/content records in different orders.
Exact comparison rejects them; sorted comparison accepts them.
Changing, adding or removing a selecting reference still fails the normalized comparison.
Duplicate counts are retained by sorting a list rather than deduplicating a set.
Raw evidence and independent image hashes remain mandatory.
No runtime asset or quality gate was changed.
