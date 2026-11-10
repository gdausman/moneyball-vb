"""
Match Planner for 3-Set Matches:
- Set 1: Target Win (Early Win or Closer strategy)
- Set 2: League Compliance (Guaranteed serve for unserved players + equal playing time)
- Set 3: Unrestricted "Death Lineup" to take the match.
"""
from typing import List, Dict, Set
from engine.models import Player, HalfLineup, SetPlan
from engine.optimizer import MoneyballOptimizer, load_players
from engine.visualizer import render_set_summary, render_court_ascii

class MatchPlanner:
    def __init__(self, optimizer: MoneyballOptimizer):
        self.opt = optimizer
        self.players = optimizer.players
        self.player_list = optimizer.player_list

    def generate_3_set_match_plan(self, set_1_strategy: str = "early_win") -> Dict:
        """
        Executes the master match strategy:
        - Set 1: Win set (using requested strategy, e.g. 'early_win' or 'closers')
        - Set 2: Absorb development & guarantee everyone serves + equal playing time
        - Set 3: 'Death Lineup' for the championship!
        """
        halves_played: Dict[str, int] = {p.name: 0 for p in self.player_list}
        served_in_pos_1_to_3: Set[str] = set()

        # --- SET 1 ---
        # Anchor: Gemma (plays both halves)
        anchor_1 = "Gemma"
        if set_1_strategy == "early_win":
            set1 = self.opt.optimize_early_win_set(set_number=1, anchor_name=anchor_1)
        elif set_1_strategy == "closers":
            set1 = self.opt.optimize_closers_set(set_number=1, anchor_name=anchor_1)
        else:
            set1 = self.opt.optimize_serve_receive_set(set_number=1, anchor_name=anchor_1)

        # Track halves and servers from Set 1
        for p in set1.first_half.players:
            halves_played[p.name] += 1
        for p in set1.second_half.players:
            halves_played[p.name] += 1

        # Positions 1, 2, and 3 are virtually guaranteed to serve in a 13-point half
        for pos in [1, 2, 3]:
            if pos in set1.first_half.positions:
                served_in_pos_1_to_3.add(set1.first_half.positions[pos].name)
            if pos in set1.second_half.positions:
                served_in_pos_1_to_3.add(set1.second_half.positions[pos].name)

        # --- SET 2 ---
        # Find who still needs to serve in P1-P3!
        unserved = [p for p in self.player_list if p.name not in served_in_pos_1_to_3]

        # Anchor for Set 2: Harper (plays both halves in Set 2)
        anchor_2 = self.players["Harper"]

        # In Set 2, explicitly give top unserved players the P1, P2, and P3 slots!
        # H1: Tessa starts at P1, Ella at P2 (so Ella gets her guaranteed serve!)
        set2_h1_players = [
            self.players["Tessa"],
            anchor_2,
            self.players["Peyton"],
            self.players["Sophie"],
            self.players["Ella"],
            self.players["Claire"]
        ]
        set2_h1_pos = self.opt.arrange_court_positions(
            set2_h1_players, 
            priority_servers=unserved, 
            designate_server=self.players["Tessa"]
        )
        set2_h1 = HalfLineup("First Half (0-13) [Serve Mandate Focus]", set2_h1_pos)

        # H2: Eileen starts at P1, Charley at P2!
        set2_h2_players = [
            self.players["Eileen"],
            anchor_2,
            self.players["Gemma"],
            self.players["Charley"],
            self.players["Olivia"],
            self.players["Eleanor"]
        ]
        set2_h2_pos = self.opt.arrange_court_positions(
            set2_h2_players, 
            priority_servers=unserved, 
            designate_server=self.players["Eileen"]
        )
        set2_h2 = HalfLineup("Second Half (13-25) [Serve Mandate Focus]", set2_h2_pos)

        for p in set2_h1.players:
            halves_played[p.name] += 1
        for p in set2_h2.players:
            halves_played[p.name] += 1

        for pos in [1, 2, 3]:
            if pos in set2_h1.positions:
                served_in_pos_1_to_3.add(set2_h1.positions[pos].name)
            if pos in set2_h2.positions:
                served_in_pos_1_to_3.add(set2_h2.positions[pos].name)

        bench2_1 = [p for p in self.player_list if p not in set2_h1_players]
        bench2_2 = [p for p in self.player_list if p not in set2_h2_players]
        set2 = SetPlan(2, "Equal Time & Serve Guarantee", set2_h1, set2_h2, anchor_2, bench2_1, bench2_2)

        # --- SET 3 ---
        # "Anything goes in the 3rd set!"
        # Put out the Death Lineup!
        set3 = self.opt.optimize_death_lineup()

        return {
            "set1": set1,
            "set2": set2,
            "set3": set3,
            "halves_played": halves_played,
            "served_in_pos_1_to_3": served_in_pos_1_to_3
        }
