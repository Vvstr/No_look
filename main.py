from fastapi import FastAPI, HTTPException
from chromadb import Client
from chromadb.config import Settings
from utils import retrieve_context_from_chroma, generate_answer, scrape_website
from models import QueryRequest, QueryResponse, ScrapeRequest, ScrapeResponse, ContextItem
from custom_logging import log_request

# ChromaDB client configuration
chroma_client = Client(Settings(persist_directory="./chroma_db"))
collection_name = "employee-handbook"
collection = chroma_client.get_or_create_collection(name=collection_name)

app = FastAPI()


# ========== Custom RAG Logic ==========
def handle_classic_rag(question: str, top_k: int) -> QueryResponse:
    context = retrieve_context_from_chroma(collection, question, top_k)
    if not context:
        raise HTTPException(status_code=404, detail="No relevant context found.")
    answer = generate_answer(question, context)
    return QueryResponse(answer=answer, context=context, scenario_used="classic")


def handle_scraping_rag(question: str, url: str, selector: str) -> QueryResponse:
    scraped_data = scrape_website(url, selector)
    if not scraped_data:
        raise HTTPException(status_code=404, detail="No data found on the website.")
    answer = generate_answer(question, scraped_data)
    return QueryResponse(answer=answer, context=scraped_data, scenario_used="scraping")


# ========== API Routes ==========
@app.post("/query", response_model=QueryResponse)
@log_request
def query_endpoint(request: QueryRequest):
    if request.scenario == "classic":
        return handle_classic_rag(request.question, request.top_k)
    elif request.scenario == "scraping":
        return handle_scraping_rag(request.question, request.url, request.selector)
    else:
        raise HTTPException(status_code=400, detail="Invalid scenario specified.")


@app.post("/scrape", response_model=ScrapeResponse)
@log_request
def scrape_endpoint(request: ScrapeRequest):
    data = scrape_website(request.url, request.selector)
    if not data:
        raise HTTPException(status_code=404, detail="No data found.")
    return ScrapeResponse(data=data)


@app.post("/add-to-chroma")
@log_request
def add_to_chroma_endpoint(documents: list[ContextItem]):
    for doc in documents:
        collection.add(documents=[doc.content])
    return {"message": "Documents added successfully."}


@app.get("/collections")
def list_collections():
    return {"collections": chroma_client.list_collections()}
