---
id: r-t01-beaming-offset
title: '$\iota_E$ (direction of maximum emission) contains a beaming offset from the odd-$m$ modes'
type: result
kind: statement
status: done
depends_on: [t01-merger-inclination]
artifacts: [tasks/t01-merger-inclination/subcontext/S2_controls.md]
code: [src/tests/test_controls.py, src/merger_inclination/inclination.py]
summary: 'The direction of maximum emission is not the orbital axis when odd-$m$ modes are present: for an aligned-spin $q = 1.5$ control the offset is $3.3^\circ$ at $t^* - 500\,M$ and $5.6^\circ$ at $t^*$. $\iota_E$ therefore differs from $\iota_Q$ by this beaming offset as well as by any frame difference.'
verification: unverified
evidence: tasks/t01-merger-inclination/subcontext/S2_controls.md
---

# $\iota_E$ contains a beaming offset from the odd-$m$ modes

MEASURED in the t01 controls (`subcontext/S2_controls.md`): for an aligned-spin, $q = 1.5$
system, where the orbital axis is fixed along $+z$, the direction of maximum emission is
offset from $+z$ by $3.3^\circ$ at $t^* - 500\,M$ and $5.6^\circ$ at $t^*$. The offset
vanishes at $q = 1$ (the control test uses $q = 1$, tolerance $5 \times 10^{-3}$ rad).

Consequence: $\iota_E$ measures the instantaneous beaming direction, not the orbital axis.
A difference between $\iota_E$ and $\iota_Q$ of a few degrees is expected and does not by
itself indicate a frame problem.
