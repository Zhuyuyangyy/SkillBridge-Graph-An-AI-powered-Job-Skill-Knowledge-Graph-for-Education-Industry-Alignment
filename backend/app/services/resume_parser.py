from app.services.mock_llm import mock_resume_parse


def parse_resume_text(text: str) -> dict:
    return mock_resume_parse(text)
