import pymongo
import logging


class databaseInterface:
    '''
    Interface with the MongoDB database of the survey
    '''

    def __init__(self,  address, port, profileName=None, ):
        '''
        Method to create a databaseInterface instance. 
        A connection to the database is established on the passed address
        and port. optionally a profile name can be passed as well
        which will be stored in the database.
        Parameters:
            address:
                IP address of the MongoDB database
            port:
                Port released on the machine with the given address.
            (profilename):
                Name of the profile, which is stored during some database operations

        '''

        self.profileName = profileName
        self.client = pymongo.MongoClient(address, port)

    def saveGoogleNewsPage(self, tiles, source, sessionNr=None):
        '''
        Method to store a collected Google News website in MongoDB database.
        All tiles for each source and each article for each tile are stored.
        The data is stored according to the following scheme:

        googleNews.source:
            profile: profile name
            sessionNr: session executed directly before collection
            html: HTML code of the website
            time: time of the survey
            screenshot: Screenshot of the website in BASE64

        googleNews.tiles:
            sourceId: ID of the document in source, to be able to assign tiles to sources
            tileNr: number of tiles from top to bottom
            tileType: either "single field", "multifield" or "panorama", type of field in HTML code

        googleNews.articles:
            googleLink: Google referrer URL 
            url: last URL after redirection
            referrerPage: html of the referrer page
            finalPage: html of the website after redirection
            profile: profile name of the collected profile
            articleNr: number of the article within a tile
            tileId: Number of the related tile
            timestamp: time of saving

        parameters:
            tiles: 
                structured tile data
            source:
                structured data to source file
            (sessionNr):
                session that was executed directly before execution


        '''
        logging.info("saving Google News Page")
        db = self.client["googleNews"]
        source["profil"] = self.profileName
        source["sessionNr"] = sessionNr
        sourceId = db.source.insert_one(source).inserted_id

        for i, tile in enumerate(tiles):
            tile["profil"] = self.profileName
            tileData = {"sourceId": sourceId,
                        "tileNr": i, "tileType": tile['tileType']}
            tileId = db.tiles.insert_one(tileData).inserted_id

            for i, article in enumerate(tile["articles"]):
                article["profil"] = self.profileName
                article["articleNr"] = i
                article["tileId"] = tileId
                db.articles.insert_one(article)
        logging.info("Google News Page saved")

    def saveFlipboardPage(self, articles, source, sessionNr=None):
        '''
        Method to store a collected Flipboard website in MongoDB database.
        All tiles for each source and each article for each tile are stored.
        The data is stored according to the following scheme:

        flipBoard.source:
            profile: profile name
            sessionNr: session that is executed directly before collection
            html: HTML code of the website
            time: time of the survey
            screenshot: Screenshot of the website in BASE64

        flipBoard.articles:
            url: url of the article
            html: html of the article
            profile: profile name of the raised profile
            articleNr: number of the article within a tile
            sourceID: number of the corresponding tile

        parameters:
            tiles: 
                structured tile data
            source:
                structured data to source file
            (sessionNr):
                session that was executed directly before execution
        '''

        logging.info("saving Flipboard Page")
        db = self.client["flipBoard"]
        source["profil"] = self.profileName
        source["sessionNr"] = sessionNr
        sourceId = db.source.insert_one(source).inserted_id

        for i, article in enumerate(articles):
            article["profil"] = self.profileName
            article["articleNr"] = i
            article["sourceID"] = sourceId
            try:
                db.articles.insert_one(article)
            except Exception as e:
                logging.error("document could not be inserted: "+str(e))

        logging.info("Flipboard Page saved")

    def saveSpiegelRss(self, articles, source):
        '''
        Method to store a collected mirror RSS feed in the MongoDB database.
        For each source Rss feed all articles are stored.
        The data is stored according to the following scheme:

        spiegel.source:
            rss: pure RSS document
            time: time of collection

        spiegel.articles:
            age: creation date of the article
            timeStamp: time of the download
            link: url of the article
            html: html code of the article's website
            sourceID: ID of the source of the article
            articleNr: number of the article per feed from first in the feed to last

        Parameters:
            articles: 
                structured data of articles
            source:
                structured data to source file

        '''
        logging.info("saving spiegelRss")
        db = self.client["spiegel"]
        sourceID = db.source.insert_one(source).inserted_id

        for i, article in enumerate(articles):
            article["sourceID"] = sourceID
            article["articleNr"] = i
            db.articles.insert_one(article)
        logging.info("SpiegelRss saved")

    def saveWNRss(self, articles, source):
        '''
        Method to store a collected mirror RSS feed in the MongoDB database.
        For each source Rss feed all articles are stored.
        The data is stored according to the following scheme:

        westfaelischeNachrichten.source:
            rss: pure RSS document
            time: time of collection

        westfaelischeNachrichten.articles:
            age: creation date of the article
            timeStamp: time of the download
            link: url of the article
            html: html code of the article's website
            sourceID: ID of the source of the article
            articleNr: number of the article per feed from first in the feed to last

        Parameters:
            articles: 
                structured data of articles
            source:
                structured data to source file
        '''
        logging.info("saving WnRss")
        db = self.client["westfaelischeNachrichten"]
        sourceID = db.source.insert_one(source).inserted_id

        for i, article in enumerate(articles):
            article["sourceID"] = sourceID
            article["articleNr"] = i
            db.articles.insert_one(article)
        logging.info("WnRss saved")

    def savePersonalizationProfile(self, personalizationDict, sessionNr):
        '''
        Method to store a collected Google Account interest profile.
        The data is stored according to the following scheme:

        googleProfile.source:
            time: time of execution
            html: html of the Google profile
            sessionNr: number of the executed session in websiteList.py
            profile: profile name

        Parameters:
            personalizationDict: 
                structured data of articles
            (sessionNo:)
                Session number directly before call
        '''

        logging.info("saving personalization profile")
        db = self.client["googleProfile"]
        personalizationDict["sessionNr"] = sessionNr
        db.source.insert_one(personalizationDict)
        logging.info("personalization profile saved")

    def saveSession(self, session, time,  sessionNr):
        '''
        Method for saving an executed session
        The data is stored according to the following scheme:

        sessions.session:
            time: time of execution
            profilename: profile name
            sessionNr: number of the executed session in websiteList.py
            elements: array with all executed steps from the session. 
                Each element contains
                    type: type of execution. youtubeSearch,googleSearch,amazonSearch,eBaySearch
                    time: time of execution
                    url: URL at the end of execution
                    screenshot: Screenshot at the end of execution
        parameters:
            session: 
                executed session
            time:
                Time of the start of the execution
            (sessionNr:)
                number of the executed session 

        '''
        logging.info("saving session")
        db = self.client["sessions"]
        sessionDict = {}
        sessionDict["time"] = time
        sessionDict["profilename"] = self.profilename
        sessionDict["sessionNr"] = sessionNr
        sessionDict["elements"] = session
        db.session.insert_one(sessionDict)
        logging.info("session saved")
