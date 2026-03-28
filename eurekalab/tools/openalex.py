"""OpenAlex API tool — comprehensive academic search with OA links and concepts."""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from eurekalab.config import settings
from eurekalab.tools.base import BaseTool

logger = logging.getLogger(__name__)

OPENALEX_BASE = "https://api.openalex.org"


class OpenAlexTool(BaseTool):
    name = "openalex_search"
    description = (
        "Search OpenAlex for academic papers. Returns rich metadata including "
        "concepts, open access URLs, citation counts, and institutional affiliations. "
        "Covers 250M+ works across all disciplines. No API key required."
    )

    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query",
                },
                "doi": {
                    "type": "string",
                    "description": "Look up a specific DOI (e.g. '10.1145/1234567')",
                },
                "limit": {
                    "type": "integer",
                    "default": 10,
                    "description": "Max results (default 10, max 25)",
                },
                "year_from": {
                    "type": "integer",
                    "description": "Filter: publication year >= this value",
                },
                "year_to": {
                    "type": "integer",
                    "description": "Filter: publication year <= this value",
                },
                "open_access_only": {
                    "type": "boolean",
                    "default": False,
                    "description": "Only return open access papers",
                },
            },
            "required": [],
        }

    async def call(
        self,
        query: str = "",
        doi: str = "",
        limit: int = 10,
        year_from: int | None = None,
        year_to: int | None = None,
        open_access_only: bool = False,
        **kwargs: Any,
    ) -> str:
        if not query and not doi:
            return json.dumps({"error": "Provide either 'query' or 'doi'"})

        headers = _build_headers()

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                if doi:
                    return await _lookup_doi(client, doi, headers)
                return await _search(
                    client, query, min(limit, 25), headers,
                    year_from=year_from, year_to=year_to,
                    open_access_only=open_access_only,
                )
        except httpx.HTTPStatusError as e:
            return json.dumps({"error": f"OpenAlex API error {e.response.status_code}"})
        except Exception as e:
            logger.exception("OpenAlex request failed")
            return json.dumps({"error": str(e)})


def _build_headers() -> dict[str, str]:
    headers: dict[str, str] = {}
    email = settings.library_contact_email
    if email:
        headers["User-Agent"] = f"EurekaLab/0.4 (mailto:{email})"
    return headers


async def _lookup_doi(
    client: httpx.AsyncClient,
    doi: str,
    headers: dict[str, str],
) -> str:
    url = f"{OPENALEX_BASE}/works/https://doi.org/{doi}"
    r = await client.get(url, headers=headers)
    r.raise_for_status()
    return json.dumps(_format_work(r.json()), indent=2)


async def _search(
    client: httpx.AsyncClient,
    query: str,
    limit: int,
    headers: dict[str, str],
    year_from: int | None = None,
    year_to: int | None = None,
    open_access_only: bool = False,
) -> str:
    params: dict[str, Any] = {
        "search": query,
        "per_page": limit,
    }

    # Build filter string
    filters: list[str] = []
    if year_from and year_to:
        filters.append(f"publication_year:{year_from}-{year_to}")
    elif year_from:
        filters.append(f"publication_year:{year_from}-")
    elif year_to:
        filters.append(f"publication_year:-{year_to}")
    if open_access_only:
        filters.append("open_access.is_oa:true")
    if filters:
        params["filter"] = ",".join(filters)

    r = await client.get(f"{OPENALEX_BASE}/works", params=params, headers=headers)
    r.raise_for_status()
    results = r.json().get("results", [])
    return json.dumps([_format_work(w) for w in results], indent=2)


def _format_work(work: dict) -> dict[str, Any]:
    """Extract key fields from an OpenAlex work object."""
    # Title
    title = work.get("title", "") or ""

    # Authors
    authors = []
    for authorship in work.get("authorships", [])[:5]:
        author = authorship.get("author", {})
        name = author.get("display_name", "")
        if name:
            authors.append(name)

    # Year
    year = work.get("publication_year")

    # DOI
    doi_url = work.get("doi", "") or ""
    doi = doi_url.replace("https://doi.org/", "") if doi_url else ""

    # Open access
    oa = work.get("open_access", {}) or {}
    oa_url = oa.get("oa_url", "") or ""
    is_oa = oa.get("is_oa", False)

    # Venue
    primary_location = work.get("primary_location", {}) or {}
    source = primary_location.get("source", {}) or {}
    venue = source.get("display_name", "") or ""

    # Concepts/topics
    concepts = []
    for concept in work.get("concepts", [])[:5]:
        name = concept.get("display_name", "")
        score = concept.get("score", 0)
        if name and score > 0.3:
            concepts.append(name)

    # Topics (newer API)
    topics = []
    for topic in work.get("topics", [])[:3]:
        name = topic.get("display_name", "")
        if name:
            topics.append(name)

    return {
        "openalex_id": work.get("id", ""),
        "title": title,
        "authors": authors,
        "year": year,
        "doi": doi,
        "venue": venue,
        "cited_by_count": work.get("cited_by_count", 0),
        "is_oa": is_oa,
        "oa_url": oa_url,
        "type": work.get("type", ""),
        "concepts": concepts,
        "topics": topics,
        "abstract": work.get("abstract", "") or "",
    }
