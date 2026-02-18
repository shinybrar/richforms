from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import AnyUrl, BaseModel, ConfigDict, Field


class Discovery(BaseModel):
    """Discovery metadata mapped to OCI labels/annotations."""

    title: str = Field(..., description="Human-readable title of the image.")
    description: str = Field(
        ...,
        description="Human-readable description of the software packaged in the image.",
    )
    source: AnyUrl = Field(..., description="URL to get source code for building the image")
    version: str = Field(..., description="Version of the packaged software.")
    created: datetime = Field(
        ..., description="Datetime on which the image was built. Conforming to RFC 3339"
    )
    keywords: list[str] = Field(
        default_factory=list,
        description="Keywords used to support software discovery and search.",
        examples=["astronomy", "analysis", "python"],
    )
    domain: list[str] = Field(
        ...,
        min_length=1,
        description="Scientific domains supported by this image.",
        examples=[["astronomy"], ["astronomy", "scientific-computing"]],
    )
    kind: list[Literal["notebook", "headless", "carta", "firefly", "contributed"]] = Field(
        ...,
        min_length=1,
        description="Discovery kinds that classify this image.",
        examples=[["headless"], ["notebook", "headless"]],
    )
    deprecated: bool = Field(
        False,
        description="Whether this image is deprecated and should no longer be used.",
    )

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Metadata(BaseModel):
    """Metadata for the image."""

    discovery: Discovery = Field(
        ..., title="Discovery", description="Canonical discovery metadata."
    )

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Maintainer(BaseModel):
    """Details about the maintainer of the image."""

    name: str = Field(..., title="Name", description="Name of the maintainer.")
    email: str = Field(..., title="Email", description="Contact email.")
    github: str | None = Field(None, title="GitHub Username", description="GitHub Username.")
    gitlab: str | None = Field(None, title="GitLab Username", description="GitLab Username.")

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Manifest(BaseModel):
    """Manifest with maintainers list."""

    version: Literal[1] = Field(1, description="Library manifest schema version.")
    maintainers: list[Maintainer] = Field(
        ...,
        title="Maintainers",
        description="Image maintainers.",
    )
