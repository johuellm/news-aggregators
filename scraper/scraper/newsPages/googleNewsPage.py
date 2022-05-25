
from bs4 import BeautifulSoup
import urllib
import logging
import time


class GoogleNewsPage:
    '''
    This class represents a Google News page
    '''

    def __init__(self, html):
        '''
        Method to create a Google News page instance. 
        At creation the article area and the "Panorama" area is saved
        Parameter:
            html: HTML code to the website
        '''
        logging.info("creating Google News Page Instance")
        self.html = html
        self.soup = BeautifulSoup(html, 'html.parser')
        self.getArticleArea()
        self.getPanoramaArea()

    def getHtml(self):
        '''
        Returns HTML code of the page
        Returns: 
            HTML 
        '''
        return self.html

    def getArticleArea(self):
        '''
        Extracts article area from HTML. And sets self.articleArea as the HTML code.

        Returns:
            Html Code des Artikelbereichs
        '''
        try:
            self.articleArea = self.soup.find(
                "div", {'class': "lBwEZb BL5WZb xP6mwf"})
            return self.articleArea
        except Exception as e:
            logging.error("could not find Article Area " + e)

    def getPanoramaArea(self):
        '''
        Extracts "Panorama" area from HTML. And sets self.articleArea as the HTML code.
        Returns:
            HTML Code of the "Panorama" area
        '''
        try:
            self.panoramaArea = self.soup.find(
                "div", {'class': "ndSf3d eDrqsc eVhOjb XWHGK j7vNaf Pz9Pcd a8arzf"})
            return self.panoramaArea
        except Exception as e:
            logging.error("could not find Panorama Area "+e)

    def getArticlesFromArticleArea(self):
        '''
        Method for extracting the individual articles from the article area
        Searches all tiles in the article area. All articles are then searched in the tiles.
        All tiles saved with associated articles.
        Returns:
            List of all tiles in structured form:
            tileType: singleField or multifield. Type of tile
            articles: all articles of a tile in the following form:
                googleLink: Google referrer page
                url: last url after redirection
                timestamp: timestamp of the download
                age: age of the article
                referrerPage: html of the referrer page
                finalPage: last source code after redirection

        '''

        tiles = self.articleArea.findAll("div", {"class": "NiLAwe"})

        tileList = []
        for tile in tiles:

            logging.info("  analyzing tile")
            rawArticles = tile.findAll("article")

            if len(rawArticles) == 1:
                tileType = "einzelFeld"
            if len(rawArticles) > 1:
                tileType = "multifeld"

            # aussortieren von Fake Kacheln
            if len(rawArticles) < 1:
                break

            articles = []
            for article in rawArticles:
                try:
                    article = GoogleNewsArticle(str(article))

                    articleDict = {
                        "googleLink": article.googleLink,
                        "url": article.url,
                        "timestamp": time.asctime(),
                        "age": article.age,
                        "referrerPage": article.referrerPage,
                        "finalPage": article.finalPage}

                    articles.append(articleDict)
                except Exception as e:
                    logging.error("article could not be analyzed: "+str(e))
                time.sleep(0.5)

            elem = {"tileType": tileType, "articles": articles}
            tileList.append(elem)

        return tileList

    def getArticlesFromPanoramaArea(self):
        '''
        Method for extracting the individual items from the panorama area
        Searches all tiles in the panorama area. All articles are then searched in the tiles.
        All tiles with associated articles are saved.
        Returns:
            List of all tiles in structured form:
            tileType: panorama, type of tile
            articles: all articles of a tile in the following form:
                googleLink: Google referrer page
                url: last url after redirection
                timestamp: timestamp of the download
                age: age of the article
                referrerPage: html of the referrer page
                finalPage: last source code after redirection
        '''
        rawArticles = self.panoramaArea.findAll("article")

        articles = []
        for article in rawArticles:
            try:
                logging.info("    analyzing article")
                article = GoogleNewsArticle(str(article))

                articleDict = {
                    "googleLink": article.googleLink,
                    "url": article.url,
                    "timestamp": time.asctime(),
                    "alter": article.age,
                    "referrerPage": article.referrerPage,
                    "finalPage": article.finalPage}

                articles.append(articleDict)
                time.sleep(1)
            except Exception as e:
                logging.error("article could not be analyzed" + str(e))

        return {"tileType": "Panorama", "articles": articles}

    def getAllArticles(self):
        '''
        Method to extract all single items
        Searches all tiles. All articles are then searched in the tiles.
        All tiles saved with associated articles.
        Returns:
            List of all tiles in structured form:
            tileType: panorama, single tile, multi tile. Tile type
            articles: all articles of a tile in the following form:
                googleLink: Google referrer page
                url: last url after redirection
                timestamp: timestamp of the download
                age: age of the article
                referrerPage: html of the referrer page
                finalPage: last source code after redirection
        '''

        articles = self.getArticlesFromArticleArea()
        articles.append(self.getArticlesFromPanoramaArea())
        return articles


class GoogleNewsArticle:
    '''
    Klasse zum repräsentieren eines GoogleNews Artikelements
    '''

    def __init__(self, articleHtml):
        '''
        This is a method to create a Google News article element.
        It extracts Html and article link from an element representing an article
        Parameters: 
            articleHtml: 
                Element representing an article element. 
                Can be for example the html tag "article".
        '''
        self.articleHtml = articleHtml
        self.soup = BeautifulSoup(articleHtml, 'html.parser')
        self.getLink()
        self.getReferrerPage()
        self.getFinalPage()
        self.getAge()

    def getLink(self):
        '''
        extracts the Google referrer link of the article and stores it in the instance of the class
        '''
        self.googleLink = "http://news.google.de/" + \
            self.soup.find("a")["href"]

    def getReferrerPage(self):
        '''
        Downloads the referrer page and stores it in self.referrerPage
        '''
        logging.info("    downloading Html of Google News Article")
        try:
            # Der User Agent wurde verändert um Bot Detection zu verhindern
            req = urllib.request.Request(
                self.googleLink,
                data=None,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
                }
            )
            response = urllib.request.urlopen(req, timeout=5)
            self.referrerPage = response.read().decode('utf-8')

        except Exception as e:
            logging.error("     could not download referrer page: " + str(e))
            self.referrerPage = None

    def getFinalPage(self):
        '''
        extracts the link to the article from the referrer page, downloads the page
        and stores the link and the page of the article in self.finalPage
        '''
        soup = BeautifulSoup(self.referrerPage, 'html.parser')
        try:
            self.url = soup.find("a", attrs={"jsname": "tljFtd"})["href"]
            # Der User Agent wurde verändert um Bot Detection zu verhindern
            req = urllib.request.Request(
                self.url,
                data=None,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
                }
            )
            response = urllib.request.urlopen(req, timeout=5)
            self.finalPage = response.read().decode('utf-8')

            logging.info("     download successfull")

        except Exception as e:
            logging.error("     could not download final page: " + str(e))
            self.finalPage = None

    def getAge(self):
        '''
        extracts the age of the article from the html code and stores it in the class
        '''
        self.age = self.soup.find("time")["datetime"]
