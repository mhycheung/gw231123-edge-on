# S1: t_ref definition (2026-09-25)

First S1 gate run (`S1/gate_2026-09-25.json` before the fix, src 602eebf): check (b)
|iota_Q(t_ref) - iota| < 1e-3 rad failed, max 0.021 rad (posterior test chunk), 0.0064 rad (prior).

Cause (tested): t_ref was estimated as the time where d(orbphase)/dt = pi f_ref. For the four
worst posterior test samples (indices 53, 97, 69, 80) that estimate lies 3-11 M from the time
where q_copr is closest to the identity (min |q - 1| = 3e-5 to 1e-4, orbphase there within
0.007 rad of 0). At that time iota_Q - iota = -5e-5, -1.1e-4, -6e-5, +1.7e-4 rad. There
d(orbphase)/dt equals 0.995-0.999 pi f_ref, and iota changes at up to 2.3e-3 rad/M, which
accounts for the error. The frame and the code are right; the t_ref estimate was wrong.

Fix: `waveform.evaluate` sets t_ref to the grid time (0.1 M) with q_copr closest to the
identity, the epoch at which gwsurrogate fixes the frame (init_quat default). This affects the
reported t_ref (t01 reported -195.6 M for the ML sample with the old estimate) and check (b)
only; iota_Q(t), iota_E(t) and all t01 angles at t* and t = 0 do not use t_ref.
