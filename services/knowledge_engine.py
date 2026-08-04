from pathlib import Path


# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Knowledge folder
KNOWLEDGE_PATH = PROJECT_ROOT / "knowledge"

# Raw research
RAW_RESEARCH_PATH = KNOWLEDGE_PATH / "raw_research"


def load_research_documents() -> dict[str, str]:
    """
    Load every markdown research document.

    Returns:
        {
            "pool_with_friends": "...",
            "football": "...",
        }
    """

    documents = {}

    if not RAW_RESEARCH_PATH.exists():
        raise FileNotFoundError(
            f"Research folder not found:\n{RAW_RESEARCH_PATH}"
        )

    for file_path in sorted(
        RAW_RESEARCH_PATH.glob("*.md")
    ):
        documents[file_path.stem] = file_path.read_text(
            encoding="utf-8"
        )

    return documents


def build_research_corpus() -> str:
    """
    Combine every research document into one large corpus.
    """

    documents = load_research_documents()

    sections = []

    for occasion, content in documents.items():

        sections.append(
            f"# {occasion}\n\n{content.strip()}"
        )

    return "\n\n".join(sections)


if __name__ == "__main__":

    print("Project Root:")
    print(PROJECT_ROOT)

    print("\nKnowledge Path:")
    print(KNOWLEDGE_PATH)

    print("\nResearch Path:")
    print(RAW_RESEARCH_PATH)

    print("\nFiles Found:")

    for file_path in sorted(
        RAW_RESEARCH_PATH.glob("*.md")
    ):
        print(
            f" - {file_path.name} ({file_path.stat().st_size} bytes)"
        )

    print("\n----------------------------------------\n")

    corpus = build_research_corpus()

    print(corpus[:3000])