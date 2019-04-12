from config import TrackingScraperConfig
from exception import (TrackingScraperAssertionError, TrackingScraperSwitcherError,
                        TrackingScraperError)
from scraper import TrackingScraper
from switcher import TrackingScraperSwitcher

from selenium.webdriver import Chrome
from selenium.common.exceptions import WebDriverException
from pymongo import MongoClient

import datetime
import logging
import time

class TrackingScraperWrapper():
    """Wrapper for an automatic extraction using the Tracking Web Scraper for containers."""

    def __init__(self):
        # Initialize today
        today = datetime.datetime.now().strftime("%Y%m%d")
        logging.basicConfig(filename = "../logs/scraper-" + today + ".log",
                            level = TrackingScraperConfig.DEFAULT_LOGGING_LEVEL,
                            format = TrackingScraperConfig.DEFAULT_LOGGING_FORMAT)
        # Initialize database
        self.__database = MongoClient()[TrackingScraperConfig.DEFAULT_DATABASE_NAME]
        self.__containers_table = self.__database[TrackingScraperConfig.DEFAULT_CONTAINER_TABLE]
        # TODO: Replace this with reading from config collection
        self.__carriers = ["Maersk", "Hapag-Lloyd", "Evergreen", "Textainer"]
        # Initialize driver
        self.__driver = Chrome(executable_path = TrackingScraperConfig.DEFAULT_PATH_CHROME)
        # Initialize failure counter
        self.__fail_counter = 0
    
    def execute(self):
        total_start = time.time()
        while True:
            no_containers = True
            # Check if fail counter is too much
            if self.__fail_counter >= TrackingScraperConfig.DEFAULT_RETRIES:
                logging.error("Too much failures, aborting")
                break
            # Extract one container for every carrier
            for carrier in self.__carriers:
                # Get container
                container = self.__containers_table.find_one({
                    "carrier": carrier,
                    "processed": False
                })
                if container is None:
                    continue
                else:
                    no_containers = False
                print("CONTAINER FOUND:", container)
                # Execute scraper
                container_start = time.time()
                if not self.execute_scraper(container):
                    break
                container_end = time.time()
                print("Container", container["container"], "time:", container_end - container_start,
                      "seconds")
            # Check if we have containers left:
            if no_containers:
                break
        total_end = time.time()
        print("Total time:", total_end - total_start, "seconds")
        # Finish execution by closing driver
        self.close()
    
    def execute_scraper(self, container):
        try:
            result = TrackingScraper(self.__driver, self.__database, container).execute()
            if not result:
                logging.error("Scraper for container %s was unsuccessful", container["container"])
            return True
        # Check assertions
        except TrackingScraperAssertionError as ex:
            logging.error(str(ex))
            if ex.assertion_type:
                self.__fail_counter += 1
                logging.error("Assertion for crucial elements failed! %d retrys left.", self.retries)
            else:
                logging.warning("Assertion for failure elements failed...")
            return True
        # Check switcher errors
        except TrackingScraperSwitcherError as ex:
            logging.error("Command: %s", TrackingScraperSwitcher.print_command(ex.command))
            logging.error(str(ex))
            return True
        # Check common errors
        except TrackingScraperError as ex:
            self.__fail_counter += 1
            logging.error("%s, %d retrys left.", str(ex), self.retries)
            return True
        except Exception:
            logging.exception("Unknown exception ocurred in scraper, aborting...")
            return False
    
    @property
    def retries(self):
        """Get the number of retries left."""
        return TrackingScraperConfig.DEFAULT_RETRIES - self.__fail_counter
    
    def close(self):
        try:
            self.__driver.close()
        except Exception:
            pass
