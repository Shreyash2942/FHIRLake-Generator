from __future__ import annotations

import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from faker import Faker


@dataclass(slots=True)
class RunContext:
    """
    RunContext stores run-level state (no globals).

    - seed: reproducibility
    - faker: shared Faker instance
    - rng: shared random.Random
    - run_id: unique run identifier
    - created_at: ISO timestamp (UTC)
    - timestamp_utc: compact timestamp for folder names
    """

    seed: Optional[int] = None
    locale: str = "en_US"

    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    timestamp_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    )

    faker: Faker = field(init=False)
    rng: random.Random = field(init=False)

    def __post_init__(self) -> None:
        self.faker = Faker(self.locale)
        if self.seed is not None:
            self.faker.seed_instance(self.seed)
            self.rng = random.Random(self.seed)
        else:
            self.rng = random.Random()

    def new_uuid(self) -> str:
        return str(uuid.uuid4())
