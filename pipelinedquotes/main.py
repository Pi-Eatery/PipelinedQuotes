import os
import logging
import requests
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

app = FastAPI()


def setup_logging():
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler("piquotes.log", mode="a")
    formatter = logging.Formatter(
        "%(asctime)s| LINE#%(lineno)d [%(levelname)s:%(levelno)s]  --  %(message)s"
    )

    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    logger.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return


load_dotenv()
setup_logging()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/quotes")
def quotes():
    try:
        scraped_data = scrape()
        return scraped_data
    except Exception:
        raise HTTPException(status_code=500, detail="Error scraping the source")


def scrape():
    quotes_small_list = []
    ethical_header = {"User-Agent": "My-First-Scraper/2.0"}

    logger.info("Currently looking for the website specified in the environment\n")
    url_to_hold = os.getenv("SCRAPING_URL")
    logger.info(f"Successfully stored website path...\n     {url_to_hold}\n")
    response = requests.get(url_to_hold, headers=ethical_header)
    response.raise_for_status()
    logger.info("Successfully reached the website.")
    soup = BeautifulSoup(response.text, "html.parser")
    quote_containers = soup.find_all("div", class_="quote")
    logger.info("Found all the quotes...")

    for container in quote_containers:
        text_element = container.find("span", class_="text")
        author_element = container.find("small", class_="author")

        if text_element and author_element:
            logger.info("Found a quote and its author")
            quote_text = text_element.get_text(strip=True)
            author_name = author_element.get_text(strip=True)
            quotes_small_list.append({"text": quote_text, "author": author_name})
            logger.info("Adding multiple key pairs now.")
        else:
            url_to_hold = None
    return quotes_small_list
