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

    if currentPageNbr < totalPageNbr:
        return url.replace("page-" + str(currentPageNbr) + ".html", "page-" + str(currentPageNbr + 1) + ".html")
    else:
        return ""


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


def main():
    url = "https://books.toscrape.com/index.html"

    response = requests.get(url)
    listCategoryUrl = categoriList(response)
    for categoriUrl in listCategoryUrl:
        allCategoryUrl(categoriUrl)
    
    
main()