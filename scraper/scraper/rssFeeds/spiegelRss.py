import feedparser
import urllib.request
from datetime import datetime
import logging
import time


class spiegelRss:
    '''
    Class that represents the Spiegel Online RSS feed
    '''

    def __init__(self):
        '''
        Method to create a spiegelRss object
        The RSS feed is loaded and the source code is stored in the object

        '''
        try:
            logging.info("loading and parsing spiegelRss")
            self.feed = feedparser.parse(
                "https://www.spiegel.de/schlagzeilen/tops/index.rss")
            response = urllib.request.urlopen(
                "https://www.spiegel.de/schlagzeilen/tops/index.rss")
            html = response.read().decode('utf-8')
            self.rssContent = html
            self.creationTime = datetime.utcnow()
        except Exception as e:
            logging.error("spiegelRSS could not be loaded: "+e)

    def getAllArticles(self):
        '''
        Method to return all articles of the loaded RSS feed.
        Each article is also called. Therefore one second is waited after 
        the call of each source code is waited

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
                time.sleep(1)
            except Exception as e:
                logging.error("Rss entry could not be analyzed: "+str(e))

        logging.info("entries analyzed")
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
