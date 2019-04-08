from config import TrackingScraperConfig
from scraper import TrackingScraper

from selenium import webdriver
from pymongo import MongoClient

import datetime
import logging
import unittest

class TrackingScraperTestCase(unittest.TestCase):
    """Unit tests for the Tracking Scraper class."""
    
    def setUp(self):
        self.driver = webdriver.Chrome(executable_path = TrackingScraperConfig.DEFAULT_PATH_CHROME)
        self.database = MongoClient()["scraper2"]
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
        assert container["last_status"]   == "container was discharged"
        assert container["last_location"] == "NORFOLK, VA"
        assert container["last_date"]     == datetime.datetime(2019, 4, 7)
        # Assert container movements
        movements = self.getMovements(container)
        assert len(movements) >= 6
        # Assert container movement #1
        assert movements[0]["status"]           == "Gate out empty"
        assert movements[0]["location"]         == "ANTWERP"
        assert movements[0]["date"]             == datetime.datetime(2019, 3, 12, 7, 33)
        assert movements[0]["transport_type"]   == "Truck"
        # Assert container movement #2
        assert movements[1]["status"]           == "Arrival in"
        assert movements[1]["location"]         == "ANTWERP"
        assert movements[1]["date"]             == datetime.datetime(2019, 3, 12, 14, 37)
        assert movements[1]["transport_type"]   == "Truck"
        # Assert container movement #3
        assert movements[2]["status"]           == "Loaded"
        assert movements[2]["location"]         == "ANTWERP"
        assert movements[2]["date"]             == datetime.datetime(2019, 3, 26, 12, 59)
        assert movements[2]["transport_type"]   == "Vessel"
        assert movements[2]["transport_ship"]   == "YM EXPRESS"
        assert movements[2]["transport_voyage"] == "038W"
        # Assert container movement #4
        assert movements[3]["status"]           == "Vessel departed"
        assert movements[3]["location"]         == "ANTWERP"
        assert movements[3]["date"]             == datetime.datetime(2019, 3, 26, 21, 54)
        assert movements[3]["transport_type"]   == "Vessel"
        assert movements[3]["transport_ship"]   == "YM EXPRESS"
        assert movements[3]["transport_voyage"] == "038W"
        # Assert container movement #5
        assert movements[4]["status"]           == "Vessel arrived"
        assert movements[4]["location"]         == "NORFOLK, VA"
        assert movements[4]["date"]             == datetime.datetime(2019, 4, 7, 3, 30)
        assert movements[4]["transport_type"]   == "Vessel"
        assert movements[4]["transport_ship"]   == "YM EXPRESS"
        assert movements[4]["transport_voyage"] == "038W"
        # Assert container movement #6
        assert movements[5]["status"]           == "Discharged"
        assert movements[5]["location"]         == "NORFOLK, VA"
        assert movements[5]["date"]             == datetime.datetime(2019, 4, 7, 9, 25)
        assert movements[5]["transport_type"]   == "Vessel"
        assert movements[5]["transport_ship"]   == "YM EXPRESS"
        assert movements[5]["transport_voyage"] == "038W"
    
    def test2Maersk(self):
        container = {
            "year": "2019",
            "manifest": "TEST",
            "detail": "3",
            "container": "MRKU5264777",
            "carrier": "Maersk"
        }
        self.executeTest(container)
        # Assert container information
        assert container["origin_point"]  == "Port Klang"
        assert container["dest_point"]    == "Callao"
        assert container["description"]   == "40ft Dry Container"
        assert container["arrival_date"]  == datetime.datetime(2019, 4, 5, 23, 29)
        assert container["last_status"]   == "Gate out"
        assert container["last_location"] == "Callao, Peru"
        assert container["last_date"]     == datetime.datetime(2019, 4, 6)
        # Assert container movements
        movements = self.getMovements(container)
        assert len(movements) >= 9
        # Assert container movement #1
        assert movements[0]["location_terminal"] == "Cogent Container Depot (M) Sdn Bhd"
        assert movements[0]["location"]          == "Port Klang, Selangor, Malaysia"
        assert movements[0]["date"]              == datetime.datetime(2019, 2, 12, 18, 32)
        assert movements[0]["status"]            == "Gate out"
        assert movements[0]["transport_type"]    == "Truck"
        # Assert container movement #2
        assert movements[1]["location_terminal"] == "Westport"
        assert movements[1]["location"]          == "Port Klang, Selangor, Malaysia"
        assert movements[1]["date"]              == datetime.datetime(2019, 2, 13, 21, 35)
        assert movements[1]["status"]            == "Gate in"
        assert movements[1]["transport_type"]    == "Truck"
        # Assert container movement #3
        assert movements[2]["location_terminal"] == "Westport"
        assert movements[2]["location"]          == "Port Klang, Selangor, Malaysia"
        assert movements[2]["date"]              == datetime.datetime(2019, 2, 15, 1, 13)
        assert movements[2]["status"]            == "Load"
        assert movements[2]["transport_ship"]    == "OOCL HAMBURG"
        assert movements[2]["transport_voyage"]  == "108E"
        assert movements[2]["transport_type"]    == "Vessel"
        # Assert container movement #4
        assert movements[3]["location_terminal"] == "Hongkong/Hk International Terminals"
        assert movements[3]["location"]          == "Hong Kong, Hong Kong"
        assert movements[3]["date"]              == datetime.datetime(2019, 2, 21, 2, 57)
        assert movements[3]["status"]            == "Discharge"
        assert movements[3]["transport_type"]    == "Vessel"
        # Assert container movement #5
        assert movements[4]["location_terminal"] == "Hongkong/Hk International Terminals"
        assert movements[4]["location"]          == "Hong Kong, Hong Kong"
        assert movements[4]["date"]              == datetime.datetime(2019, 2, 24, 15, 17)
        assert movements[4]["status"]            == "Gate out"
        assert movements[4]["transport_type"]    == "Truck"
        # Assert container movement #6
        assert movements[5]["location_terminal"] == "Hong Kong Modern Terminals Ltd"
        assert movements[5]["location"]          == "Hong Kong, Hong Kong"
        assert movements[5]["date"]              == datetime.datetime(2019, 2, 24, 15, 29)
        assert movements[5]["status"]            == "Gate in"
        assert movements[5]["transport_type"]    == "Truck"
        # Assert container movement #7
        assert movements[6]["location_terminal"] == "Hong Kong Modern Terminals Ltd"
        assert movements[6]["location"]          == "Hong Kong, Hong Kong"
        assert movements[6]["date"]              == datetime.datetime(2019, 3, 5, 15, 51)
        assert movements[6]["status"]            == "Load"
        assert movements[6]["transport_ship"]    == "CHASTINE MAERSK"
        assert movements[6]["transport_voyage"]  == "908E"
        assert movements[6]["transport_type"]    == "Vessel"
        # Assert container movement #8
        assert movements[7]["location_terminal"] == "APM Terminals in Callao Port"
        assert movements[7]["location"]          == "Callao, Peru"
        assert movements[7]["date"]              == datetime.datetime(2019, 4, 5, 23, 29)
        assert movements[7]["status"]            == "Discharge"
        assert movements[7]["transport_type"]    == "Vessel"
        # Assert container movement #9
        assert movements[8]["location_terminal"] == "APM Terminals in Callao Port"
        assert movements[8]["location"]          == "Callao, Peru"
        assert movements[8]["date"]              == datetime.datetime(2019, 4, 6, 14, 11)
        assert movements[8]["status"]            == "Gate out"
        assert movements[8]["transport_type"]    == "Truck"
    
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
        assert container["type"]         == "40'(SH)"
        assert container["arrival_date"] == datetime.datetime(2019, 4, 11)
        assert container["vgm"]          == 30260
        # Assert container movements
        movements = self.getMovements(container)
        assert len(movements) >= 1
        assert movements[0]["date"]             == datetime.datetime(2019, 3, 7)
        assert movements[0]["status"]           == "Loaded (FCL) on vessel"
        assert movements[0]["location"]         == "CALLAO (PE)"
        assert movements[0]["transport_ship"]   == "EVER LAMBENT"
        assert movements[0]["transport_voyage"] == "0403-037W"
        assert movements[0]["estimated"]        == False
    
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
        query = {
            "year": container["year"],
            "manifest": container["manifest"],
            "detail": container["detail"],
            "container": container["container"]
        }
        for movement in self.container_movements.find(query).sort("date", 1):
            movements.append(movement)
        return movements

if __name__ == "__main__":
    logging.basicConfig(filename = "tests.log", level = logging.INFO,
                        format = "[%(levelname)s %(asctime)s] %(message)s")
    unittest.main()
