class TrackingScraperError(Exception):
    """General exception for the Container Tracking Scraper."""
    pass

class TrackingScraperTimeoutError(TrackingScraperError):
    """Exception for timeouts in the web browser used by the Container Tracking Scraper."""
    def __init__(self, page_loaded):
        message = "Timeout exceeded" if page_loaded else "Could not load page"
        super().__init__(message + ", scraping was unsuccessful")
        # Save attributes
        self.page_loaded = page_loaded

class TrackingScraperAssertionError(TrackingScraperError):
    """Exception for assertion commands in the Container Tracking Scraper."""
    def __init__(self, process_type, assertion_type):
        # Write message
        message = "not found" if assertion_type else "found"
        super().__init__("Assertion failed, " + process_type + " element(s) unexpectedly " + message)
        # Save attributes
        self.process_type   = process_type
        self.assertion_type = assertion_type

class TrackingScraperSwitcherError(TrackingScraperError):
    """Exception for errors in the Container Tracking Scraper Switcher command file."""
    def __init__(self, message, command):
        # Write message
        super().__init__(message)
        # Save attributes
        self.command = command
