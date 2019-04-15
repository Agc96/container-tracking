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
        logging.basicConfig(filename = TrackingScraperConfig.DEFAULT_LOGGING_FILE,
                            level    = TrackingScraperConfig.DEFAULT_LOGGING_LEVEL,
                            format   = TrackingScraperConfig.DEFAULT_LOGGING_FORMAT)
        # Initialize database
        self.database = MongoClient()[TrackingScraperConfig.DEFAULT_DATABASE_NAME]
        self.containers_table = self.database[TrackingScraperConfig.DEFAULT_CONTAINER_TABLE]
        # TODO: Replace this with reading from config collection
        self.carriers = ["Maersk", "Hapag-Lloyd", "Evergreen", "Textainer"]
        # Initialize failure counters
        # self.failures = [0] * len(self.carriers)
        self.fail_counter = 0
        # Initialize driver
        self.driver = Chrome(executable_path = TrackingScraperConfig.DEFAULT_PATH_CHROME)
        self.driver.set_page_load_timeout(TrackingScraperConfig.DEFAULT_TIMEOUT_LONG)
    
    def execute(self):
        total_start = time.time()
        finish_execution = False
        while not finish_execution:
            no_containers = True
            # Check if total failure counter is too much
            if self.fail_counter >= TrackingScraperConfig.DEFAULT_RETRIES_ALL:
                logging.error("Too much failures in total, aborting...")
                break
            # Extract one container for every carrier
            for index, carrier in enumerate(self.carriers):
                # Check if failure counter for this carrier is too much
                # if self.failures[index] >= TrackingScraperConfig.DEFAULT_RETRIES_SINGLE:
                #     logging.warning("Too much failures in carrier %s, skipping...", carrier)
                #     continue
                # Get container
                container = self.containers_table.find_one({
                    "carrier": carrier,
                    "processed": False
                })
                if container is None: continue
                # Execute scraper
                no_containers = False
                if self.execute_scraper(container, index) is False:
                    finish_execution = True
            # Check if we have containers left:
            if no_containers:
                logging.info("Finished scraping!")
                break
        total_end = time.time() 
        print("Total time:", total_end - total_start, "seconds")
        # Finish execution by closing driver
        self.close()
    
    def execute_scraper(self, container, index):
        container_start = time.time()
        result = TrackingScraper(self.driver, self.database, container).execute()
        if result is None:
            return False
        if result is False:
            print("Scraper for container", container["container"], "was unsuccessful.",
                  self.retries(), "retries left.")
            self.fail_counter += 1
        container_end = time.time()
        while (container_end - container_start) < TrackingScraperConfig.DEFAULT_TIMEOUT:
            time.sleep(1)
            container_end = time.time()
        print("Container", container["container"], "time:", container_end - container_start,
              "seconds")
        return True
    
    def retries(self):
        """Get the number of retries left."""
        return TrackingScraperConfig.DEFAULT_RETRIES_ALL - self.fail_counter
    
    def close(self):
        try:
            self.driver.close()
        except Exception:
            pass

# Main execution
if __name__ == "__main__":
    TrackingScraperWrapper().execute()
