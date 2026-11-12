---
name: volleyball-optimizer
description: >-
  Guides running, simulating, and optimizing youth volleyball lineups and match strategies for Moneyball VB.
  Use whenever analyzing player stats, generating 3-set match plans, or checking CYO league compliance.
---

# Volleyball Lineup Optimizer & Match Planner

This skill guides running and customizing the Moneyball VB rotation optimization engine.

## Key Files
- Match Planner & Strategies: `engine/match_planner.py`
- Optimization Engine: `engine/optimizer.py`
- Dynamic In-Game Optimizer: `engine/mobile_optimizer.py`
- Roster & Ratings: `players.json`
- Match & Set History: `games.json`
- Web Server: `server.py`
- CLI Entrypoint: `main.py`

## Quick Tasks

1. **Run Full 3-Set Match Simulation**:
   ```bash
   python3 main.py
   ```
2. **Launch Interactive Web UI / Scorekeeper**:
   ```bash
   python3 server.py
   # Access via browser at http://localhost:8080
   ```
3. **League Rules Enforced**:
   - 6 players on court at all times.
   - Midway substitution swap at point 13.
   - 5-serve limit per player per rotation before mandatory sideout.
   - Equal playing time: all players must play at least 2 halves across sets 1 & 2.
