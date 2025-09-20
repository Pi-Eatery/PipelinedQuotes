import sys
import csv
import lxml
import requests
from fastapi import FastAPI
from bs4 import BeautifulSoup, Comment

app = FastAPI()

@app.get("/health")
@app.get("/quotes")

def health():
    return {"status": "ok"}

"""
A class to scrape quotes from 'http://quotes.toscrape.com'

This scraper scrolls through the website's pages, extracts quotes and authors,
and saves them to a CSV file. It is designed to follow modern scraping ethics,
including setting a custom User-Agent and adding delays between requests.
"""
class QuoteScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.quotes_master_list = []
        # SECURITY NOTE: A descriptive User-Agent is essential for ethical scraping.
        # It distinguishes this bot from malicious traffic.
        self.ethical_headers = {'User-Agent': 'MyFirstScraper/1.0'}

    """
    Fetches the HTML content of a given URL.

    Args:
        url (str): The URL of the web page to start scraping

    Returns:
        requests.Response: The response object containing the page's HTML, 
            or None if the request fails
    """
    def get_html_page(self, url):
        try:
            response = requests.get(url, headers=self.ethical_headers)
            # .raise_for_status() will raise an HTTPError for bad responses
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {url}: {e}")

    """
    Finds and extracts quote data from the page's HTML structure

    Args:
        soup_object (BeautifulSoup): A BeautifulSoup object representing
            the parsed HTML of a page.

    Returns:
        quotes_list: A list of dictionaries, where each dictionary
            represents a quote with the 'text' and 'author' keys.
    """
    def extract_quotes(self, soup_object):
        quotes_list = []
        quote_containers = soup_object.find_all('div', class_='quote')
        for container in quote_containers:
            text_element = container.find('span', class_='text')
            author_element = container.find('small', class_='author')
            if text_element and author_element:
                # Using strip=True ensures the captured text data is clean
                quote_text = text_element.get_text(strip=True)
                author_text = author_element.get_text(strip=True)
            quotes_list.append({
                'text': quote_text,
                'author': author_text
            })
        return quotes_list
    

    """
    Finds the relative URL of the 'next' page link if there is one.

    Args:
        soup_object (BeautifulSoup): A BeautifulSoup object representing 
            the parsed HTML of a page.

    Returns:
        str: The href attribute of
            the 'next' page link, or None if it is not found.
    """
    def find_next_link(self, soup_object):
        button_element = soup_object.find('li', class_='next')
        if button_element and button_element.find('a'):
            return button_element.find('a')['href']
        return None
    

    """
    Saves the list of quotes to a CSV file.

    Args:
        filename (str): The name of the output CSV file.
            Defaults to 'quotes.csv'
    """
    def save_to_csv(self, filename="quotes.csv"):
        if not self.quotes_master_list:
            print("No quotes to save.")
            return

        headers = ['text', 'author']
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(self.quotes_master_list)
        print(f"Data written to {filename}")


    """
    The main controller for all the logic in the scraping process.

    It loops through all pages of a website, extracts the quotes from each page,
        and saves the final list to a CSV file.
    """
    def scrape(self):
        url_to_scrape = self.base_url
        while url_to_scrape:
            print(f"Scraping page: {url_to_scrape}")
            page_to_scrape = self.get_html_page(url_to_scrape)

            if not page_to_scrape:
                break
    
            soup = BeautifulSoup(page_to_scrape.text, 'lxml')
            scraped_quotes = self.extract_quotes(soup)
            self.quotes_master_list.extend(scraped_quotes)

            url_sub = self.find_next_link(soup)
            if url_sub:
                url_to_scrape = self.base_url + url_sub
                # CRITICAL: Always include a delay in the scraping loop
                # to avoid overwhelming the server.
                # DO NOT REMOVE THE NEXT LINE
                time.sleep(1)
            else:
                print(f"No more pages to scrape!")
                url_to_scrape = None
    
        if self.quotes_master_list:
            self.save_to_csv()
            print(f"I found {len(self.quotes_master_list)} quotes!\n")
            print(f"Data saved to quotes.csv")
        else:
            print(f"Scraping failed...\nI couldn't find any quotes on this page:\n{self.base_url}")


if __name__ == '__main__':
    scraper = QuoteScraper()
    # The entry point. This kicks off the scraping job
    scraper.scrape()
