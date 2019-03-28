class TrackingScraperError(Exception):
    """Custom exception for the Tracking Web Scraper."""
    pass

class TrackingScraperConfig:
    """Constants and basic configuration for the Tracking Web Scraper."""
    
    # Default timeout, in seconds
    DEFAULT_TIMEOUT        = 60
    # Default wait for long actions, in seconds
    DEFAULT_WAIT_LONG      = 5
    # Default wait for short actions, in seconds
    DEFAULT_WAIT_SHORT     = 1.5
    
    # Default value for the key "required" in all types
    DEFAULT_KEY_REQUIRED   = True
    # Default value for the key "action" in type "alert"
    DEFAULT_KEY_ACTION     = True
    # Default value for the key "wait" in type "click"
    DEFAULT_KEY_WAIT       = True
    # Default value for the key "clean" in type "write"
    DEFAULT_KEY_CLEAN      = False
    # Default value for the key "enter" in type "write"
    DEFAULT_KEY_ENTER      = False
    
    # Default thousand separator symbol
    DEFAULT_THOUSAND_SYMBOL = ","
    # Default datetime locale information
    DEFAULT_DATETIME_LOCALE = {
        "hours": -5
    }
