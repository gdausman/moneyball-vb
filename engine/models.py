"""
Data models for Moneyball VB.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Player:
    number: int
    name: str
    serve_consistency: int
    serve_power: int
    serve_receive: int
    rally_hits: int
    total_score: int
    tier: str

    @property
    def expected_serve_value(self) -> float:
        """
        Expected service points metric for youth volleyball:
        Power creates aces, deep disruption, and free balls (scarcest offensive asset in CYO youth volleyball).
        Consistency gets the ball over the net without unforced errors.
        Total score reflects overall athleticism and composure under pressure.
        """
        return (self.serve_power * 1.8) + (self.serve_consistency * 1.3) + (self.total_score * 0.25)

    @property
    def defense_value(self) -> float:
        """
        Serve receive defense:
        First contact (serve_receive) is the rarest skill in CYO volleyball; rally_hits saves scrambles.
        """
        return (self.serve_receive * 2.5) + (self.rally_hits * 1.5) + (self.total_score * 0.2)

    def to_dict(self) -> Dict:
        return {
            "number": self.number,
            "name": self.name,
            "serve_consistency": self.serve_consistency,
            "serve_power": self.serve_power,
            "serve_receive": self.serve_receive,
            "rally_hits": self.rally_hits,
            "total_score": self.total_score,
            "tier": self.tier
        }

@dataclass
class HalfLineup:
    half_name: str  # "First Half (0-13)" or "Second Half (13-25)"
    # Positions 1 to 6: 1=RB (Server), 2=RF, 3=MF, 4=LF, 5=LB, 6=MB
    positions: Dict[int, Player] = field(default_factory=dict)

    @property
    def players(self) -> List[Player]:
        return [self.positions[i] for i in range(1, 7) if i in self.positions]

    @property
    def total_score(self) -> int:
        return sum(p.total_score for p in self.players)

    @property
    def avg_receive(self) -> float:
        if not self.players:
            return 0.0
        return sum(p.serve_receive for p in self.players) / len(self.players)

    @property
    def avg_serve_consistency(self) -> float:
        if not self.players:
            return 0.0
        return sum(p.serve_consistency for p in self.players) / len(self.players)

    @property
    def avg_serve_power(self) -> float:
        if not self.players:
            return 0.0
        return sum(p.serve_power for p in self.players) / len(self.players)

@dataclass
class SetPlan:
    set_number: int
    strategy_name: str
    first_half: HalfLineup
    second_half: HalfLineup
    anchor_player: Player  # Plays both halves
    bench_first_half: List[Player]
    bench_second_half: List[Player]
