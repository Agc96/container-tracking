from config import TrackingScraperConfig
from exception import TrackingScraperError

import datetime
import logging

class TrackingScraperConverter:
    """Utility class to convert text to other Python types."""
    
    def __init__(self, raw_text, format_type, configuration):
        self.__raw_text      = raw_text
        self.__format_type   = format_type
        self.__configuration = configuration
    
    def convert(self):
        """Try to convert to the desired type, if none found, return text as-is."""
        try:
            method = getattr(self, "_convert_to_" + self.__format_type)
            return method()
        except AttributeError:
            logging.info("Convertion to " + self.__format_type + " not supported, resorting to text")
            return self.__raw_text
        except TypeError:
            raise TrackingScraperError("Convertion to " + self.__format_type + " cannot be invoked")
    
    def _convert_to_int(self):
        """Convert text to an integer."""
        try:
            return int(self.__raw_text.replace(TrackingScraperConfig.DEFAULT_THOUSAND_SYMBOL, ""))
        except ValueError:
            logging.info("Convertion to integer failed, resorting to text")
            return self.__raw_text
    
    def _convert_to_float(self):
        """Convert text to a double-precision floating-point number."""
        try:
            return float(self.__raw_text.replace(TrackingScraperConfig.DEFAULT_THOUSAND_SYMBOL, ""))
        except ValueError:
            logging.info("Convertion to float failed, resorting to text")
            return self.__raw_text
    
    def _convert_to_double(self):
        # Alias for self._convert_to_float().
        return self._convert_to_float()
    
    def _convert_to_date(self):
        """Convert text to a Python datetime object."""
        # Get datetime patterns
        try:
            patterns = self.__configuration["general"]["date_formats"]
        except KeyError:
            logging.info("Datetime patterns not found, resorting to text")
            return self.__raw_text
        
        # Try each pattern until it matches one
        for pattern in patterns:
            try:
                return datetime.datetime.strptime(self.__raw_text, pattern)
            except ValueError:
                continue
        
        # If none of the patterns matched, return text as-is
        logging.info("None of the patterns matched, resorting to text")
        return self.__raw_text
    
    def _convert_to_datetime(self):
        return self._convert_to_date()
    
    def _convert_to_time(self):
        """Convert text to a Python time object."""
        value = self._convert_to_date()
        if isinstance(value, datetime.datetime):
            return value.time()
        return value
    
    def _convert_to_datelocal(self):
        """Convert text to a Python datetime object taking the defined locale into account."""
        value = self._convert_to_date()
        if isinstance(value, datetime.datetime):
            return value - datetime.timedelta(**TrackingScraperConfig.DEFAULT_DATETIME_LOCALE)
        return value
    
    def _convert_to_timelocal(self):
        """Convert text to a Python time object taking the defined locale into account."""
        value = self._convert_to_datelocal()
        if isinstance(value, datetime.datetime):
            return value.time()
        return value
    
    def _convert_to_status(self):
        """Convert text to a tracking status based on the configuration for translation."""
        # TO-DO
        return self.__raw_text
