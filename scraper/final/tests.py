from utils import TrackingScraperConfig
from scraper import TrackingScraper

from selenium import webdriver
from pymongo import MongoClient

import datetime
import unittest

class TrackingScraperTestCase(unittest.TestCase):
    
    def setUp(self):
        self.driver = webdriver.Chrome(executable_path = TrackingScraperConfig.DEFAULT_PATH_CHROME)
        self.database = MongoClient()["tracking_scraper"]
        self.containers = self.database["containers"]
        self.container_movements = self.database["container_movements"]
    
    def tearDown(self):
        self.driver.close()
    
    def test1HapagLloyd(self):
        container = {
            "year": "2019",
            "manifest": "TEST",
            "detail": "1",
            "container": "FSCU5670046",
            "carrier": "Hapag-Lloyd"
        }
        self.executeTest(container)
        # Assert container information
        assert container["type"]          == "45RT"
        assert container["description"]   == "REEFER CONTAINER"
        assert container["length"]        == "40'"
        assert container["width"]         == "8'"
        assert container["height"]        == "9'6\""
        assert container["tare"]          == 4640
        assert container["max_payload"]   == 29360
        assert container["last_status"]   == "vessel departed"
        assert container["last_location"] == "ANTWERP"
        assert container["last_date"]     == datetime.datetime(2019, 3, 26)
    
    def test2Maersk(self):
        container = {
            "year": "2019",
            "manifest": "TEST",
            "detail": "3",
            "container": "MAEU6835658",
            "carrier": "Maersk"
        }
        self.executeTest(container)
        # Assert container information
        assert container["origin_point"]  == "Izmit Korfezi"
        assert container["dest_point"]    == "Melbourne"
        assert container["description"]   == "20ft Dry Container"
        assert container["arrival_date"]  == datetime.datetime(2019, 3, 3, 9, 49)
        assert container["last_status"]   == "Gate out"
        assert container["last_location"] == "Melbourne, Victoria, Australia"
        assert container["last_date"]     == datetime.datetime(2019, 3, 5)
    
    def test3Evergreen(self):
        container = {
            "year": "2019",
            "manifest": "TEST",
            "detail": "4",
            "container": "EGSU9089973",
            "carrier": "Evergreen"
        }
        self.executeTest(container)
        # Assert container information
        assert container["type"]          == "40'(SH)"
        assert container["arrival_date"]  == datetime.datetime(2019, 4, 11)
        assert container["vessel_voyage"] == "EVER LAMBENT 0403-037W"
    
    def test4Textainer(self):
        container = {
            "year": "2019",
            "manifest": "TEST",
            "detail": "5",
            "container": "TEMU3806660",
            "carrier": "Textainer"
        }
        self.executeTest(container)
        # Assert container information
        assert container["last_status"] == "ON HIRE"
        assert container["last_date"]   == datetime.datetime(2017, 8, 1)
        assert container["carrier"]     == "Maersk"
    
    def executeTest(self, container):
        scraper = TrackingScraper(self.driver, self.database, container)
        assert scraper.execute() is True
    
    def getMovements(self, container):
        movements = []
        query = dict(container).pop("carrier")
        for movement in self.container_movements.find(query).sort("date", 1):
            movements.append(movement)
        return movements

if __name__ == "__main__":
    unittest.main()
