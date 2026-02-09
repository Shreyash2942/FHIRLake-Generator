# Core/runtime/context.py
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
    RunContext stores run-level state that should NOT be global:
    - seed: for reproducibility
    - faker: shared Faker instance
    - rng: shared random generator
    - run_id: unique run identifier
    - timestamp_utc: consistent timestamp used in filenames/metadata
    """
    seed: Optional[int] = None
    locale: str = "en_US"

    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    )

    faker: Faker = field(init=False)
    rng: random.Random = field(init=False)

    def __post_init__(self) -> None:
        self.faker = Faker(self.locale)
        # Make Faker + random reproducible if seed is provided
        if self.seed is not None:
            self.faker.seed_instance(self.seed)
            self.rng = random.Random(self.seed)
        else:
            self.rng = random.Random()

    def new_uuid(self) -> str:
        """Convenience helper for generating UUIDs (string)."""
        return str(uuid.uuid4())
