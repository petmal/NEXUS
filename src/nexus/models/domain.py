"""Versioned, validated domain envelopes; legacy episode encodings stay unchanged.

Only data-only, code-registered schemas can be loaded. Payloads contain JSON data,
not executable imports. Public roles cannot deserialize a private truth payload.
"""

from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator


class DomainEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: ClassVar[str]
    ontology: str
    version: Literal["domain-v1"] = "domain-v1"
    payload: dict[str, JsonValue]

    @model_validator(mode="after")
    def validate_payload(self):
        from nexus.ontology.payloads import schema_for

        schema = schema_for(self.ontology, self.role)
        self.payload = schema.model_validate(self.payload).model_dump(mode="json")
        return self

    def data(self):
        from nexus.ontology.payloads import schema_for

        return schema_for(self.ontology, self.role).model_validate(self.payload)


class DomainArtifact(DomainEnvelope):
    role = "artifact"
    id: str
    location: str


class DomainStock(DomainEnvelope):
    role = "stock"
    id: str
    location: str
    remaining: int | None = Field(default=None, ge=0)


class DomainInvestigation(DomainEnvelope):
    role = "investigation"

    @property
    def theory(self) -> int:
        return self.data().theory

    @property
    def discovery(self) -> int:
        return self.data().discovery


class DomainTruth(DomainEnvelope):
    role = "truth"
