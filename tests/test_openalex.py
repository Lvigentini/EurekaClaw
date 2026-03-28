"""Tests for OpenAlexTool with mocked httpx."""

import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from eurekalab.tools.openalex import OpenAlexTool, _format_work


MOCK_WORK = {
    "id": "https://openalex.org/W12345",
    "title": "Attention Is All You Need",
    "authorships": [
        {"author": {"display_name": "Ashish Vaswani"}},
        {"author": {"display_name": "Noam Shazeer"}},
    ],
    "publication_year": 2017,
    "doi": "https://doi.org/10.5555/3295222.3295349",
    "open_access": {
        "is_oa": True,
        "oa_url": "https://arxiv.org/pdf/1706.03762",
    },
    "primary_location": {
        "source": {"display_name": "NeurIPS"},
    },
    "cited_by_count": 90000,
    "type": "article",
    "concepts": [
        {"display_name": "Transformer", "score": 0.95},
        {"display_name": "Attention", "score": 0.88},
        {"display_name": "Deep learning", "score": 0.75},
        {"display_name": "Irrelevant concept", "score": 0.1},
    ],
    "topics": [
        {"display_name": "Natural Language Processing"},
        {"display_name": "Neural Machine Translation"},
    ],
    "abstract": "The dominant sequence transduction models are based on...",
}

MOCK_SEARCH_RESPONSE = {
    "results": [MOCK_WORK],
}


class TestFormatWork:
    def test_extracts_title(self):
        result = _format_work(MOCK_WORK)
        assert result["title"] == "Attention Is All You Need"

    def test_extracts_doi(self):
        result = _format_work(MOCK_WORK)
        assert result["doi"] == "10.5555/3295222.3295349"

    def test_extracts_authors(self):
        result = _format_work(MOCK_WORK)
        assert result["authors"] == ["Ashish Vaswani", "Noam Shazeer"]

    def test_extracts_year(self):
        result = _format_work(MOCK_WORK)
        assert result["year"] == 2017

    def test_extracts_oa_info(self):
        result = _format_work(MOCK_WORK)
        assert result["is_oa"] is True
        assert result["oa_url"] == "https://arxiv.org/pdf/1706.03762"

    def test_extracts_venue(self):
        result = _format_work(MOCK_WORK)
        assert result["venue"] == "NeurIPS"

    def test_extracts_citation_count(self):
        result = _format_work(MOCK_WORK)
        assert result["cited_by_count"] == 90000

    def test_filters_low_score_concepts(self):
        result = _format_work(MOCK_WORK)
        assert "Transformer" in result["concepts"]
        assert "Irrelevant concept" not in result["concepts"]

    def test_extracts_topics(self):
        result = _format_work(MOCK_WORK)
        assert "Natural Language Processing" in result["topics"]

    def test_handles_empty_work(self):
        result = _format_work({})
        assert result["title"] == ""
        assert result["authors"] == []
        assert result["doi"] == ""
        assert result["year"] is None

    def test_handles_none_fields(self):
        work = {"title": None, "doi": None, "open_access": None, "primary_location": None}
        result = _format_work(work)
        assert result["title"] == ""
        assert result["doi"] == ""
        assert result["is_oa"] is False


class TestOpenAlexTool:
    @pytest.fixture
    def tool(self):
        return OpenAlexTool()

    def test_name(self, tool):
        assert tool.name == "openalex_search"

    def test_schema_has_query_and_doi(self, tool):
        schema = tool.input_schema()
        assert "query" in schema["properties"]
        assert "doi" in schema["properties"]
        assert "open_access_only" in schema["properties"]

    @pytest.mark.asyncio
    async def test_requires_query_or_doi(self, tool):
        result = json.loads(await tool.call())
        assert "error" in result

    @pytest.mark.asyncio
    async def test_search_mode(self, tool):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = MOCK_SEARCH_RESPONSE

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("eurekalab.tools.openalex.httpx.AsyncClient", return_value=mock_client):
            result = json.loads(await tool.call(query="attention transformers"))

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["title"] == "Attention Is All You Need"
        assert result[0]["doi"] == "10.5555/3295222.3295349"

    @pytest.mark.asyncio
    async def test_doi_lookup(self, tool):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = MOCK_WORK

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("eurekalab.tools.openalex.httpx.AsyncClient", return_value=mock_client):
            result = json.loads(await tool.call(doi="10.5555/3295222.3295349"))

        assert isinstance(result, dict)
        assert result["title"] == "Attention Is All You Need"

    @pytest.mark.asyncio
    async def test_search_with_year_filter(self, tool):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"results": []}

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("eurekalab.tools.openalex.httpx.AsyncClient", return_value=mock_client):
            result = json.loads(await tool.call(query="test", year_from=2020, year_to=2024))

        # Verify filter was passed
        call_args = mock_client.get.call_args
        params = call_args.kwargs.get("params", {})
        assert "publication_year:2020-2024" in params.get("filter", "")

    @pytest.mark.asyncio
    async def test_search_oa_only(self, tool):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"results": []}

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("eurekalab.tools.openalex.httpx.AsyncClient", return_value=mock_client):
            result = json.loads(await tool.call(query="test", open_access_only=True))

        call_args = mock_client.get.call_args
        params = call_args.kwargs.get("params", {})
        assert "open_access.is_oa:true" in params.get("filter", "")
