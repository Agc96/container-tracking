from datetime import datetime

class TrackingScraperError(Exception):
    """Custom exception for the Tracking Scraper class."""
    def __init__(self, message = None, container = None, carrier = None, exception = None):
        # Call base class constructor
        super().__init__(message)
        # Declare custom attributes
        self.container = container
        self.carrier = carrier
        self.time = datetime.today()
    def __str__(self):
        return super().__str__()

try:
    raise TrackingScraperError
except TrackingScraperError as ex:
    print(ex)
