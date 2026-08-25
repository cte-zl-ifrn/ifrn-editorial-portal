import pytest

from src.errors import InvalidFrontMatterError
from src.markdown import split_front_matter


def test_splits_front_matter_and_body():
    raw = "---\ntitle: Exemplo\ncategory: moodle\n---\n\n# Título\n\nCorpo.\n"

    result = split_front_matter(raw)

    assert result.front_matter == {"title": "Exemplo", "category": "moodle"}
    assert result.front_matter_raw == "---\ntitle: Exemplo\ncategory: moodle\n---\n"
    assert result.body == "\n# Título\n\nCorpo.\n"


def test_front_matter_raw_plus_body_reproduces_original():
    raw = "---\ntitle: Exemplo\ntags:\n  - a\n  - b\n---\nCorpo com\nmúltiplas linhas.\n"

    result = split_front_matter(raw)

    assert result.front_matter_raw + result.body == raw


def test_document_without_front_matter():
    raw = "# Sem front matter\n\nSó corpo.\n"

    result = split_front_matter(raw)

    assert result.front_matter == {}
    assert result.front_matter_raw == ""
    assert result.body == raw


def test_empty_front_matter_block():
    raw = "---\n---\nCorpo.\n"

    result = split_front_matter(raw)

    assert result.front_matter == {}
    assert result.front_matter_raw == "---\n---\n"
    assert result.body == "Corpo.\n"


def test_unterminated_front_matter_raises():
    raw = "---\ntitle: Exemplo\n\n# Sem delimitador de fechamento\n"

    with pytest.raises(InvalidFrontMatterError):
        split_front_matter(raw)


def test_invalid_yaml_syntax_raises():
    raw = "---\ntitle: [não fechado\n---\nCorpo.\n"

    with pytest.raises(InvalidFrontMatterError):
        split_front_matter(raw)


def test_front_matter_that_is_not_a_mapping_raises():
    raw = "---\n- item1\n- item2\n---\nCorpo.\n"

    with pytest.raises(InvalidFrontMatterError):
        split_front_matter(raw)


def test_empty_document():
    assert split_front_matter("") == split_front_matter("")  # não deve lançar
    result = split_front_matter("")
    assert result.front_matter == {}
    assert result.front_matter_raw == ""
    assert result.body == ""
