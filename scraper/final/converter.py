from config import ScraperConfig
from errors import ScraperError
from query import ScraperQuery

from geopy.exc import GeopyError
from geopy.geocoders import Nominatim

import datetime

class ScraperConverter:
    """Utility class to convert text to other Python types."""
    
    # OpenStreetMap Nominatim API service for geocoding
    GEOCODER = Nominatim(user_agent = ScraperConfig.GEOCODING_USER_AGENT)
    
    def __init__(self, switcher, document, raw_text, format_type):
        self.carrier     = switcher.carrier
        self.config      = switcher.config
        self.logger      = switcher.logger
        self.document    = document
        self.raw_text    = raw_text
        self.format_type = format_type
    
    def convert(self):
        """Try to convert to the desired type, if none found, return text as-is."""
        try:
            method = getattr(self, "convert_to_" + self.format_type)
            return method()
        except AttributeError:
            self.logger.debug("Convertion to " + self.format_type + " not supported, resorting to text")
            return self.raw_text
        except TypeError:
            raise ScraperError("Convertion to " + self.format_type + " cannot be invoked")
    
    def convert_to_int(self):
        """Convert text to an integer."""
        try:
            return int(self.raw_text.replace(ScraperConfig.DEFAULT_THOUSAND_SYMBOL, ""))
        except ValueError:
            self.logger.debug("Convertion to integer failed, resorting to text")
            return self.raw_text
    
    def convert_to_float(self):
        """Convert text to a double-precision floating-point number."""
        try:
            return float(self.raw_text.replace(ScraperConfig.DEFAULT_THOUSAND_SYMBOL, ""))
        except ValueError:
            self.logger.debug("Convertion to float failed, resorting to text")
            return self.raw_text
    
    def convert_to_double(self):
        # Alias for self.convert_to_float().
        return self.convert_to_float()
    
    def convert_to_date(self):
        """Convert text to a Python datetime object."""
        # Get datetime patterns
        try:
            patterns = self.config["general"]["dates"]
        except KeyError:
            self.logger.debug("Datetime patterns not found, resorting to text")
            return self.raw_text
        
        # Try each pattern until it matches one
        for pattern in patterns:
            try:
                return datetime.datetime.strptime(self.raw_text, pattern)
            except ValueError:
                continue
        
        # If none of the patterns matched, return text as-is
        self.logger.debug("None of the patterns matched, resorting to text")
        return self.raw_text
    
    def convert_to_datetime(self):
        return self.convert_to_date()
    
    def convert_to_time(self):
        """Convert text to a Python time object."""
        value = self.convert_to_date()
        if isinstance(value, datetime.datetime):
            return value.time()
        return value
    
    def convert_to_datelocal(self):
        """Convert text to a Python datetime object taking the defined locale into account."""
        value = self.convert_to_date()
        if isinstance(value, datetime.datetime):
            return value - datetime.timedelta(**ScraperConfig.DEFAULT_DATETIME_LOCALE)
        return value
    
    def convert_to_timelocal(self):
        """Convert text to a Python time object taking the defined locale into account."""
        value = self.convert_to_datelocal()
        if isinstance(value, datetime.datetime):
            return value.time()
        return value
    
    def convert_to_location(self):
        """Convert text to a location with latitude and longitude geographical points."""
        # Use last line as parent location and check if it's in database
        location = self.raw_text.split("\n")[-1]
        result = ScraperQuery.execute_id("SELECT id FROM tracking_location WHERE name = %s", (location,))
        if result is not None:
            return result
        # If it's not, query location to Nominatim and save coordinates to document and the database
        latitude, longitude = None, None
        try:
            coordinates = self.GEOCODER.geocode(location)
            if coordinates is not None:
                latitude = coordinates.latitude
                longitude = coordinates.longitude
            else:
                self.logger.warning("Couldn't find information for location {}".format(location))
        except Exception:
            self.logger.exception("Error while trying to query geocode")
        # Save location to database and 
        with psycopg2.connect(**ScraperConfig.DATABASE_DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO tracking_location (name, latitude, longitude)
                    VALUES (%s, %s, %s) RETURNING id""", (0, self.raw_text, self.carrier["id"]))
                result = cur.fetchone()
                cur.commit()
            conn.commit()
        return result.get("id") if result is not None else None
    
    def convert_to_status(self):
        """Convert text to a tracking status based on the configuration for translation."""
        # Get carrier and status (text from the DOM)
        result = ScraperQuery.execute_id("""SELECT id FROM tracking_movement_status WHERE
            enterprise_id = %s AND name = %s""", (self.carrier["id"], self.raw_text))
        if result is not None:
            return result
        # Get status code from database
        with psycopg2.connect(**ScraperConfig.DATABASE_DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO tracking_movement_status (status, name, enterprise_id)
                    VALUES (%s, %s, %s) RETURNING id""", (0, self.raw_text, self.carrier["id"]))
                result = cur.fetchone()
                cur.commit()
            conn.commit()
        return result.get("id") if result is not None else None
    
    def convert_to_vehicle(self):
        """Convert text to a tracking vehicle type based on the common configuration."""
        return ScraperQuery.execute_id("SELECT id FROM tracking_vehicle WHERE original_name = %s",
                                        (self.raw_text,))
