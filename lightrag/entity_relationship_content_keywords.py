import re

import ollama
from ollama import Options
from pydantic.dataclasses import dataclass

from lightrag.prompt import PROMPTS

# from typing import TypeVar

T = PROMPTS["DEFAULT_TUPLE_DELIMITER"]
R = PROMPTS["DEFAULT_RECORD_DELIMITER"]
C = PROMPTS["DEFAULT_COMPLETION_DELIMITER"]

@dataclass(eq=True, frozen=True)
class ExtractedEntity:
    name: str
    type: str
    description: str

@dataclass(eq=True, frozen=True)
class ExtractedRelationship:
    source: str
    target: str
    description: str
    keywords: frozenset[str]
    strength: float

@dataclass
class EntitiesRelationshipsContentKeywords:
    entities: set[ExtractedEntity]
    relationships: set[ExtractedRelationship]
    content_keywords: set[str]

    @staticmethod
    def parse(text: str) -> "EntitiesRelationshipsContentKeywords":
        entities = [ExtractedEntity(item[0].strip('"'), item[1].strip('"'), item[2].strip('"')) for item in
                    re.findall(f'\\(?"entity"<\\|>"?(.+)"?<\\|>"?(.+)"?<\\|>"?(.+)"?\\)', text)]
        if len(entities) == 0:
            entities = [ExtractedEntity(item[0].strip('"'), "EntityType", item[1].strip('"')) for item in
                        re.findall(f'\\(?"entity"<\\|>"?(.+)"?<\\|>"?(.+)"?\\)', text)]
        relationships = []
        for item in re.findall(f'\\(?"relationship"<\\|>"?(.+)"?<\\|>"?(.+)"?<\\|>"?(.+)"?<\\|>"?(.+)"?<\\|>(\\d*\\.?\\d*)\\)', text):
            source = item[0].strip('"')
            target = item[1].strip('"')
            description = item[2].strip('"')
            keywords = frozenset(k.strip() for k in str(item[3]).strip('"').split(","))
            strength = float(item[4])
            relationships.append(ExtractedRelationship(source, target, description, keywords, strength))
        pre_content_keywords = re.findall('"?content_keywords"?\\*{0,2}<\\|>"?.+"?', text)
        if len(pre_content_keywords) == 0:
            m = []
        else:
            content_keywords = pre_content_keywords[0]
            cks = content_keywords.rstrip(C).strip(f")<|COMPLETE|>")
            m = [ck.strip().strip('"').strip("<").strip(">") for ck in re.search('<\\|>"?(.+)"?', cks).group(1).split(",")]
        return EntitiesRelationshipsContentKeywords(
            entities=set(entities),
            relationships=set(relationships),
            content_keywords=set(m),
        )

    async def merge_entity_types_async(self) -> "EntitiesRelationshipsContentKeywords":
        entity_types = [entity.type for entity in self.entities]
        OLLAMA_HOST = "http://81.94.156.214:11434"
        LLM_MODEL = "qwen2.5:14b-instruct-q5_K_M"
        entities_relationships_content_keywords = await extract_entity_type_relation_async(OLLAMA_HOST, LLM_MODEL, entity_types)

        self.entities.update(entities_relationships_content_keywords.entities)
        self.relationships.update(entities_relationships_content_keywords.relationships)
        for entity in self.entities:
            self.relationships.add(ExtractedRelationship(
                entity.name,
                entity.type,
                f"{entity.name} is instance of {entity.type}",
                frozenset(),
                10.0
            ))
        self.content_keywords.update(entities_relationships_content_keywords.content_keywords)
        return self

    def to_text(self):
        return ("".join([f'("entity"{T}{e.name}{T}{e.type}{T}{e.description}){R}\n' for e in self.entities]) +
                "".join([f'("relationship"{T}{r.source}{T}{r.target}{T}{r.description}{T}{", ".join(r.keywords)}{T}{r.strength}){R}\n' for r in
                         self.relationships]) +
                f"""("content_keywords"{T}{", ".join(self.content_keywords)}){C}""")

async def extract_entity_types_async(
        ollama_host: str,
        llm_model: str,
        text: str,
) -> set[str]:
    ollama_client = ollama.AsyncClient(host=ollama_host)
    llm_answer = (await ollama_client.chat(
        model=llm_model,
        messages=[{"role": "user", "content": PROMPTS["entity_type_extraction"].format(input_text=text)}],
        options=Options(num_ctx=32768, seed=348957006),  # sic! 348957006
    )).message.content

    entity_types: set[str] = set(et.lower() for et in PROMPTS["DEFAULT_ENTITY_TYPES"])
    try:
        for match in re.findall(r"\*\*[^\\*\n]+\*\*", llm_answer):
            for ets in match.strip("0123456789*.-: ").split("&"):
                for et in ets.split("/"):
                    entity_types.add(et.strip().lower())
    except:
        ...
    return set(entity_types)

async def _extract_entity_type_relation_async(
        ollama_host: str,
        llm_model: str,
        entity_types: list[str],
) -> EntitiesRelationshipsContentKeywords:
    ollama_client = ollama.AsyncClient(host=ollama_host)
    prompt = PROMPTS["entity_type_relation_extraction"].format(
        entity_types=entity_types,
        tuple_delimiter=PROMPTS["DEFAULT_TUPLE_DELIMITER"],
        record_delimiter=PROMPTS["DEFAULT_RECORD_DELIMITER"],
        completion_delimiter=PROMPTS["DEFAULT_COMPLETION_DELIMITER"],
    )
    llm_answer = (await ollama_client.chat(
        model=llm_model,
        messages=[{"role": "user", "content": prompt}, ],
        options=Options(num_ctx=32768, temperature=0, seed=42),
    )).message.content

    return EntitiesRelationshipsContentKeywords.parse(llm_answer)

async def extract_entity_type_relation_async(
        ollama_host: str,
        llm_model: str,
        entity_types: list[str],
) -> EntitiesRelationshipsContentKeywords:
    while True:
        try:
            result = await _extract_entity_type_relation_async(ollama_host, llm_model, entity_types)
            break
            # print(len(result.entities), len(result.relationships))
        except Exception as e:
            print(e)
    return result
