"""Strict policy schema models for hardened local security controls."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr


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

    model_config = ConfigDict(extra="forbid")

    default_action: PolicyAction = PolicyAction.DENY
    allow_cloud_destinations: StrictBool = False
    allowed_local_destinations: list[StrictStr] = Field(
        default_factory=lambda: ["127.0.0.1", "localhost", "::1"]
    )


class AuditPolicy(BaseModel):
    """Minimal local audit contract for policy-relevant actions."""

    model_config = ConfigDict(extra="forbid")

    enabled: StrictBool = True
    include_reason_codes: StrictBool = True
    sink: StrictStr = "jsonl"


class ArtifactEncryptionPolicy(BaseModel):
    """Application-layer encryption for repo-local artifacts under ``hardened_local``.

    When ``require_encryption`` is true under hardened_local, loaders must not silently
    disable encryption or fall back to plaintext for protected artifacts (D-03).
    """

    model_config = ConfigDict(extra="forbid")

    enabled: StrictBool = False
    require_encryption: StrictBool = False
    key_env_var: StrictStr = "CRG_ARTIFACT_ENCRYPTION_KEY"


class HardenedPolicy(BaseModel):
    """Top-level policy contract for local-only hardened behavior."""

    model_config = ConfigDict(extra="forbid")

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
    artifact_encryption: ArtifactEncryptionPolicy = Field(
        default_factory=ArtifactEncryptionPolicy
    )
