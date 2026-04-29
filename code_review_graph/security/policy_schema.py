"""Strict policy schema models for hardened local security controls."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class PolicyMode(str, Enum):
    HARDENED_LOCAL = "hardened_local"
    STANDARD = "standard"


class PolicyAction(str, Enum):
    ALLOW = "allow"
    DENY = "deny"


class ProtectedDataClass(str, Enum):
    SOURCE_SNIPPET = "source_snippet"
    SYMBOL_CONTEXT = "symbol_context"
    FULL_FILE_CONTENT = "full_file_content"
    EMBEDDING_INPUT = "embedding_input"


class EgressPolicy(BaseModel):
    """Outbound controls used by runtime integrations."""

    model_config = ConfigDict(extra="forbid", strict=True)

    default_action: PolicyAction = PolicyAction.DENY
    allow_cloud_destinations: bool = False
    allowed_local_destinations: list[str] = Field(
        default_factory=lambda: ["127.0.0.1", "localhost", "::1"]
    )


class AuditPolicy(BaseModel):
    """Minimal local audit contract for policy-relevant actions."""

    model_config = ConfigDict(extra="forbid", strict=True)

    enabled: bool = True
    include_reason_codes: bool = True
    sink: str = "jsonl"


class HardenedPolicy(BaseModel):
    """Top-level policy contract for local-only hardened behavior."""

    model_config = ConfigDict(extra="forbid", strict=True)

    mode: PolicyMode = PolicyMode.HARDENED_LOCAL
    egress: EgressPolicy = Field(default_factory=EgressPolicy)
    protected_data_classes: list[ProtectedDataClass] = Field(
        default_factory=lambda: [
            ProtectedDataClass.SOURCE_SNIPPET,
            ProtectedDataClass.SYMBOL_CONTEXT,
            ProtectedDataClass.FULL_FILE_CONTENT,
            ProtectedDataClass.EMBEDDING_INPUT,
        ]
    )
    audit: AuditPolicy = Field(default_factory=AuditPolicy)
