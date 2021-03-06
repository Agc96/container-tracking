import datetime
import logging
import os
import sys

import psycopg2
import psycopg2.extras

class ScraperConfig:
    """Constants and basic configuration for the Tracking Web Scraper."""
    
    # Default values for scraper resetting and failure count
    ROUNDS_RESTART         = 150
    ROUNDS_FAILURE_WARNING = 20
    ROUNDS_FAILURE_WAIT    = 60
    
    # WebDriver locations
    PATH_CHROME  = "C:/WebDriver/chromedriver" if sys.platform == "win32" else "/usr/local/bin/chromedriver"
    PATH_FIREFOX = "C:/WebDriver/geckodriver"  if sys.platform == "win32" else "/usr/local/bin/geckodriver"
    
    # Default database and table names
    @staticmethod
    def get_database():
        return psycopg2.connect(cursor_factory=psycopg2.extras.RealDictCursor,
                                host=os.getenv("DB_HOST", "localhost"),
                                dbname=os.getenv("DB_NAME", "tracking"),
                                user=os.getenv("DB_USER", "scraper"),
                                password=os.getenv("DB_PASS"))
    
    # Default configuration Nominatim geocode API service
    GEOCODING_USER_AGENT = "Tracking Scraper for Containers"

    # Default logging configuration
    @staticmethod
    def getlogger(carrier):
        """Get logging configuration for the Tracking Scraper."""
        # Prepare formatter
        formatter = logging.Formatter("[%(levelname)s %(asctime)s] %(message)s")
        # Prepare handler filename and logger name
        today    = datetime.datetime.now().strftime("%Y%m%d")
        filename = "../logs/scraper-{}-{}.log".format(carrier, today)
        logname  = "scraper-{}".format(carrier)
        # Prepare handler
        handler = logging.FileHandler(filename)
        handler.setFormatter(formatter)
        # Prepare logger
        logger = logging.getLogger(logname)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        return logger
    
    # Default timeouts, in seconds
    DEFAULT_TIMEOUT_SHORT   = 30
    DEFAULT_TIMEOUT_NORMAL  = 60
    DEFAULT_TIMEOUT_LONG    = 90
    # Default waits, in seconds
    DEFAULT_WAIT_SHORT      = 1.5
    DEFAULT_WAIT_NORMAL     = 3
    DEFAULT_WAIT_LONG       = 5
    
    # Default value for the key "required" in all types
    DEFAULT_KEY_REQUIRED    = True
    # Default value for the key "action" in type "alert"
    DEFAULT_KEY_ACTION      = True
    # Default value for the key "wait" in type "click"
    DEFAULT_KEY_WAIT        = True
    # Default value for the key "clean" in type "write"
    DEFAULT_KEY_CLEAN       = False
    # Default value for the key "enter" in type "write"
    DEFAULT_KEY_ENTER       = False
    # Default value for the key "overwrite" in multiple configuration
    DEFAULT_KEY_OVERWRITE   = False
    # Default value for the key "frame" in selector types
    DEFAULT_KEY_FRAME       = False
    
    # Default value for the key "processed" in upserting container info
    DEFAULT_KEY_PROCESSED   = True
    # Default value for the key "estimated" in container movements
    DEFAULT_KEY_ESTIMATED   = True
    
    # Default thousand separator symbol
    DEFAULT_THOUSAND_SYMBOL = ","
    # Default datetime locale information
    DEFAULT_DATETIME_LOCALE = {"hours": -5}
    
    # Default image to black-and-white pixel pivot
    DEFAULT_BNW_PIVOT       = 32
    # Default value for the key "alphabet" in image processing (include alphabet symbols?)
    DEFAULT_KEY_ALPHABET    = True
    # Default value for the key "numbers" in image processing (include numeric symbols?)
    DEFAULT_KEY_NUMBERS     = False
    # Default value for the key "length" in image processing (desired text length)
    DEFAULT_KEY_LENGTH      = 4
