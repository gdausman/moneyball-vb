"""
Moneyball VB - 4th Grade Rotation Optimizer
Main CLI to run strategies and print game plans.
"""
import os
import sys
from engine.optimizer import load_players, MoneyballOptimizer
from engine.visualizer import render_set_summary, render_court_ascii
from engine.match_planner import MatchPlanner

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYERS_FILE = os.path.join(BASE_DIR, "players.json")

def main():
    players = load_players(PLAYERS_FILE)
    opt = MoneyballOptimizer(players)
    planner = MatchPlanner(opt)

    print("================================================================================")
    print("                      MONEYBALL VB: 4TH GRADE OPTIMIZER                         ")
    print("================================================================================")
    print(f"Loaded {len(players)} players.")
    print("League Rules: 6 on court, midway swap at pt 13, 5-serve limit, equal playing time.\n")

    # Generate the 3-Set Tournament Game Plan:
    # Strategy: Win Set 1 (Early Win), Equalize & Guarantee Serves in Set 2, Death Lineup in Set 3
    plan = planner.generate_3_set_match_plan(set_1_strategy="early_win")

    print(render_set_summary(plan["set1"]))
    print(render_set_summary(plan["set2"]))

    print("════════════════════════════════════════════════════════════════════════════════════")
    print("  SET 3: 'ANYTHING GOES' — THE DEATH LINEUP (TOURNAMENT CHAMPIONSHIP)")
    print("════════════════════════════════════════════════════════════════════════════════════")
    print(f"  Team Strength: {plan['set3'].total_score} pts | Avg Rcv: {plan['set3'].avg_receive:.1f}/5 | Avg Srv Cons: {plan['set3'].avg_serve_consistency:.1f}/5")
    print(render_court_ascii(plan["set3"]))

    print("\n════════════════════════════════════════════════════════════════════════════════════")
    print("  LEAGUE COMPLIANCE & PLAYING TIME AUDIT (AFTER SET 1 & 2)")
    print("════════════════════════════════════════════════════════════════════════════════════")
    print("Player       | Halves Played (Set 1+2) | Guaranteed Serve Slot (Pos 1-3)?")
    print("-------------+-------------------------+----------------------------------")
    for p in opt.player_list:
        hp = plan["halves_played"][p.name]
        srv = "✓ YES" if p.name in plan["served_in_pos_1_to_3"] else "✗ NO"
        full_game = "✓ (Full Game)" if hp >= 2 else "✗"
        print(f"#{p.number:<2} {p.name:<8} | {hp} halves {full_game:<13} | {srv}")

if __name__ == "__main__":
    main()
