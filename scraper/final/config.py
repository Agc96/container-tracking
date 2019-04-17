from datetime import datetime

import logging

class TrackingScraperConfig:
    """Constants and basic configuration for the Tracking Web Scraper."""
    
    # Default retries for the scraping wrapper
    DEFAULT_RETRIES_CARRIER = [5, 1, 5, 5]
    DEFAULT_RETRIES_TOTAL   = 5 * len(DEFAULT_RETRIES_CARRIER)
    # Default extraction rounds until resetting of the scraper
    DEFAULT_RESTART_ROUNDS  = 150
    # Default executable paths for webdrivers
    DEFAULT_PATH_CHROME     = "../driver/chromedriver"
    DEFAULT_PATH_FIREFOX    = "../driver/geckodriver"
    
    # Default database name
    DEFAULT_DATABASE_NAME   = "scraper2"
    # Default table names
    DEFAULT_CONTAINER_TABLE = "containers"
    DEFAULT_MOVEMENT_TABLE  = "container_movements"
    DEFAULT_CONFIG_TABLE    = "carriers"
    DEFAULT_STATUS_TABLE    = "statuses"
    # Default parameters for containers and movements
    DEFAULT_CONTAINER_QUERY = ["container"]
    DEFAULT_CONTAINER_COPY  = DEFAULT_CONTAINER_QUERY + ["carrier"]
    DEFAULT_MOVEMENT_QUERY  = DEFAULT_CONTAINER_QUERY + ["location", "status"]
    
    # Default configuration Nominatim geocode API service
    DEFAULT_GEOCODE_AGENT   = "Tracking Scraper for Containers" # User agent
    DEFAULT_GEOCODE_MAX     = 64 # Maximum quantity of geocode items to store in cache
    # Default logging configuration
    DEFAULT_LOGGING_FILE    = "../logs/scraper-" + datetime.now().strftime("%Y%m%d") + ".log"
    DEFAULT_LOGGING_LEVEL   = logging.INFO
    DEFAULT_LOGGING_FORMAT  = "[%(levelname)s %(asctime)s] %(message)s"
    
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
    DEFAULT_DATETIME_LOCALE = {
        "hours": -5
    }
    
    # Default image to black-and-white pixel pivot
    DEFAULT_BNW_PIVOT       = 32
    # Default value for the key "alphabet" in image processing (include alphabet symbols?)
    DEFAULT_KEY_ALPHABET    = True
    # Default value for the key "numbers" in image processing (include numeric symbols?)
    DEFAULT_KEY_NUMBERS     = False
    # Default value for the key "length" in image processing (desired text length)
    DEFAULT_KEY_LENGTH      = 4
