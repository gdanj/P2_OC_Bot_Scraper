import requests
from math import ceil
from scrapy.selector import Selector


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
    if "../" in url:
        result = url.split("../")[-1]

    if "books/" in url:
        result = "https://books.toscrape.com/"  + result

    if "../../" in url:
        result = "https://books.toscrape.com/catalogue/" + result

    return result


def nestPage(url, totalPageNbr):
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
        currentPageUrl = formatUrl(nestPage(categoriUrl, totalPageNbr))
        i += 1
    return result

def bookScraper(url):
    """Récupère les information sur la page produit et retourne une list"""

    response = requests.get(url)
    universal_product_code = ""
    title = "#content_inner > article > div.row > div.col-sm-6.product_main > h1::text"
    price_including_tax = ""
    price_excluding_tax = ""
    number_available = ""
    product_description = ""
    category = ""
    review_rating = ""
    image_url = ""
    """Selector(text=response.text).css(universal_product_code).get(), Selector(text=response.text).css(title).get(), Selector(text=response.text).css(price_including_tax).get(), Selector(text=response.text).css(price_excluding_tax).get(), Selector(text=response.text).css(number_available).get(), Selector(text=response.text).css(product_description).get(), Selector(text=response.text).css(category).get(), Selector(text=response.text).css(review_rating).get(), Selector(text=response.text).css(image_url).get(),"""
    return [
        url,
        Selector(text=response.text).css(title).get()
    ]

def booksIteration(listBooks):
    """Fait un csv avec les url de la list passé en parametre"""

    for bookUrl in listBooks:
        print(bookScraper(formatUrl(bookUrl)))


def main():
    url = "https://books.toscrape.com/index.html"

    response = requests.get(url)
    listCategoryUrl = categoriList(response)
    for categoriUrl in listCategoryUrl:
        resultCategori = allCategoryUrl(categoriUrl)
        booksIteration(resultCategori)



main()