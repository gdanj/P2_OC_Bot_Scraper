import requests
from math import ceil
from requests.api import head
from scrapy.selector import Selector
from pprintpp import pprint
import re
import pandas as pd



def pageNbr(response):
    """Retourne un Int du nombre de résultats possède cette catégorie,
    en divisant le numbre de livre total par le numbre de vivre par page"""

    articlesNbrUrl = "#default > div > div > div > div > form > strong:nth-child(2)" + "::text"
    return ceil(int(Selector(text=response.text).css(articlesNbrUrl).get()) / 20)


def scrapAllBooks(response):
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

    if "media" in url:
        return url.replace("../../", "https://books.toscrape.com/")

    if "../" in url:
        result = url.split("../")[-1]

    if "books/" in url:
        result = "https://books.toscrape.com/"  + result

    if "../../" in url:
        result = "https://books.toscrape.com/catalogue/" + result

    return result


def nestPage(url):
    """Retourne un Str de l'url de la page de résultat suivant, ou un de str vide si il n'y a pas de page suivant"""

    if "index.html" in url:
        url = url.replace("index.html", "page-1.html")
        currentPageNbr = 1
    else:
        currentPageNbr = int(url.split("/")[-1].replace("page-","").replace(".html", ""))
    
    return url.replace("page-" + str(currentPageNbr) + ".html", "page-" + str(currentPageNbr + 1) + ".html")


def allCategoryUrl(categoriUrl):
    """Retourne tout les urls d'une catégorie"""

    currentPageUrl = formatUrl(categoriUrl)
    response = requests.get(currentPageUrl)
    totalPageNbr = pageNbr(response)
    i = 0
    result = []
    while i < totalPageNbr:
        response = requests.get(currentPageUrl)
        result += scrapAllBooks(response)
        currentPageUrl = formatUrl(nestPage(categoriUrl))
        i += 1
    return result

def bookScraper(url):
    """Récupère les information sur la page produit et retourne une list"""

    response = requests.get(url)
    universal_product_code = "article > table tr:nth-child(1) > td::text"
    title = "div .product_main h1::text"
    price_including_tax = "#content_inner > article > table tr:nth-child(4) > td::text"
    price_excluding_tax = "#content_inner > article > table tr:nth-child(3) > td::text"
    number_available = "#content_inner > article > div.row > div.col-sm-6.product_main > p.instock.availability"
    product_description = "#content_inner > article > p::text"
    category = "#default > div > div > ul > li:nth-child(3) > a::text"
    review_rating = "article > table tr:nth-child(7) > td::text"
    image_url = "div > div > div > img::attr(src)"

    return [
        url,
        Selector(text=response.text).css(universal_product_code).get(),
        Selector(text=response.text).css(title).get(),
        Selector(text=response.text).css(price_including_tax).get(),
        Selector(text=response.text).css(price_excluding_tax).get(),
        re.search(r'[+-]?\b[0-9]+\b', Selector(text=response.text).css(number_available).get()).group(0),
        Selector(text=response.text).css(product_description).get(),
        Selector(text=response.text).css(category).get(),
        Selector(text=response.text).css(review_rating).get(),
        formatUrl(Selector(text=response.text).css(image_url).get())
    ]


def createCSV(data, categoriName):
    """Crée un fichier csv à partir de la List de List 'data' nommé par la variable 'categoriName',
    si le fichier existe déjà il sera remplacé"""

    header = [ "product_page_url", "universal_ product_code (upc)", "title", "price_including_tax", "price_excluding_tax", "number_available", "product_description", "category", "review_rating", "image_url", ]
    csv = pd.DataFrame(data, columns=header)
    csv.to_csv(categoriName + '.csv', index=False)



def booksIteration(listBooks, categoriUrl):
    """Fait un csv avec les url de la list passé en parametre"""
    categoriName = categoriUrl.split("/")[3].split("_")[0]
    data = []
    print("Scraping de la catégorie " + categoriName + ".")
    for bookUrl in listBooks:
        data.append(bookScraper(formatUrl(bookUrl)))
        createCSV(data, categoriName)
    print("Création de CSV " + categoriName + ".")

def main():
    url = "https://books.toscrape.com/index.html"

    response = requests.get(url)
    listCategoryUrl = categoriList(response)
    for categoriUrl in listCategoryUrl:
        resultCategori = allCategoryUrl(categoriUrl)
        booksIteration(resultCategori, categoriUrl)

main()