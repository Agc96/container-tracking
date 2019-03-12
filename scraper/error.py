from datetime import datetime

class TrackingScraperError(Exception):
    """
    Custom exception for the Tracking Scraper class.
    """
    
    def __init__(self, message, container = None, carrier = None, exception = None):
        # Call base class constructor
        super().__init__(message)
        
        # Declare custom attributes
        self.__message = message
        self.__container = container
        self.__carrier = carrier
        self.__datetime = datetime.today()
        self.__exception = exception
    
    def __str__(self):
        # Generate base string with general info
        message = "{0}, carrier={1}, container={2}: {3}."
        message = message.format(str(self.__datetime), self.__carrier, self.__container, self.__message)
        
        # Generate custom message
        if self.__exception is not None:
            message += " " + str(self.__exception) #.replace("\n", "")
        
        return message

