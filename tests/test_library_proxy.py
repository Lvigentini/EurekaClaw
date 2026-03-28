"""Tests for university library proxy rewriting, session management, and publishers."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from eurekalab.integrations.library.proxy import (
    ProxyRewriter,
    AuthenticatedSession,
    parse_cookie_string,
    parse_netscape_cookie_file,
)
from eurekalab.integrations.library.publishers import (
    resolve_pdf_url,
    identify_publisher,
)


# ---------------------------------------------------------------------------
# ProxyRewriter
# ---------------------------------------------------------------------------

class TestProxyRewriterNone:
    def test_none_mode_returns_unchanged(self):
        pr = ProxyRewriter(proxy_url="https://proxy.lib.edu", mode="none")
        assert pr.rewrite("https://doi.org/10.1234") == "https://doi.org/10.1234"

    def test_empty_url_returns_unchanged(self):
        pr = ProxyRewriter(proxy_url="", mode="prefix")
        assert pr.rewrite("https://doi.org/10.1234") == "https://doi.org/10.1234"

    def test_is_configured_false_for_none(self):
        pr = ProxyRewriter(proxy_url="https://proxy.lib.edu", mode="none")
        assert pr.is_configured is False


class TestProxyRewriterPrefix:
    def test_prefix_with_equals(self):
        pr = ProxyRewriter(
            proxy_url="https://ezproxy.lib.edu/login?url=",
            mode="prefix",
        )
        result = pr.rewrite("https://doi.org/10.1234/test")
        assert result == "https://ezproxy.lib.edu/login?url=https://doi.org/10.1234/test"

    def test_prefix_without_equals(self):
        pr = ProxyRewriter(
            proxy_url="https://proxy.lib.edu",
            mode="prefix",
        )
        result = pr.rewrite("https://doi.org/10.1234/test")
        assert result == "https://proxy.lib.edu/https://doi.org/10.1234/test"

    def test_is_configured_true(self):
        pr = ProxyRewriter(proxy_url="https://ezproxy.lib.edu/login?url=", mode="prefix")
        assert pr.is_configured is True


class TestProxyRewriterSuffix:
    def test_suffix_rewrites_domain(self):
        pr = ProxyRewriter(
            proxy_url="https://ezproxy.lib.edu",
            mode="suffix",
        )
        result = pr.rewrite("https://doi.org/10.1234/test")
        assert "doi-org.ezproxy.lib.edu" in result
        assert "/10.1234/test" in result

    def test_suffix_complex_domain(self):
        pr = ProxyRewriter(
            proxy_url="https://ezproxy.lib.edu",
            mode="suffix",
        )
        result = pr.rewrite("https://ieeexplore.ieee.org/document/12345")
        assert "ieeexplore-ieee-org.ezproxy.lib.edu" in result


class TestProxyRewriterVPN:
    def test_vpn_returns_unchanged(self):
        pr = ProxyRewriter(proxy_url="https://vpn.lib.edu", mode="vpn")
        url = "https://doi.org/10.1234/test"
        assert pr.rewrite(url) == url


# ---------------------------------------------------------------------------
# Cookie parsing
# ---------------------------------------------------------------------------

class TestParseCookieString:
    def test_simple_cookies(self):
        cookies = parse_cookie_string("name1=value1; name2=value2")
        assert cookies == {"name1": "value1", "name2": "value2"}

    def test_skips_attributes(self):
        cookies = parse_cookie_string("session=abc; domain=.lib.edu; path=/; secure")
        assert cookies == {"session": "abc"}

    def test_empty_string(self):
        assert parse_cookie_string("") == {}

    def test_whitespace_handling(self):
        cookies = parse_cookie_string("  name = value ; foo = bar  ")
        assert cookies == {"name": "value", "foo": "bar"}


class TestParseNetscapeCookieFile:
    def test_parses_valid_file(self, tmp_path):
        cookie_file = tmp_path / "cookies.txt"
        cookie_file.write_text(
            "# Netscape HTTP Cookie File\n"
            ".lib.edu\tTRUE\t/\tFALSE\t0\tezproxy\tABC123\n"
            ".lib.edu\tTRUE\t/\tFALSE\t0\tEZproxySID\txyz789\n"
        )
        cookies = parse_netscape_cookie_file(cookie_file)
        assert cookies == {"ezproxy": "ABC123", "EZproxySID": "xyz789"}

    def test_skips_comments_and_empty(self, tmp_path):
        cookie_file = tmp_path / "cookies.txt"
        cookie_file.write_text(
            "# Comment\n"
            "\n"
            ".lib.edu\tTRUE\t/\tFALSE\t0\tsession\tval\n"
        )
        cookies = parse_netscape_cookie_file(cookie_file)
        assert cookies == {"session": "val"}

    def test_missing_file(self, tmp_path):
        cookies = parse_netscape_cookie_file(tmp_path / "nonexistent.txt")
        assert cookies == {}


# ---------------------------------------------------------------------------
# AuthenticatedSession persistence
# ---------------------------------------------------------------------------

class TestSessionPersistence:
    def test_save_and_load(self, tmp_path):
        session_file = tmp_path / "session.json"

        with patch("eurekalab.integrations.library.proxy.SESSION_FILE", session_file):
            AuthenticatedSession.save_session(
                proxy_url="https://ezproxy.lib.edu/login?url=",
                proxy_mode="prefix",
                cookies={"ezproxy": "ABC123"},
            )

            session = AuthenticatedSession.from_session_file()
            assert session is not None
            assert session.cookies == {"ezproxy": "ABC123"}
            assert session.proxy.mode == "prefix"

    def test_load_missing_file(self, tmp_path):
        with patch("eurekalab.integrations.library.proxy.SESSION_FILE", tmp_path / "nope.json"):
            assert AuthenticatedSession.from_session_file() is None

    def test_status_unconfigured(self, tmp_path):
        with patch("eurekalab.integrations.library.proxy.SESSION_FILE", tmp_path / "nope.json"):
            status = AuthenticatedSession.get_session_status()
            assert status["configured"] is False

    def test_status_configured(self, tmp_path):
        session_file = tmp_path / "session.json"
        session_file.write_text(json.dumps({
            "proxy_url": "https://proxy.lib.edu",
            "proxy_mode": "prefix",
            "cookies": {"a": "1", "b": "2"},
            "updated_at": "2026-03-28T10:00:00",
        }))

        with patch("eurekalab.integrations.library.proxy.SESSION_FILE", session_file):
            status = AuthenticatedSession.get_session_status()
            assert status["configured"] is True
            assert status["cookie_count"] == 2


# ---------------------------------------------------------------------------
# Publisher patterns
# ---------------------------------------------------------------------------

class TestPublisherPatterns:
    def test_acm(self):
        url = resolve_pdf_url("https://dl.acm.org/doi/10.1145/1234.5678", "10.1145/1234.5678")
        assert url == "https://dl.acm.org/doi/pdf/10.1145/1234.5678"

    def test_springer(self):
        url = resolve_pdf_url("https://link.springer.com/article/10.1007/123", "10.1007/123")
        assert url == "https://link.springer.com/content/pdf/10.1007/123.pdf"

    def test_wiley(self):
        url = resolve_pdf_url("https://onlinelibrary.wiley.com/doi/10.1002/abc", "10.1002/abc")
        assert url == "https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/abc"

    def test_taylor_francis(self):
        url = resolve_pdf_url("https://www.tandfonline.com/doi/full/10.1080/123", "10.1080/123")
        assert url == "https://www.tandfonline.com/doi/pdf/10.1080/123"

    def test_sage(self):
        url = resolve_pdf_url("https://journals.sagepub.com/doi/10.1177/123", "10.1177/123")
        assert url == "https://journals.sagepub.com/doi/pdf/10.1177/123"

    def test_ieee_with_id(self):
        url = resolve_pdf_url("https://ieeexplore.ieee.org/document/9876543", "10.1109/TIT.2023")
        assert url is not None
        assert "9876543" in url

    def test_unknown_publisher(self):
        url = resolve_pdf_url("https://unknown-publisher.com/paper", "10.9999/unknown")
        assert url is None

    def test_nature(self):
        url = resolve_pdf_url("https://www.nature.com/articles/s41586-023-12345-6", "10.1038/s41586-023-12345-6")
        assert url is not None
        assert "s41586-023-12345-6" in url
        assert url.endswith(".pdf")


class TestIdentifyPublisher:
    def test_known(self):
        assert identify_publisher("https://dl.acm.org/doi/10.1145/123") == "ACM Digital Library"
        assert identify_publisher("https://ieeexplore.ieee.org/document/123") == "IEEE Xplore"

    def test_unknown(self):
        assert identify_publisher("https://example.com") is None
