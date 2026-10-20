"""Public construction state shared by the two discovery pilots."""

from pydantic import BaseModel, ConfigDict, StrictInt


class Payload(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Reading(Payload):
    query: tuple[StrictInt, ...]
    values: tuple[StrictInt, ...]


class Specimen(Payload):
    build: tuple[StrictInt, ...] | None = None
    reading: Reading | None = None


class Stock(Payload):
    pass
