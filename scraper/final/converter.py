from config import TrackingScraperConfig
from errors import TrackingScraperError

from geopy.exc import GeopyError
from geopy.geocoders import Nominatim

import datetime

class TrackingScraperConverter:
    """Utility class to convert text to other Python types."""
    
    # OpenStreetMap Nominatim API service for geocoding
    GEOCODER = Nominatim(user_agent = TrackingScraperConfig.GEOCODING_USER_AGENT)
    
    def __init__(self, database, document, configuration, logger, raw_text, format_type):
        self.database        = database
        self.statuses_table  = database[TrackingScraperConfig.DEFAULT_STATUS_TABLE]
        self.locations_table = database[TrackingScraperConfig.DEFAULT_LOCATIONS_TABLE]
        self.document        = document
        self.configuration   = configuration
        self.logger          = logger
        self.raw_text        = raw_text
        self.format_type     = format_type
    
    def convert(self):
        """Try to convert to the desired type, if none found, return text as-is."""
        try:
            method = getattr(self, "convert_to_" + self.format_type)
            return method()
        except AttributeError:
            self.logger.debug("Convertion to " + self.format_type + " not supported, resorting to text")
            return self.raw_text
        except TypeError:
            raise TrackingScraperError("Convertion to " + self.format_type + " cannot be invoked")
    
    def convert_to_int(self):
        """Convert text to an integer."""
        try:
            return int(self.raw_text.replace(TrackingScraperConfig.DEFAULT_THOUSAND_SYMBOL, ""))
        except ValueError:
            self.logger.debug("Convertion to integer failed, resorting to text")
            return self.raw_text
    
    def convert_to_float(self):
        """Convert text to a double-precision floating-point number."""
        try:
            return float(self.raw_text.replace(TrackingScraperConfig.DEFAULT_THOUSAND_SYMBOL, ""))
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
            patterns = self.configuration["general"]["date_formats"]
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
            return value - datetime.timedelta(**TrackingScraperConfig.DEFAULT_DATETIME_LOCALE)
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
        coordinates = self.locations_table.find_one({
            "location" : location
        })
        if coordinates is not None:
            self.save_cached_location(coordinates)
            return self.raw_text
        # If it's not, query location to Nominatim and save coordinates to document and the database
        try:
            coordinates = self.GEOCODER.geocode(location)
            if coordinates is not None:
                self.save_queried_location(coordinates, location)
                return self.raw_text
        except Exception:
            self.logger.exception("Error while trying to query geocode")
        # Go to the scraper switcher to save the location as text
        self.logger.warning("Couldn't find information for this location")
        return self.raw_text
    
    def save_cached_location(self, coordinates):
        try:
            self.document["latitude"]  = coordinates["latitude"]
            self.document["longitude"] = coordinates["longitude"]
            # self.logger.debug(location, coordinates["latitude"], coordinates["longitude"], "in database")
        except KeyError as ex:
            self.logger.warning("No %s found in database coordinate, suspicious...", str(ex))
    
    def save_queried_location(self, coordinates, location):
        # Save attribute to document
        try:
            self.document["latitude"]  = coordinates.latitude
            self.document["longitude"] = coordinates.longitude
            # self.logger.debug(location, coordinates.latitude, coordinates.longitude, "by Nominatim")
        except AttributeError as ex:
            self.logger.warning("No %s found in Nominatim coordinate, suspicious...", str(ex))
        # Save attribute to location database
        try:
            self.locations_table.insert_one({
                "location"  : location,
                "latitude"  : coordinates.latitude,
                "longitude" : coordinates.longitude
            })
        except Exception as ex:
            self.logger.error("Location could not be saved: %s", str(ex))
    
    def convert_to_status(self):
        """Convert text to a tracking status based on the configuration for translation."""
        # Get carrier and status (text from the DOM)
        carrier = self.document.get("carrier")
        status  = self.raw_text
        # Get status code from database
        if carrier is not None:
            translation = self.statuses_table.find_one({
                carrier: status
            })
            self.document["status_code"] = translation["code"] if translation else 0
        else:
            raise TrackingScraperError("Convert to status: carrier not found")
        # Finally, go to the scraper switcher to save the status as text
        return status
    
    def convert_to_vehicle(self):
        """Convert text to a tracking vehicle type based on the common configuration."""
        # TODO: Don't hardcode this
        vehicles = {
            "Vessel" : 1,
            "Truck"  : 2,
            "Train"  : 3
        }
        self.document["vehicle_code"] = vehicles.get(self.raw_text, 0)
        # Finally, go to the scraper switcher to save the vehicle as text
        return self.raw_text
