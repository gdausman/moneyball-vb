"""
Visualizer for volleyball court rotations and team sheets.
"""
from typing import Dict, List
from engine.models import Player, HalfLineup, SetPlan

def format_player_badge(p: Player) -> str:
    return f"#{p.number} {p.name[:7]:<7} (Tot:{p.total_score})"

def render_court_ascii(half: HalfLineup) -> str:
    """
    Renders standard 6v6 court:
    NET
    [4: LF] [3: MF] [2: RF]
    [5: LB] [6: MB] [1: RB/Server]
    """
    p1 = half.positions.get(1)
    p2 = half.positions.get(2)
    p3 = half.positions.get(3)
    p4 = half.positions.get(4)
    p5 = half.positions.get(5)
    p6 = half.positions.get(6)

    def name_box(p: Player, pos_name: str) -> str:
        if not p:
            return f"[{pos_name}: Empty]"
        return f"{pos_name}: #{p.number} {p.name} (Rcv:{p.serve_receive} Srv:{p.serve_consistency}/{p.serve_power})"

    b4 = f"P4 (LF): #{p4.number} {p4.name}" if p4 else "P4: Empty"
    b3 = f"P3 (MF): #{p3.number} {p3.name}" if p3 else "P3: Empty"
    b2 = f"P2 (RF): #{p2.number} {p2.name} [Srv #2]" if p2 else "P2: Empty"

    b5 = f"P5 (LB): #{p5.number} {p5.name}" if p5 else "P5: Empty"
    b6 = f"P6 (MB): #{p6.number} {p6.name}" if p6 else "P6: Empty"
    b1 = f"P1 (RB): #{p1.number} {p1.name} [★ Srv #1]" if p1 else "P1: Empty"

    col_w = 26
    border = "═" * (col_w * 3 + 4)
    div_line = "─" * (col_w * 3 + 4)

    court = [
        f"        ╔{border}╗",
        f"        ║{'▲ ▲ ▲ NET ▲ ▲ ▲':^{col_w * 3 + 4}}║",
        f"        ╠{border}╣",
        f"        ║ {b4:<{col_w}} │ {b3:<{col_w}} │ {b2:<{col_w}} ║",
        f"        ║{div_line}║",
        f"        ║ {b5:<{col_w}} │ {b6:<{col_w}} │ {b1:<{col_w}} ║",
        f"        ╚{border}╝",
        f"             [Serve Order: P1 (Start) ➔ P2 ➔ P3 ➔ P4 ➔ P5 ➔ P6]"
    ]
    return "\n".join(court)

def render_set_summary(set_plan: SetPlan) -> str:
    h1 = set_plan.first_half
    h2 = set_plan.second_half
    anchor = set_plan.anchor_player

    bench1_names = ", ".join([f"#{p.number} {p.name}" for p in set_plan.bench_first_half])
    bench2_names = ", ".join([f"#{p.number} {p.name}" for p in set_plan.bench_second_half])

    output = []
    output.append(f"════════════════════════════════════════════════════════════════════════════════════")
    output.append(f"  SET {set_plan.set_number}: {set_plan.strategy_name.upper()} STRATEGY")
    output.append(f"  Full-Set Anchor: #{anchor.number} {anchor.name} (Plays both halves)")
    output.append(f"════════════════════════════════════════════════════════════════════════════════════\n")

    output.append(f"▶ 1ST HALF (Points 0 to ~13)")
    output.append(f"  Team Strength: {h1.total_score} pts | Avg Rcv: {h1.avg_receive:.1f}/5 | Avg Srv Cons: {h1.avg_serve_consistency:.1f}/5")
    output.append(f"  Bench (Waiting to sub): {bench1_names}")
    output.append(render_court_ascii(h1))
    output.append("")

    output.append(f"------------------------------------------------------------------------------------")
    output.append(f"⇄ MIDWAY SUBSTITUTION (At Point ~13): 5 Players OUT, 5 Players IN")
    output.append(f"  #{anchor.number} {anchor.name} stays on the court!")
    output.append(f"------------------------------------------------------------------------------------\n")

    output.append(f"▶ 2ND HALF (Points 13 to 25)")
    output.append(f"  Team Strength: {h2.total_score} pts | Avg Rcv: {h2.avg_receive:.1f}/5 | Avg Srv Cons: {h2.avg_serve_consistency:.1f}/5")
    output.append(f"  Bench (Resting): {bench2_names}")
    output.append(render_court_ascii(h2))
    output.append("")

    return "\n".join(output)
