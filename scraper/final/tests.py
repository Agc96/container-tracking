from config import TrackingScraperConfig
from scraper import TrackingScraper

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
from datetime import datetime

import logging
import unittest

class TrackingScraperTestCase(unittest.TestCase):
    """Unit tests for the Tracking Scraper class."""
    
    def setUp(self):
        options = Options()
        options.add_argument("--start-maximized")
        self.driver = WebDriver(executable_path = TrackingScraperConfig.DEFAULT_PATH_CHROME, options = options)
        self.database = MongoClient()[TrackingScraperConfig.DEFAULT_DATABASE_NAME]
        self.container_movements = self.database[TrackingScraperConfig.DEFAULT_MOVEMENT_TABLE]
    
    def tearDown(self):
        self.driver.close()
    
    def test_1_HapagLloyd(self):
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
        assert container["last_date"]     == datetime(2019, 4, 9)
        # Assert container movements
        movements = self.getMovements(container)
        assert len(movements) >= 7
        # Assert container movement #1
        assert movements[0]["date"]             == datetime(2019, 3, 12, 7, 33)
        assert movements[0]["status"]           == "Gate out empty"
        assert movements[0]["status_code"]      == 1
        assert movements[0]["location"]         == "ANTWERP"
        assert movements[0]["latitude"]         == 51.2211097
        assert movements[0]["longitude"]        == 4.3997081
        assert movements[0]["transport_type"]   == "Truck"
        assert movements[0]["estimated"]        == False
        # Assert container movement #2
        assert movements[1]["date"]             == datetime(2019, 3, 12, 14, 37)
        assert movements[1]["status"]           == "Arrival in"
        assert movements[0]["status_code"]      == 2
        assert movements[1]["location"]         == "ANTWERP"
        assert movements[1]["latitude"]         == 51.2211097
        assert movements[1]["longitude"]        == 4.3997081
        assert movements[1]["transport_type"]   == "Truck"
        assert movements[1]["estimated"]        == False
        # Assert container movement #3
        assert movements[2]["date"]             == datetime(2019, 3, 26, 12, 59)
        assert movements[2]["status"]           == "Loaded"
        assert movements[0]["status_code"]      == 3
        assert movements[2]["location"]         == "ANTWERP"
        assert movements[2]["latitude"]         == 51.2211097
        assert movements[2]["longitude"]        == 4.3997081
        assert movements[2]["transport_ship"]   == "YM EXPRESS"
        assert movements[2]["transport_voyage"] == "038W"
        assert movements[2]["transport_type"]   == "Vessel"
        assert movements[2]["estimated"]        == False
        # Assert container movement #4
        assert movements[3]["date"]             == datetime(2019, 3, 26, 21, 54)
        assert movements[3]["status"]           == "Vessel departed"
        assert movements[0]["status_code"]      == 4
        assert movements[3]["location"]         == "ANTWERP"
        assert movements[3]["latitude"]         == 51.2211097
        assert movements[3]["longitude"]        == 4.3997081
        assert movements[3]["transport_ship"]   == "YM EXPRESS"
        assert movements[3]["transport_voyage"] == "038W"
        assert movements[3]["transport_type"]   == "Vessel"
        assert movements[3]["estimated"]        == False
        # Assert container movement #5
        assert movements[4]["date"]             == datetime(2019, 4, 7, 3, 30)
        assert movements[4]["status"]           == "Vessel arrived"
        assert movements[0]["status_code"]      == 5
        assert movements[4]["location"]         == "NORFOLK, VA"
        assert movements[4]["latitude"]         == 36.8462923
        assert movements[4]["longitude"]        == -76.2929252
        assert movements[4]["transport_type"]   == "Vessel"
        assert movements[4]["transport_ship"]   == "YM EXPRESS"
        assert movements[4]["transport_voyage"] == "038W"
        assert movements[4]["estimated"]        == False
        # Assert container movement #6
        assert movements[5]["date"]             == datetime(2019, 4, 7, 9, 25)
        assert movements[5]["status"]           == "Discharged"
        assert movements[0]["status_code"]      == 7
        assert movements[5]["location"]         == "NORFOLK, VA"
        assert movements[5]["latitude"]         == 36.8462923
        assert movements[5]["longitude"]        == -76.2929252
        assert movements[5]["transport_type"]   == "Vessel"
        assert movements[5]["transport_ship"]   == "YM EXPRESS"
        assert movements[5]["transport_voyage"] == "038W"
        assert movements[5]["estimated"]        == False
        # Assert container movement #7
        assert movements[6]["date"]             == datetime(2019, 4, 9, 16, 49)
        assert movements[6]["status"]           == "Departure from"
        assert movements[0]["status_code"]      == 0
        assert movements[6]["location"]         == "NORFOLK, VA"
        assert movements[6]["latitude"]         == 36.8462923
        assert movements[6]["longitude"]        == -76.2929252
        assert movements[6]["transport_type"]   == "Truck"
        assert movements[6]["estimated"]        == False
        # Assert container movement #8
        assert movements[7]["date"]             == datetime(2019, 4, 11, 12, 30)
        assert movements[7]["status"]           == "Gate in empty"
        assert movements[7]["status_code"]      == 0
        assert movements[7]["location"]         == "NORFOLK, VA"
        assert movements[7]["latitude"]         == 36.8462923
        assert movements[7]["longitude"]        == -76.2929252
        assert movements[7]["transport_type"]   == "Truck"
        assert movements[7]["estimated"]        == False
    
    def test_2_Maersk(self):
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
        assert container["last_date"]     == datetime(2019, 4, 6)
        # Assert container movements
        movements = self.getMovements(container)
        assert len(movements) >= 9
        # Assert container movement #1
        assert movements[0]["date"]             == datetime(2019, 2, 12, 18, 32)
        assert movements[0]["location"]         == "Cogent Container Depot (M) Sdn Bhd\nPort Klang, Selangor, Malaysia"
        assert movements[0]["latitude"]         == 3.0027625
        assert movements[0]["longitude"]        == 101.3966735
        assert movements[0]["status"]           == "Empty"
        assert movements[0]["transport_type"]   == "Truck"
        assert movements[0]["estimated"]        == False
        # Assert container movement #2
        assert movements[1]["date"]             == datetime(2019, 2, 13, 21, 35)
        assert movements[1]["location"]         == "Westport\nPort Klang, Selangor, Malaysia"
        assert movements[1]["latitude"]         == 3.0027625
        assert movements[1]["longitude"]        == 101.3966735
        assert movements[1]["status"]           == "Gate in"
        assert movements[1]["transport_type"]   == "Truck"
        assert movements[1]["estimated"]        == False
        # Assert container movement #3
        assert movements[2]["date"]             == datetime(2019, 2, 15, 1, 13)
        assert movements[2]["location"]         == "Westport\nPort Klang, Selangor, Malaysia"
        assert movements[2]["latitude"]         == 3.0027625
        assert movements[2]["longitude"]        == 101.3966735
        assert movements[2]["status"]           == "Load"
        assert movements[2]["transport_ship"]   == "OOCL HAMBURG"
        assert movements[2]["transport_voyage"] == "108E"
        assert movements[2]["transport_type"]   == "Vessel"
        assert movements[2]["estimated"]        == False
        # Assert container movement #4
        assert movements[3]["date"]             == datetime(2019, 2, 21, 2, 57)
        assert movements[3]["location"]         == "Hongkong/Hk International Terminals\nHong Kong, Hong Kong"
        assert movements[3]["latitude"]         == 22.350627
        assert movements[3]["longitude"]        == 114.1849161
        assert movements[3]["status"]           == "Discharge"
        assert movements[3]["transport_type"]   == "Vessel"
        assert movements[3]["estimated"]        == False
        # Assert container movement #5
        assert movements[4]["date"]             == datetime(2019, 2, 24, 15, 17)
        assert movements[4]["location"]         == "Hongkong/Hk International Terminals\nHong Kong, Hong Kong"
        assert movements[4]["latitude"]         == 22.350627
        assert movements[4]["longitude"]        == 114.1849161
        assert movements[4]["status"]           == "Gate out"
        assert movements[4]["transport_type"]   == "Truck"
        assert movements[4]["estimated"]        == False
        # Assert container movement #6
        assert movements[5]["date"]             == datetime(2019, 2, 24, 15, 29)
        assert movements[5]["location"]         == "Hong Kong Modern Terminals Ltd\nHong Kong, Hong Kong"
        assert movements[5]["latitude"]         == 22.350627
        assert movements[5]["longitude"]        == 114.1849161
        assert movements[5]["status"]           == "Gate in"
        assert movements[5]["transport_type"]   == "Truck"
        assert movements[5]["estimated"]        == False
        # Assert container movement #7
        assert movements[6]["date"]             == datetime(2019, 3, 5, 15, 51)
        assert movements[6]["location"]         == "Hong Kong Modern Terminals Ltd\nHong Kong, Hong Kong"
        assert movements[6]["latitude"]         == 22.350627
        assert movements[6]["longitude"]        == 114.1849161
        assert movements[6]["status"]           == "Load"
        assert movements[6]["transport_ship"]   == "CHASTINE MAERSK"
        assert movements[6]["transport_voyage"] == "908E"
        assert movements[6]["transport_type"]   == "Vessel"
        assert movements[6]["estimated"]        == False
        # Assert container movement #8
        assert movements[7]["date"]             == datetime(2019, 4, 5, 23, 29)
        assert movements[7]["location"]         == "APM Terminals in Callao Port\nCallao, Peru"
        assert movements[7]["latitude"]         == -12.066667
        assert movements[7]["longitude"]        == -77.15
        assert movements[7]["status"]           == "Discharge"
        assert movements[7]["transport_type"]   == "Vessel"
        assert movements[7]["estimated"]        == False
        # Assert container movement #9
        assert movements[8]["date"]             == datetime(2019, 4, 6, 14, 11)
        assert movements[8]["location"]         == "APM Terminals in Callao Port\nCallao, Peru"
        assert movements[8]["latitude"]         == -12.066667
        assert movements[8]["longitude"]        == -77.15
        assert movements[8]["status"]           == "Gate out"
        assert movements[8]["transport_type"]   == "Truck"
        assert movements[8]["estimated"]        == False
    
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
        assert container["last_status"]    == "Discharged (FCL)"
        assert container["last_location"]  == "HUANGPU, GUANGDONG (CN)"
        assert container["last_date"]      == datetime(2019, 4, 11)
        # Assert container movements
        movements = self.getMovements(container)
        assert len(movements) >= 3
		# Assert container movement #1
        assert movements[0]["date"]             == datetime(2019, 3, 7)
        assert movements[0]["location"]         == "CALLAO (PE)"
        assert movements[0]["latitude"]         == -12.066667
        assert movements[0]["longitude"]        == -77.15
        assert movements[0]["status"]           == "Loaded (FCL) on vessel"
        assert movements[0]["transport_ship"]   == "EVER LAMBENT"
        assert movements[0]["transport_voyage"] == "0403-037W"
        assert movements[0]["transport_type"]   == "Vessel"
        assert movements[0]["estimated"]        == False
		# Assert container movement #2
        assert movements[1]["date"]             == datetime(2019, 4, 10)
        assert movements[1]["location"]         == "HONG KONG (HK)"
        assert movements[1]["latitude"]         == 22.350627
        assert movements[1]["longitude"]        == 114.1849161
        assert movements[1]["status"]           == "Despatched by barge"
        assert movements[1]["transport_ship"]   == "EVER LAMBENT"
        assert movements[1]["transport_voyage"] == "0403-037W"
        assert movements[1]["transport_type"]   == "Vessel"
        assert movements[1]["estimated"]        == False
        # Assert container movement #3
        assert movements[2]["date"]             == datetime(2019, 4, 11)
        assert movements[2]["location"]         == "HUANGPU, GUANGDONG (CN)"
        assert movements[2]["location"]         == 23.1824507
        assert movements[2]["longitude"]        == 113.4760861
        assert movements[2]["status"]           == "Discharged (FCL)"
        assert movements[2]["transport_ship"]   == "EVER LAMBENT"
        assert movements[2]["transport_voyage"] == "0403-037W"
        assert movements[2]["transport_type"]   == "Vessel"
        assert movements[2]["estimated"]        == False
    
    def test_4_Textainer(self):
        container = {
            "year": "2019",
            "manifest": "TEST",
            "detail": "5",
            "container": "TEMU3806660",
            "carrier": "Textainer"
        }
        self.executeTest(container)
        # Assert container information
        assert container["carrier"] == "Maersk"
    
    def executeTest(self, container):
        scraper = TrackingScraper(self.driver, self.database, container)
        assert scraper.execute() is True, "Scraper execution failed, check log for details."
    
    def getMovements(self, container):
        movements = []
        query = {
            "container": container["container"]
        }
        for movement in self.container_movements.find(query).sort("date", 1):
            movements.append(movement)
        return movements

if __name__ == "__main__":
    logging.basicConfig(filename = "tests-" + datetime.now().strftime("%Y%m%d") + ".log",
                        level = TrackingScraperConfig.DEFAULT_LOGGING_LEVEL,
                        format = TrackingScraperConfig.DEFAULT_LOGGING_FORMAT)
    unittest.main()
