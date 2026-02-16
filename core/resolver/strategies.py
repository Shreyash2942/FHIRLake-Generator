from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Protocol, Sequence, TypeVar


T = TypeVar("T")


class SelectionStrategy(Protocol, Generic[T]):
    """Strategy interface for choosing an item from a sequence."""

    def pick(self, items: Sequence[T]) -> T:
        ...


@dataclass(slots=True)
class RandomChoiceStrategy(SelectionStrategy[T]):
    """
    Random choice strategy using ctx.rng.

    NOTE: rng must provide .choice().
    """
    rng: object

    def pick(self, items: Sequence[T]) -> T:
        return self.rng.choice(list(items))


@dataclass(slots=True)
class RoundRobinStrategy(SelectionStrategy[T]):
    """Deterministic round-robin selection."""
    _idx: int = 0

    def pick(self, items: Sequence[T]) -> T:
        if not items:
            raise ValueError("Cannot pick from empty sequence.")
        item = items[self._idx % len(items)]
        self._idx += 1
        return item
