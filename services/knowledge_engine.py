import os

import yaml

import json

from dotenv import load_dotenv

from pathlib import Path

from openai import OpenAI

load_dotenv()
client = OpenAI()

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


def load_master_evidence() -> list[str]:
    """
    Load PintFinder's canonical evidence vocabulary.

    Each non-empty line in master_evidence.md
    represents one allowed evidence concept.
    """

    evidence_path = (
        KNOWLEDGE_PATH
        / "master_evidence.md"
    )

    if not evidence_path.exists():
        raise FileNotFoundError(
            f"Master evidence file not found:\n"
            f"{evidence_path}"
        )

    evidence = []

    for line in evidence_path.read_text(
        encoding="utf-8"
    ).splitlines():

        item = line.strip()

        if not item:
            continue

        if item.startswith("#"):
            continue

        evidence.append(item)

    return evidence

def test_ai_connection() -> str:
    """
    Test that PintFinder can successfully call
    the OpenAI API.
    """

    response = client.responses.create(
        model="gpt-5.4-mini",
        input=(
            "Reply with exactly: "
            "PintFinder AI connected"
        ),
    )

    return response.output_text

def extract_review_evidence(
    review_text: str,
) -> list[dict]:
    """
    Use AI to extract contextual evidence from a review.

    The model may only use evidence concepts from
    PintFinder's master evidence vocabulary.
    """

    if not isinstance(review_text, str):
        return []

    review_text = review_text.strip()

    if not review_text:
        return []

    allowed_evidence = load_master_evidence()
    ontology_definitions = load_ontology_definitions()

    vocabulary_lines = []

    for evidence_id in allowed_evidence:

        ontology = ontology_definitions.get(
            evidence_id,
            {},
        )

        definition = ontology.get(
            "description"
        )

        domains = ontology.get(
            "domains",
            [],
        )

        parts = [
            evidence_id
        ]

        if domains:
            parts.append(
                "Domains: "
                + ", ".join(domains)
            )

        if definition:
            parts.append(
                "Definition: "
                + definition.strip()
            )

        vocabulary_lines.append(
            " | ".join(parts)
        )
    vocabulary = "\n".join(
        vocabulary_lines
    )
    

    prompt = f"""
You are PintFinder's review evidence extraction engine.

Analyse the review and extract every meaningful piece of
evidence that is explicitly stated or strongly implied.

You MUST only use evidence types from the allowed
PintFinder vocabulary below.

Do not invent evidence types.

For each piece of evidence return:

- type
- confidence from 0 to 100
- sentiment: positive, neutral, negative, or unknown
- source_text
- temporal:
    - days
    - daypart
    - recurring

Important:

Important reasoning rules:

A review may contain multiple pieces of evidence about the
same concept. Preserve them separately when their context
differs.

If a reviewer describes something as generally available
but unavailable or harder to access at a specific time,
extract BOTH:
- the general positive availability evidence
- the time-specific negative availability evidence

Infer consequences only when they are strongly supported
by the review.

Example:
"Tables are usually easy to get on except Thursday nights
when the league takes over"

should produce:
- pool_game_availability: positive, general
- pool_league: neutral, Thursday evening
- pool_game_availability: negative, Thursday evening

Temporal language must be normalised:
- morning -> morning
- afternoon -> afternoon
- evening -> evening
- night / nights -> evening
- late night -> late_night

Days must be lowercase:
monday, tuesday, wednesday, thursday, friday, saturday,
sunday.

Do not infer repeat visits merely because someone says
they like or love the venue. Repeat evidence requires
language indicating repeated visits, returning, being a
regular, or equivalent behaviour.

Do not treat an activity such as a pool league as
inherently positive or negative.

Return ONLY a JSON array.
Do not include markdown or explanation.

ALLOWED EVIDENCE:

{vocabulary}

REVIEW:

{review_text}
"""

    response = client.responses.create(
        model="gpt-5.4-mini",
        input=prompt,
    )

    raw_output = response.output_text.strip()

    try:
        evidence = json.loads(
            raw_output
        )
    except json.JSONDecodeError:
        print(
            "AI returned invalid evidence JSON:"
        )
        print(raw_output)
        return []

    if not isinstance(evidence, list):
        return []

    allowed_set = set(
        allowed_evidence
    )

    validated_evidence = []

    for item in evidence:

        if not isinstance(item, dict):
            continue

        evidence_type = item.get(
            "type"
        )

        if evidence_type not in allowed_set:
            continue

        validated_evidence.append(
            item
        )

    return validated_evidence

def load_ontology_definitions() -> dict:
    """
    Load evidence definitions and domains from
    PintFinder's working ontology YAML files.
    """

    working_path = (
        KNOWLEDGE_PATH
        / "working"
    )

    definitions = {}

    if not working_path.exists():
        return definitions

    for file_path in sorted(
        working_path.glob("*.yaml")
    ):
        with file_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = yaml.safe_load(file)

        if not isinstance(data, dict):
            continue

        for domain, category_data in data.items():

            if not isinstance(category_data, dict):
                continue

            evidence_items = category_data.get(
                "evidence",
                [],
            )

            if not isinstance(evidence_items, list):
                continue

            for item in evidence_items:

                # Existing simple ontology entries
                if isinstance(item, str):

                    if item not in definitions:
                        definitions[item] = {
                            "description": None,
                            "domains": [],
                        }

                    if domain not in definitions[item]["domains"]:
                        definitions[item]["domains"].append(
                            domain
                        )

                # Rich ontology entries
                elif isinstance(item, dict):

                    evidence_id = item.get("id")

                    if not evidence_id:
                        continue

                    existing = definitions.get(
                        evidence_id,
                        {
                            "description": None,
                            "domains": [],
                        },
                    )

                    description = item.get(
                        "description"
                    )

                    if description:
                        existing["description"] = description

                    if domain not in existing["domains"]:
                        existing["domains"].append(
                            domain
                        )

                    definitions[evidence_id] = existing

    return definitions

def load_domain_concepts(
    domain: str,
) -> list[str]:
    """
    Load all evidence concept IDs belonging
    to one ontology domain.
    """

    file_path = (
        KNOWLEDGE_PATH
        / "working"
        / f"{domain}.yaml"
    )

    if not file_path.exists():
        return []

    with file_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        return []

    domain_data = data.get(
        domain,
        {},
    )

    if not isinstance(domain_data, dict):
        return []

    evidence_items = domain_data.get(
        "evidence",
        [],
    )

    concepts = []

    for item in evidence_items:

        if isinstance(item, str):
            concepts.append(item)

        elif isinstance(item, dict):
            evidence_id = item.get("id")

            if evidence_id:
                concepts.append(evidence_id)

    return concepts

def generate_evidence_definition(
    evidence_id: str,
    domain: str,
    neighbouring_concepts: list[str],
) -> str:
    """
    Generate a draft semantic definition for one
    evidence concept using its domain and neighbours.
    """

    neighbours = "\n".join(
        f"- {concept}"
        for concept in neighbouring_concepts
        if concept != evidence_id
    )

    prompt = f"""
You are building a semantic evidence ontology for analysing
pub and venue reviews.

DOMAIN:
{domain}

CONCEPT TO DEFINE:
{evidence_id}

NEIGHBOURING CONCEPTS IN THIS DOMAIN:
{neighbours}

Define the concept precisely enough that another AI can
consistently decide whether review evidence belongs to this
concept or to one of its neighbouring concepts.

Requirements:

- Interpret the concept specifically within the stated domain.
- Explain what evidence belongs to this concept.
- Establish its semantic boundary from similar neighbouring concepts.
- State what should NOT be classified here where useful.
- Do not redefine the concept as a general venue attribute if
  the domain makes it more specific.
- Do not invent new evidence concept IDs.
- Keep the definition concise: 2-4 sentences.
- Return ONLY the definition.
"""

    response = client.responses.create(
        model="gpt-5.4-mini",
        input=prompt,
    )

    raw_output = response.output_text.strip()

    try:
        definitions = json.loads(
            raw_output
        )
    except json.JSONDecodeError:
        print(
            "AI returned invalid definition JSON:"
        )
        print(raw_output)
        return {}

    if not isinstance(definitions, dict):
        return {}

    return definitions

def generate_domain_definitions(
    domain: str,
    concepts: list[str],
    existing_definitions: dict,
) -> str:
    """
    Generate draft definitions for all undefined
    concepts within one ontology domain.
    """

    existing_lines = []

    undefined_concepts = []

    for concept in concepts:

        existing = existing_definitions.get(
            concept,
            {},
        ).get(
            "description"
        )

        if existing:
            existing_lines.append(
                f"{concept}: {existing.strip()}"
            )
        else:
            undefined_concepts.append(
                concept
            )

    prompt = f"""
You are building a semantic evidence ontology for analysing
pub and venue reviews.

DOMAIN:
{domain}

ALL CONCEPTS IN THIS DOMAIN:

{chr(10).join(concepts)}

ALREADY DEFINED CONCEPTS:

{chr(10).join(existing_lines)}

CONCEPTS THAT REQUIRE DEFINITIONS:

{chr(10).join(undefined_concepts)}

Generate a precise definition for every undefined concept.

The definitions must establish clear semantic boundaries
between neighbouring concepts so another AI can classify
review evidence consistently.

Requirements:

- Interpret every concept specifically within the domain.
- Explain what review evidence belongs to each concept.
- Distinguish overlapping concepts from one another.
- State what should NOT belong where useful.
- Do not invent, remove or rename concept IDs.
- Keep each definition concise.
- Return ONLY valid JSON.
- Use this exact structure:

{{
    "concept_id": "definition"
}}
"""

    response = client.responses.create(
        model="gpt-5.4-mini",
        input=prompt,
    )

    return response.output_text.strip()
def load_domain_concepts(
    domain: str,
) -> list[str]:
    """
    Load all evidence concept IDs belonging
    to one ontology domain.
    """

    file_path = (
        KNOWLEDGE_PATH
        / "working"
        / f"{domain}.yaml"
    )

    if not file_path.exists():
        return []

    with file_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        return []

    domain_data = data.get(
        domain,
        {},
    )

    if not isinstance(domain_data, dict):
        return []

    evidence_items = domain_data.get(
        "evidence",
        [],
    )

    concepts = []

    for item in evidence_items:

        if isinstance(item, str):
            concepts.append(item)

        elif isinstance(item, dict):
            evidence_id = item.get("id")

            if evidence_id:
                concepts.append(evidence_id)

    return concepts

def generate_evidence_definition(
    evidence_id: str,
    domain: str,
    neighbouring_concepts: list[str],
) -> str:
    """
    Generate a draft semantic definition for one
    evidence concept using its domain and neighbours.
    """

    neighbours = "\n".join(
        f"- {concept}"
        for concept in neighbouring_concepts
        if concept != evidence_id
    )

    prompt = f"""
You are building a semantic evidence ontology for analysing
pub and venue reviews.

DOMAIN:
{domain}

CONCEPT TO DEFINE:
{evidence_id}

NEIGHBOURING CONCEPTS IN THIS DOMAIN:
{neighbours}

Define the concept precisely enough that another AI can
consistently decide whether review evidence belongs to this
concept or to one of its neighbouring concepts.

Requirements:

- Interpret the concept specifically within the stated domain.
- Explain what evidence belongs to this concept.
- Establish its semantic boundary from similar neighbouring concepts.
- State what should NOT be classified here where useful.
- Do not redefine the concept as a general venue attribute if
  the domain makes it more specific.
- Do not invent new evidence concept IDs.
- Keep the definition concise: 2-4 sentences.
- Return ONLY the definition.
"""

    response = client.responses.create(
        model="gpt-5.4-mini",
        input=prompt,
    )

    return response.output_text.strip()

def generate_domain_definitions(
    domain: str,
    concepts: list[str],
    existing_definitions: dict,
) -> str:
    """
    Generate draft definitions for all undefined
    concepts within one ontology domain.
    """

    existing_lines = []

    undefined_concepts = []

    for concept in concepts:

        existing = existing_definitions.get(
            concept,
            {},
        ).get(
            "description"
        )

        if existing:
            existing_lines.append(
                f"{concept}: {existing.strip()}"
            )
        else:
            undefined_concepts.append(
                concept
            )

    prompt = f"""
You are building a semantic evidence ontology for analysing
pub and venue reviews.

DOMAIN:
{domain}

ALL CONCEPTS IN THIS DOMAIN:

{chr(10).join(concepts)}

ALREADY DEFINED CONCEPTS:

{chr(10).join(existing_lines)}

CONCEPTS THAT REQUIRE DEFINITIONS:

{chr(10).join(undefined_concepts)}

Generate a precise definition for every undefined concept.

The definitions must establish clear semantic boundaries
between neighbouring concepts so another AI can classify
review evidence consistently.

Requirements:

- Interpret every concept specifically within the domain.
- Explain what review evidence belongs to each concept.
- Distinguish overlapping concepts from one another.
- State what should NOT belong where useful.
- Do not invent, remove or rename concept IDs.
- Keep each definition concise.
- Return ONLY valid JSON.
- Use this exact structure:

{{
    "concept_id": "definition"
}}
"""

    response = client.responses.create(
        model="gpt-5.4-mini",
        input=prompt,
    )

    raw_output = response.output_text.strip()

    try:
        audit = json.loads(
            raw_output
        )
    except json.JSONDecodeError:
        print(
            "AI returned invalid ontology audit JSON:"
        )
        print(raw_output)

        return {
            "duplicates": [],
            "overlaps": [],
            "distinct": [],
        }

    if not isinstance(audit, dict):
        return {
            "duplicates": [],
            "overlaps": [],
            "distinct": [],
        }

    return audit
def audit_domain_definitions(
    domain: str,
    definitions: dict,
) -> dict:
    """
    Audit one ontology domain for duplicate,
    overlapping, or poorly separated concepts.
    """

    definition_lines = []

    for concept, definition in definitions.items():
        definition_lines.append(
            f"{concept}: {definition}"
        )

    prompt = f"""
You are auditing a semantic evidence ontology used to
classify pub and venue reviews.

DOMAIN:
{domain}

CONCEPT DEFINITIONS:

{chr(10).join(definition_lines)}

Analyse the concepts as a complete domain.

Identify:

1. DUPLICATES
Concepts that represent essentially the same evidence and
may not justify separate IDs.

2. OVERLAPS
Concepts that are legitimately different but whose current
definitions do not establish a sufficiently clear boundary.

3. DISTINCT
Concepts that already have a clear semantic purpose and
boundary.

Be conservative about declaring duplicates. Two concepts
should only be duplicates when review evidence could not
reliably distinguish them.

For every duplicate or overlap:
- name the affected concept IDs
- explain the collision
- recommend whether to merge them or retain both
- if retaining both, provide a precise semantic boundary

Do not invent new concept IDs.

Return ONLY valid JSON using this structure:

{{
    "duplicates": [
        {{
            "concepts": ["concept_a", "concept_b"],
            "reason": "...",
            "recommendation": "..."
        }}
    ],
    "overlaps": [
        {{
            "concepts": ["concept_a", "concept_b"],
            "reason": "...",
            "boundary": "..."
        }}
    ],
    "distinct": [
        "concept_id"
    ]
}}
"""

    response = client.responses.create(
        model="gpt-5.4-mini",
        input=prompt,
    )

    raw_output = response.output_text.strip()

    try:
        audit = json.loads(
            raw_output
        )
    except json.JSONDecodeError:
        print(
            "AI returned invalid ontology audit JSON:"
        )
        print(raw_output)

        return {
            "duplicates": [],
            "overlaps": [],
            "distinct": [],
        }

    if not isinstance(audit, dict):
        return {
            "duplicates": [],
            "overlaps": [],
            "distinct": [],
        }

    return audit