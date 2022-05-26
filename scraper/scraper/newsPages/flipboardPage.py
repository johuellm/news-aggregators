from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import urllib
import time


class flipboard_page:
    '''
    This class symbolizes a flipboard page
    '''

    def __init__(self, html):
        '''
        Method to create a flipboard page instance
        Parameters:
            html: source code of the page
        '''

        self.html = html
        self.soup = BeautifulSoup(html, 'html.parser')
        logging.info("flipboardPage instance created")

    def get_article_list_items_html(self):
        '''
        extracts all article elements from the raw html source code
        Returns:
            list of all elements that represent an article
        '''
        try:
            logging.info("getting article List from Flipboard page")
            mydivs = self.soup.findAll("li", {"class": "item-list__item"})
            return mydivs
        except Exception as e:
            logging.info("articleList could not be found: "+e)

    def getAllArticles(self):
        '''
        returns all articles in a structured form. 
        First all elements which represent an article are extracted from the html code.
        After that flipboard_articlelements are created for all elements.
        From thta the return structure is created. 
        Erroneous articles are discarded and an error is pushed to the log file.
        Returns:
            List of all articles in a structured form: 
                url: article url
                timestamp: time of save
                html: html sourcecode of the article
        '''
        logging.info("getting Articles from Flipboard")
        rawArticles = self.get_article_list_items_html()
        articles = []
        for article in rawArticles:
            try:
                article = flipboard_articleElement(str(article))
                articleDict = {
                    "url": article.url,
                    "timestamp": datetime.utcnow(),
                    "html": article.html}
                time.sleep(1)
            except Exception as e:
                logging.error("article could not be parsed "+str(e))

            articles.append(articleDict)

        return(articles)

    def getHtml(self):
        '''
        returns source code of the currently opened website.
        Returns: 
            source code of the website
        '''
        return self.html


class flipboard_articleElement:
    '''
    This class represents a Flipboard article, which is created from an article element.
    '''

    def __init__(self, articleHtml):
        '''
        Method to create a Flipboard article element.
        HTML and article link are extracted form an element which represents an article.

        Parameter: 
            articleHtml: 
                element that represents an article. 
                eg. html tag "li" with class "item-list_item"
        '''
        self.articleHtml = articleHtml
        self.soup = BeautifulSoup(articleHtml, 'html.parser')
        self.get_link()
        self.getHtml()

    def get_link(self):
        '''
        extracts link of an article element
        Returns:
            link: link to the article
        '''
        self.flipboardLink = self.soup.findAll(
            "a", {"class": "outbound-link"})[0]["href"]
        return self.flipboardLink

    def getHtml(self):
        '''
        downloads the HTML code of the article. 
        The user agent of urllib was changed to prevent bot detection. 
        self.html and self. url are set form content
        '''
        logging.info("  downloading page")
        try:

            # Der User Agent wurde verändert um Bot Detection zu verhindern
            req = urllib.request.Request(
                self.flipboardLink,
                data=None,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
                }
            )

            response = urllib.request.urlopen(req, timeout=4)
            self.html = response.read().decode('utf-8')
            self.url = response.url
            logging.info("  page downloaded")
        except Exception as e:
            logging.error("  download failed: " + str(e))
