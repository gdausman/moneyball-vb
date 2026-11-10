"""
Mobile-Optimized Volleyball Match Engine for 4th Grade.
Supports:
- Dynamic active roster (6 to 12 players)
- Match strategies: 'drop_first', 'drop_second', 'balanced'
- Tactical biases: 'offense', 'defense', 'balanced'
- Set 3 'Death Lineup' with safe substitution advisor
- Equal playing time and serve guarantees
"""
from typing import List, Dict, Any, Tuple
from engine.models import Player, HalfLineup

class DynamicOptimizer:
    def __init__(self, all_players: List[Player]):
        self.players_list = list(all_players)
        self.all_players = {p.name: p for p in all_players}

    def calc_serve_threat(self, p: Player, tactical_bias: str = "balanced") -> float:
        """
        Calculates realistic offensive serving threat for 4th grade:
        - Power (1.8x - 2.2x): Scarcest offensive asset; produces unreturnable aces and free balls.
        - Consistency (1.1x - 1.4x): Getting it in play cleanly.
        - Total score (0.25x): Athletic composure under pressure.
        """
        if tactical_bias == "offense":
            return (p.serve_power * 2.2) + (p.serve_consistency * 1.1) + (p.total_score * 0.25)
        elif tactical_bias == "defense":
            return (p.serve_power * 1.5) + (p.serve_consistency * 1.5) + (p.total_score * 0.25)
        return (p.serve_power * 1.8) + (p.serve_consistency * 1.3) + (p.total_score * 0.25)

    def calc_defense_value(self, p: Player) -> float:
        """
        Calculates serve-receive and scramble defense rating:
        - Serve receive (2.5x): First contact pass quality.
        - Rally hits (1.5x): 2nd and 3rd touch scramble saving.
        """
        return (p.serve_receive * 2.5) + (p.rally_hits * 1.5) + (p.total_score * 0.2)

    def arrange_positions(
        self,
        six_players: List[Player],
        tactical_bias: str = "balanced",
        priority_servers: List[Player] = None,
        designate_p1: Player = None,
        start_mode: str = "serve"  # "serve" (we serve first) or "receive" (we receive first)
    ) -> Dict[int, Player]:
        """
        Assigns 6 players to court positions (1 to 6) following youth volleyball laws:
        - Front-Loading: Best servers are assigned to earliest service rotations (Pos 1, 2, 3).
        - If Serving First: Pos 1 serves 1st, Pos 2 serves 2nd, Pos 3 serves 3rd.
        - If Receiving First: Pos 2 rotates to serve 1st, Pos 3 serves 2nd, Pos 4 serves 3rd.
        - Court Defense: Pos 6 (Middle Back) holds the best remaining pass anchor.
        - Hiding Weak Receivers: Pos 4 (Left Front Net) hides the weakest passer from direct service pressure.
        """
        available = list(six_players)
        positions: Dict[int, Player] = {}

        # 1. Gather server candidates
        if priority_servers:
            cands = [p for p in available if p in priority_servers]
            cands = sorted(cands, key=lambda p: self.calc_serve_threat(p, tactical_bias), reverse=True)
        else:
            cands = sorted(available, key=lambda p: self.calc_serve_threat(p, tactical_bias), reverse=True)

        by_serve = sorted(available, key=lambda p: self.calc_serve_threat(p, tactical_bias), reverse=True)

        if start_mode == "serve":
            # --- SERVE FIRST ---
            # Pos 1: Server 1 (Top Ace Weapon, e.g. Tessa)
            if designate_p1 and designate_p1 in available:
                p1 = designate_p1
            elif cands:
                p1 = cands[0]
            else:
                p1 = by_serve[0]

            positions[1] = p1
            available.remove(p1)
            if p1 in cands:
                cands.remove(p1)

            # Pos 2: Server 2 (Second Weapon, e.g. Eileen)
            p2 = cands[0] if cands else sorted(available, key=lambda p: self.calc_serve_threat(p, tactical_bias), reverse=True)[0]
            positions[2] = p2
            available.remove(p2)
            if p2 in cands:
                cands.remove(p2)

            # Pos 3: Server 3 (Third Weapon, e.g. Harper)
            p3 = cands[0] if cands else sorted(available, key=lambda p: self.calc_serve_threat(p, tactical_bias), reverse=True)[0]
            positions[3] = p3
            available.remove(p3)
            if p3 in cands:
                cands.remove(p3)

            # 3 players remain for non-serving slots: Pos 4 (Net), Pos 5 (LB), Pos 6 (MB)
            # Pos 4: Hide weakest receiver at Left Front (Net) away from back-row serve receive
            by_def_weakest = sorted(available, key=self.calc_defense_value)
            p4 = by_def_weakest[0]
            positions[4] = p4
            available.remove(p4)

            # Pos 6: Best remaining passer at Middle Back (Pass Anchor)
            by_def_strongest = sorted(available, key=self.calc_defense_value, reverse=True)
            positions[6] = by_def_strongest[0]
            positions[5] = by_def_strongest[1]

        else:
            # --- RECEIVE FIRST ---
            # Team rotates on first side-out before serving: Pos 2 -> Pos 1 (1st server)
            p_srv1 = cands[0] if cands else by_serve[0]
            positions[2] = p_srv1
            available.remove(p_srv1)
            if p_srv1 in cands:
                cands.remove(p_srv1)

            p_srv2 = cands[0] if cands else sorted(available, key=lambda p: self.calc_serve_threat(p, tactical_bias), reverse=True)[0]
            positions[3] = p_srv2
            available.remove(p_srv2)
            if p_srv2 in cands:
                cands.remove(p_srv2)

            p_srv3 = cands[0] if cands else sorted(available, key=lambda p: self.calc_serve_threat(p, tactical_bias), reverse=True)[0]
            positions[4] = p_srv3
            available.remove(p_srv3)
            if p_srv3 in cands:
                cands.remove(p_srv3)

            by_def = sorted(available, key=self.calc_defense_value, reverse=True)
            positions[6] = by_def[0]  # MB
            positions[5] = by_def[1]  # LB
            positions[1] = by_def[2]  # RB (6th server)

        return positions

    def plan_match(
        self,
        active_numbers: List[Any],
        tactical_bias: str = "balanced",
        match_strategy: str = "balanced",
        set3_mode: str = "win",  # "win", "even", "reps"
        start_mode: str = "serve"  # "serve" (we serve first) or "receive" (we receive first)
    ) -> Dict[str, Any]:
        """
        Generates full 3-set game plan for the active roster.
        set3_mode:
        - 'win': Win at all costs (Death Lineup of top 6)
        - 'even': Even playing time (balances minutes across all 3 sets with midway swap)
        - 'reps': Get reps (starts developing girls after winning Sets 1 & 2)
        """
        active_players = []
        for item in active_numbers:
            if isinstance(item, Player):
                if item not in active_players:
                    active_players.append(item)
            elif isinstance(item, str):
                if item in self.all_players and self.all_players[item] not in active_players:
                    active_players.append(self.all_players[item])
                else:
                    for p in self.players_list:
                        if (p.name == item or f"{p.number}_{p.name}" == item) and p not in active_players:
                            active_players.append(p)
                            break
            elif isinstance(item, int):
                for p in self.players_list:
                    if p.number == item and p not in active_players:
                        active_players.append(p)
                        break
            elif isinstance(item, dict):
                p_name = item.get("name")
                if p_name and p_name in self.all_players and self.all_players[p_name] not in active_players:
                    active_players.append(self.all_players[p_name])

        active_players = sorted(active_players, key=lambda p: p.total_score, reverse=True)
        n = len(active_players)

        if n < 6:
            raise ValueError(f"Need at least 6 active players to field a team (got {n}).")

        # Bench size = n - 6.
        # At point 13 midway swap: (n - 6) players sub in, (n - 6) sub out.
        # Number of anchors who play full set (both halves) = 6 - (n - 6) = 12 - n.
        # E.g., for n=11: 1 anchor. For n=10: 2 anchors. For n=9: 3 anchors. For n=8: 4 anchors.
        num_anchors = max(0, 12 - n)
        bench_size = n - 6

        # Sort players into talent tiers for set distribution
        best_players = active_players[:6]
        worst_players = list(reversed(active_players))[:6]

        served_p1_p3: set = set()
        s1s2_halves: Dict[str, int] = {p.name: 0 for p in active_players}
        s3_halves: Dict[str, int] = {p.name: 0 for p in active_players}
        s3_status: Dict[str, str] = {p.name: "— (Pending)" for p in active_players}

        # -------------------------------------------------------------
        # SET 1 & SET 2 GENERATION
        # -------------------------------------------------------------
        def partition_set(anchors: List[Player], non_anchor_ordering: List[Player]) -> Tuple[List[Player], List[Player], List[Player]]:
            """
            Guarantees exactly 6 distinct players for H1 and 6 distinct players for H2:
            - num_anchors play both H1 and H2.
            - (6 - num_anchors) players play H1 only.
            - (6 - num_anchors) players play H2 only.
            """
            non_anchors = [p for p in non_anchor_ordering if p not in anchors]
            half_singles_count = 6 - num_anchors

            h1_singles = non_anchors[:half_singles_count]
            h2_singles = non_anchors[half_singles_count:half_singles_count * 2]

            pool_h1 = list(anchors) + h1_singles
            pool_h2 = list(anchors) + h2_singles
            return anchors, pool_h1, pool_h2

        # All players sorted best-to-worst and worst-to-best
        all_best_to_worst = list(active_players)
        all_worst_to_best = list(reversed(active_players))

        def select_s2_anchors(candidates: List[Player], s1_a: List[Player], count: int) -> List[Player]:
            disjoint = [p for p in candidates if p not in s1_a]
            if len(disjoint) >= count:
                return disjoint[:count]
            needed = count - len(disjoint)
            return disjoint + [p for p in candidates if p in s1_a][:needed]

        if match_strategy == "drop_first":
            # Set 1 (Drop): Anchors are lowest-rated (e.g. Ella), they stay in both halves of Set 1
            s1_anchors = all_worst_to_best[:num_anchors]
            s1_anchors, s1_pool_h1, s1_pool_h2 = partition_set(s1_anchors, all_worst_to_best)

            # Set 2 (Win): Anchor MUST BE DIFFERENT! Pick from top tier (e.g. Tessa)
            # Guarantee: Set 1 anchor (Ella) MUST sub out in Set 2!
            s2_anchors = select_s2_anchors(all_best_to_worst, s1_anchors, num_anchors)
            s2_anchors, s2_pool_h1, s2_pool_h2 = partition_set(s2_anchors, all_best_to_worst)

        elif match_strategy == "drop_second":
            # Set 1 (Win): Anchor is top player (e.g. Tessa) who stays in both halves of Set 1
            s1_anchors = all_best_to_worst[:num_anchors]
            s1_anchors, s1_pool_h1, s1_pool_h2 = partition_set(s1_anchors, all_best_to_worst)

            # Set 2 (Drop): Anchor MUST BE DIFFERENT! Pick from developing tier (e.g. Ella)
            # Guarantee: Set 1 anchor (Tessa) MUST sub out in Set 2!
            s2_anchors = select_s2_anchors(all_worst_to_best, s1_anchors, num_anchors)
            s2_anchors, s2_pool_h1, s2_pool_h2 = partition_set(s2_anchors, all_worst_to_best)

        else:  # balanced
            # Pick solid middle anchors, ensuring Set 1 and Set 2 have completely different anchors
            mid_start = max(0, min(3, len(active_players) - num_anchors))
            s1_anchors = active_players[mid_start:mid_start + num_anchors]

            # Set 2 anchor is strictly chosen from remaining players (e.g. Tessa or Harper)
            s2_anchors = select_s2_anchors(active_players, s1_anchors, num_anchors)

            # Alternate strong and developing players into H1 and H2
            alt_order = []
            left = 0
            right = len(active_players) - 1
            while left <= right:
                if left == right:
                    alt_order.append(active_players[left])
                else:
                    alt_order.append(active_players[left])
                    alt_order.append(active_players[right])
                left += 1
                right -= 1

            s1_anchors, s1_pool_h1, s1_pool_h2 = partition_set(s1_anchors, alt_order)
            s2_anchors, s2_pool_h1, s2_pool_h2 = partition_set(s2_anchors, alt_order)

        # --- Build Set 1 ---
        serve_slots = [1, 2, 3] if start_mode == "serve" else [2, 3, 4]
        s1_h1_pos = self.arrange_positions(s1_pool_h1, tactical_bias=tactical_bias, start_mode=start_mode)
        s1_h1 = HalfLineup("Set 1: First Half (0–13)", s1_h1_pos)
        for p in s1_h1.players:
            s1s2_halves[p.name] += 1
        for pos in serve_slots:
            served_p1_p3.add(s1_h1.positions[pos].name)

        unserved_s1 = [p for p in active_players if p.name not in served_p1_p3]
        s1_h2_pos = self.arrange_positions(s1_pool_h2, tactical_bias=tactical_bias, priority_servers=unserved_s1, start_mode=start_mode)
        s1_h2 = HalfLineup("Set 1: Second Half (13–25)", s1_h2_pos)
        for p in s1_h2.players:
            s1s2_halves[p.name] += 1
        for pos in serve_slots:
            served_p1_p3.add(s1_h2.positions[pos].name)

        # --- Build Set 2 ---
        # Prioritize players who haven't served yet in Pos 1-3
        unserved = [p for p in active_players if p.name not in served_p1_p3]

        s2_h1_pos = self.arrange_positions(s2_pool_h1, tactical_bias=tactical_bias, priority_servers=unserved, start_mode=start_mode)
        s2_h1 = HalfLineup("Set 2: First Half (0–13)", s2_h1_pos)
        for p in s2_h1.players:
            s1s2_halves[p.name] += 1
        for pos in serve_slots:
            served_p1_p3.add(s2_h1.positions[pos].name)

        unserved_s2 = [p for p in active_players if p.name not in served_p1_p3]
        s2_h2_pos = self.arrange_positions(s2_pool_h2, tactical_bias=tactical_bias, priority_servers=unserved_s2, start_mode=start_mode)
        s2_h2 = HalfLineup("Set 2: Second Half (13–25)", s2_h2_pos)
        for p in s2_h2.players:
            s1s2_halves[p.name] += 1
        for pos in serve_slots:
            served_p1_p3.add(s2_h2.positions[pos].name)

        # --- Build Set 3: Based on set3_mode ('win', 'even', 'reps') ---
        # Set 3 is played strictly to 15 points. Mid-set substitutions happen at 8 points.
        set3_result = {}
        if set3_mode == "win":
            # 1. Win at all costs (Death Lineup)
            top_6 = active_players[:6]
            set3_pos = self.arrange_positions(top_6, tactical_bias="offense", start_mode=start_mode)
            set3_lineup = HalfLineup("Set 3: Championship Lineup (15 Pts)", set3_pos)
            bench_s3 = active_players[6:]
            for p in top_6:
                s3_halves[p.name] = 2  # Plays full 15-pt set
                s3_status[p.name] = "Full Set (15 pts)"
            for p in bench_s3:
                s3_status[p.name] = "Bench"

            safe_subs = []
            for bp in bench_s3:
                p4_player = set3_pos.get(4)
                if p4_player and bp.total_score >= 7:
                    safe_subs.append({
                        "bench_player": bp.to_dict(),
                        "court_player": p4_player.to_dict(),
                        "position": "Pos 4 (Left Front)",
                        "situation": "Lead Protection (Up by 3+ points)",
                        "reason": f"Sub #{bp.number} {bp.name} for #{p4_player.number} {p4_player.name} at the net without hurting back-row defense."
                    })

            set3_result = {
                "mode": "win",
                "mode_title": "🏆 Win at All Costs (15-pt Deciding Set)",
                "description": "Deciding set to 15 points. Peak 6 players on court. Built to take the championship.",
                "is_split": False,
                "lineup": self._serialize_half(set3_lineup),
                "bench": [p.to_dict() for p in bench_s3],
                "safe_subs": safe_subs
            }

        elif set3_mode == "even":
            # 2. Even playing time (Midway swap at 8 points balancing minutes across match)
            # Girls with lowest minutes in Sets 1 & 2 get priority
            sorted_by_minutes = sorted(active_players, key=lambda p: (s1s2_halves[p.name], -p.total_score))
            s3_h1_players = sorted_by_minutes[:6]
            s3_h1_pos = self.arrange_positions(s3_h1_players, tactical_bias="balanced", start_mode=start_mode)
            s3_h1 = HalfLineup("Set 3: First Half (0–8 pts)", s3_h1_pos)
            for p in s3_h1_players:
                s3_halves[p.name] = 1
                s3_status[p.name] = "1st Half (0–8 pts)"

            # Second half (8-15 points): Remaining players sub in
            remaining = [p for p in active_players if p not in s3_h1_players]
            anchors_needed = 6 - len(remaining)
            s3_anchors = s3_h1_players[:anchors_needed]
            s3_h2_players = remaining + s3_anchors
            s3_h2_pos = self.arrange_positions(s3_h2_players, tactical_bias="balanced", start_mode=start_mode)
            s3_h2 = HalfLineup("Set 3: Second Half (8–15 pts)", s3_h2_pos)
            for p in remaining:
                s3_halves[p.name] = 1
                s3_status[p.name] = "2nd Half (8–15 pts)"
            for p in s3_anchors:
                s3_halves[p.name] = 2
                s3_status[p.name] = "Both Halves (0–15 pts)"

            bench_s3_h1 = [p.to_dict() for p in active_players if p not in s3_h1_players]
            bench_s3_h2 = [p.to_dict() for p in active_players if p not in s3_h2_players]

            set3_result = {
                "mode": "even",
                "mode_title": "⚖️ Even Playing Time (Sub at 8 Points)",
                "description": "Deciding set to 15 points. Midway substitution happens at 8 points (side switch) so bench balances playing time.",
                "is_split": True,
                "first_half": self._serialize_half(s3_h1),
                "second_half": self._serialize_half(s3_h2),
                "anchors": [p.name for p in s3_anchors],
                "bench_first_half": bench_s3_h1,
                "bench_second_half": bench_s3_h2,
                "safe_subs": []
            }

        else:  # "reps"
            # 3. Get reps (We already won 2-0! Let developing players shine)
            sorted_worst_first = list(reversed(active_players))
            dev_six = sorted_worst_first[:6]
            reps_pos = self.arrange_positions(dev_six, tactical_bias="balanced", designate_p1=dev_six[0], start_mode=start_mode)
            reps_lineup = HalfLineup("Set 3: Development & Reps Lineup (15 Pts)", reps_pos)
            bench_reps = sorted_worst_first[6:]
            for p in dev_six:
                s3_halves[p.name] = 2
                s3_status[p.name] = "Full Set (15 pts)"
            for p in bench_reps:
                s3_status[p.name] = "Bench"

            safe_subs = [
                {
                    "position": "Pos 6 (Middle Back)",
                    "situation": "Stabilizer Sub",
                    "reason": f"If opponents go on a scoring run, sub in #{active_players[0].number} {active_players[0].name} for 2 rotations to pass and settle the team."
                }
            ]

            set3_result = {
                "mode": "reps",
                "mode_title": "🌟 Get Reps (15-pt Exhibition Set)",
                "description": "Match is already won! Developing girls get starting roles and high-volume serving reps in a fun, zero-pressure set to 15.",
                "is_split": False,
                "lineup": self._serialize_half(reps_lineup),
                "bench": [p.to_dict() for p in bench_reps],
                "safe_subs": safe_subs
            }

        # Compliance Audit Table
        audit = []
        for p in active_players:
            s1s2_h = s1s2_halves[p.name]
            srv = p.name in served_p1_p3
            s3_stat = s3_status.get(p.name, "—")
            s3_h = s3_halves.get(p.name, 0)
            audit.append({
                "number": p.number,
                "name": p.name,
                "s1s2_halves": s1s2_h,
                "s1s2_full_game_met": s1s2_h >= 2,
                "s1s2_served": srv,
                "set3_status": s3_stat,
                "set3_halves": s3_h,
                "total_halves": s1s2_h + s3_h
            })

        return {
            "meta": {
                "active_count": n,
                "tactical_bias": tactical_bias,
                "match_strategy": match_strategy,
                "anchors_set1": [p.name for p in s1_anchors],
                "anchors_set2": [p.name for p in s2_anchors],
            },
            "set1": {
                "first_half": self._serialize_half(s1_h1),
                "second_half": self._serialize_half(s1_h2),
                "bench_first_half": [p.to_dict() for p in active_players if p not in s1_pool_h1],
                "bench_second_half": [p.to_dict() for p in active_players if p not in s1_pool_h2]
            },
            "set2": {
                "first_half": self._serialize_half(s2_h1),
                "second_half": self._serialize_half(s2_h2),
                "bench_first_half": [p.to_dict() for p in active_players if p not in s2_pool_h1],
                "bench_second_half": [p.to_dict() for p in active_players if p not in s2_pool_h2]
            },
            "set3": set3_result,
            "audit": audit
        }

    def _serialize_half(self, half: HalfLineup) -> Dict[str, Any]:
        return {
            "half_name": half.half_name,
            "total_score": half.total_score,
            "avg_receive": round(half.avg_receive, 2),
            "avg_serve_consistency": round(half.avg_serve_consistency, 2),
            "avg_serve_power": round(half.avg_serve_power, 2),
            "positions": {
                pos: player.to_dict() for pos, player in half.positions.items()
            }
        }
