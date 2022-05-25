import logging
import argparse
from datetime import datetime


from scraper.newsPages import googleNewsPage, flipboardPage
from scraper.rssFeeds import spiegelRss, wnRss
from scraper.storageInterfaces import databaseInterface
from scraper.personalizer import personalizer

from config.config import config
from config.websiteList import sessions


def googleNews(personalizerInstance,  databaseInterfaceInstance, sessionNr):
    '''
    Method to retrieve and store all articles on Google News.
    It calls Google News, translates the page into structured information
    and this information is stored in the database.
    The Personalizer and Database Interface instances are passed to perform the collection of 
    Google News with other actions of the same browser and database connection.
    The sessionNr is used to store any executed sessions in the database. 
    stored.

    Parameters:
        personalizerInstance :
            The instance of the personalizer class to be used for personalization.
            should be

        databaseInterfaceInstance:
            The instance of the databaseinterface class to be used for storing the data.
            data

        sessionNr:
            Number of one of the session that was executed directly before calling Google News.

    '''

    googleNewsSource = personalizerInstance.accessGoogleNews()
    googleNewsInstance = googleNewsPage.GoogleNewsPage(
        googleNewsSource["html"])
    databaseInterfaceInstance.saveGoogleNewsPage(
        googleNewsInstance.getAllArticles(), googleNewsSource, sessionNr)


def flipBoard(personalizerInstance,  databaseInterfaceInstance, sessionNr):
    '''
    Method to call and save all articles on Flipboard.
    It calls Flipboard, translates the page into structured information
    and this information is stored in the database.
    The Personalizer and Database Interface instances are passed in to perform the collection of 
    Flipboard with other actions of the same browser and database connection.
    The sessionNr is used to store any executed sessions in the database. 

    Parameters:
        personalizerInstance :
            The instance of the personalizer class to be used for personalization.
            should be

        databaseInterfaceInstance:
            The instance of the databaseinterface class to be used for storing the data.
            data

        sessionNr:
            Number of one of the session that was running right before Flipboard was called.

    '''

    flipboardSource = personalizerInstance.accessFlipboard()
    flipboardInstance = flipboardPage.flipboard_page(flipboardSource["html"])
    databaseInterfaceInstance.saveFlipboardPage(
        flipboardInstance.getAllArticles(), flipboardSource, sessionNr)


def googleNewsAndFlipboard(personalizerInstance,  databaseInterfaceInstance, sessionNr):
    '''
    Method to access Google News and Flipboard one by one.
    Parameters:
        personalizerInstance :
            The instance of the personalizer class to use for personalization.
            should be

        databaseInterfaceInstance:
            The instance of the databaseinterface class to be used for storing the data.
            data


        sessionNr:
            Number of one of the sessions that was executed directly before calling GoogleNews.
    '''

    googleNews(personalizerInstance,  databaseInterfaceInstance, sessionNr)
    flipBoard(personalizerInstance,  databaseInterfaceInstance, sessionNr)


def wn(databaseInterfaceInstance):
    '''
    Method for collecting the RSS feed of the Westfälische Nachrichten. 
    The RSS feed is downloaded and stored in the database. 

    Parameters:
        databaseInterfaceInstance:
            The instance of the databaseinterface class to be used for storing the data.
            data


        sessionNr:
            Number of one of the sessions that was executed directly before calling GoogleNews.
    '''

    rssInstance = wnRss.wnRss()
    databaseInterfaceInstance.saveWNRss(
        rssInstance.getAllArticles(), rssInstance.getRssData())


def spiegel(databaseInterfaceInstance):
    '''
    Method for collecting the RSS feed from Spiegel Online. 
    The RSS feed is downloaded and stored in the database. 

    Parameters:
        databaseInterfaceInstance:
            The instance of the databaseinterface class to be used for storing the data.
            data


        sessionNr:
            Number of one of the sessions that was executed directly before calling GoogleNews.
    '''

    rssInstance = spiegelRss.spiegelRss()
    databaseInterfaceInstance.saveSpiegelRss(
        rssInstance.getAllArticles(), rssInstance.getRssData())


def testPersonalization(personalizerInstance,  databaseInterfaceInstance, sessionNr):
    '''
    Method for collecting the interests in the Google News account settings. 
    The account settings of the Google profile are accessed and the source code of the profile is
    stored in the database.

    Parameters:
        databaseInterfaceInstance:
            The instance of the databaseinterface class to be used for storing the data.
            data

        sessionNr:
            Number of one of the sessions that was executed directly before calling GoogleNews.
    '''

    adProfileHtml = personalizerInstance.getGoogleAdProfile()
    databaseInterfaceInstance.savePersonalizationProfile(
        adProfileHtml, sessionNr)


def main():
    '''
    Here the main process of the program is defined. 
    The commands from the command line are translated.
    Subsequently, a database connection is established.
    If specified the Westfälische Nachrichten or Spiegel Online rss feeds are colleted.
    If personalization steps are specified, a Personalizer instance is created.
    Then a session is executed and saved.
    Subsequently, if specified, Google News, Flipboard or Google News and Flipboard are collected 
    and the personalization profile is saved.
    The browser is then closed
    '''

    # Übersetzung der Commandline Argumente
    parser = argparse.ArgumentParser()
    parser.add_argument('--type')
    parser.add_argument('--session')
    session = vars(parser.parse_args())["session"]
    execType = vars(parser.parse_args())["type"]

    # Erstellen des Datenbankinterface
    databaseInterfaceInstance = databaseInterface.databaseInterface(
        config["dbAdress"], config["dbPort"], config["profileName"])

    # Erhebung Westfälische Nachrichten
    if execType == "wn":
        wn(databaseInterfaceInstance)

    # Erhebung Spiegel Online
    elif execType == "spiegel":
        spiegel(databaseInterfaceInstance)

    else:
        # Erstellen der Personalisierungsinstanz
        personalizerInstance = personalizer.personalizer(
            config["profilePath"], config["userAgent"], config["profileName"])

        # Ausführen der Session falls spezifiziert
        if session:
            logging.info("sessionNr:"+str(session))
            sessionNr = int(session)
            session = sessions[sessionNr]
            sessionStart = datetime.utcnow()
            performedSession = personalizerInstance.performSession(session)
            databaseInterfaceInstance.saveSession(
                performedSession, sessionStart,  sessionNr)
        else:
            sessionNr = None

        # Ausführen eines Erhebungsschritts falls spezifiziert
        if execType == "googleNews":
            googleNews(personalizerInstance,
                       databaseInterfaceInstance, sessionNr)
        elif execType == "flipBoard":
            flipBoard(personalizerInstance,
                      databaseInterfaceInstance, sessionNr)
        elif execType == "googleNewsAndFlipboard":
            googleNewsAndFlipboard(personalizerInstance,
                                   databaseInterfaceInstance, sessionNr)

        elif execType == "testPersonalization":
            testPersonalization(personalizerInstance,
                                databaseInterfaceInstance, sessionNr)

        personalizerInstance.closeDriver()


if __name__ == "__main__":
    '''
    Logging is started at this point. 
    If an exception is sent at any point in the code, it is stored in the log.
    The main function is then executed. 
    '''
    logging.basicConfig(format='%(module)s %(levelname)s %(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                        filename=config["logFile"], level="INFO")

    logging.info("scraper started\n \n \n")

    try:
        main()
    except Exception as e:
        logging.exception("Fatal error in main Loop!!" + str(e))
