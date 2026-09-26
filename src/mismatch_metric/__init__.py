"""Mismatch metric of NRSur7dq4 over the intrinsic parameters and the inclination at merger,
with the extrinsic nuisances profiled (task t03-mismatch-volume).

Conventions (R01): q = m2/m1 <= 1 (bilby); M detector-frame total mass in Msun; spins
Cartesian in the LAL L-n frame at f_ref = 10 Hz; iota, phi_ref as passed to LAL; angles in
radians; t_c in s. Inner product 4 Re sum_D int a b^* / S_D df over 20-448 Hz with the PE's
PSDs. The metric is g_ij = <d_i h^, d_j h^> for the unit-norm signal h^, so that the mismatch
1 - <h^(x), h^(x + dx)> = dx^T g dx / 2 to second order.
"""
