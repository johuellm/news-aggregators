from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


import logging
import time
from random import randint, shuffle
from datetime import datetime

import os
import shutil


class personalizer:

    '''
    A class that performs personalization in the context of this work.
    Functions of the class are to start Chrome with a
    saved Chrome profile, calling multiple URLs with this
    Chrome profile and calling Flipboard or Google News.
    '''

    def __init__(self, profilePath, userAgent, profileName):
        '''
        Method to prepare a Personalizer instance.

        :param profilePath: Path where the profiles were stored.
        :param userAgent: The user agent to use when using the scraper.
        :param profileName: The name of the profile. Used to select the profile in the profile folder.
        '''
        logging.info("personalizer initalizing")
        self.profilePath = profilePath
        self.profileName = profileName
        self.userAgent = userAgent
        self.createDriver()
        logging.info("personalizer initialized")

    def createDriver(self):
        '''
        Method to create a geckodriver instance for use with Firefox.
        Parameterization is explained in the code.
        The profile is duplicated by Firefox when using the geckodriver.
        For this reason the geckodriver must be closed using the closeDriver() function of this
        class
        '''
        profile = webdriver.FirefoxProfile(
            self.profilePath+self.profileName)

        # change user agent
        profile.set_preference("general.useragent.override", self.userAgent)

        # change language to german
        profile.set_preference('intl.accept_languages', 'de-DE, de')

        # open gecokdriver
        driver = webdriver.Firefox(
            profile)

        # set virtual screen size 1920*1090
        driver.set_window_size(1920, 1080)

        # installation of the plugin "I dont care about cookies"
        # https://addons.mozilla.org/de/firefox/addon/i-dont-care-about-cookies/

        workingDirectory = os.path.abspath(os.getcwd())

        addonPath = workingDirectory + \
            "/thirdPartyplugins/firefox/i_dont_care_about_cookies-3.2.9-an+fx.xpi"

        driver.install_addon(
            addonPath, temporary=True)

        self.driver = driver
        time.sleep(5)

        logging.info("driver created")

    def closeDriver(self):
        '''
        Method to close the driver
        The profile is copied from the temporary folder to the profile folder.
        '''

        mozprofile = self.driver.capabilities["moz:profile"]
        try:

            os.remove(mozprofile + "/lock")
        except:
            pass

        workingDirectory = os.path.abspath(os.getcwd())
        path = workingDirectory+"/profile/firefox/"+self.profileName
        if os.path.exists(path):
            shutil.rmtree(path)
        shutil.copytree(mozprofile, path)

        time.sleep(3)
        self.driver.quit()

        logging.info("driver closed")

    def __waitForElementByXpath(self, xpath, timeout=10):
        '''
        Helper method to automate waiting for a browser element. 
        It waits at most the time "timeout" for an Xpath to appear in the DOM. 
        Then the element is returned as a Selenium web element.

        Parameters:
            xpath: 
                Xpath to the element that is being waited for.
            timeout:
                maximum waiting time

        return:
            Returns Selenium web element to the Xpath.

        '''
        element = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath)))

        delay = randint(1, 3)

        time.sleep(delay)
        return element

    def __waitForElementsByXpath(self, xpath, timeout=10):
        '''
        Helper method to automate waiting for multiple browser elements. 
        It waits at most the time "timeout" for multiple elements to appear in the DOM. 
        Then the group of elements matching the Xpath is returned as a Selenium web element. 

        Parameters: 
            xpath: 
                Xpath to the elements being waited for

            timeout: 
                maximum waiting time

        returns:
            Returns Selenium web elements to the Xpath.
        '''

        elements = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_all_elements_located((By.XPATH, xpath)))

        delay = randint(1, 3)
        time.sleep(delay)
        return elements

    def __openLinkOfElem(self, elem):
        '''
        Method to find the URL of a web item and open it.
        It would be better to click on the links by the click method of the web element, 
        as this would more closely simulate to the user behavior. 
        In tests, however, this has led to detection by Bot Detection on Google. 

        Parameters: 
            elem: 
                Element whose link is to be returned
        '''

        link = elem.find_element_by_tag_name("a").get_attribute('href')
        self.driver.get(link)

        time.sleep(2)

    def performSession(self, session, shuffleSession=True):
        '''
        Method to load the list of websites and xpaths stored in the config to:
        - confirm tracking, search Youtube, search Google, search
        Amazon and search ebay. 

        Parameters
            session: 
                The session to run. The structure is documented in the readme.

            shuffleSession: 
                Random order of the elements of a session.

        Returns:
            Array
                All executed single elements. 
        '''

        logging.info("performing personalization on session")

        if shuffleSession:
            shuffle(session)

        performedSession = []

        for entry in session:
            if (entry["type"] == "website"):
                performedSession.append(self.accessWebsite(
                    entry["link"]))

            elif (entry["type"] == "youtubeSearch"):
                performedSession.append(
                    self.useYoutubeSearch(entry["searchTerm"]))

            elif entry["type"] == "googleSearch":
                performedSession.append(
                    self.useGoogleSearch(entry["searchTerm"]))

            elif entry["type"] == "amazonSearch":
                performedSession.append(
                    self.useAmazonSearch(entry["searchTerm"]))

            elif entry["type"] == "ebaySearch":
                performedSession.append(
                    self.useEbaySearch(entry["searchTerm"]))

            elif entry["type"] == "instagramSearch":
                performedSession.append(
                    self.useInstagramSearch(entry["searchTerm"]))

        sessionLength = len(session)
        logging.info(str(sessionLength) + " websites accessed")
        return performedSession

    def accessWebsite(self, url: str):
        '''
        Method to call a URL and confirm the cookie banner,
        if it appears.
        1. the URL is called
        2. if cookiePopupXpath is passed, a specified time is waited until the banner appears.
        If the cookie banner appears, it is confirmed. 
        The time to wait is set in config.py under timeToWaitForCookieBanner.
        3. there is a timeout for as long as specified under delay in config.py

        Parameters:
            url : str
                The URL to the website, which should be called
            cookiePopupXpath : str
                The XPath to the element that confirms the banner.

        Returns:
            output: Dict
                type, time, url, screenshot and (error)

        '''
        output = {"type": "website", "time": datetime.utcnow()}
        try:
            logging.info("accessing website: "+url)
            self.driver.get(url)

            timeOnWebsite = randint(5, 20)
            time.sleep(timeOnWebsite)
            logging.info("accessed %s going to sleep for %s seconds" %
                         (url, timeOnWebsite))

        except Exception as e:
            logging.error("could not access website")
            logging.error(str(e))
            output["error"] = str(e)
        output["url"] = self.driver.current_url
        output["screenshot"] = self.driver.get_screenshot_as_png()
        return output

    def useYoutubeSearch(self, searchTerm: str):
        '''
        Method to go to the Youtube website, search for the searchTerm and select any video.
        1. URL is called
        2. the search field is located, the searchTerm is entered and confirmed with Enter
        3. all video elements are located and a random element is retrieved

        Parameters: 
            searchTerm : str
                The string to be searched for

        Returns:
            output: Dict
                type, time, url, screenshot and (error)
        '''
        logging.info("using youtubeSearch: "+searchTerm)
        output = {"type": "youtubeSearch", "time": datetime.utcnow()}
        try:
            self.driver.get("https://www.youtube.com/")

            elem = self.__waitForElementByXpath('//input[@id="search"]')
            elem.click()
            time.sleep(1)
            enterkeyString = u'\ue007'
            elem.send_keys(
                searchTerm + enterkeyString)
            # time.sleep(2)
            elems = self.__waitForElementsByXpath("//ytd-video-renderer")

            # elems = self.driver.find_elements_by_xpath("//ytd-video-renderer")
            ranElemNr = randint(0, len(elems)-1)

            elem = elems[ranElemNr]
            self.__openLinkOfElem(elem)

            try:
                playButton = self.__waitForElementByXpath(
                    '//button[@aria-label="Wiedergabe"]')
                playButton.click()
            except:
                pass

            timeInVideo = randint(8*60, 12*60)
            logging.info(
                "youtubeSearch successfull. going to sleep for %s" % str(timeInVideo))
            time.sleep(timeInVideo)

        except Exception as e:
            logging.error("video search failed: "+str(e))
            output["error"] = str(e)
            time.sleep(30)
        output["url"] = self.driver.current_url
        output["screenshot"] = self.driver.get_screenshot_as_png()
        return output

    def useAmazonSearch(self, searchTerm: str):
        '''
        Method to call Amazon website, search for a searchTerm and open a random product.
        1. URl is called
        2. search bar at the top is located, searchTerm is entered and confirmed with Enter
        3. products are located and a random product is clicked

        Parameters: 
            searchTerm : str
                The string to be searched for

        Returns:
            output: Dict
                type, time, url, screenshot and (error)
        '''
        output = {"type": "amazonSearch", "time": datetime.utcnow()}
        logging.info("using Amazon search: "+searchTerm)
        try:

            self.driver.get("https://www.amazon.de/")

            searchBox = self.__waitForElementByXpath(
                '//input[@id="twotabsearchtextbox"]')
            enterkeyString = u'\ue007'
            searchBox.send_keys(
                searchTerm + enterkeyString)

            elems = self.__waitForElementsByXpath(
                '//div[@data-component-type="s-search-result"]')

            ranElemNr = randint(0, len(elems)-1)

            elem = elems[ranElemNr]

            self.__openLinkOfElem(elem)

            timeOnResult = randint(10, 30)
            logging.info(
                "Amazon search result opened \n going to sleep for %s seconds" % str(timeOnResult))

            time.sleep(timeOnResult)

        except Exception as e:
            logging.error("amazon search: "+str(e))
            output["error"] = str(e)
            time.sleep(30)
        output["url"] = self.driver.current_url
        output["screenshot"] = self.driver.get_screenshot_as_png()
        return output

    def useGoogleSearch(self, searchTerm: str):
        '''
        Method to call Google website, search for a searchTerm and open a random result.
        1. URl is called
        2. search bar is located, searchTerm is entered and confirmed with Enter
        3. results are localized and a random result is called

        Parameters: 
            searchTerm : str
                The string to be searched for

        Returns:
            output: Dict
                type, time, url, screenshot and (error)
        '''
        output = {"type": "googleSearch", "time": datetime.utcnow()}
        try:
            logging.info("performing googleSearch: "+searchTerm)
            self.driver.get("https://www.google.de/")

            searchBox = self.__waitForElementByXpath(
                '//input[@name="q"]')
            enterkeyString = u'\ue007'
            searchBox.send_keys(searchTerm + enterkeyString)
            time.sleep(2)

            elems = self.__waitForElementsByXpath(
                '//div[@class="g"]')
            ranElemNr = randint(0, len(elems)-1)
            elem = elems[ranElemNr]
            self.__openLinkOfElem(elem)

            timeOnResult = randint(10, 30)
            logging.info(
                "Google search result opened \n going to sleep for %s seconds" % str(timeOnResult))

            time.sleep(timeOnResult)

        except Exception as e:
            logging.error("search failed: "+str(e))
            output["error"] = str(e)
            time.sleep(30)
        output["url"] = self.driver.current_url
        output["screenshot"] = self.driver.get_screenshot_as_png()
        return output

    def useEbaySearch(self, searchTerm: str):
        '''
        Method to call eBay website, search for a searchTerm and open a random product.
        1. URl is called
        2. search bar at the top is located, searchTerm is entered and confirmed with Enter
        3. products are located and a random product is opened

        Parameters: 
            searchTerm : str
                The string to be searched for

        Returns:
            output: Dict
                type, time, url, screenshot and (error)
        '''
        output = {"type": "ebaySearch", "time": datetime.utcnow()}
        try:

            logging.info("using eBaySearch: "+searchTerm)
            self.driver.get("https://www.ebay.de/")

            searchBox = self.__waitForElementByXpath(
                '//input[contains(@class, "ui-autocomplete-input")]')

            enterkeyString = u'\ue007'
            searchBox.send_keys(searchTerm + enterkeyString)

            # elems = self.__waitForElementsByXpath("s-item")
            elems = self.__waitForElementsByXpath(
                "//li[contains(@class, 's-item')]")

            ranElemNr = randint(1, 8)
            elem = elems[ranElemNr]

            self.__openLinkOfElem(elem)

            timeOnResult = randint(10, 30)
            logging.info(
                "eBay search result opened \n going to sleep for %s seconds" % str(timeOnResult))

            time.sleep(timeOnResult)
        except Exception as e:
            logging.error("search failed: "+str(e))

            output["error"] = str(e)
            time.sleep(30)
        output["url"] = self.driver.current_url
        output["screenshot"] = self.driver.get_screenshot_as_png()
        return output

    def accessGoogleNews(self, scroll=True):
        '''
        Method to open Google News. 
        After the call of Google News a time which is specified in config.py under delay is waited

        Parameters:
            scroll:bool
                scroll down on the website

        Returns:
            output: Dict
                html, time, and screenshot
        '''
        try:
            logging.info("accessing google News")
            url = "https://news.google.de/"
            self.driver.get(url)
            logging.info("accessed "+url)
            sleepTime = randint(5, 10)
            time.sleep(sleepTime)
            if scroll:
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(5)
            return {"html": self.getPageSource(), "time": datetime.utcnow(), "screenshot": self.driver.get_screenshot_as_png()}
        except Exception as e:
            logging.error("Google News could not be opened: " + str(e))

    def accessFlipboard(self):
        '''
        Method to open Flipboard. 
        After calling Flipboard the program waits for a time defined in config.py under delay.

        Returns:
            output: Dict
                html, time, and screenshot
        '''
        try:
            logging.info("accessing flipboard")
            url = "https://flipboard.com/"
            self.driver.get(url)
            logging.info("accessed "+url)
            time.sleep(30)

            return {"html": self.getPageSource(), "time": datetime.utcnow(), "screenshot": self.driver.get_screenshot_as_png()}
        except Exception as e:
            logging.error("Flipboard could not be opened: " + str(e))

    def getPageSource(self):
        '''
        Returns the current HTML DOM as a string.

        Returns:
            str
                html pagesource as string

        '''
        return str(self.driver.page_source)

    def getGoogleAdProfile(self):
        '''
        Open Google's "Personalized Advertising" tab and returns the HTML
        Returns:
            Array
                time, html, profil

        '''

        self.driver.get("https://adssettings.google.com/authenticated")
        time.sleep(5)
        return {"time": datetime.utcnow(), "html": self.getPageSource(), "profil": self.profileName}

    def getLocation(self):
        # Für Debugging
        self.driver.get("https://www.whatismyip-address.com/?check")
        time.sleep(5)
