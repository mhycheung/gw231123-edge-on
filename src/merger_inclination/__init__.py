"""Orbital inclination at the peak of the observed strain, from NRSur7dq4(v2).

Conventions (stated once, R01):
- Frame: the LAL source frame at f_ref, which is gwsurrogate's inertial frame: z along the
  orbital angular momentum at f_ref, x from the lighter to the heavier BH.
- Line of sight: N = n(iota, pi/2 - phase) in that frame (LAL / gwsurrogate convention).
- Strain: h = h_+ - i h_x = sum_lm h_lm -2Y_lm(theta, phi).
- Units: geometric (G = c = 1), times in units of the total detector-frame mass M. Angles in
  radians.
"""

from .defaults import DEFAULTS  # noqa: F401
