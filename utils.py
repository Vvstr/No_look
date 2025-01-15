import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService


def retrieve_context_from_chroma(collection, question: str, top_k: int = 2):
    results = collection.query(query_texts=[question], n_results=top_k)
    return [doc["document"] for doc in results["documents"]]


def generate_answer(question: str, context: list[str]):
    prompt = f"Question: {question}\nContext: {' '.join(context)}\nAnswer:"
    return "Generated answer"


def scrape_website(url: str, selector: str):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    try:
        driver.get(url)
        time.sleep(2)
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        return [el.text for el in elements]
    finally:
        driver.quit()
