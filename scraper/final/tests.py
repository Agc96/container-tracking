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
    
    def OKAY_test_1_HapagLloyd(self):
        container = {
            "year": "2019",
            "manifest": "TEST",
            "detail": "1",
            "container": "FSCU5670046",
            "carrier": "Hapag-Lloyd"
        }
        self.executeTest(container)
        # Assert container information
        assert container["description"]   == "REEFER CONTAINER"
        assert container["last_status"]   == "container departed"
        assert container["last_location"] == "NORFOLK, VA"
        assert container["last_date"]     == datetime.datetime(2019, 4, 9)
        # Assert container movements
        movements = self.getMovements(container)
        assert len(movements) >= 7
        # Assert container movement #1
        assert movements[0]["date"]             == datetime.datetime(2019, 3, 12, 7, 33)
        assert movements[0]["status"]           == "Gate out empty"
        assert movements[0]["location"]         == "ANTWERP"
        assert movements[0]["transport_type"]   == "Truck"
        assert movements[0]["estimated"]        == False
        # Assert container movement #2
        assert movements[1]["date"]             == datetime.datetime(2019, 3, 12, 14, 37)
        assert movements[1]["status"]           == "Arrival in"
        assert movements[1]["location"]         == "ANTWERP"
        assert movements[1]["transport_type"]   == "Truck"
        assert movements[1]["estimated"]        == False
        # Assert container movement #3
        assert movements[2]["date"]             == datetime.datetime(2019, 3, 26, 12, 59)
        assert movements[2]["status"]           == "Loaded"
        assert movements[2]["location"]         == "ANTWERP"
        assert movements[2]["transport_ship"]   == "YM EXPRESS"
        assert movements[2]["transport_voyage"] == "038W"
        assert movements[2]["transport_type"]   == "Vessel"
        assert movements[2]["estimated"]        == False
        # Assert container movement #4
        assert movements[3]["date"]             == datetime.datetime(2019, 3, 26, 21, 54)
        assert movements[3]["status"]           == "Vessel departed"
        assert movements[3]["location"]         == "ANTWERP"
        assert movements[3]["transport_ship"]   == "YM EXPRESS"
        assert movements[3]["transport_voyage"] == "038W"
        assert movements[3]["transport_type"]   == "Vessel"
        assert movements[3]["estimated"]        == False
        # Assert container movement #5
        assert movements[4]["date"]             == datetime.datetime(2019, 4, 7, 3, 30)
        assert movements[4]["status"]           == "Vessel arrived"
        assert movements[4]["location"]         == "NORFOLK, VA"
        assert movements[4]["transport_type"]   == "Vessel"
        assert movements[4]["transport_ship"]   == "YM EXPRESS"
        assert movements[4]["transport_voyage"] == "038W"
        assert movements[4]["estimated"]        == False
        # Assert container movement #6
        assert movements[5]["date"]             == datetime.datetime(2019, 4, 7, 9, 25)
        assert movements[5]["status"]           == "Discharged"
        assert movements[5]["location"]         == "NORFOLK, VA"
        assert movements[5]["transport_type"]   == "Vessel"
        assert movements[5]["transport_ship"]   == "YM EXPRESS"
        assert movements[5]["transport_voyage"] == "038W"
        assert movements[5]["estimated"]        == False
        # Assert container movement #7
        assert movements[6]["date"]             == datetime.datetime(2019, 4, 9, 16, 49)
        assert movements[6]["status"]           == "Departure from"
        assert movements[6]["location"]         == "NORFOLK, VA"
        assert movements[6]["transport_type"]   == "Truck"
        assert movements[6]["estimated"]        == False
    
    def OKAY_test_2_Maersk(self):
        container = {
            "year": "2019",
            "manifest": "TEST",
            "detail": "3",
            "container": "MRKU5264777",
            "carrier": "Maersk"
        }
        self.executeTest(container)
        # Assert container information
        assert container["description"]   == "40ft Dry Container"
        assert container["last_status"]   == "Gate out"
        assert container["last_location"] == "Callao, Peru"
        assert container["last_date"]     == datetime.datetime(2019, 4, 6)
        # Assert container movements
        movements = self.getMovements(container)
        assert len(movements) >= 9
        # Assert container movement #1
        assert movements[0]["date"]              == datetime.datetime(2019, 2, 12, 18, 32)
        assert movements[0]["location"]          == "Cogent Container Depot (M) Sdn Bhd\nPort Klang, Selangor, Malaysia"
        assert movements[0]["status"]            == "Gate out"
        assert movements[0]["transport_type"]    == "Truck"
        assert movements[0]["estimated"]         == False
        # Assert container movement #2
        assert movements[1]["date"]              == datetime.datetime(2019, 2, 13, 21, 35)
        assert movements[1]["location"]          == "Westport\nPort Klang, Selangor, Malaysia"
        assert movements[1]["status"]            == "Gate in"
        assert movements[1]["transport_type"]    == "Truck"
        assert movements[1]["estimated"]         == False
        # Assert container movement #3
        assert movements[2]["date"]              == datetime.datetime(2019, 2, 15, 1, 13)
        assert movements[2]["location"]          == "Westport\nPort Klang, Selangor, Malaysia"
        assert movements[2]["status"]            == "Load"
        assert movements[2]["transport_ship"]    == "OOCL HAMBURG"
        assert movements[2]["transport_voyage"]  == "108E"
        assert movements[2]["transport_type"]    == "Vessel"
        assert movements[2]["estimated"]         == False
        # Assert container movement #4
        assert movements[3]["date"]              == datetime.datetime(2019, 2, 21, 2, 57)
        assert movements[3]["location"]          == "Hongkong/Hk International Terminals\nHong Kong, Hong Kong"
        assert movements[3]["status"]            == "Discharge"
        assert movements[3]["transport_type"]    == "Vessel"
        assert movements[3]["estimated"]         == False
        # Assert container movement #5
        assert movements[4]["date"]              == datetime.datetime(2019, 2, 24, 15, 17)
        assert movements[4]["location"]          == "Hongkong/Hk International Terminals\nHong Kong, Hong Kong"
        assert movements[4]["status"]            == "Gate out"
        assert movements[4]["transport_type"]    == "Truck"
        assert movements[4]["estimated"]         == False
        # Assert container movement #6
        assert movements[5]["date"]              == datetime.datetime(2019, 2, 24, 15, 29)
        assert movements[5]["location"]          == "Hong Kong Modern Terminals Ltd\nHong Kong, Hong Kong"
        assert movements[5]["status"]            == "Gate in"
        assert movements[5]["transport_type"]    == "Truck"
        assert movements[5]["estimated"]         == False
        # Assert container movement #7
        assert movements[6]["date"]              == datetime.datetime(2019, 3, 5, 15, 51)
        assert movements[6]["location"]          == "Hong Kong Modern Terminals Ltd\nHong Kong, Hong Kong"
        assert movements[6]["status"]            == "Load"
        assert movements[6]["transport_ship"]    == "CHASTINE MAERSK"
        assert movements[6]["transport_voyage"]  == "908E"
        assert movements[6]["transport_type"]    == "Vessel"
        assert movements[6]["estimated"]         == False
        # Assert container movement #8
        assert movements[7]["date"]              == datetime.datetime(2019, 4, 5, 23, 29)
        assert movements[7]["location"]          == "APM Terminals in Callao Port\nCallao, Peru"
        assert movements[7]["status"]            == "Discharge"
        assert movements[7]["transport_type"]    == "Vessel"
        assert movements[7]["estimated"]         == False
        # Assert container movement #9
        assert movements[8]["date"]              == datetime.datetime(2019, 4, 6, 14, 11)
        assert movements[8]["location"]          == "APM Terminals in Callao Port\nCallao, Peru"
        assert movements[8]["status"]            == "Gate out"
        assert movements[8]["transport_type"]    == "Truck"
        assert movements[8]["estimated"]         == False
    
    def test_3_Evergreen(self):
        container = {
            "year": "2019",
            "manifest": "TEST",
            "detail": "4",
            "container": "EGSU9089973",
            "carrier": "Evergreen"
        }
        self.executeTest(container)
        # Assert container information
        assert container["description"]    == "40'(SH)"
        assert container["last_status"]    == "Despatched by barge"
        assert container["last_location"]  == "HONG KONG (HK)"
        assert container["last_date"]      == datetime.datetime(2019, 4, 10)
        # Assert container movements
        movements = self.getMovements(container)
        assert len(movements) >= 2
		# Assert container movement #1
        assert movements[0]["date"]             == datetime.datetime(2019, 3, 7)
        assert movements[0]["location"]         == "CALLAO (PE)"
        assert movements[0]["status"]           == "Loaded (FCL) on vessel"
        assert movements[0]["transport_ship"]   == "EVER LAMBENT"
        assert movements[0]["transport_voyage"] == "0403-037W"
        assert movements[0]["transport_type"]   == "Vessel"
        assert movements[0]["estimated"]        == False
		# Assert container movement #2
        assert movements[1]["date"]             == datetime.datetime(2019, 4, 10)
        assert movements[1]["location"]         == "HONG KONG (HK)"
        assert movements[1]["status"]           == "Despatched by barge"
        assert movements[1]["transport_ship"]   == "EVER LAMBENT"
        assert movements[1]["transport_voyage"] == "0403-037W"
        assert movements[1]["transport_type"]   == "Vessel"
        assert movements[1]["estimated"]        == False
    
    def OKAY_test_4_Textainer(self):
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
        scraper = TrackingScraper(self.driver, self.containers, self.container_movements, container)
        assert scraper.execute() is True
    
    def getMovements(self, container):
        movements = []
        query = {
            # "year": container["year"],
            # "manifest": container["manifest"],
            # "detail": container["detail"],
            "container": container["container"]
        }
        for movement in self.container_movements.find(query).sort("date", 1):
            movements.append(movement)
        return movements

if __name__ == "__main__":
    today = datetime.datetime.now().strftime("%Y%m%d")
    logging.basicConfig(filename = "tests-" + today + ".log", level = logging.INFO,
                        format = "[%(levelname)s %(asctime)s] %(message)s")
    unittest.main()
