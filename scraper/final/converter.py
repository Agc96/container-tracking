from config import TrackingScraperConfig
from errors import TrackingScraperError

from geopy.exc import GeopyError
from geopy.geocoders import Nominatim
from pymongo import MongoClient

import datetime
import logging

class TrackingScraperConverter:
    """Utility class to convert text to other Python types."""
    
    # Nominatim geolocator instance
    GEOLOCATOR = Nominatim(user_agent = TrackingScraperConfig.DEFAULT_GEOCODE_AGENT)
    # MongoDB collection instances
    DATABASE   = MongoClient()[TrackingScraperConfig.DEFAULT_DATABASE_NAME]
    STATUSES   = DATABASE[TrackingScraperConfig.DEFAULT_STATUS_TABLE]
    LOCATIONS  = DATABASE[TrackingScraperConfig.DEFAULT_LOCATIONS_TABLE]
    
    def __init__(self, document, raw_text, format_type, configuration):
        self.document      = document
        self.raw_text      = raw_text
        self.format_type   = format_type
        self.configuration = configuration
    
    def convert(self):
        """Try to convert to the desired type, if none found, return text as-is."""
        try:
            method = getattr(self, "convert_to_" + self.format_type)
            return method()
        except AttributeError:
            logging.info("Convertion to " + self.format_type + " not supported, resorting to text")
            return self.raw_text
        except TypeError:
            raise TrackingScraperError("Convertion to " + self.format_type + " cannot be invoked")
    
    def convert_to_int(self):
        """Convert text to an integer."""
        try:
            return int(self.raw_text.replace(TrackingScraperConfig.DEFAULT_THOUSAND_SYMBOL, ""))
        except ValueError:
            logging.info("Convertion to integer failed, resorting to text")
            return self.raw_text
    
    def convert_to_float(self):
        """Convert text to a double-precision floating-point number."""
        try:
            return float(self.raw_text.replace(TrackingScraperConfig.DEFAULT_THOUSAND_SYMBOL, ""))
        except ValueError:
            logging.info("Convertion to float failed, resorting to text")
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
            logging.info("Datetime patterns not found, resorting to text")
            return self.raw_text
        
        # Try each pattern until it matches one
        for pattern in patterns:
            try:
                return datetime.datetime.strptime(self.raw_text, pattern)
            except ValueError:
                continue
        
        # If none of the patterns matched, return text as-is
        logging.info("None of the patterns matched, resorting to text")
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
        # Get location (raw text) as address
        location = self.raw_text
        # Use last line as parent location and check if it's in database
        query = location.split("\n")[-1]
        if self.get_location(query):
            return location
        if self.save_location(query):
            return location
        # If that didn't work, try removing a comma
        try:
            query = query.split(",", 1)[1]
            if self.get_location(query):
                return location
            if self.save_location(query):
                return location
        except IndexError:
            pass
        # Finally, go to the scraper switcher to save the location as text
        return location
    
    def get_location(self, location):
        coordinates = self.LOCATIONS.find_one({ "location": location })
        if coordinates is None:
            # logging.info(location, "not found in database")
            return False
        try:
            self.document["latitude"]  = coordinates["latitude"]
            self.document["longitude"] = coordinates["longitude"]
            # logging.info(location, coordinates["latitude"], coordinates["longitude"], "in database")
        except KeyError as ex:
            logging.warning("No %s found in database coordinate, suspicious...", str(ex))
        return True
    
    def save_location(self, location):
        try:
            coordinates = self.GEOLOCATOR.geocode(location)
        except Exception:
            logging.exception("Error while trying to query geocode")
            return False
        if coordinates is None:
            # logging.info(location, "not found by Nominatim")
            return False
        # Save attribute to document
        try:
            self.document["latitude"]  = coordinates.latitude
            self.document["longitude"] = coordinates.longitude
            # logging.info(location, coordinates.latitude, coordinates.longitude, "by Nominatim")
        except AttributeError as ex:
            logging.warning("No %s found in Nominatim coordinate, suspicious...", str(ex))
        # Save attribute to location database
        try:
            query = {
                "location"  : location,
                "latitude"  : coordinates.latitude,
                "longitude" : coordinates.longitude
            }
            self.LOCATIONS.update_one({"location": location}, {"$set": query}, upsert = True)
        except Exception as ex:
            logging.error("Location could not be saved: %s", str(ex))
        return True
    
    def convert_to_status(self):
        """Convert text to a tracking status based on the configuration for translation."""
        # Get carrier and status (text from the DOM)
        carrier = self.document.get("carrier")
        status  = self.raw_text
        # Get status code from database
        if carrier is not None:
            translation = self.STATUSES.find_one({ carrier: status })
            self.document["status_code"] = translation["code"] if translation else 0
        else:
            raise TrackingScraperError("Convert to status: carrier not found")
        # Finally, go to the scraper switcher to save the status as text
        return status
    
    def convert_to_vehicle(self):
        """Convert text to a tracking vehicle type based on the common configuration."""
        # Get vehicle (text from the DOM)
        # TODO: Don't hardcode this
        vehicle = self.raw_text
        if vehicle == "Vessel":
            self.document["vehicle_code"] = 1
        elif vehicle == "Truck":
            self.document["vehicle_code"] = 2
        elif vehicle == "Train":
            self.document["vehicle_code"] = 3
        else:
            self.document["vehicle_code"] = 0
        # Finally, go to the scraper switcher to save the vehicle as text
        return vehicle
