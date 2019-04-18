from config import TrackingScraperConfig
from scraper import TrackingScraper

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime

import logging
import unittest

class TrackingScraperTestCase(unittest.TestCase):
    """Unit tests for the Tracking Scraper class."""
    
    def setUp(self):
        # Initialize WebDriver
        options = Options()
        options.add_argument("--start-maximized")
        self.driver = WebDriver(executable_path = TrackingScraperConfig.DEFAULT_PATH_CHROME, options = options)
        # Initialize database
        self.database  = MongoClient()["scrapertests"]
        self.movements = self.database[TrackingScraperConfig.DEFAULT_MOVEMENT_TABLE]
    
    def tearDown(self):
        self.driver.close()
    
    def test01_Maersk(self):
        container = {
            "container"    : "MNBU9027602",
            "carrier"      : "Maersk",
            # "carrier_code" : 1,
            "requested_at" : datetime(2019, 4, 17)
        }
        self.assertContainer(container, {
            "description"   : "40ft High Cube Reefer Container",
            "arrival_date"  : datetime(2019, 5, 10),
            "last_status"   : "Load",
            "last_location" : "Callao, Peru",
            "last_date"     : datetime(2019, 4, 13)
        })
        # Assert container movements
        self.assertMovements(container, [
            {
                "location"     : "Alconsa Callao\nCallao, Peru",
                "latitude"     : -12.066667,
                "longitude"    : -77.15,
                "date"         : datetime(2019, 4, 9, 19, 59),
                "status"       : "Empty",
                "status_code"  : 1,
                "vehicle"      : "Truck",
                "vehicle_code" : 2,
                "estimated"    : False
            },
            {
                "location"     : "APM Terminals in Callao Port\nCallao, Peru",
                "latitude"     : -12.066667,
                "longitude"    : -77.15,
                "date"         : datetime(2019, 4, 10, 16, 53),
                "status"       : "Gate in",
                "status_code"  : 2,
                "vehicle"      : "Truck",
                "vehicle_code" : 2,
                "estimated"    : False
            },
            {
                "location"     : "APM Terminals in Callao Port\nCallao, Peru",
                "latitude"     : -12.066667,
                "longitude"    : -77.15,
                "date"         : datetime(2019, 4, 13, 8, 21),
                "status"       : "Load",
                "status_code"  : 3,
                "vehicle"      : "Vessel",
                "vehicle_code" : 1,
                "vessel"       : "LARS MAERSK",
                "voyage"       : "914W",
                "estimated"    : False
            },
            {
                "location"     : "Balboa Port Terminal\nBalboa, Panama",
                "latitude"     : 8.3479957,
                "longitude"    : -78.8971729791261,
                "date"         : datetime(2019, 4, 18),
                "status"       : "Discharge",
                "status_code"  : 7,
                "vehicle"      : "Vessel",
                "vehicle_code" : 1,
                "estimated"    : True
            },
            {
                "location"     : "Balboa Port Terminal\nBalboa, Panama",
                "latitude"     : 8.3479957,
                "longitude"    : -78.8971729791261,
                "date"         : datetime(2019, 4, 20),
                "status"       : "On rail",
                "status_code"  : 0,
                "vehicle"      : "Train",
                "vehicle_code" : 3,
                "estimated"    : True
            },
            {
                "location"     : "Manzanillo Terminal\nManzanillo, Panama",
                "latitude"     : 8.194041,
                "longitude"    : -82.8767907,
                "date"         : datetime(2019, 4, 20),
                "status"       : "Off rail",
                "status_code"  : 0,
                "vehicle"      : "Train",
                "vehicle_code" : 3,
                "estimated"    : True
            },
            {
                "location"     : "Manzanillo Terminal\nManzanillo, Panama",
                "latitude"     : 8.194041,
                "longitude"    : -82.8767907,
                "date"         : datetime(2019, 4, 21),
                "status"       : "Load",
                "status_code"  : 3,
                "vehicle"      : "Vessel",
                "vehicle_code" : 1,
                "vessel"       : "MAERSK NESTON",
                "voyage"       : "916E",
                "estimated"    : True
            },
            {
                "location"     : "SALERNo SCT SalerNo Container Termi\nSalerno, Salarno, Italy",
                "latitude"     : 46.138917,
                "longitude"    : 10.5204375,
                "date"         : datetime(2019, 5, 10),
                "status"       : "Discharge",
                "status_code"  : 7,
                "vehicle"      : "Vessel",
                "vehicle_code" : 1,
                "estimated"    : True
            },
            {
                "location"     : "SALERNo SCT SalerNo Container Termi\nSalerno, Salarno, Italy",
                "latitude"     : 46.138917,
                "longitude"    : 10.5204375,
                "date"         : datetime(2019, 5, 10),
                "status"       : "Gate out",
                "status_code"  : 8,
                "vehicle"      : "Truck",
                "vehicle_code" : 2,
                "estimated"    : True
            }
        ])
    
    def TODAVIA_test02_HapagLloyd(self):
        container = {
            "container"    : "FSCU5670046",
            "carrier"      : "Hapag-Lloyd",
            # "carrier_code" : 2,
            "requested_at" : datetime(2019, 4, 17)
        }
        # Assert container information
        self.assertContainer(dict(container), {
            "description"   : "REEFER CONTAINER",
            "last_status"   : "container departed",
            "last_location" : "NORFOLK, VA",
            "last_date"     : datetime(2019, 4, 9)
        })
        # Assert container movements
        # self.assertMovements(container)
    
    def LISTO_test03_Evergreen(self):
        container = {
            "container"    : "EGSU9089973",
            "carrier"      : "Evergreen",
            # "carrier_code" : 3,
            "requested_at" : datetime(2019, 4, 17)
        }
        # Assert container information
        self.assertContainer(container, {
            "description"   : "40'(SH)",
            # "arrival_date"  : datetime(2019, 4, 11),
            "last_status"   : "Discharged (FCL)",
            "last_location" : "HUANGPU, GUANGDONG (CN)",
            "last_date"     : datetime(2019, 4, 11)
        })
        # Assert container movements
        self.assertMovements(container, [
            {
                "location"     : "CALLAO (PE)",
                "latitude"     : -12.066667,
                "longitude"    : -77.15,
                "date"         : datetime(2019, 3, 7),
                "status"       : "Loaded (FCL) on vessel",
                "status_code"  : 3,
                "vehicle"      : "Vessel",
                "vehicle_code" : 1,
                "vessel"       : "EVER LAMBENT",
                "voyage"       : "0403-037W",
                "estimated"    : False
            },
            {
                "location"     : "HONG KONG (HK)",
                "latitude"     : 22.350627,
                "longitude"    : 114.1849161,
                "date"         : datetime(2019, 4, 10),
                "status"       : "Despatched by barge",
                "status_code"  : 0,
                "vehicle"      : "Vessel",
                "vehicle_code" : 1,
                "vessel"       : "EVER LAMBENT",
                "voyage"       : "0403-037W",
                "estimated"    : False
            },
            {
                "location"     : "HUANGPU, GUANGDONG (CN)",
                "latitude"     : 23.1824507,
                "longitude"    : 113.4760861,
                "date"         : datetime(2019, 4, 11),
                "status"       : "Discharged (FCL)",
                "status_code"  : 7,
                "vehicle"      : "Vessel",
                "vehicle_code" : 1,
                "vessel"       : "EVER LAMBENT",
                "voyage"       : "0403-037W",
                "estimated"    : False
            }
        ])
    
    def TODAVIA_test04_Textainer(self):
        container = {
            "container":    "TEMU3806660",
            "carrier":      "Textainer",
            "requested_at": datetime(2019, 4, 17)
        }
        # Assert container information
        self.assertContainer(container, {
            "carrier": "Maersk"
        })
    
    def assertContainer(self, container, expected):
        # Execute scraper and assert result
        scraper = TrackingScraper(self.driver, self.database, dict(container))
        if scraper.execute() is not True:
            self.fail("Scraper execution failed, check log for details.")
        # Assert from expected container items
        self.assertTrackingDict(scraper.container, expected, "Container")
    
    def assertMovements(self, container, expected):
        # Query movements
        query_container = { "container": container["container"]}
        query_sorting   = [("date", ASCENDING), ("_id", ASCENDING)]
        cursor = list(self.movements.find(query_container).sort(query_sorting))
        # Assert movement count is at least the size of the expected movement list
        if len(cursor) < len(expected):
            message = "Not enough movements for container {0} (expected at least {1})"
            self.fail(message.format(container["container"], len(expected)))
        # Iterate movements
        for index, movement in enumerate(cursor):
            # Assert from container table
            self.assertTrackingDict(movement, container, "Movement at index {3}", index)
            # Assert from expected movement list at selected index
            self.assertTrackingDict(movement, expected[index], "Movement at index {3}", index)
    
    def assertTrackingDict(self, dictionary, subset, name, index = None):
        for key, value in subset.items():
            # Check if dictionary has the key
            if key not in dictionary:
                message = name + " doesn't have key {0} (expected {1})"
                self.fail(message.format(key, value, None, index))
            # Check if values are equal
            elif subset[key] != dictionary[key]:
                message = name + " doesn't match key {0} (expected {1}, got {2})"
                self.fail(message.format(key, value, dictionary[key], index))

if __name__ == "__main__":
    logging.basicConfig(filename = "tests-" + datetime.now().strftime("%Y%m%d") + ".log",
                        level = TrackingScraperConfig.DEFAULT_LOGGING_LEVEL,
                        format = TrackingScraperConfig.DEFAULT_LOGGING_FORMAT)
    unittest.main()
