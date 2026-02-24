import requests
import time
import csv
import sqlite3
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import argparse
import os



BASE_URL = "http://books.toscrape.com/catalogue/page-{}.html"


def fetch_with_retry(url, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response
        except requests.RequestException as e:
            print("Error:", e)

        wait_time = 2 ** attempt
        print(f"Retrying in {wait_time} seconds...")
        time.sleep(wait_time)
    return None

def crawl_listing_pages():
    all_books = []
    seen_upcs = set() 
    for page in range(1,51):
        url = BASE_URL.format(page)
        print(f"Scraping page {page}: {url}")
        response = fetch_with_retry(url)
        if not response:
            continue
        if response.status_code != 200:
            print(f"Failed to fetch page {page}")
            continue
        soup = BeautifulSoup(response.text, "html.parser")
        books = soup.find_all("article", class_="product_pod")
        for book in books:

            title = book.h3.a["title"]
            relative_url = book.h3.a["href"]
            product_url = urljoin(url, relative_url)
            price = book.find("p", class_="price_color").text.strip()
            availability = book.find("p", class_="instock availability").text.strip()
            rating_class = book.find("p", class_="star-rating")["class"]
            rating = rating_class[1]
            
            detail_response = fetch_with_retry(product_url)
            if not detail_response:
                continue

            detail_soup = BeautifulSoup(detail_response.text, "html.parser")

            # Extract UPC
            upc = detail_soup.find("th", string="UPC").find_next("td").text.strip()

            # Deduplication
            if upc in seen_upcs:
                continue
            seen_upcs.add(upc)

            # Extract Category
            breadcrumb = detail_soup.find("ul", class_="breadcrumb").find_all("a")
            category = breadcrumb[2].text.strip()

            # Extract Description
            desc_tag = detail_soup.find("div", id="product_description")
            if desc_tag:
                description = desc_tag.find_next_sibling("p").text.strip()
            else:
                description = None
            
            book_data = {
                "title": title,
                "price": price,
                "availability": availability,
                "rating": rating,
                "product_url": product_url,
                "upc": upc,
                "category": category,
                "description": description,
            }
            all_books.append(book_data)
            time.sleep(1)
    return all_books

def save_to_sqlite(books, path):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            price TEXT,
            availability TEXT,
            rating TEXT,
            product_url TEXT UNIQUE,
            upc TEXT UNIQUE,
            category TEXT,
            description TEXT
        )
    """)

    for book in books:
        cursor.execute("""
            INSERT OR IGNORE INTO books
            (title, price, availability, rating, product_url, upc, category, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            book["title"],
            book["price"],
            book["availability"],
            book["rating"],
            book["product_url"],
            book["upc"],
            book["category"],
            book["description"]
        ))

    conn.commit()
    conn.close()

def save_to_csv(books, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=books[0].keys())
        writer.writeheader()
        writer.writerows(books)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    books = crawl_listing_pages()
    print("\nTotal books collected:", len(books))

    if books:
        save_to_csv(books, os.path.join(args.out, "books.csv"))
        save_to_sqlite(books, os.path.join(args.out, "books.sqlite"))
        print("Data saved successfully.")

