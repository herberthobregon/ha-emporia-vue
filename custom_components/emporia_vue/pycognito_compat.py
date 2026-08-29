"""Compatibility shims for pycognito + PyJWT on Python 3.13+."""

from __future__ import annotations

import base64
from typing import Any

_PATCHED = False


def encode_token_for_digest(access_token: str | bytes) -> bytes:
    """Return the access token as UTF-8 bytes for OIDC at_hash hashing."""
    if isinstance(access_token, str):
        return access_token.encode("utf-8")
    return access_token


def at_hash_from_digest(digest: bytes) -> str:
    """Encode the left half of a digest as an OIDC at_hash string."""
    return (
        base64.urlsafe_b64encode(digest[: (len(digest) // 2)])
        .decode("ascii")
        .rstrip("=")
    )


def compute_at_hash(access_token: str | bytes, algorithm: str = "RS256") -> str:
    """Compute the OIDC at_hash claim for an access token."""
    import jwt

    alg_obj = jwt.get_algorithm_by_name(algorithm)
    digest = alg_obj.compute_hash_digest(encode_token_for_digest(access_token))
    return at_hash_from_digest(digest)


def apply_pycognito_at_hash_compat() -> None:
    """Patch pycognito so Hosted UI / SSO ID tokens verify on modern PyJWT.

    pycognito still hashes ``access_token`` as a ``str`` and then either
    strips padding from ``bytes`` with a ``str`` or compares ``bytes`` to the
    ``at_hash`` claim (``str``). PyJWT + cryptography on Python 3.13+ require
    bytes for ``compute_hash_digest``, which raises TypeError during Google/SSO
    token login.
    """
    global _PATCHED
    if _PATCHED:
        return

    from jwt.algorithms import Algorithm
    from pycognito import Cognito

    original_verify = Cognito.verify_token
    original_digest = Algorithm.compute_hash_digest
    original_b64encode = base64.urlsafe_b64encode

    def _compute_hash_digest(self: Any, bytestr: bytes | str) -> bytes:
        digest = original_digest(self, encode_token_for_digest(bytestr))
        # compute_hash_digest is only used in pycognito's at_hash block, which
        # runs after JWT decode. Switch b64encode to a str so .rstrip("=") and
        # comparison against the claim both succeed.
        base64.urlsafe_b64encode = _urlsafe_b64encode_as_str
        return digest

    def _urlsafe_b64encode_as_str(payload: bytes | str) -> str:
        encoded = original_b64encode(payload)
        if isinstance(encoded, bytes):
            return encoded.decode("ascii")
        return encoded

    def verify_token(self: Any, token: str, id_name: str, token_use: str) -> Any:
        Algorithm.compute_hash_digest = _compute_hash_digest
        try:
            return original_verify(self, token, id_name, token_use)
        finally:
            Algorithm.compute_hash_digest = original_digest
            base64.urlsafe_b64encode = original_b64encode

    verify_token._emporia_at_hash_patched = True  # type: ignore[attr-defined]
    Cognito.verify_token = verify_token  # type: ignore[method-assign]
    _PATCHED = True
