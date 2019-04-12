class TrackingScraperError(Exception):
    """Custom general exception for the Tracking Web Scraper."""
    pass

class TrackingScraperAssertionError(TrackingScraperError):
    """Exception for assertion commands."""
    def __init__(self, process_type, assertion_type):
        # Write message
        message = "not found" if assertion_type else "found"
        super().__init__("Assertion failed, " + process_type + " element(s) unexpectedly " + message)
        # Save attributes
        self.process_type   = process_type
        self.assertion_type = assertion_type

class TrackingScraperSwitcherError(TrackingScraperError):
    """Exception for errors in the Tracking Scraper Switcher command file."""
    def __init__(self, message, command):
        # Write message
        super().__init__(message)
        # Save attributes
        self.command = command
