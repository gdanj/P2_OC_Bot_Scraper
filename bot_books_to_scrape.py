import requests
from scrapy.selector import Selector

url = "https://books.toscrape.com/catalogue/category/books/add-a-comment_18/index.html"
response = requests.get(url)
articlesNbrUrl = "#default > div > div > div > div > form > strong:nth-child(2)" + "::text"
urlAllBooks = "div:nth-child(2) > ol > li > article > div.image_container > a::attr(href)"
print(int(Selector(text=response.text).css(articlesNbrUrl).getall()[0]) / 20)