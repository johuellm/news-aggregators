import feedparser
import urllib.request
import urllib.error
import urllib.parse
import time
from datetime import datetime
import logging


class wnRss:
    '''
    Class to represent the Westfaelische Nachrichten RSS feed
    '''

    def __init__(self):
        '''
        Method to create a wnRss object
        The RSS feed is loaded and the source code is stored in the object

        '''
        try:
            logging.info("loading and parsing wn Rss ")
            self.feed = feedparser.parse(
                "https://www.wn.de/rss/feed/wn_epaper")
            response = urllib.request.urlopen(
                "https://www.wn.de/rss/feed/wn_epaper")
            html = response.read().decode('utf-8')
            self.rssContent = html
            self.creationTime = datetime.utcnow()
        except Exception as e:
            logging.error("could not load or parse wn Rss:" + str(e))

    def getAllArticles(self):
        '''
        Method to return all articles of the loaded RSS feed.
        Each article is also called with a one second delay between them.

        Returns:
            Array
                All articles with the following information:
                    age: publication date
                    timeStamp: timestamp
                    url: Url of the article
                    html: page source of the article
        '''
        articleList = []
        for entry in self.feed["entries"]:
            try:
                logging.info("analyzing entry")
                response = urllib.request.urlopen(entry["link"])
                html = response.read().decode('utf-8')
                out = {"age": entry["published"], "timeStamp": datetime.utcnow(
                ), "url": entry["link"],  "html": html}
                articleList.append(out)
                logging.info("entry analyzed")
                time.sleep(1)
            except Exception as e:
                logging.error("could not analyze article: "+str(e))
        return articleList

    def getRssData(self):
        '''
        Returns the source code of the RSS feed and the call time. 
        Returns:
            Array
                Array with content:
                rss: rss source code
                time: rss retrieval time
        '''
        return {"rss": self.rssContent, "time": self.creationTime}
