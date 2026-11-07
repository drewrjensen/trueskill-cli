from typing import Any, Sequence, Tuple, Optional

class Rating:
    mu: float
    sigma: float
    def __init__(
        self, mu: Optional[float] = ..., sigma: Optional[float] = ...
    ) -> None: ...

class TrueSkill:
    mu: float
    sigma: float
    beta: float
    tau: float
    draw_probability: float
    def __init__(
        self,
        mu: float = ...,
        sigma: float = ...,
        beta: float = ...,
        tau: float = ...,
        draw_probability: float = ...,
        backend: Any = ...,
    ) -> None: ...
    def create_rating(
        self, mu: Optional[float] = ..., sigma: Optional[float] = ...
    ) -> Rating: ...
    def rate(
        self,
        rating_groups: Sequence[Sequence[Rating]],
        ranks: Optional[Sequence[int]] = ...,
        weights: Optional[Sequence[Sequence[float]]] = ...,
    ) -> Sequence[Tuple[Rating, ...]]: ...
    def quality(self, rating_groups: Sequence[Sequence[Rating]]) -> float: ...

def rate(
    rating_groups: Sequence[Sequence[Rating]],
    ranks: Optional[Sequence[int]] = ...,
    weights: Optional[Sequence[Sequence[float]]] = ...,
    env: Optional[TrueSkill] = ...,
) -> Sequence[Tuple[Rating, ...]]: ...
def quality(
    rating_groups: Sequence[Sequence[Rating]],
    env: Optional[TrueSkill] = ...,
) -> float: ...
def rate_1vs1(
    rating1: Rating,
    rating2: Rating,
    drawn: bool = ...,
    min_delta: float = ...,
    env: Optional[TrueSkill] = ...,
) -> Tuple[Rating, Rating]: ...
def quality_1vs1(
    rating1: Rating,
    rating2: Rating,
    env: Optional[TrueSkill] = ...,
) -> float: ...
