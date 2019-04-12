from config import TrackingScraperConfig
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
        # Initialize logging
        logging.basicConfig(filename = "../logs/scraper-" + datetime.datetime.now().strftime("%Y%m%d") + ".log",
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
        finish_execution = False
        while not finish_execution:
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
                # Execute scraper
                no_containers = False
                if self.execute_scraper(container) is False:
                    finish_execution = True
            # Check if we have containers left:
            if no_containers:
                break
        total_end = time.time() 
        print("Total time:", total_end - total_start, "seconds")
        # Finish execution by closing driver
        self.close()
    
    def execute_scraper(self, container):
        container_start = time.time()
        result = TrackingScraper(self.__driver, self.__database, container).execute()
        if result is None:
            return False
        if result is False:
            print("Scraper for container", container["container"], "was unsuccessful.",
                  self.retries, "retries left.")
            self.__fail_counter += 1
        container_end = time.time()
        while (container_end - container_start) < TrackingScraperConfig.DEFAULT_TIMEOUT:
            time.sleep(1)
            container_end = time.time()
        print("Container", container["container"], "time:", container_end - container_start,
              "seconds")
        return True
    
    @property
    def retries(self):
        """Get the number of retries left."""
        return TrackingScraperConfig.DEFAULT_RETRIES - self.__fail_counter
    
    def close(self):
        try:
            self.__driver.close()
        except Exception:
            pass
