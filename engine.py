# engine.py
"""
MODULE 2: ENGINE — BKT topological vortex unbinding computation pipeline.
"""
import numpy as np
import config
from data import get_horizontal_bonds, get_vertical_bonds, get_plaquettes
from scipy.signal import hilbert
from scipy.optimize import curve_fit

def compute_instantaneous_phase(returns, window=21):
    T, N = returns.shape
    half = window // 2
    theta = np.full((T, N), np.nan)
    for i in range(N):
        for t in range(half, T - half):
            seg = returns[t - half:t + half + 1, i].copy()
            seg = seg - np.mean(seg)
            if np.std(seg) < 1e-12:
                theta[t, i] = 0.0
            else:
                analytic = hilbert(seg)
                theta[t, i] = np.angle(analytic[half])
    return theta

def compute_rolling_correlation(returns, window=40):
    T, N = returns.shape
    rho = np.full((T, N, N), np.nan)
    for t in range(window - 1, T):
        seg = returns[t - window + 1:t + 1, :]
        seg_d = seg - seg.mean(axis=0)
        std = seg.std(axis=0)
        std[std < 1e-12] = 1e-12
        corr = (seg_d.T @ seg_d) / (window * np.outer(std, std))
        np.fill_diagonal(corr, 1.0)
        rho[t] = corr
    return rho

def compute_rolling_coupling(rho):
    return np.where(np.isnan(rho), np.nan, np.maximum(0.0, rho))

def compute_effective_temperature(returns, window=40):
    T, N = returns.shape
    daily_cross_std = np.std(returns, axis=1)
    T_eff = np.full(T, np.nan)
    for t in range(window - 1, T):
        T_eff[t] = np.mean(daily_cross_std[t - window + 1:t + 1]) * np.sqrt(252)
    return T_eff

def compute_phase_stiffness(J, T_eff):
    T = J.shape[0]
    K = np.full(T, np.nan)
    triu_idx = np.triu_indices(J.shape[1], k=1)
    for t in range(T):
        if np.isnan(J[t]).any() or np.isnan(T_eff[t]): continue
        J_mean = np.mean(J[t][triu_idx])
        T_clipped = max(T_eff[t], config.CONFIG["T_EFF_FLOOR"])
        K[t] = J_mean / T_clipped
    return K

def _wrap(x):
    return x - 2.0 * np.pi * np.round(x / (2.0 * np.pi))

def compute_vortex_field(theta, lattice_shape):
    plaquettes = get_plaquettes()
    T = theta.shape[0]
    n_plaq = len(plaquettes)
    q = np.zeros((T, n_plaq))
    for t in range(T):
        if np.isnan(theta[t]).any():
            q[t] = np.nan
            continue
        for p_idx, (i, j, k, l) in enumerate(plaquettes):
            d1 = _wrap(theta[t, j] - theta[t, i])
            d2 = _wrap(theta[t, k] - theta[t, j])
            d3 = _wrap(theta[t, l] - theta[t, k])
            d4 = _wrap(theta[t, i] - theta[t, l])
            winding = (d1 + d2 + d3 + d4) / (2.0 * np.pi)
            q[t, p_idx] = winding
            assert abs(winding - round(winding)) < 1e-6
    return q

def compute_vortex_density(q):
    T = q.shape[0]
    n_plaq = q.shape[1]
    n_v = np.full(T, np.nan)
    for t in range(T):
        if np.isnan(q[t]).any(): continue
        n_v[t] = np.sum(np.abs(q[t]) > 0.5) / n_plaq
    return n_v

def compute_helicity_modulus(theta, J, T_eff, lattice_shape):
    h_bonds = get_horizontal_bonds()
    T = theta.shape[0]
    e_daily = np.full(T, np.nan)
    s_daily = np.full(T, np.nan)
    for t in range(T):
        if np.isnan(theta[t]).any() or np.isnan(J[t]).any(): continue
        cos_vals = np.empty(len(h_bonds))
        sin_vals = np.empty(len(h_bonds))
        for b_idx, (i, j) in enumerate(h_bonds):
            dphi = theta[t, i] - theta[t, j]
            cos_vals[b_idx] = J[t, i, j] * np.cos(dphi)
            sin_vals[b_idx] = J[t, i, j] * np.sin(dphi)
        e_daily[t] = np.mean(cos_vals)
        s_daily[t] = np.mean(sin_vals)
    
    window = config.CONFIG["WINDOW_HELICITY"]
    Upsilon = np.full(T, np.nan)
    for t in range(window - 1, T):
        e_w = e_daily[t - window + 1:t + 1]
        s_w = s_daily[t - window + 1:t + 1]
        if np.isnan(e_w).any() or np.isnan(s_w).any(): continue
        T_clipped = max(T_eff[t], config.CONFIG["T_EFF_FLOOR"])
        Upsilon[t] = np.mean(e_w) - np.mean(s_w ** 2) / T_clipped
    return Upsilon

def classify_regime(Upsilon, T_eff):
    threshold = config.CONFIG["KT_CRITICAL"]
    T = len(Upsilon)
    regime = np.array(['UNKNOWN'] * T, dtype=object)
    Upsilon_tilde = np.full(T, np.nan)
    for t in range(T):
        if np.isnan(Upsilon[t]) or np.isnan(T_eff[t]): continue
        T_clipped = max(T_eff[t], config.CONFIG["T_EFF_FLOOR"])
        Upsilon_tilde[t] = Upsilon[t] / T_clipped
        regime[t] = 'QLRO-COHERENT' if Upsilon_tilde[t] > threshold else 'VORTEX-UNBOUND'
    return regime, Upsilon_tilde

def compute_phase_correlation_surface(theta, rho, n_bins=40):
    T, N = theta.shape
    C = np.full((T, n_bins), np.nan)
    r_edges = np.linspace(0, 2, n_bins + 1)
    r_centers = 0.5 * (r_edges[:-1] + r_edges[1:])
    triu = np.triu_indices(N, k=1)
    for t in range(T):
        if np.isnan(theta[t]).any() or np.isnan(rho[t]).any(): continue
        d_ij = np.sqrt(2.0 * np.maximum(0.0, 1.0 - rho[t][triu]))
        cos_diff = np.cos(theta[t, triu[0]] - theta[t, triu[1]])
        for b in range(n_bins):
            mask = (d_ij >= r_edges[b]) & (d_ij < r_edges[b + 1])
            if b == n_bins - 1:
                mask = (d_ij >= r_edges[b]) & (d_ij <= r_edges[b + 1])
            if mask.sum() > 0:
                C[t, b] = np.mean(cos_diff[mask])
    return C, r_centers

def fit_decay_models(C, r_centers):
    T, n_bins = C.shape
    eta = np.full(T, np.nan)
    xi = np.full(T, np.nan)
    best_model = np.array(['UNKNOWN'] * T, dtype=object)
    floor = config.CONFIG["C_FLOOR"]
    log_r = np.log(r_centers + 1e-10)
    for t in range(T):
        if np.isnan(C[t]).all(): continue
        c_clipped = np.maximum(C[t], floor)
        log_c = np.log(c_clipped)
        valid = np.isfinite(log_c) & np.isfinite(log_r) & ~np.isnan(C[t])
        if valid.sum() < 3: continue
        ss_tot = np.sum((log_c[valid] - np.mean(log_c[valid])) ** 2)
        if ss_tot < 1e-15: continue
        
        A_p = np.vstack([log_r[valid], np.ones(valid.sum())]).T
        sol_p, _, _, _ = np.linalg.lstsq(A_p, log_c[valid], rcond=None)
        r2_p = 1.0 - np.sum((log_c[valid] - A_p @ sol_p) ** 2) / ss_tot
        eta[t] = np.clip(-sol_p[0], 0, 5)
        
        A_e = np.vstack([r_centers[valid], np.ones(valid.sum())]).T
        sol_e, _, _, _ = np.linalg.lstsq(A_e, log_c[valid], rcond=None)
        r2_e = 1.0 - np.sum((log_c[valid] - A_e @ sol_e) ** 2) / ss_tot
        xi[t] = np.clip(-1.0 / sol_e[0], 0, 5) if sol_e[0] < -1e-10 else np.nan
        
        if r2_p >= r2_e: best_model[t] = 'POWER'
        else: best_model[t] = 'EXPONENTIAL'
    return eta, xi, best_model

def find_crossings(Upsilon_tilde, threshold):
    crossings = []
    valid = ~np.isnan(Upsilon_tilde)
    for t in range(1, len(Upsilon_tilde)):
        if valid[t] and valid[t - 1]:
            if (Upsilon_tilde[t - 1] - threshold) * (Upsilon_tilde[t] - threshold) < 0:
                crossings.append(t)
    return crossings

def fit_kosterlitz_singularity(xi, T_eff, best_model, crossing_indices):
    results = []
    for idx in crossing_indices:
        lo, hi = max(0, idx - 15), min(len(xi), idx + 16)
        t_range = np.arange(lo, hi)
        valid = (np.isfinite(xi[t_range]) & np.isfinite(T_eff[t_range]) & (best_model[t_range] == 'EXPONENTIAL'))
        if valid.sum() < 4: results.append(None); continue
        T_KT = T_eff[idx]
        def model(T, a, b): return a * np.exp(b / np.sqrt(np.abs(T / T_KT - 1.0) + 1e-10))
        try:
            popt, _ = curve_fit(model, T_eff[t_range][valid], xi[t_range][valid], p0=[0.5, 1.0], maxfev=5000)
            results.append({'a': float(popt[0]), 'b': float(popt[1]), 'T_KT': float(T_KT), 't_fit': t_range[valid]})
        except: results.append(None)
    return results

def vortex_fugacity(K, mu=None):
    if mu is None: mu = config.CONFIG["MU_CORE"]
    return np.where(np.isnan(K), np.nan, np.exp(-mu * np.nan_to_num(K, nan=0.0)))

def integrate_rg_flow(K, y, l_max=8, n_steps=200):
    T = len(K)
    rg_label = np.array(['UNKNOWN'] * T, dtype=object)
    dl = l_max / n_steps
    pi = np.pi
    for t in range(T):
        if np.isnan(K[t]) or np.isnan(y[t]): continue
        K_inv = 1.0 / max(K[t], 1e-10)
        y_t = y[t]
        escaped = False
        for _ in range(n_steps):
            def f_ki(ki, yy): return 4.0 * pi**3 * yy**2
            def f_y(ki, yy): return (2.0 - pi / max(ki, 1e-10)) * yy
            k1ki, k1y = f_ki(K_inv, y_t), f_y(K_inv, y_t)
            k2ki, k2y = f_ki(K_inv + 0.5*dl*k1ki, y_t + 0.5*dl*k1y), f_y(K_inv + 0.5*dl*k1ki, y_t + 0.5*dl*k1y)
            k3ki, k3y = f_ki(K_inv + 0.5*dl*k2ki, y_t + 0.5*dl*k2y), f_y(K_inv + 0.5*dl*k2ki, y_t + 0.5*dl*k2y)
            k4ki, k4y = f_ki(K_inv + dl*k3ki, y_t + dl*k3y), f_y(K_inv + dl*k3ki, y_t + dl*k3y)
            K_inv += (dl/6.0)*(k1ki + 2*k2ki + 2*k3ki + k4ki)
            y_t += (dl/6.0)*(k1y + 2*k2y + 2*k3y + k4y)
            K_inv, y_t = max(K_inv, 1e-10), max(y_t, 0.0)
            if y_t > 5.0: rg_label[t] = 'RG-DISORDERED'; escaped = True; break
        if not escaped:
            if y_t < 0.01: rg_label[t] = 'RG-ORDERED'
            elif y_t > y[t] * 1.5: rg_label[t] = 'RG-DISORDERED'
            else: rg_label[t] = 'RG-ORDERED'
    return rg_label

def compute_rg_agreement(regime, rg_label, t_valid):
    agree = count = 0
    for t in t_valid:
        if regime[t] == 'UNKNOWN' or rg_label[t] == 'UNKNOWN': continue
        count += 1
        if (regime[t] == 'QLRO-COHERENT') == (rg_label[t] == 'RG-ORDERED'): agree += 1
    return agree / max(count, 1)

def compute_mean_correlation_distance(rho, t_valid):
    T, N, _ = rho.shape
    mean_d = np.full(T, np.nan)
    triu = np.triu_indices(N, k=1)
    for t in t_valid:
        mean_d[t] = np.mean(np.sqrt(2.0 * np.maximum(0.0, 1.0 - rho[t][triu])))
    return mean_d