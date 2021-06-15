import requests
from math import ceil
from scrapy.selector import Selector

url = "https://books.toscrape.com/catalogue/category/books_1/index.html"

def pageNbr(response):
    """Retourne un Int du nombre de résultats possède cette catégorie,
    en divisant le numbre de livre total par le numbre de vivre par page"""
    articlesNbrUrl = "#default > div > div > div > div > form > strong:nth-child(2)" + "::text"
    return ceil(int(Selector(text=response.text).css(articlesNbrUrl).get()) / 20)

def categoriScrap(response):
    """Retourne une List de Str comtenant les urls de chaque livre."""

    urlAllBooks = "div:nth-child(2) > ol > li > article > div.image_container > a::attr(href)"
    return Selector(text=response.text).css(urlAllBooks).getall()

def categoriList(response):
    """Retourne une List de Str contenant chaque url des categories"""
    urlAllCategory = ".nav > li:nth-child(1) > ul:nth-child(2) > li > a:nth-child(1)::attr(href)"
    return Selector(text=response.text).css(urlAllCategory).getall()

def formatUrl(url):
    """Retourne une url valide"""
    result = url
    if "../" in url:
        result = url.split("../")[-1]

    if "books/" in url:
        result = "https://books.toscrape.com/catalogue/category/" + result.replace("index.html", "page-1.html")

    if "../../" in url:
        result = "https://books.toscrape.com/catalogue/" + result

    return result



response = requests.get(url)

print(pageNbr(response))
print("\n")
print(formatUrl(categoriScrap(response)[2]))
print("\n")
print(formatUrl(categoriList(response)[2]))