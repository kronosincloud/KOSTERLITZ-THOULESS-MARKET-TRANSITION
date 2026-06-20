# config.py
"""
Configuration for the Kosterlitz-Thouless Market Transition pipeline.
Bloomberg Dark Standard theme + custom BKT colormap.
"""
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

THEME = {
    "BG":           "#000000",
    "PANEL_BG":     "#080808",
    "GRID":         "#1a1a1a",
    "SPINE":        "#333333",
    "TEXT":         "#ffffff",
    "TEXT_DIM":     "#aaaaaa",
    "ORANGE":       "#ff9500",
    "ORANGE_HOT":   "#ff6b00",
    "CYAN":         "#00f2ff",
    "YELLOW":       "#ffd400",
    "GREEN":        "#00ff41",
    "RED":          "#ff3050",
    "MAGENTA":      "#ff1493",
    "PINK":         "#ff2a9e",
    "BLUE":         "#00bfff",
    "FONT":         "Arial",
}

# High-contrast "Neon Spike" colormap
CMAP_BKT = LinearSegmentedColormap.from_list("bkt_market", [
    "#020205",   # Deep Void
    "#1a0a2a",   # Dark Indigo
    "#ff1493",   # Neon Magenta (crisis)
    "#ff4500",   # Red-Orange
    "#ffd400",   # Neon Yellow (critical)
    "#00f2ff",   # Neon Cyan (ordered)
    "#ffffff",   # White Peaks (max coherence)
])

CONFIG = {
    "N_ASSETS": 30,
    "N_SECTORS": 6,
    "SECTORS": ["TECH", "FINA", "HEAL", "ENER", "CONS", "INDU"],
    "ASSETS_PER_SECTOR": 5,
    "LATTICE_SHAPE": (6, 5),
    "T_TOTAL": 750,
    "GARCH_OMEGA": 2e-6,
    "GARCH_ALPHA": 0.08,
    "GARCH_BETA": 0.90,
    "BASE_WITHIN_CORR": 0.40,
    "BASE_CROSS_CORR": 0.15,
    "STRESS_WITHIN_CORR": 0.75,
    "STRESS_CROSS_CORR": 0.05,
    "STRESS_OMEGA_MULT": 8.0,
    "STRESS_WINDOWS": [(150, 185), (380, 420), (580, 620)],
    "WINDOW_PHASE": 21,
    "WINDOW_CORR": 40,
    "WINDOW_TEMP": 40,
    "WINDOW_HELICITY": 10,
    "MU_CORE": np.pi**2 / 2,
    "KT_CRITICAL": 2.0 / np.pi,
    "RG_L_MAX": 8,
    "RG_N_STEPS": 200,
    "N_R_BINS": 40,
    "C_FLOOR": 1e-4,
    "T_EFF_FLOOR": 1e-6,
    "N_GROW": 45,
    "N_HOLD": 20,
    "N_ORBIT": 55,
    "DPI": 100,
    "OUTPUT_DIR": "outputs",
    "PNG_PATH": "outputs/bkt_market_transition.png",
    "GIF_PATH": "outputs/bkt_market_transition.gif",
}