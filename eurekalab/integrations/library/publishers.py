"""Publisher-specific PDF URL patterns for resolving DOIs to direct PDF links."""

from __future__ import annotations

import logging
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


# Each entry maps a publisher to its domain patterns and PDF URL construction.
# "pdf_template" uses {doi} as placeholder.  If "extract_id" is present, it
# extracts a publisher-specific ID from the landing-page URL via regex, and
# "pdf_template" may use {id} instead.

PUBLISHER_PATTERNS: list[dict[str, str]] = [
    {
        "name": "ACM Digital Library",
        "domain": "dl.acm.org",
        "pdf_template": "https://dl.acm.org/doi/pdf/{doi}",
    },
    {
        "name": "IEEE Xplore",
        "domain": "ieeexplore.ieee.org",
        "extract_id": r"/document/(\d+)",
        "pdf_template": "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber={id}",
    },
    {
        "name": "Springer",
        "domain": "link.springer.com",
        "pdf_template": "https://link.springer.com/content/pdf/{doi}.pdf",
    },
    {
        "name": "Elsevier (ScienceDirect)",
        "domain": "sciencedirect.com",
        "pdf_template": "https://www.sciencedirect.com/science/article/pii/{id}/pdf",
        "extract_id": r"/pii/([A-Z0-9]+)",
    },
    {
        "name": "Wiley",
        "domain": "onlinelibrary.wiley.com",
        "pdf_template": "https://onlinelibrary.wiley.com/doi/pdfdirect/{doi}",
    },
    {
        "name": "Taylor & Francis",
        "domain": "tandfonline.com",
        "pdf_template": "https://www.tandfonline.com/doi/pdf/{doi}",
    },
    {
        "name": "SAGE",
        "domain": "journals.sagepub.com",
        "pdf_template": "https://journals.sagepub.com/doi/pdf/{doi}",
    },
    {
        "name": "MDPI",
        "domain": "mdpi.com",
        "pdf_template": "https://www.mdpi.com/{id}/pdf",
        "extract_id": r"mdpi\.com/(\d+-\d+/\d+/\d+/\d+)",
    },
    {
        "name": "Nature",
        "domain": "nature.com",
        "pdf_template": "https://www.nature.com/articles/{id}.pdf",
        "extract_id": r"/articles/([^/?#]+)",
    },
    {
        "name": "Oxford Academic",
        "domain": "academic.oup.com",
        "pdf_template": "https://academic.oup.com/{id}",
        "extract_id": r"(.*)",  # OUP uses varied paths; best effort
    },
    {
        "name": "Cambridge University Press",
        "domain": "cambridge.org",
        "pdf_template": "https://www.cambridge.org/core/services/aop-cambridge-core/content/view/{id}",
        "extract_id": r"/article/[^/]+/([A-F0-9]+)",
    },
    {
        "name": "APS (Physical Review)",
        "domain": "journals.aps.org",
        "pdf_template": "https://journals.aps.org/prl/pdf/{doi}",
    },
    {
        "name": "IOP Science",
        "domain": "iopscience.iop.org",
        "pdf_template": "https://iopscience.iop.org/article/{doi}/pdf",
    },
]


def resolve_pdf_url(landing_url: str, doi: str) -> str | None:
    """Given a publisher landing page URL and DOI, attempt to construct a direct PDF URL.

    Returns the PDF URL if a matching publisher pattern is found, else None.
    """
    parsed = urlparse(landing_url)
    host = parsed.hostname or ""

    for pattern in PUBLISHER_PATTERNS:
        if pattern["domain"] not in host:
            continue

        template = pattern["pdf_template"]

        # If we need a publisher-specific ID, extract it from the URL
        if "extract_id" in pattern and "{id}" in template:
            m = re.search(pattern["extract_id"], landing_url)
            if m:
                pub_id = m.group(1)
                result = template.replace("{id}", pub_id)
                logger.debug("Publisher %s: resolved PDF → %s", pattern["name"], result)
                return result
            # Couldn't extract ID — fall through to DOI-based template
            if "{doi}" not in template:
                continue

        if "{doi}" in template:
            result = template.replace("{doi}", doi)
            logger.debug("Publisher %s: resolved PDF → %s", pattern["name"], result)
            return result

    return None


def identify_publisher(url: str) -> str | None:
    """Return the publisher name for a given URL, or None."""
    parsed = urlparse(url)
    host = parsed.hostname or ""
    for pattern in PUBLISHER_PATTERNS:
        if pattern["domain"] in host:
            return pattern["name"]
    return None
