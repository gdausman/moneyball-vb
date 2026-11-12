# Moneyball VB 🏐

**St. Cecilia CYO Volleyball Rotation Optimizer & Match Planner**  
Designed for St. Cecilia CYO Volleyball, applying data-driven roster optimization, rotation tracking, and league rule enforcement.

---

## Overview

In CYO youth volleyball, service efficiency and receive stability determine match outcomes. **Moneyball VB** models player ratings (consistency, power, receive, rally hits) and solves for optimal lineups while strictly enforcing league rules:
- **6 players on court** at all times.
- **Midway rotation swap** at point 13.
- **5-serve maximum** per player per rotation before a mandatory sideout.
- **Equal playing time guarantee**: Every roster player must play at least 2 halves across Sets 1 & 2.
- **Guaranteed serve positions**: Players needing service opportunities are seeded in positions 1–3.

---

## Architecture & Directory Layout

```
Moneyball VB/
├── main.py              # CLI entry point to run simulations & 3-set match plans
├── server.py            # Local HTTP API server (built on standard library http.server)
├── index.html           # Desktop / tablet responsive web interface & scorekeeper
├── players.json         # Roster ratings, tiers, jersey numbers, and metrics
├── games.json           # Historical match logs and saved rotations
├── static/              # Static web assets (CSS/JS, logos)
├── st_cecilia_logo.png  # Team crest / asset
└── engine/              # Core algorithmic optimization engine
    ├── models.py        # Data classes: Player, HalfLineup, SetPlan
    ├── optimizer.py     # Strategy solvers (Early Win, Closers, Defense, Death Lineup)
    ├── match_planner.py # 3-set tournament progression & compliance auditor
    ├── visualizer.py    # Terminal ASCII court renderer & report generator
    └── mobile_optimizer.py # Dynamic in-game rotation solver
```

---

## Strategy Sets

1. **Early Win (Set 1)**: Front-loads elite servers in Positions 1–3 to seize momentum and force quick leads.
2. **League Compliance & Equalizer (Set 2)**: Solves the constraint puzzle—guarantees unserved players rotate into serving positions while equalizing court time.
3. **The "Death Lineup" (Set 3)**: Unrestricted, highest composite power score for the deciding set / tournament championship.

---

## Quickstart

### 1. Run CLI Match Plan & Compliance Audit
```bash
cd "Moneyball VB"
python3 main.py
```

### 2. Launch Local Web Application
```bash
cd "Moneyball VB"
python3 server.py
```
Open **[http://localhost:8080](http://localhost:8080)** in your browser for the interactive rotation board, substitution manager, and live scorekeeper.
