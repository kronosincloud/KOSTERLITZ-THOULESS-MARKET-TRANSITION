# animate.py
"""
MODULE 4: ANIMATE — 120-frame GIF with Mirror Image Rule.
GROW(45)/HOLD(20)/ORBIT(55) schedule with shared Normalize.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import imageio
import config
from visual import draw_dashboard, _canvas_to_rgb
from matplotlib.colors import Normalize

def _ease_quintic(x):
    x = np.clip(x, 0.0, 1.0)
    return 6 * x**5 - 15 * x**4 + 10 * x**3

def render_gif(data, norm=None):
    import os
    os.makedirs(config.CONFIG["OUTPUT_DIR"], exist_ok=True)
    t_valid = data['t_valid']; N_t = len(t_valid)
    if norm is None: norm = Normalize(vmin=data['z_min'], vmax=data['z_max'])

    N_grow, N_hold, N_orbit = config.CONFIG["N_GROW"], config.CONFIG["N_HOLD"], config.CONFIG["N_ORBIT"]
    total_frames = N_grow + N_hold + N_orbit
    schedule = []

    # PHASE 1: GROW
    for i in range(N_grow):
        raw = i / max(1, N_grow - 1); eased = _ease_quintic(raw)
        schedule.append({"phase": "GROW", "tc": max(2, int(eased * N_t)), "z_scale": 0.05 + 0.95 * eased, "elev": 5 + 20 * eased, "azim": -60 + 5 * eased})

    # PHASE 2: HOLD
    for i in range(N_hold):
        schedule.append({"phase": "HOLD", "tc": N_t, "z_scale": 1.0, "elev": 25 + 2 * np.sin(2 * np.pi * i / N_hold), "azim": -55 + 5 * (i / N_hold)})

    # PHASE 3: CONTINUOUS ORBIT
    hold_end_azim = -55 + 5 * ((N_hold - 1) / N_hold)
    hold_end_elev = 25 + 2 * np.sin(2 * np.pi * (N_hold - 1) / N_hold)
    for orb_prog in np.linspace(0.0, 1.0, N_orbit):
        schedule.append({"phase": "ORBIT", "tc": N_t, "z_scale": 1.0, "elev": hold_end_elev + 15 * np.sin(np.pi * orb_prog * 1.4), "azim": hold_end_azim + 360.0 * orb_prog})

    print(f"[ANIMATE] Rendering {total_frames} frames...")
    frames = []
    for fi, sched in enumerate(schedule):
        fig = draw_dashboard(data, frame_params=sched, norm=norm)
        frames.append(_canvas_to_rgb(fig))
        plt.close(fig)
        if (fi + 1) % 20 == 0: print(f"  Frame {fi+1}/{total_frames} [{sched['phase']}]")

    imageio.mimsave(config.CONFIG["GIF_PATH"], frames, fps=10, loop=0)
    print(f"[ANIMATE] Saved to {config.CONFIG['GIF_PATH']}")