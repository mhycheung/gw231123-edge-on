"""Numerical settings, declared in one place (R04). Values from plan.md of t01."""

DEFAULTS = {
    "model": "NRSur7dq4v2",   # gwsurrogate model name
    "dt": 0.1,                # time step of the surrogate evaluation, M
    "f_low": 0.0,             # 0: full surrogate length
    "peak_tol": 0.01,         # tolerance on t*, M
    "n_sphere": 20000,        # Fibonacci sphere points for the emission maximum (~1.6 deg)
    "angle_tol": 1e-6,        # Nelder-Mead tolerance on the emission direction, rad
    "series_before": 1000.0,  # iota_E(t) from t* - series_before ...
    "series_after": 50.0,     # ... to t* + series_after, M
    "series_step": 1.0,       # spacing of iota_E(t), M
}
