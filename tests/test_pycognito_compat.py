"""Tests for the pycognito at_hash compatibility shim."""

from __future__ import annotations

import base64
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any

import pytest

MODULE_PATH = (
    Path(__file__).parents[1]
    / "custom_components"
    / "emporia_vue"
    / "pycognito_compat.py"
)
SPEC = spec_from_file_location("emporia_vue_pycognito_compat", MODULE_PATH)
assert SPEC and SPEC.loader
COMPAT = module_from_spec(SPEC)
SPEC.loader.exec_module(COMPAT)

jwt = pytest.importorskip("jwt")


def test_str_and_bytes_access_tokens_produce_the_same_at_hash() -> None:
    """OIDC hashes the ASCII octets of the access token, whether str or bytes."""
    access_token = "example-access-token"
    from_str = COMPAT.compute_at_hash(access_token)
    from_bytes = COMPAT.compute_at_hash(access_token.encode("utf-8"))

    assert from_str == from_bytes
    assert isinstance(from_str, str)
    assert "=" not in from_str


def test_unpatched_pyjwt_rejects_string_access_tokens() -> None:
    """Reproduce the pycognito TypeError on modern PyJWT/cryptography."""
    alg_obj = jwt.get_algorithm_by_name("RS256")

    with pytest.raises(TypeError, match="bytestring|buffer"):
        alg_obj.compute_hash_digest("example-access-token")


def test_unpatched_at_hash_rstrip_and_compare_are_type_mismatched() -> None:
    """After hashing, pycognito rstrip("=") on bytes and compares bytes to str."""
    digest = jwt.get_algorithm_by_name("RS256").compute_hash_digest(
        b"example-access-token"
    )
    encoded = base64.urlsafe_b64encode(digest[: (len(digest) // 2)])
    claim = COMPAT.at_hash_from_digest(digest)

    assert isinstance(encoded, bytes)
    with pytest.raises(TypeError, match="bytes-like"):
        encoded.rstrip("=")
    assert encoded.rstrip(b"=").decode("ascii") == claim
    assert encoded.rstrip(b"=") != claim


def test_shim_makes_pycognito_at_hash_path_accept_str_tokens() -> None:
    """The wrap must encode the token and compare at_hash as a string."""
    pycognito = pytest.importorskip("pycognito")

    access_token = "example-access-token"
    expected = COMPAT.compute_at_hash(access_token)
    captured: dict[str, Any] = {}

    def broken_verify_token(self: Any, token: str, id_name: str, token_use: str) -> str:
        alg_obj = jwt.get_algorithm_by_name("RS256")
        digest = alg_obj.compute_hash_digest(self.access_token)
        at_hash = base64.urlsafe_b64encode(digest[: (len(digest) // 2)]).rstrip("=")
        captured["at_hash"] = at_hash
        if at_hash != expected:
            raise AssertionError("at_hash claim does not match access_token.")
        return token

    original = pycognito.Cognito.verify_token
    COMPAT._PATCHED = False
    pycognito.Cognito.verify_token = broken_verify_token
    try:
        COMPAT.apply_pycognito_at_hash_compat()

        fake = type("FakeCognito", (), {"access_token": access_token})()
        assert pycognito.Cognito.verify_token(fake, "id", "id_token", "id") == "id"
        assert captured["at_hash"] == expected
        assert isinstance(captured["at_hash"], str)
    finally:
        pycognito.Cognito.verify_token = original
        COMPAT._PATCHED = False
        COMPAT.apply_pycognito_at_hash_compat()
