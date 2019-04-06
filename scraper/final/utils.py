class TrackingScraperError(Exception):
    """Custom exception for the Tracking Web Scraper."""
    pass

class TrackingScraperConfig:
    """Constants and basic configuration for the Tracking Web Scraper."""
    
    # Default executable path for the Google Chrome webdriver
    DEFAULT_PATH_CHROME     = "../driver/chromedriver"
    # Default executable path for the Firefox webdriver
    DEFAULT_PATH_FIREFOX    = "../driver/geckodriver"
    
    # Default timeout for short processing, in seconds
    DEFAULT_TIMEOUT         = 30
    # Default timeout for long processing, in seconds
    DEFAULT_TIMEOUT_LONG    = 90
    # Default wait for long actions, in seconds
    DEFAULT_WAIT_LONG       = 5
    # Default wait for short actions, in seconds
    DEFAULT_WAIT_SHORT      = 1.5
    
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
