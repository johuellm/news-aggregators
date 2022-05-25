<h1>Scraper</h1>
This program includes all the code of the scraper used for the survey.
The code has been tested on both Mac OS X and Ubuntu.

<h2> Prerequisites </h2>

- Firefox
    The latest Firefox version must be installed.

- Geckodriver
    The current Geckodriver version must be installed. 
    It has been tested with version 0.29.0.

- Python 3 with pip
    A Python 3 version with pip must be installed on the system. 
    All dependencies from the requirements.txt file must be installed.

For installation on Ubuntu, the calls from the Dockerfile can be used.

<h2> Configuration </h2>
There are two configuration files. 
config.py is used for general configuration.
WebsiteList.py is used to store the individual sessions and calls.
<h3> config.py </h3>

    profilePath - folder in which the profile is stored
    logFile - path and filename of the log file
    dbAdress - IP address of the Mongodb database
    dbPort - port of the database
    profileName - name of the collected profile
    userAgent - user agent overriding the browser user agent
<h3> websiteList.py </h3>
The individual sessions are stored as an array in an array. 
Session one is accordingly located at sessions[0]. A session contains multiple session elements.
A session element is a Python dict with the keys type and searchTerm.
type can be googleSearch,youtubeSearch,amazonSearch or ebaySearch.
searchTerm specifies the string to search.
<h2> Preparation for use </h2>.

1. creation of a browser profile
    To create a new browser profile, the Firefox profile manager must be opened.
    On Ubuntu, this can be achieved by opening Firefox via `firefox -ProfileManager`.
    A new profile must now be created. 
    The folder of the profile must be named after the profileName in config.py and must be in the path profilePath.

2. prepare the browser profile
    The profile should be prepared. To use Google News and Flipboard, the browser profile must be logged into accounts of the services.

3. start of the database
    Before starting the survey, a MongoDB instance must be started at the address from config.py.
        
<h2> Usage without docker </h2>
To use this program without docker, main.py has to be called from a terminal opened at the path of main.py.
The following parameters can be passed. All parameters can be combined: <br>
    
    main.py

        --session <INT>
            Execute the session in place INT from the websiteList.py 

        --type <TYPE>
            TYPE specifies the type of execution. Possible are: 
                googleNews - collection of Google News
                flipboard - survey of Flipboard
                googleNewsAndFlipboard - Survey of Google News and Flipboard
                wn - Erhebung des RSS Feeds der Westfälischen Nachrichten
                spiegel - Erhebung des RSS Feeds von Spiegel Online
                testPersonalization - Collection of the personalization profile from the Google account settings

<h2> Usage with Docker </h2>

1. Create the image
    To create an image, docker build must be run: https://docs.docker.com/engine/reference/commandline/build/


2. Running the image
        When running the image, multiple folders must be made available to the container. The easiest way to do this is a bind mount: https://docs.docker.com/storage/bind-mounts/

        /app/config - contains the config files. For execution at arbitrary times commands can be stored in the schedule.sh output. You can use "at" as scheduler. A sample file is stored in the config folder.

        /app/log - folder for log files

        /app/profile/firefox - folder containing profile folders

<h2> individual components </h2>
The file main.py is used to control the program flow.
All components are stored in the scraper folder. The components are divided by function

        newsPages - translating news pages into structured form and downloading the linked articles
        personalizer - control of a browser profile with personalization and download of the individual websiteList
        rssFeeds - collection of the RSS feeds from WN and Spiegel
        storageInterfaces - interaction with the database

<h2> Python Libraries </h3>

selenium - API for Geckodriver https://pypi.org/project/selenium/

bs4 - HTML Parser https://pypi.org/project/beautifulsoup4/

feedparser - RSS Parser https://pypi.org/project/feedparser/

pymongo - Tools for Mongo DB https://pypi.org/project/pymongo/

<h2> Plugins </h3>

I dont care about cookies - firefox extension to accept all displayed cookies. https://addons.mozilla.org/de/firefox/addon/i-dont-care-about-cookies/


