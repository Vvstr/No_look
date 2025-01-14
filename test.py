from fastapi import FastAPI, HTTPException
from typing import List, Optional
from chromadb import Client
from chromadb.config import Settings
from transformers import pipeline
from funcs import *
from models import *

import subprocess

# TODO Убрать
DOCKER_IMAGE = "chroma-db"
DOCKER_CONTAINER_NAME = "chromadb_container"
DOCKER_PORT = 8000

if subprocess.run(["docker", "ps", "-q", "-f", f"name={DOCKER_CONTAINER_NAME}"],
                  capture_output=True).stdout.strip() == b"":
    print("Starting ChromaDB Docker container...")
    subprocess.run([
        "docker", "run", "-d", "--name", DOCKER_CONTAINER_NAME, "-p", f"{DOCKER_PORT}:8000", DOCKER_IMAGE
    ])

# Conf ChromaDB Client
chroma_client = Client(Settings(host="http://localhost", port=DOCKER_PORT, persist_directory="./chroma_db"))
collection_name = "employee-handbook"
if collection_name not in chroma_client.list_collections():
    chroma_client.create_collection(name=collection_name)
collection = chroma_client.get_collection(name=collection_name)

qa_pipeline = pipeline("text2text-generation", model="google/flan-t5-large")

app = FastAPI()


# ========== RAG ==========
def classic_rag(question: str, top_k: int) -> QueryResponse:
    context = retrieve_context_from_chroma(question, top_k)
    if not context:
        raise HTTPException(status_code=404, detail="No relevant context found.")
    context_str = "\n".join(context)
    answer = generate_answer(question, context_str)
    return QueryResponse(answer=answer, context=context, scenario_used="classic")


def scraping_rag(question: str, url: str, selector: str) -> QueryResponse:
    scraped_data = scrape_website(url, selector)
    if not scraped_data:
        raise HTTPException(status_code=404, detail="No relevant data found on the website.")
    context_str = "\n".join(scraped_data)
    answer = generate_answer(question, context_str)
    return QueryResponse(answer=answer, context=scraped_data, scenario_used="scraping")


def combined_rag(question: str, top_k: int, url: str, selector: str) -> QueryResponse:
    chroma_context = retrieve_context_from_chroma(question, top_k)
    scraped_data = scrape_website(url, selector)
    combined_context = chroma_context + scraped_data
    if not combined_context:
        raise HTTPException(status_code=404, detail="No relevant context found.")
    context_str = "\n".join(combined_context)
    answer = generate_answer(question, context_str)
    return QueryResponse(answer=answer, context=combined_context, scenario_used="combined")


# ========== Routes ==========
@app.post("/query", response_model=QueryResponse)
def query_endpoint(request: QueryRequest):
    scenario = request.scenario
    question = request.question
    top_k = request.top_k

    # TODO доделать выбор сценариев
    if scenario == "classic":
        return classic_rag(question, top_k)
    elif scenario == "scraping":

        url =
        selector = ".policy-text"
        return scraping_rag(question, url, selector)
    elif scenario == "combined":

        url =
        selector = ".policy-text"
        return combined_rag(question, top_k, url, selector)
    else:
        raise HTTPException(status_code=400, detail="Invalid scenario specified.")


@app.post("/scrape", response_model=ScrapeResponse)
def scrape_endpoint(request: ScrapeRequest):
    try:
        data = scrape_website(request.url, request.selector)
        return ScrapeResponse(data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add-to-chroma")
def add_to_chroma(documents: List[ContextItem]):
    try:
        for doc in documents:
            collection.add(documents=[doc.content])
        return {"message": "Документ успешно добавлен."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/collections")
def list_collections():
    try:
        collections = chroma_client.list_collections()
        return {"collections": collections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========== How to Use ==========
# 1. Запустить приложение: `main:app --reload`
# 2. Отправить запрос:
#    POST на `/query` с телом запроса `{ "question": "вопрос", "top_k": 3, "scenario": "classic" }`
# 3. Выполните парсинг веб-сайта(ДОДЕЛАТЬ):
#    POST на `/scrape` с телом запроса `{ "url": "URL", "selector": "CSS_SELECTOR" }`
# 4. Добавить документ/ы в ChromaDB:
#    POST на `/add-to-chroma` с телом запроса `[ { "content": "текст документа" } ]`
# 5. Доступные коллекции:
#    GET запрос на `/collections`
