# Semantic activation regression review

Four functional DOM tests were run against the unchanged verifier and failed: offscreen placeholder, offscreen placeholder inside shadow DOM, absent placeholder, and already enabled semantics. The tests execute the actual extracted reader against a stateful minimal DOM; clicking the hidden placeholder enables a real Spin node, while physical taps are separately counted. They test behavior rather than a prescribed text pattern.

The fix activates the intended accessibility element directly and removes the fallback top-left game tap. Actual gameplay actions still use CDP physical input; screenshot capture, error collection and viewport checks remain untouched. The real Flutter3.44 Chrome session independently confirmed direct placeholder activation yielded usable controls and a settled spin. The fixture does not prove compatibility with every future browser/Flutter version, so final runtime remains required.
