# visual.py
"""
MODULE 3: VISUAL — Static PNG rendering of the BKT Market Transition dashboard.
High-contrast neon journal cover aesthetic.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import Normalize
import config

def _canvas_to_rgb(fig):
    fig.canvas.draw()
    try: return np.asarray(fig.canvas.buffer_rgba())[:, :, :3]
    except AttributeError:
        w, h = fig.canvas.get_width_height()
        return np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8).reshape(h, w, 3)

def _style_ax(ax):
    ax.set_facecolor(config.THEME["PANEL_BG"])
    for sp in ax.spines.values():
        sp.set_color(config.THEME["SPINE"]); sp.set_linewidth(0.5)
    ax.tick_params(colors=config.THEME["TEXT_DIM"], labelsize=7, direction="in", length=3)
    ax.yaxis.grid(True, color=config.THEME["GRID"], lw=0.3, alpha=0.4)

def _fill_nans_2d(arr):
    arr = arr.copy()
    for i in range(arr.shape[0]):
        row = arr[i, :]
        valid = ~np.isnan(row)
        if valid.any() and not valid.all():
            idx = np.arange(len(row))
            arr[i, :] = np.interp(idx, idx[valid], row[valid])
        elif not valid.any():
            arr[i, :] = 0.0
    return arr

def _draw_3d_surface(ax3d, data, tc, z_scale, norm):
    t_valid = data['t_valid']
    r_centers = data['r_centers']
    C_valid = data['C_valid']
    z_min, z_max = data['z_min'], data['z_max']

    n_show = min(tc, C_valid.shape[0])
    C_show = C_valid[:n_show, :] * z_scale

    R_grid = np.broadcast_to(r_centers[np.newaxis, :], (n_show, len(r_centers)))
    T_grid = np.broadcast_to(t_valid[:n_show, np.newaxis], (n_show, len(r_centers))).astype(float)

    pane_color = (0.02, 0.02, 0.02, 1)
    ax3d.xaxis.set_pane_color(pane_color); ax3d.yaxis.set_pane_color(pane_color); ax3d.zaxis.set_pane_color(pane_color)
    for axis in (ax3d.xaxis, ax3d.yaxis, ax3d.zaxis):
        axis._axinfo["grid"]["color"] = (0.13, 0.13, 0.13, 0.6)
        axis._axinfo["grid"]["linewidth"] = 0.4

    # Exaggerated Z scale for spikes and neon mesh wireframe
    ax3d.plot_surface(
        R_grid, T_grid, C_show, cmap=config.CMAP_BKT, alpha=0.90,
        rstride=1, cstride=2, edgecolor=(0.0, 0.8, 1.0, 0.1), linewidth=0.15,
        antialiased=True, vmin=norm.vmin, vmax=norm.vmax, zorder=1,
    )

    z_floor = z_min - 0.12
    try:
        ax3d.contourf(R_grid, T_grid, C_show, zdir="z", offset=z_floor,
                      cmap=config.CMAP_BKT, alpha=0.45, levels=20, vmin=norm.vmin, vmax=norm.vmax)
    except: pass

    # Ridge 1: Triple-glow Neon Orange Upsilon_tilde
    mean_d = data['mean_d']
    r1_x, r1_y, r1_z = [], [], []
    for i in range(n_show):
        t = t_valid[i]
        if np.isnan(mean_d[t]): continue
        r_bin = np.argmin(np.abs(r_centers - mean_d[t]))
        r1_x.append(r_centers[r_bin]); r1_y.append(float(t)); r1_z.append(C_valid[i, r_bin] * z_scale)

    if len(r1_x) > 1:
        ax3d.plot(r1_x, r1_y, r1_z, color=config.THEME["ORANGE"], lw=8, alpha=0.1, zorder=20)
        ax3d.plot(r1_x, r1_y, r1_z, color=config.THEME["ORANGE"], lw=3.5, alpha=0.4, zorder=21)
        ax3d.plot(r1_x, r1_y, r1_z, color=config.THEME["ORANGE_HOT"], lw=1.2, alpha=1.0, zorder=22)
        ax3d.scatter([r1_x[-1]], [r1_y[-1]], [r1_z[-1]], s=50, color=config.THEME["YELLOW"], edgecolor="white", linewidth=0.8, zorder=25)

    # Ridge 2: Triple-glow Neon Cyan Vortex Density
    n_v = data['n_v']
    nv_vals = np.array([n_v[t_valid[i]] if i < n_show else np.nan for i in range(n_show)])
    nv_valid = nv_vals[~np.isnan(nv_vals)]
    if len(nv_valid) > 0 and nv_valid.max() > 1e-10:
        nv_scaled = (z_min + (nv_vals / nv_valid.max()) * (z_max - z_min) * 0.6 * z_scale)
        m = ~np.isnan(nv_vals)
        if m.sum() > 1:
            r2_x = np.full(n_show, r_centers[0]); r2_y = t_valid[:n_show].astype(float); r2_z = nv_scaled
            ax3d.plot(r2_x[m], r2_y[m], r2_z[m], color=config.THEME["CYAN"], lw=8, alpha=0.1, zorder=18)
            ax3d.plot(r2_x[m], r2_y[m], r2_z[m], color=config.THEME["CYAN"], lw=3.5, alpha=0.4, zorder=19)
            ax3d.plot(r2_x[m], r2_y[m], r2_z[m], color="#00ffff", lw=1.2, alpha=1.0, zorder=20)
            ax3d.scatter([r2_x[m][-1]], [r2_y[m][-1]], [r2_z[m][-1]], s=50, color=config.THEME["YELLOW"], edgecolor="white", linewidth=0.8, zorder=25)

    ax3d.set_xlabel("CORRELATION DISTANCE  d", fontsize=11, fontweight="bold", color=config.THEME["TEXT_DIM"], labelpad=10, fontfamily=config.THEME["FONT"])
    ax3d.set_ylabel("TIME  t", fontsize=11, fontweight="bold", color=config.THEME["TEXT_DIM"], labelpad=10, fontfamily=config.THEME["FONT"])
    ax3d.set_zlabel(r"$C(r,t)$", fontsize=12, fontweight="bold", color=config.THEME["TEXT_DIM"], labelpad=10, fontfamily=config.THEME["FONT"])
    ax3d.tick_params(axis="both", colors=config.THEME["TEXT_DIM"], labelsize=8)
    ax3d.set_box_aspect([1.2, 1.0, 1.4]) # Exaggerated Z for visual spikes
    
    ax3d.text2D(0.02, 0.95, r"$QLRO \leftrightarrow Vortex Plasma$", transform=ax3d.transAxes, color=config.THEME["CYAN"], fontsize=10, fontfamily=config.THEME["FONT"], alpha=0.8)

def _draw_panel_1(ax, data, tc):
    t_valid = data['t_valid']; Ut = data['Upsilon_tilde']; threshold = config.CONFIG["KT_CRITICAL"]
    n_show = min(tc, len(t_valid))
    for (s, e) in config.CONFIG["STRESS_WINDOWS"]: ax.axvspan(s, e, color=config.THEME["RED"], alpha=0.06)
    for i in range(n_show):
        if Ut[t_valid[i]] > threshold: ax.axvspan(t_valid[i] - 0.5, t_valid[i] + 0.5, color=config.THEME["CYAN"], alpha=0.04)
    
    ax.plot(t_valid[:n_show], Ut[t_valid[:n_show]], color=config.THEME["CYAN"], lw=2.0, alpha=1.0, label=r"$\tilde{\Upsilon}$")
    ax.fill_between(t_valid[:n_show], Ut[t_valid[:n_show]], threshold, color=config.THEME["CYAN"], alpha=0.05)
    ax.axhline(threshold, color=config.THEME["ORANGE"], ls="--", lw=1.5, alpha=1.0, label=r"$2/\pi$")
    ax.set_ylim(-0.5, max(np.nanmax(Ut[t_valid]) * 1.2, threshold * 2))
    ax.set_title(r"$\tilde{\Upsilon}(t)$ vs $2/\pi$", color=config.THEME["TEXT"], fontsize=9, fontweight="bold", fontfamily=config.THEME["FONT"], pad=2)
    leg = ax.legend(loc="upper left", fontsize=7, facecolor=config.THEME["BG"], edgecolor=config.THEME["GRID"])
    for text in leg.get_texts(): text.set_color(config.THEME["TEXT_DIM"])

def _draw_panel_2(ax, data, tc):
    t_valid = data['t_valid']; n_v = data['n_v']; n_show = min(tc, len(t_valid))
    for (s, e) in config.CONFIG["STRESS_WINDOWS"]: ax.axvspan(s, e, color=config.THEME["RED"], alpha=0.08)
    ax.plot(t_valid[:n_show], n_v[t_valid[:n_show]], color=config.THEME["MAGENTA"], lw=2.0, alpha=1.0)
    ax.fill_between(t_valid[:n_show], 0, n_v[t_valid[:n_show]], color=config.THEME["MAGENTA"], alpha=0.2)
    ax.set_title(r"Vortex Density $n_v(t)$", color=config.THEME["TEXT"], fontsize=9, fontweight="bold", fontfamily=config.THEME["FONT"], pad=2)
    ax.set_ylim(-0.02, max(np.nanmax(n_v[t_valid]) * 1.3, 0.1))

def _draw_panel_3(ax, data, tc):
    t_valid = data['t_valid']; q = data['q']; n_show = min(tc, len(t_valid))
    q_show = np.zeros((n_show, 20))
    for i in range(n_show):
        if not np.isnan(q[t_valid[i]]).any(): q_show[i, :] = q[t_valid[i], :]
    
    q_rgb = np.full((n_show, 20, 3), 0.02)
    q_rgb[q_show == 1] = [1.0, 0.58, 0.0]
    q_rgb[q_show == -1] = [0.0, 0.95, 1.0]
    ax.imshow(q_rgb, aspect='auto', extent=[t_valid[0], t_valid[0] + n_show, -0.5, 19.5], origin='upper', interpolation='nearest')
    
    sectors = config.CONFIG["SECTORS"]
    ax.set_yticks([2, 6, 10, 14, 18]); ax.set_yticklabels([f"{sectors[c][:2]}-{sectors[c+1][:2]}" for c in range(5)], fontsize=6)
    ax.set_title("Vortex Plaquette Field", color=config.THEME["TEXT"], fontsize=9, fontweight="bold", fontfamily=config.THEME["FONT"], pad=2)

def _draw_panel_4(ax, data, tc):
    t_valid = data['t_valid']; eta = data['eta']; xi = data['xi']; T_eff = data['T_eff']
    ks_fits = data['ks_fits']; regime = data['regime']; n_show = min(tc, len(t_valid)); ts = t_valid[:n_show]
    for (s, e) in config.CONFIG["STRESS_WINDOWS"]: ax.axvspan(s, e, color=config.THEME["RED"], alpha=0.05)
    
    eta_vals = np.where(regime == 'QLRO-COHERENT', eta, np.nan)
    xi_vals = np.where(regime == 'VORTEX-UNBOUND', xi, np.nan)

    ax.plot(ts, eta_vals[ts], color=config.THEME["YELLOW"], lw=2.0, alpha=1.0, label=r"$\eta$ (QLRO)")
    ax.plot(ts, xi_vals[ts], color=config.THEME["MAGENTA"], lw=2.0, alpha=1.0, label=r"$\xi$ (disordered)")
    
    for fit in ks_fits:
        if fit is None: continue
        t_fit = fit['t_fit']; t_fit = t_fit[t_fit < t_valid[0] + n_show]
        if len(t_fit) < 2: continue
        T_fit = T_eff[t_fit]; T_KT = fit['T_KT']; a, b = fit['a'], fit['b']
        ax.plot(t_fit, a * np.exp(b / np.sqrt(np.abs(T_fit / T_KT - 1.0) + 1e-10)), 'w--', lw=1.0, alpha=0.8)
        
    ax.set_title(r"$\eta(t)$ / $\xi(t)$ + BKT Singularity", color=config.THEME["TEXT"], fontsize=9, fontweight="bold", fontfamily=config.THEME["FONT"], pad=2)
    leg = ax.legend(loc="upper left", fontsize=6, facecolor=config.THEME["BG"], edgecolor=config.THEME["GRID"])
    for text in leg.get_texts(): text.set_color(config.THEME["TEXT_DIM"])

def _draw_inset(ax_ins, data):
    t_valid = data['t_valid']; T_eff = data['T_eff']; Upsilon = data['Upsilon']
    ax_ins.set_facecolor("#050508")
    for sp in ax_ins.spines.values(): sp.set_color("#333333"); sp.set_linewidth(0.5)
    ax_ins.tick_params(axis="both", colors=config.THEME["TEXT_DIM"], labelsize=6, direction="in", length=2)
    ax_ins.yaxis.grid(True, lw=0.3, alpha=0.3, color=config.THEME["GRID"])
    ax_ins.xaxis.grid(True, lw=0.3, alpha=0.3, color=config.THEME["GRID"])

    T_vals = T_eff[t_valid]; U_vals = Upsilon[t_valid]
    time_colors = np.linspace(0, 1, len(t_valid))
    ax_ins.scatter(T_vals, U_vals, c=time_colors, cmap='plasma', s=12, alpha=0.2, edgecolors='none')
    ax_ins.scatter(T_vals, U_vals, c=time_colors, cmap='plasma', s=3, alpha=0.9, edgecolors='none')

    T_line = np.linspace(T_vals.min(), T_vals.max(), 50)
    ax_ins.plot(T_line, config.CONFIG["KT_CRITICAL"] * T_line, color=config.THEME["ORANGE"], ls="--", lw=1.5, alpha=1.0)
    ax_ins.set_xlabel(r"$T_{eff}$", color=config.THEME["TEXT_DIM"], fontsize=6)
    ax_ins.set_ylabel(r"$\Upsilon$", color=config.THEME["TEXT_DIM"], fontsize=6)
    ax_ins.set_title("2D BKT PHASE MAP", color=config.THEME["ORANGE"], fontsize=7, fontweight="bold", fontfamily=config.THEME["FONT"])

def draw_dashboard(data, frame_params=None, norm=None):
    t_valid = data['t_valid']
    if frame_params is None:
        tc, z_scale, elev, azim = len(t_valid), 1.0, 25, -55
    else:
        tc, z_scale, elev, azim = frame_params['tc'], frame_params['z_scale'], frame_params['elev'], frame_params['azim']

    if norm is None: norm = Normalize(vmin=data['z_min'], vmax=data['z_max'])

    fig = plt.figure(figsize=(19.2, 10.8), dpi=config.CONFIG["DPI"], facecolor=config.THEME["BG"])
    fig.patch.set_facecolor(config.THEME["BG"])

    gs = GridSpec(4, 2, width_ratios=[2.2, 1], left=0.05, right=0.97, top=0.87, bottom=0.07, hspace=0.35, wspace=0.08, figure=fig)
    ax3d = fig.add_subplot(gs[:, 0], projection="3d")
    ax3d.set_facecolor(config.THEME["BG"])

    panels = [fig.add_subplot(gs[i, 1]) for i in range(4)]
    for p in panels: _style_ax(p)
    ax_ins = fig.add_axes([0.045, 0.06, 0.22, 0.16])

    _draw_3d_surface(ax3d, data, tc, z_scale, norm)
    ax3d.view_init(elev=elev, azim=azim)

    _draw_panel_1(panels[0], data, tc)
    _draw_panel_2(panels[1], data, tc)
    _draw_panel_3(panels[2], data, tc)
    _draw_panel_4(panels[3], data, tc)
    _draw_inset(ax_ins, data)

    n_events = data['n_events']
    fig.text(0.50, 0.96, "KOSTERLITZ-THOULESS MARKET TRANSITION", ha="center", va="center", fontsize=28, fontweight="bold", color=config.THEME["ORANGE"], fontfamily=config.THEME["FONT"])
    fig.text(0.50, 0.93, r"$H=-\sum J_{ij}\cos(\theta_i-\theta_j)$" f"   $\\tilde\\Upsilon_c=2/\\pi$   VORTEX EVENTS: {n_events}", ha="center", va="center", fontsize=12, color=config.THEME["TEXT_DIM"], fontfamily=config.THEME["FONT"])
    
    K_mean = float(np.nanmean(data['K'][t_valid])); T_mean = float(np.nanmean(data['T_eff'][t_valid]))
    Ut_mean = float(np.nanmean(data['Upsilon_tilde'][t_valid])); rg_agree = data['rg_agree']
    current_regime = data['regime'][t_valid[-1]] if len(t_valid) > 0 else 'UNKNOWN'
    
    fig.text(0.96, 0.88, f"K_mean={K_mean:.2f}   T_eff_mean={T_mean:.3f}   <Y~>={Ut_mean:.2f}   RG-AGREE={rg_agree:.1%}   PHASE: {current_regime}", ha="right", va="center", fontsize=11, fontweight="bold", color=config.THEME["YELLOW"], fontfamily=config.THEME["FONT"])
    fig.text(0.98, 0.012, "@Laksh", ha="right", va="bottom", fontsize=10, color=config.THEME["TEXT_DIM"], fontfamily=config.THEME["FONT"], alpha=0.6)
    return fig

def render_static(data):
    import os
    os.makedirs(config.CONFIG["OUTPUT_DIR"], exist_ok=True)
    norm = Normalize(vmin=data['z_min'], vmax=data['z_max'])
    fig = draw_dashboard(data, frame_params=None, norm=norm)
    fig.savefig(config.CONFIG["PNG_PATH"], dpi=config.CONFIG["DPI"], facecolor=config.THEME["BG"])
    plt.close(fig)
    print(f"[STATIC] Saved to {config.CONFIG['PNG_PATH']}")
    return norm