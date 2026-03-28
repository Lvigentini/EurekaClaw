"""ProxyRewriter and AuthenticatedSession for university library access."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)

SESSION_FILE = Path.home() / ".eurekalab" / "library_session.json"


class ProxyRewriter:
    """Rewrite URLs to route through a university library proxy.

    Modes:
        prefix  — prepend proxy URL: ``{proxy_url}{target_url}``
        suffix  — replace target domain: ``target-domain.proxy.host``
        vpn     — no rewriting (access is at network level)
        none    — disabled
    """

    def __init__(self, proxy_url: str = "", mode: str = "none") -> None:
        self.proxy_url = proxy_url.rstrip("/")
        self.mode = mode

    def rewrite(self, url: str) -> str:
        if self.mode == "none" or not self.proxy_url:
            return url
        if self.mode == "vpn":
            return url
        if self.mode == "prefix":
            return self._rewrite_prefix(url)
        if self.mode == "suffix":
            return self._rewrite_suffix(url)
        logger.warning("ProxyRewriter: unknown mode '%s', returning original URL", self.mode)
        return url

    def _rewrite_prefix(self, url: str) -> str:
        """EZproxy prefix mode: ``https://ezproxy.lib.edu/login?url=https://...``"""
        separator = "" if self.proxy_url.endswith("=") else "/"
        return f"{self.proxy_url}{separator}{url}"

    def _rewrite_suffix(self, url: str) -> str:
        """EZproxy suffix mode: ``https://doi-org.ezproxy.lib.edu/...``

        Replaces dots in the target domain with hyphens and appends the
        proxy host as suffix.
        """
        parsed = urlparse(url)
        proxy_parsed = urlparse(self.proxy_url)
        proxy_host = proxy_parsed.hostname or proxy_parsed.path

        target_host = parsed.hostname or ""
        rewritten_host = target_host.replace(".", "-") + "." + proxy_host

        return parsed._replace(
            netloc=rewritten_host,
            scheme=parsed.scheme or "https",
        ).geturl()

    @property
    def is_configured(self) -> bool:
        return self.mode != "none" and bool(self.proxy_url)


class AuthenticatedSession:
    """HTTP client with university library session cookies and proxy rewriting."""

    def __init__(
        self,
        proxy: ProxyRewriter,
        cookies: dict[str, str] | None = None,
    ) -> None:
        self.proxy = proxy
        self.cookies = cookies or {}

    async def get(self, url: str, **kwargs: Any) -> httpx.Response:
        """GET *url* through the proxy with session cookies."""
        rewritten = self.proxy.rewrite(url)
        async with httpx.AsyncClient(
            cookies=self.cookies,
            follow_redirects=True,
            timeout=kwargs.pop("timeout", 60),
        ) as client:
            return await client.get(rewritten, **kwargs)

    @classmethod
    def from_session_file(cls, proxy: ProxyRewriter | None = None) -> AuthenticatedSession | None:
        """Load a saved session from ``~/.eurekalab/library_session.json``.

        Returns None if the file doesn't exist or is invalid.
        """
        if not SESSION_FILE.exists():
            return None

        try:
            data = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Failed to read library session file: %s", e)
            return None

        if proxy is None:
            proxy = ProxyRewriter(
                proxy_url=data.get("proxy_url", ""),
                mode=data.get("proxy_mode", "none"),
            )

        cookies = data.get("cookies", {})
        if not cookies:
            logger.warning("Library session file has no cookies")
            return None

        return cls(proxy=proxy, cookies=cookies)

    @staticmethod
    def save_session(
        proxy_url: str,
        proxy_mode: str,
        cookies: dict[str, str],
    ) -> Path:
        """Persist session data to ``~/.eurekalab/library_session.json``."""
        SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "proxy_url": proxy_url,
            "proxy_mode": proxy_mode,
            "cookies": cookies,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        SESSION_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        logger.info("Library session saved to %s", SESSION_FILE)
        return SESSION_FILE

    @staticmethod
    def get_session_status() -> dict[str, Any]:
        """Return current session status for display."""
        if not SESSION_FILE.exists():
            return {"configured": False, "message": "No library session configured"}

        try:
            data = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {"configured": False, "message": "Session file is corrupt"}

        return {
            "configured": True,
            "proxy_url": data.get("proxy_url", ""),
            "proxy_mode": data.get("proxy_mode", "none"),
            "cookie_count": len(data.get("cookies", {})),
            "updated_at": data.get("updated_at", "unknown"),
        }


def parse_cookie_string(cookie_str: str) -> dict[str, str]:
    """Parse a ``Cookie`` header string into a dict.

    Accepts: ``name=value; name2=value2; ...``
    """
    cookies: dict[str, str] = {}
    for part in cookie_str.split(";"):
        part = part.strip()
        if "=" in part:
            key, _, value = part.partition("=")
            key = key.strip()
            value = value.strip()
            # Skip common non-cookie attributes
            if key.lower() not in ("domain", "path", "expires", "max-age", "secure", "httponly", "samesite"):
                cookies[key] = value
    return cookies


def parse_netscape_cookie_file(path: Path) -> dict[str, str]:
    """Parse a Netscape-format cookies.txt file into a dict.

    Format: ``domain\\tTRUE\\tpath\\tFALSE\\texpiry\\tname\\tvalue``
    """
    cookies: dict[str, str] = {}
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) >= 7:
                name = parts[5]
                value = parts[6]
                cookies[name] = value
    except (OSError, IndexError) as e:
        logger.warning("Failed to parse cookie file %s: %s", path, e)
    return cookies
