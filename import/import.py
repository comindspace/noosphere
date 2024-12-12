import asyncio
import logging
import os
import shutil
from datetime import datetime
from time import time

import ollama
import pyarrow.compute as pc
import pyarrow.parquet as pq
from PIL.Image import MODES
from dotenv import load_dotenv
from neo4j import GraphDatabase
from pyarrow import Table

from frames_benchmark_record import FramesBenchmarkRecord
from lightrag import LightRAG, QueryParam
from lightrag.entity_relationship_content_keywords import extract_entity_types_async
from lightrag.llm import ollama_model_complete, ollama_embedding
from lightrag.utils import EmbeddingFunc
from load_csv import load_csv
from redirected_links import redirected_links

logging.getLogger("httpx").setLevel(logging.WARNING)

load_dotenv()

EMBEDDING_MODEL = os.environ["EMBEDDING_MODEL"]
LLM_MODEL = os.environ["LLM_MODEL"]
OLLAMA_HOST = os.environ["OLLAMA_HOST"]
QUESTIONS = int(os.environ["QUESTIONS"])
WORKING_DIR = os.environ["WORKING_DIR"]
ANSWERS_DIR = os.environ["ANSWERS_DIR"]
NEO4J_URI = os.environ["NEO4J_URI"]
NEO4J_USERNAME = os.environ["NEO4J_USERNAME"]
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]

LINK = "link"
TEXT = "text"
SEQUENCE_JUST = 9
PERCENT_JUST = 7
TIME_FORMAT = "%H:%M:%S"
RETRIES = 5

MODES = ["naive", "local", "global", "hybrid"]

PSVD = "|"

FRAMES_PROMPT = """===Task===

I need your help in evaluating an answer provided by an LLM against a ground truth answer. Your task is to determine if the ground truth answer is present in the LLM’s response. Please analyze the provided data and make a decision.
===Instructions===
1. Carefully compare the "Predicted Answer" with the "Ground Truth Answer".
2. Consider the substance of the answers – look for equivalent information or correct answers. Do not focus on exact wording unless the exact wording is crucial to the meaning.
3. Your final decision should be based on whether the meaning and the vital facts of the "Ground Truth Answer" are present in the "Predicted Answer:"

===Input Data===
- Question: «{question}»
- Predicted Answer: «{answer}»
- Ground Truth Answer: «{ground_truth}»

===Output Format===
Provide your final evaluation in the following format:
"Explanation:" (How you made the decision?)
"Decision:" ("TRUE" or "FALSE" )

Please proceed with the evaluation. """

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

async def is_frames_answer_true_async(question: str, answer: str, ground_truth: str) -> bool:
    return "TRUE" in (await ollama.AsyncClient(host=OLLAMA_HOST).chat(
        model=LLM_MODEL,
        messages=[
            {"role": "user", "content": FRAMES_PROMPT.format(
                question=question,
                answer=answer,
                ground_truth=ground_truth
            )},
        ],
    )).message.content

def answer_file_path(id: int) -> str:
    return os.path.join(ANSWERS_DIR, f"{str(id).rjust(3, "0")}.txt")

async def question_test_async(test: FramesBenchmarkRecord, table: Table):
    if os.path.exists(answer_file_path(test.id)):
        return
    with GraphDatabase.driver(uri=NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)) as driver:
        driver.execute_query(f"MATCH (n) DETACH DELETE n")
    if os.path.exists(WORKING_DIR):
        shutil.rmtree(WORKING_DIR)
    if not os.path.exists(WORKING_DIR):
        os.mkdir(WORKING_DIR)

    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=ollama_model_complete,
        llm_model_name=LLM_MODEL,
        llm_model_max_async=16,
        llm_model_max_token_size=32768,
        llm_model_kwargs=dict(host=OLLAMA_HOST, options=dict(num_ctx=32768, temperature=0, seed=42)),
        embedding_func=EmbeddingFunc(
            embedding_dim=768,
            max_token_size=8192,
            func=lambda texts: ollama_embedding(
                texts,
                embed_model=EMBEDDING_MODEL,
                host=OLLAMA_HOST
            ),
        ),
        graph_storage="Neo4JStorage",
    )

    test_n = test.id + 1
    print(datetime.now().strftime(TIME_FORMAT),
          f"{test_n} / {str(QUESTIONS).rjust(3)}".rjust(SEQUENCE_JUST + 5),
          f"{round(100.0 * test_n / QUESTIONS, 1)} %".rjust(PERCENT_JUST))
    links = list(enumerate(redirected_links(test.wiki_links)))
    question_entity_types: set[str] = set()
    for link_i, link in links:
        link_n = link_i + 1
        text = str(table.filter(pc.match_substring(table[LINK], link))[TEXT][0])
        print("\t", datetime.now().strftime(TIME_FORMAT),
              f"{link_n} / {str(len(links)).rjust(3)}".rjust(SEQUENCE_JUST),
              f"{round(100.0 * link_n / len(links), 1)} %".rjust(PERCENT_JUST),
              link,
              len(text))
        start_article = time()
        entity_types = await extract_entity_types_async(OLLAMA_HOST, LLM_MODEL, text)
        print("\t", entity_types)
        question_entity_types.update(entity_types)
        await rag.ainsert(text, entity_types=entity_types)
        print("\t", time() - start_article)

    # Check answer
    question = test.prompt

    answers: dict[str, bool] = {}
    answer_file_content = ''
    for mode in MODES:
        predicted_answer = await rag.aquery(question, param=QueryParam(mode=mode))
        is_true = await is_frames_answer_true_async(question, predicted_answer, test.answer)
        answers[mode] = is_true
        answer_file_content += f"{mode}\n{predicted_answer}\n{is_true}\n"
    line = f"{test.id}{PSVD}{test.prompt}{PSVD}{answers["naive"]}{PSVD}{answers["local"]}{PSVD}{answers["global"]}{PSVD}{answers["hybrid"]}\n"
    with open("statistics.psv", "a", encoding="utf-8") as statistics_file:
        statistics_file.write(line)
    general_true = answers["naive"] or answers["local"] or answers["global"] or answers["hybrid"]
    print(general_true)
    with open(answer_file_path(test.id), "w", encoding="utf-8") as answer_file:
        answer_file.write(f"{question_entity_types}\n{answer_file_content}\n{general_true} for {test.answer}\n")
    # with GraphDatabase.driver(uri=NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)) as driver:
    #     driver.execute_query(f"MATCH (n) DETACH DELETE n")
    # if os.path.exists(WORKING_DIR):
    #     shutil.rmtree(WORKING_DIR)

async def main():
    start = time()

    table = pq.read_table("train-00000-of-00001.parquet", memory_map=True)
    tests = load_csv("test.tsv", FramesBenchmarkRecord, delimiter="\t")

    if not os.path.exists(ANSWERS_DIR):
        os.mkdir(ANSWERS_DIR)

    total_tests = tests[:QUESTIONS]
    for test in total_tests:
        for i in range(RETRIES):
            try:
                await question_test_async(test, table)
                break
            except Exception as e:
                print(e)
                if i >= RETRIES - 1:
                    raise
    print("total time:", time() - start)

if __name__ == "__main__":
    asyncio.run(main())
