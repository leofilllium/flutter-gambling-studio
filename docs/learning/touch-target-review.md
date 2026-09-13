# Transformed touch target audit review

This proposal changes the existing B15 check only. A Joker’s Encore Chrome run measured SPIN semantic rectangles at 55.56–55.87 logical pixels while static widget geometry reported the required 56. The cause was an idle scale around the whole interactive subtree. The saved evidence distinguishes that observed geometry failure from separate composition and network findings.

The revision preserves the existing 48×48/56 minimums, both text scales, enabled/disabled checks, label fitting and alignment. It explicitly samples idle and press extrema and examines transformed interaction and semantic bounds. A stable interaction box with animated decoration resolves this cause without forbidding button feedback or requiring every animation to change shape. The rule does not alter game math, art, compliance, runtime gates or authorization. No new skill is added.

Validation is a structured guidance review: compare the one changed B15 row to the remote base, assert all prior constraints remain, verify the frontmatter is unchanged, verify the mobile/gameplay contract links resolve, and ensure no unrelated source changes. The current game's implementation regression and subsequent Chrome recheck remain the game's QA responsibility. This proposal alone does not prove that implementation is fixed.
