import pytest

from app.modules.context.provider import INSTRUCTIONS_VERSION, load_instructions


def test_instructions_file_for_current_version_exists() -> None:
    instructions = load_instructions()

    assert INSTRUCTIONS_VERSION == "v1"
    assert instructions.startswith("Você é o Yoda")


def test_unknown_instructions_version_fails() -> None:
    with pytest.raises(FileNotFoundError):
        load_instructions("v999")
