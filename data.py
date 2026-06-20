# data.py
"""
MODULE 1: DATA — Build sector lattice and generate synthetic GARCH universe
with embedded stress regimes.
"""
import numpy as np
import config

def log(msg):
    from datetime import datetime
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def build_sector_lattice():
    n_cols, n_rows = config.CONFIG["LATTICE_SHAPE"]
    lattice = {}
    for col in range(n_cols):
        for row in range(n_rows):
            idx = col * n_rows + row
            lattice[idx] = (col, row)
    log(f"Lattice built: {n_cols}×{n_rows} = {len(lattice)} assets")
    return lattice

def get_horizontal_bonds():
    n_cols, n_rows = config.CONFIG["LATTICE_SHAPE"]
    bonds = []
    for col in range(n_cols - 1):
        for row in range(n_rows):
            i = col * n_rows + row
            j = (col + 1) * n_rows + row
            bonds.append((i, j))
    assert len(bonds) == 25
    return bonds

def get_vertical_bonds():
    n_cols, n_rows = config.CONFIG["LATTICE_SHAPE"]
    bonds = []
    for col in range(n_cols):
        for row in range(n_rows - 1):
            i = col * n_rows + row
            j = col * n_rows + (row + 1)
            bonds.append((i, j))
    assert len(bonds) == 24
    return bonds

def get_plaquettes():
    n_cols, n_rows = config.CONFIG["LATTICE_SHAPE"]
    plaqs = []
    for col in range(n_cols - 1):
        for row in range(n_rows - 1):
            i = col * n_rows + row
            j = (col + 1) * n_rows + row
            k = (col + 1) * n_rows + (row + 1)
            l = col * n_rows + (row + 1)
            plaqs.append((i, j, k, l))
    assert len(plaqs) == 20
    return plaqs

def _build_correlation_matrix(stress_active):
    n = config.CONFIG["N_ASSETS"]
    aps = config.CONFIG["ASSETS_PER_SECTOR"]
    if stress_active:
        within = config.CONFIG["STRESS_WITHIN_CORR"]
        cross = config.CONFIG["STRESS_CROSS_CORR"]
    else:
        within = config.CONFIG["BASE_WITHIN_CORR"]
        cross = config.CONFIG["BASE_CROSS_CORR"]
    C = np.full((n, n), cross)
    for s in range(config.CONFIG["N_SECTORS"]):
        for i in range(aps):
            for j in range(aps):
                if i != j:
                    C[s * aps + i, s * aps + j] = within
    np.fill_diagonal(C, 1.0)
    return C

def simulate_garch_universe():
    T = config.CONFIG["T_TOTAL"]
    N = config.CONFIG["N_ASSETS"]
    rng = np.random.default_rng(42)

    omega = config.CONFIG["GARCH_OMEGA"]
    alpha = config.CONFIG["GARCH_ALPHA"]
    beta = config.CONFIG["GARCH_BETA"]
    sigma2_0 = omega / (1.0 - alpha - beta)

    garch_shocks = rng.standard_normal(T) * np.sqrt(sigma2_0)
    is_stress = np.zeros(T, dtype=bool)
    for (s, e) in config.CONFIG["STRESS_WINDOWS"]:
        is_stress[s:e] = True

    sigma2 = np.zeros(T)
    sigma2[0] = sigma2_0
    for t in range(1, T):
        w = omega * (config.CONFIG["STRESS_OMEGA_MULT"] if is_stress[t] else 1.0)
        sigma2[t] = w + alpha * garch_shocks[t - 1] ** 2 + beta * sigma2[t - 1]
        sigma2[t] = np.clip(sigma2[t], sigma2_0 * 0.1, sigma2_0 * 100.0)

    C_normal = _build_correlation_matrix(False)
    C_stress = _build_correlation_matrix(True)
    L_normal = np.linalg.cholesky(C_normal + 1e-8 * np.eye(N))
    L_stress = np.linalg.cholesky(C_stress + 1e-8 * np.eye(N))

    log_rets = np.zeros((T, N))
    for t in range(T):
        L = L_stress if is_stress[t] else L_normal
        shocks = L @ rng.standard_normal(N)
        log_rets[t] = shocks * np.sqrt(sigma2[t])

    vol_proxy = np.sqrt(sigma2) * np.sqrt(252)
    log(f"Generated {T}×{N} returns. Stress days: {is_stress.sum()}")
    return log_rets, vol_proxy, is_stress

def inject_stress_regimes(log_rets, vol_proxy, is_stress):
    return log_rets, vol_proxy, is_stress