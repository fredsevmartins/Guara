"""Validated public inputs. Unknown fields are rejected rather than silently discarded."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, field_validator

Relationship = Literal["SUPPORTS", "CONTRADICTS", "RELATED", "INCONCLUSIVE"]
Review = Literal["ACCEPTED_FOR_USE", "NEEDS_REVIEW", "REJECTED", "INCONCLUSIVE"]
SourceType = Literal[
    "SCIENTIFIC_PAPER",
    "DATASET",
    "TECHNICAL_DOCUMENT",
    "EXPERIMENT",
    "WEBSITE_REFERENCE",
    "USER_PROVIDED_STATEMENT",
    "OTHER",
]


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Claim(Input):
    original_statement: str = Field(min_length=1, max_length=20000)
    subject: str | None = Field(default=None, max_length=500)
    predicate: str | None = Field(default=None, max_length=500)
    value: FiniteFloat | str | None = None
    unit: str | None = Field(default=None, max_length=100)
    context: dict[str, Any] = Field(default_factory=dict)
    provenance: dict[str, Any] = Field(default_factory=dict)

    @field_validator("original_statement")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("Statement must not be blank")
        return value


class Source(Input):
    title: str = Field(min_length=1, max_length=2000)
    source_type: SourceType = "OTHER"
    authors: list[str] = Field(default_factory=list)
    doi: str | None = None
    url: str | None = None
    publication_date: str | None = None
    file_path: str | None = None


class Link(Input):
    claim_id: str
    source_id: str
    relationship: Relationship
    source_location: str = Field(min_length=1, max_length=2000)
    excerpt: str = Field(min_length=1, max_length=20000)
    actor: str = Field(min_length=1, max_length=500)
