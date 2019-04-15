from config import TrackingScraperConfig
from mail import TrackingScraperEmail
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
        self.create_driver()
    
    def execute(self):
        total_start = time.time()
        finish_execution = False
        while not finish_execution:
            no_containers = True
            # Extract one container for every carrier
            for index, carrier in enumerate(self.carriers):
                # Check if failure counter is too much
                if self.fail_counter >= TrackingScraperConfig.DEFAULT_RETRIES_ALL:
                    logging.error("Too much failures in total, aborting...")
                    finish_execution = True
                    break
                # Check if failure counter is suspicious
                if self.fail_counter >= TrackingScraperConfig.DEFAULT_RETRIES_SINGLE:
                    logging.warning("%d failures in this run...", self.fail_counter)
                    self.send_mail(TrackingScraperEmail.ERRORS_MESSAGE)
                # Get container
                container = self.containers_table.find_one({
                    "carrier": carrier,
                    "processed": False
                })
                if container is None:
                    continue
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
        # Finish execution by closing driver and sending mail
        self.send_mail(TrackingScraperEmail.FINISH_MESSAGE)
        self.close()
    
    def execute_scraper(self, container, index):
        container_start = time.time()
        result = TrackingScraper(self.driver, self.database, container).execute()
        # Unknown exception ocurred
        if result is None:
            return False
        # Error scraping a container, restart driver
        if result is False:
            print("Scraper for container", container["container"], "was unsuccessful.",
                  "Total failure count:", self.fail_counter)
            # Create new driver
            self.create_driver(True)
            # Add to failure count
            self.fail_counter += 1
        # Calculate time
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
    
    def create_driver(self, error = False):
        # Close driver if it exists
        self.close(error)
        # Create new webdriver
        self.driver = Chrome(executable_path = TrackingScraperConfig.DEFAULT_PATH_CHROME)
        self.driver.maximize_window()
        self.driver.set_page_load_timeout(TrackingScraperConfig.DEFAULT_TIMEOUT_LONG)
    
    def close(self, error = False):
        try:
            if error:
                self.driver.save_screenshot("../errors/error_" + str(self.fail_counter) + ".png")
            self.driver.close()
        except:
            pass
    
    def send_mail(self, message):
        try:
            TrackingScraperEmail(self.fail_counter).send(message)
        except:
            print("Could not send mail to administrator")
    
    def __del__(self):
        self.close()

# Main execution
if __name__ == "__main__":
    TrackingScraperWrapper().execute()
