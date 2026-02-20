import requests
import time
from bs4 import BeautifulSoup

BASE_URL = "http://books.toscrape.com/catalogue/page-{}.html"

def crawl_listing_pages():
    all_books = []
    for page in range(1, 51):
        url = BASE_URL.format(page)
        print(f"Scraping page {page}: {url}")
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch page {page}")
            continue
        soup = BeautifulSoup(response.text, "html.parser")
        books = soup.find_all("article", class_="product_pod")
        for book in books:
            title = book.h3.a["title"]
            relative_url = book.h3.a["href"]
            product_url = (
                "http://books.toscrape.com/catalogue/"
                + relative_url.replace("../", "")
            )
            price = book.find("p", class_="price_color").text.strip()
            availability = book.find("p", class_="instock availability").text.strip()
            rating_class = book.find("p", class_="star-rating")["class"]
            rating = rating_class[1]
            book_data = {
                "title": title,
                "price": price,
                "availability": availability,
                "rating": rating,
                "product_url": product_url,
            }
            all_books.append(book_data)
    return all_books
if __name__ == "__main__":
    books = crawl_listing_pages()
    print("\nTotal books collected:", len(books))