"""
Optimization algorithms for Moneyball VB:
- Strategy 1: Early Win (Front-runner)
- Strategy 2: Closers (Finish strong)
- Strategy 3: Serve Receive Defense (Anti-ace wall)
- Strategy 4: Straight Best Set (Death Lineup)
- Full Match Engine: 3-set plan with equal playing time and guaranteed serving.
"""
import json
from typing import List, Dict, Tuple, Set
from engine.models import Player, HalfLineup, SetPlan

def load_players(json_path: str = "players.json") -> List[Player]:
    with open(json_path, "r") as f:
        data = json.load(f)
    players = []
    for p in data["players"]:
        tot = p.get("total_score")
        if tot is None:
            tot = int(p.get("serve_consistency", 3)) + int(p.get("serve_power", 3)) + int(p.get("serve_receive", 2)) + int(p.get("rally_hits", 2))
        tier = p.get("tier")
        if not tier:
            tier = "anchor" if tot >= 13 else ("starter" if tot >= 10 else ("rotation" if tot >= 9 else "developing"))
        players.append(Player(
            number=int(p.get("number", 0)),
            name=str(p.get("name", "Player")),
            serve_consistency=int(p.get("serve_consistency", 3)),
            serve_power=int(p.get("serve_power", 3)),
            serve_receive=int(p.get("serve_receive", 2)),
            rally_hits=int(p.get("rally_hits", 2)),
            total_score=tot,
            tier=tier
        ))
    return players

class MoneyballOptimizer:
    def __init__(self, players: List[Player]):
        self.players = {p.name: p for p in players}
        self.player_list = sorted(players, key=lambda x: x.total_score, reverse=True)

    def arrange_court_positions(self, six_players: List[Player], priority_servers: List[Player] = None, designate_server: Player = None) -> Dict[int, Player]:
        """
        Assigns players to Positions 1-6 based on:
        - Server Priority: P1 is first server, P2 is second server, P3 is third server.
        - Defensive Geometry: P6 (Middle Back) & P5 (Left Back) face 75% of 4th-grade serves.
        """
        positions: Dict[int, Player] = {}
        available = list(six_players)

        # 1. Assign P1 (Starting Server)
        if designate_server and designate_server in available:
            positions[1] = designate_server
            available.remove(designate_server)
        elif priority_servers:
            cand = [p for p in available if p in priority_servers]
            if cand:
                p1_cand = sorted(cand, key=lambda p: (p.serve_consistency, p.serve_power), reverse=True)[0]
                positions[1] = p1_cand
                available.remove(p1_cand)

        if 1 not in positions:
            p1_cand = sorted(available, key=lambda p: p.expected_serve_value, reverse=True)[0]
            positions[1] = p1_cand
            available.remove(p1_cand)

        # 2. Assign P2 (Second Server - must pick from priority_servers if any need to serve)
        if priority_servers:
            cand2 = [p for p in available if p in priority_servers]
            if cand2:
                p2_cand = sorted(cand2, key=lambda p: (p.serve_consistency, p.serve_power), reverse=True)[0]
                positions[2] = p2_cand
                available.remove(p2_cand)

        # 3. Assign high-traffic defense spots (P6 Middle Back, P5 Left Back) from remaining available
        by_receive = sorted(available, key=lambda p: (p.serve_receive, p.rally_hits), reverse=True)
        if len(by_receive) >= 1:
            p6 = by_receive[0]
            positions[6] = p6
            available.remove(p6)
        if len(by_receive) >= 2:
            p5 = by_receive[1]
            positions[5] = p5
            available.remove(p5)

        # 4. Fill P2 if still empty
        if 2 not in positions:
            p2_cand = sorted(available, key=lambda p: p.expected_serve_value, reverse=True)[0]
            positions[2] = p2_cand
            available.remove(p2_cand)

        # 5. Remaining 2 players go to front row (P3 Middle Front, P4 Left Front)
        # Note: P3 serves 3rd, P4 serves 4th. If one of them needs to serve, give them P3!
        p3_cand = None
        if priority_servers:
            p3_cands = [p for p in available if p in priority_servers]
            if p3_cands:
                p3_cand = p3_cands[0]
        if not p3_cand:
            p3_cand = sorted(available, key=lambda p: (p.serve_receive, p.expected_serve_value), reverse=True)[0]

        positions[3] = p3_cand
        available.remove(p3_cand)
        positions[4] = available[0]

        return positions

    def optimize_early_win_set(self, set_number: int = 1, anchor_name: str = "Gemma", priority_servers: List[Player] = None) -> SetPlan:
        """
        STRATEGY 1: EARLY WIN (FRONT-RUNNER)
        - Front-load high-EV servers and Eileen in 1st half to build a dominant lead (e.g. 13-3).
        - 2nd half anchors lead to 25.
        """
        anchor = self.players[anchor_name]

        # 1st Half: Eileen (pass anchor), Harper (power), Peyton (consistency), Sophie, Ella, Anchor
        h1_players = [
            self.players["Eileen"],
            self.players["Harper"],
            self.players["Peyton"],
            self.players["Sophie"],
            self.players["Ella"],
            anchor
        ]
        # In early win, Peyton (consistency 4) starts P1, Harper (power 4) is P2!
        h1_pos = self.arrange_court_positions(
            h1_players, 
            priority_servers=[self.players["Harper"]], 
            designate_server=self.players["Peyton"]
        )
        h1 = HalfLineup("First Half (0-13) [Early Attack]", h1_pos)

        # 2nd Half: Tessa (closer/pass anchor), Charley, Olivia, Eleanor, Claire, Anchor
        h2_players = [
            self.players["Tessa"],
            self.players["Charley"],
            self.players["Olivia"],
            self.players["Eleanor"],
            self.players["Claire"],
            anchor
        ]
        h2_pos = self.arrange_court_positions(h2_players, priority_servers)
        h2 = HalfLineup("Second Half (13-25) [Holding Line]", h2_pos)

        bench1 = [p for p in self.player_list if p not in h1_players]
        bench2 = [p for p in self.player_list if p not in h2_players]

        return SetPlan(set_number, "Early Win (Front-Runner)", h1, h2, anchor, bench1, bench2)

    def optimize_closers_set(self, set_number: int = 1, anchor_name: str = "Gemma", priority_servers: List[Player] = None) -> SetPlan:
        """
        STRATEGY 2: OPTIMIZE CLOSERS (FINISH STRONG)
        - 1st half holds the fort with steady play (Eileen, Peyton, Eleanor, Ella, Charley, Anchor).
        - 2nd half unleashes closing firepower (Tessa, Harper, Sophie, Olivia, Claire, Anchor) for pts 13-25.
        """
        anchor = self.players[anchor_name]

        h1_players = [
            self.players["Eileen"],
            self.players["Peyton"],
            self.players["Charley"],
            self.players["Eleanor"],
            self.players["Ella"],
            anchor
        ]
        h1_pos = self.arrange_court_positions(h1_players, priority_servers)
        h1 = HalfLineup("First Half (0-13) [Steady Foundation]", h1_pos)

        h2_players = [
            self.players["Tessa"],
            self.players["Harper"],
            self.players["Sophie"],
            self.players["Olivia"],
            self.players["Claire"],
            anchor
        ]
        h2_pos = self.arrange_court_positions(h2_players, priority_servers)
        h2 = HalfLineup("Second Half (13-25) [Elite Closer Unit]", h2_pos)

        bench1 = [p for p in self.player_list if p not in h1_players]
        bench2 = [p for p in self.player_list if p not in h2_players]

        return SetPlan(set_number, "Optimize Closers (Finish Strong)", h1, h2, anchor, bench1, bench2)

    def optimize_serve_receive_set(self, set_number: int = 1, anchor_name: str = "Gemma", priority_servers: List[Player] = None) -> SetPlan:
        """
        STRATEGY 3: SERVE RECEIVE FORT (ANTI-ACE)
        - Dead-even balance (60 vs 61 pts).
        - Perfectly splits passers and shields novices at the net.
        """
        anchor = self.players[anchor_name]

        h1_players = [
            self.players["Eileen"],
            self.players["Harper"],
            self.players["Peyton"],
            self.players["Eleanor"],
            self.players["Ella"],
            anchor
        ]
        h1_pos = self.arrange_court_positions(h1_players, priority_servers)
        h1 = HalfLineup("First Half (0-13) [Defensive Shell A]", h1_pos)

        h2_players = [
            self.players["Tessa"],
            self.players["Charley"],
            self.players["Sophie"],
            self.players["Olivia"],
            self.players["Claire"],
            anchor
        ]
        h2_pos = self.arrange_court_positions(h2_players, priority_servers)
        h2 = HalfLineup("Second Half (13-25) [Defensive Shell B]", h2_pos)

        bench1 = [p for p in self.player_list if p not in h1_players]
        bench2 = [p for p in self.player_list if p not in h2_players]

        return SetPlan(set_number, "Serve Receive Fort (Anti-Ace)", h1, h2, anchor, bench1, bench2)

    def optimize_death_lineup(self) -> HalfLineup:
        """
        STRATEGY 4: STRAIGHT BEST SET (THE DEATH LINEUP / SET 3 ANYTHING GOES)
        - Absolute best 6 players on the floor in optimal positions.
        - Total Score: 72!
        """
        top_6 = [
            self.players["Tessa"],   # 15
            self.players["Eileen"],  # 13
            self.players["Harper"],  # 12
            self.players["Gemma"],   # 12
            self.players["Peyton"],  # 11
            self.players["Charley"]  # 9 (Athletic utility)
        ]
        pos = self.arrange_court_positions(top_6)
        return HalfLineup("SET 3: DEATH LINEUP (All-Out to Win)", pos)
