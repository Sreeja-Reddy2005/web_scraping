import requests
import re
import csv
from bs4 import BeautifulSoup

url = "http://books.toscrape.com/"
response = requests.get(url)
print(response.status_code)
soup=BeautifulSoup(response.text,"html.parser")

print(soup.title.text)

books = soup.find_all("article", class_="product_pod")

for book in books:
    link = book.h3.a["href"]
    print(link)

books=soup.find_all("a")
for book in books:
    print(book.get("href"))

image=soup.find_all('div',class_="image_container")
print(image)
for i in image:
    j=i.img['src']
    print(j)

links=[]                
link=soup.find_all('div',class_="page_inner")
for i in link:
    j=i.a.text
    links.append(j)
print(links)
    

img1=[]
with open('sreeja.csv','w') as csv_file:
    write=csv.writer(csv_file)
    write.writerow(image)
    for i in image:
        j=i.img['src']
        img1.append(j)
    write.writerow(img1)


books = soup.find_all("article", class_="product_pod")

#to get the prices of the books
for book in books:
    price_text = book.find("p", class_="price_color").text
    price = re.search(r"[£]\d+\.\d+", price_text).group()   
    print("prices of books are:",price)


for book in books:
    title = book.h3.a["title"]
    
    class_list = book.find("p", class_="star-rating")["class"]
    class_string = " ".join(class_list)

    rating = re.search(r"(One|Two|Three|Four|Five)", class_string).group()
    
    print("Title:", title)
    print("Rating:", rating)
    print("-" * 40)