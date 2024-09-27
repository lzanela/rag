import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import sys

def fetch_page_content(url):
    """
    Fetch the HTML content of a page given its URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.text
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def is_valid_url(url, base_url):
    """
    Check if a URL is valid and belongs to the same domain as the base URL.
    """
    parsed_url = urlparse(url)
    parsed_base_url = urlparse(base_url)
    return (parsed_url.scheme in ['http', 'https'] and
            parsed_url.netloc == parsed_base_url.netloc and
            url not in visited_urls)

def extract_links(html_content, base_url):
    """
    Extract all internal links from the HTML content.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    links = []

    for a_tag in soup.find_all("a", href=True):
        href = a_tag['href']
        # Resolve relative URLs
        full_url = urljoin(base_url, href)
        if is_valid_url(full_url, base_url):
            links.append(full_url)
            visited_urls.add(full_url)

    return links

def scrape_docs(url):
    """
    Scrape the content of the documentation from the given URL.
    """
    print(f"Scraping {url} ...")
    html_content = fetch_page_content(url)
    if html_content:
        # Parse the page content and add to docs_content
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract and store the main content
        main_content = soup.find_all(['h1', 'h2', 'h3', 'p', 'pre', 'code'])
        for content in main_content:
            text = content.get_text().strip()
            if text:  # Add only non-empty lines
                docs_content.append(text)

        # Extract links and continue scraping them
        links = extract_links(html_content, base_url)
        for link in links:
            scrape_docs(link)

def save_docs_to_txt(filename):
    """
    Save the scraped documentation content to a text file.
    """
    with open(filename, "w", encoding="utf-8") as file:
        for line in docs_content:
            file.write(line + "\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scrape_docs.py <base_url> <output_filename>")
        sys.exit(1)

    # Get the base URL and output file name from command line arguments
    base_url = sys.argv[1]
    output_filename = sys.argv[2]

    # Initialize a set to keep track of visited URLs and a list for documentation content
    visited_urls = set()
    docs_content = []

    # Start scraping from the base documentation URL
    scrape_docs(base_url)

    # Save all the scraped content to a text file
    save_docs_to_txt(output_filename)
    print(f"Documentation scraping completed and saved to {output_filename}.")
