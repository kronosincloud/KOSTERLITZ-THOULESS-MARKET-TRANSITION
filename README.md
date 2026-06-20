
# KOSTERLITZ-THOULESS MARKET TRANSITION
### Topological Vortex Unbinding in Sector Phase-Coherence Networks
> *A novel application of 2016 Nobel Prize-winning condensed matter physics to financial markets, treating sector rotations not as correlated drift, but as a topological phase field governed by the universal 2/π transition threshold.*

---

## What Is This?

The Berezinskii–Kosterlitz–Thouless (BKT) transition is the defining example of a **topological phase transition** — a transition driven not by symmetry breaking, but by the unbinding of topological defects (vortex–antivortex pairs) in a 2D system of continuous phase angles. Below the transition, the system has quasi-long-range order (QLRO); above it, vortices proliferate and screen all correlations. 

This project bridges this condensed matter physics framework to quantitative finance. We construct a fixed 6×5 lattice of 30 S&P 500 proxy assets across 6 sectors. The instantaneous oscillation phase of each asset's return cycle is extracted via the Hilbert transform, mapping the cross-sectional market snapshot to a 2D XY spin field. 

The **3D surface** visualizes the phase-correlation function $C(r,t)$, where $r$ is the correlation-distance between assets. The shape of this surface—algebraic (power-law) decay vs. exponential cliff—reveals the market's topological phase in real-time.

### Physics → Finance Mapping

| BKT / XY Model Quantity | Market Definition |
|---|---|
| Spin phase angle $\theta_i$ | Instantaneous Hilbert-transform phase of asset $i$'s return |
| Coupling $J_{ij}$ | Rolling realized correlation $\rho_{ij}(t)$, positive part only |
| Temperature $T$ | Rolling cross-sectional realized volatility (market "heat") |
| Vortex / antivortex | Lattice plaquette where wrapped phase winding = $\pm 2\pi$ |
| Helicity modulus $\Upsilon$ | Lattice-estimated resistance of the network to a global phase twist |
| Universal jump $\Upsilon_c/T_c = 2/\pi$ | Exact, parameter-free threshold separating coherent vs. vortex-unbound regimes |

---

## Why This Has Never Been Done Before

- **Nobody has** mapped financial return phases to a 2D XY Hamiltonian to detect topological phase transitions.
- **Nobody has** detected integer winding number vortices in sector correlation networks as signatures of market fragmentation.
- **Nobody has** applied the exact $2/\pi$ universal jump threshold—parameter-free and exact for every 2D XY system—to classify financial regimes.
- **Nobody has** fit the Kosterlitz essential singularity $\xi \sim \exp(b/\sqrt{|T/T_{KT}-1|})$ to market correlation lengths near regime crossings.
- **Nobody has** rendered this as a production-quality 3D Bloomberg Dark visualization.

---

## The Mathematics

### 1. Phase Field Extraction
For asset $i$, take the 21-day centered window of demeaned daily log returns, apply the Hilbert transform, and read the instantaneous phase:
```latex
\theta_i(t) = \arg( r_{demeaned}(t) + j \cdot \text{Hilbert}[r_{demeaned}](t) ) \in (-\pi, \pi]
```

### 2. Market XY Hamiltonian & Effective Temperature
```latex
H(t) = - \sum_{\langle ij \rangle} J_{ij}(t) \cos(\theta_i(t) - \theta_j(t))
```
Where $J_{ij} = \max(0, \rho_{ij})$ and $T_{eff}(t) = \text{mean}(\sigma_{cross}) \times \sqrt{252}$.

### 3. Vortex Winding Number
For every elementary plaquette traversed counterclockwise:
```latex
q = \frac{1}{2\pi} \sum \text{wrap}(\theta_{next} - \theta_{current})
```
Where $\text{wrap}(x) = x - 2\pi \cdot \text{round}(x/2\pi)$ maps differences to $(-\pi, \pi]$.

### 4. Helicity Modulus & Universal Jump
```latex
\Upsilon(t) = \langle e \rangle_{10d} - \frac{1}{T_{eff}(t)} \langle s^2 \rangle_{10d}
```
The reduced helicity modulus $\tilde{\Upsilon} = \Upsilon / T_{eff}$ undergoes a universal jump at the critical point:
```latex
\tilde{\Upsilon}_c = \frac{2}{\pi} \approx 0.6366
```

### Interpretation Table

| Value | Market State |
|---|---|
| $\tilde{\Upsilon} > 2/\pi$ | **QLRO-COHERENT**: Sector rotations propagate coherently. Vortices are bound. |
| $\tilde{\Upsilon} < 2/\pi$ | **VORTEX-UNBOUND**: Phase defects proliferate. Correlations screen locally. |
| $\xi \to \infty$ (Essential Singularity) | Market approaches topological criticality. |

---

## Visual Design

This project adheres strictly to the [**@Laksh Visual Style**](SKILL.md) (Bloomberg Dark Standard). 

### Colour System

| Hex | Semantic Meaning |
|---|---|
| `#000000` | Void Black (Background) |
| `#080808` | Panel Background |
| `#ff9500` | Orange (Titles, Critical Threshold $2/\pi$) |
| `#00f2ff` | Cyan (QLRO Coherent phase, $\tilde{\Upsilon}$) |
| `#ff1493` | Magenta (Vortex-Unbound phase, Crisis) |
| `#ffd400` | Yellow (HUD Stats, Endpoint markers) |

### Custom Colormap (`CMAP_BKT`)
A high-contrast "Neon Spike" colormap mapping correlation values to phases:
- `#020205` (Deep Void) → `#ff1493` (Neon Magenta/Crisis) → `#ff4500` (Red-Orange) → `#ffd400` (Yellow/Critical) → `#00f2ff` (Cyan/Ordered) → `#ffffff` (White Peaks/Max Coherence).

### 3D Rendering Techniques
- **Exaggerated Z-Aspect**: `set_box_aspect([1.2, 1.0, 1.4])` to visually amplify the "cliffs" of phase transitions.
- **Neon Triple-Glow Ridges**: Two hero ridge lines ($\tilde{\Upsilon}$ and $n_v$) rendered with three overlapping lines of decreasing width and increasing alpha to simulate a neon tube glow.
- **Floor Contour Shadow**: `contourf` projected onto the z-floor with `alpha=0.45` to ground the 3D surface.

---

## Outputs

### Static PNG (`bkt_market_transition.png`)
1920×1080 resolution, Layout Type B (4-row right column + bottom-left inset).

| Panel | Content |
|---|---|
| **Main 3D Surface** | $C(r,t)$ phase correlation surface with $\tilde{\Upsilon}$ (orange) and $n_v$ (cyan) ridges. |
| **Right Panel 1** | $\tilde{\Upsilon}(t)$ vs $2/\pi$ universal threshold with regime shading. |
| **Right Panel 2** | Vortex Density $n_v(t)$ with injected stress window shading. |
| **Right Panel 3** | Vortex/antivortex plaquette heatmap (20 plaquettes × time). |
| **Right Panel 4** | $\eta(t)$ (QLRO) / $\xi(t)$ (disordered) switching line + BKT singularity fit. |
| **Bottom-Left Inset** | 2D BKT Phase Map: $\Upsilon$ vs $T_{eff}$ with theoretical line. |

### Animated GIF (`bkt_market_transition.gif`)
120-frame, 12-second loop at 10 FPS. Enforces the Mirror Image Rule.

| Phase | Frames | Duration | Camera Behavior |
|---|---|---|---|
| **GROW** | 0–44 (45) | 4.5 sec | Rises from `elev=5` to `25`. Z-scale 0.05→1.0 (Quintic ease). |
| **HOLD** | 45–64 (20) | 2.0 sec | Gentle elevation "breathing" (`±2°`). |
| **ORBIT** | 65–119 (55) | 5.5 sec | Continuous 360° azimuth rotation. |

---

## Project Structure & Pipeline

```text
├── config.py
├── data.py
├── engine.py
├── visual.py
├── animate.py
├── main.py
├── outputs/
│   ├── bkt_market_transition.png
│   └── bkt_market_transition.gif
└── README.md
```

**Pipeline Pattern:**
1. **MODULE 1 (Data)**: `data.py` — Generates synthetic GARCH(1,1) returns with embedded stress regimes on a 6×5 sector lattice.
2. **MODULE 2 (Engine)**: `engine.py` — Computes Hilbert phases, vortex windings, helicity modulus, and integrates the Kosterlitz RG flow.
3. **MODULE 3 (Visual)**: `visual.py` — Renders the static 1920×1080 PNG dashboard.
4. **MODULE 4 (Animate)**: `animate.py` — Renders the 120-frame animated GIF.

---

## Installation, Usage, & Configuration

### Installation
```bash
pip install numpy scipy matplotlib imageio
```

### Usage
Run the complete pipeline end-to-end (generates synthetic data):
```bash
python main.py
```

### Configuration
Key parameters can be adjusted in `config.py`:

| Parameter | Default | Description |
|---|---|---|
| `T_TOTAL` | 750 | Number of trading days to simulate (~3 years). |
| `GARCH_OMEGA` | 2e-6 | Base GARCH volatility scale. |
| `STRESS_WINDOWS` | `[(150, 185), ...]` | Time windows to inject cross-sector fragmentation. |
| `WINDOW_PHASE` | 21 | Centered window for Hilbert transform phase extraction. |
| `KT_CRITICAL` | $2/\pi$ | Universal Nelson-Kosterlitz jump threshold. |

### Stock Universe
The simulation uses 30 proxy assets mapped to a fixed 6×5 lattice:

| Sector | Assets (Proxy Tickers) |
|---|---|
| **TECH** | AAPL, MSFT, NVDA, AVGO, ADBE |
| **FINA** | JPM, BAC, WFC, MS, GS |
| **HEAL** | JNJ, UNH, LLY, PFE, MRK |
| **ENER** | XOM, CVX, COP, EOG, SLB |
| **CONS** | AMZN, TSLA, HD, MCD, NKE |
| **INDU** | CAT, UNP, HON, GE, BA |

---

## Academic References

1. V. L. Berezinskii (1971) — *Destruction of long-range order in one-dimensional and two-dimensional systems having a continuous symmetry group* — Sov. Phys. JETP 32, 493.
2. J. M. Kosterlitz and D. J. Thouless (1973) — *Ordering, metastability and phase transitions in two-dimensional systems* — J. Phys. C: Solid State Phys. 6, 1181.
3. D. R. Nelson and J. M. Kosterlitz (1977) — *Universal Jump in the Superfluid Density of Two-Dimensional Superfluids* — Phys. Rev. Lett. 39, 1201.
4. P. M. Chaikin and T. C. Lubensky (1995) — *Principles of Condensed Matter Physics* — Cambridge University Press.
5. D. Gabor (1946) — *Theory of communication* — J. IEE 93, 429.
```
