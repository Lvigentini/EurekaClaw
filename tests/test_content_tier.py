"""Tests for Paper content tier tracking."""
import pytest
from eurekaclaw.types.artifacts import Paper


def test_paper_default_content_tier():
    p = Paper(paper_id="p1", title="Test", authors=["A"])
    assert p.content_tier == "metadata"


def test_paper_content_tier_full_text():
    p = Paper(paper_id="p1", title="Test", authors=["A"],
              content_tier="full_text", full_text="some content")
    assert p.content_tier == "full_text"
    assert p.full_text == "some content"


def test_paper_local_pdf_path():
    p = Paper(paper_id="p1", title="Test", authors=["A"],
              local_pdf_path="/tmp/paper.pdf")
    assert p.local_pdf_path == "/tmp/paper.pdf"


def test_paper_source_default():
    p = Paper(paper_id="p1", title="Test", authors=["A"])
    assert p.source == "search"


def test_paper_source_zotero():
    p = Paper(paper_id="p1", title="Test", authors=["A"], source="zotero")
    assert p.source == "zotero"


def test_paper_user_notes():
    p = Paper(paper_id="p1", title="Test", authors=["A"],
              user_notes="Important theorem in section 3")
    assert p.user_notes == "Important theorem in section 3"


def test_paper_backward_compatible():
    p = Paper(
        paper_id="old-paper", title="Old Style", authors=["B"],
        year=2024, abstract="An abstract", venue="NeurIPS",
        arxiv_id="2401.12345", relevance_score=0.8,
    )
    assert p.content_tier == "metadata"
    assert p.full_text is None
    assert p.local_pdf_path is None
    assert p.source == "search"
