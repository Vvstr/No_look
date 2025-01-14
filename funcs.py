from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService


def retrieve_context_from_chroma(question: str, top_k: int = 2) -> List[str]:
    results = collection.query(query_texts=[question], n_results=top_k)
    return [result["document"] for result in results["documents"]]


def generate_answer(question: str, context: str) -> str:
    prompt = f"Answer the question based on the context:\n\nQuestion: {question}\nContext: {context}\n\nAnswer:"
    response = qa_pipeline(prompt, max_length=200, num_return_sequences=1)
    return response[0]['generated_text'].strip()


def scrape_website(url: str, element_selector: str) -> List[str]:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        time.sleep(3)  # Allow time for page to load
        elements = driver.find_elements(By.CSS_SELECTOR, element_selector)
        return [el.text for el in elements]
    finally:
        driver.quit()