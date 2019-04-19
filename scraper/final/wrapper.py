from config import TrackingScraperConfig
from mail import TrackingScraperEmail
from scraper import TrackingScraper
from switcher import TrackingScraperSwitcher

from selenium.webdriver import Chrome
from selenium.common.exceptions import WebDriverException, NoSuchElementException
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
        self.database   = MongoClient()[TrackingScraperConfig.DEFAULT_DATABASE_NAME]
        self.containers = self.database[TrackingScraperConfig.DEFAULT_CONTAINER_TABLE]
        # TODO: Replace this with reading from config collection
        self.carriers = ["Maersk", "Hapag-Lloyd", "Evergreen", "Textainer"]
        # Initialize counters
        self.scraper_counter_total    = 0
        self.failure_counter_total    = 0
        self.scraper_counter_carriers = [0] * len(self.carriers)
        self.failure_counter_carriers = [0] * len(self.carriers)
        # Initialize driver
        self.create_driver()
        self.finish = False
    
    def execute(self):
        total_start = time.time()

        while not self.finish:
            no_containers = True
            # Extract one container for every carrier
            for index, carrier in enumerate(self.carriers):
                # Apply checkers
                check = self.check_carrier(index)
                if check is True:
                    continue
                if check is False:
                    break
                # Get container
                container = self.containers.find_one({ "carrier": carrier, "processed": False })
                if container is None:
                    continue
                # Execute scraper
                no_containers = False
                self.execute_scraper(container, index, carrier)
            # Check if we have containers left:
            if no_containers:
                self.finish = True
        
        # Print usage time
        print("Finished scraping! Will everything be OK?")
        total_end = time.time()
        print("Total time:", total_end - total_start, "seconds")
        print("Extracted", self.scraper_counter_total, "containers")
        
        # Finish execution by closing driver and sending mail
        self.send_mail(TrackingScraperEmail.FINISH_MESSAGE)
        self.close()
    
    def check_carrier(self, index):
        # Check if carrier failure counter is too much
        if self.failure_counter_carriers[index] >= TrackingScraperConfig.DEFAULT_RETRIES_CARRIER[index]:
            return True
        # Check if total failure counter is too much
        if self.failure_counter_total >= TrackingScraperConfig.DEFAULT_RETRIES_TOTAL:
            print("Too much failures in total, aborting...")
            self.finish = True
            return False
        # Check if a scraper counter for a carrier is too much
        for scraper_counter in self.scraper_counter_carriers:
            if scraper_counter >= TrackingScraperConfig.DEFAULT_RESTART_ROUNDS:
                self.create_driver(False)
                self.scraper_counter_carriers = [0] * len(self.carriers)
                break
        return None
    
    def execute_scraper(self, container, index, carrier):
        start  = time.time()
        result = TrackingScraper(self.driver, self.database, container).execute()

        # In case an unknown exception ocurred, finish execution
        if result is None:
            self.finish = True
            return False
        
        # In case there was an error scraping a container, restart the driver
        if result is False:
            # Add to failure count
            self.failure_counter_carriers[index] += 1
            self.failure_counter_total += 1
            print("Scraper for container", container["container"], "was unsuccessful.",
                  "Total failure count:", self.failure_counter_total)
            # Send mails
            self.send_mail(TrackingScraperEmail.CARRIER_MESSAGE, carrier)
            if self.failure_counter_carriers[index] >= TrackingScraperConfig.DEFAULT_RETRIES_CARRIER[index]:
                self.send_mail(TrackingScraperEmail.ERRORS_MESSAGE, self.failure_counter_total)
            # Create new driver
            self.create_driver(True)
        
        # Add to counter
        self.scraper_counter_carriers[index] += 1
        self.scraper_counter_total += 1
        
        # Print usage time
        container_time = self.get_container_time(start)
        print("Container", container["container"], "time:", container_time, "seconds")
        return True
    
    def get_container_time(self, start):
        # Wait until we've reached the timeout, to avoid saturating the servers
        end = time.time()
        while (end - start) < TrackingScraperConfig.DEFAULT_TIMEOUT_SHORT:
            time.sleep(1)
            end = time.time()
        return end - start
    
    @property
    def retries(self):
        """Number of retries left."""
        return TrackingScraperConfig.DEFAULT_RETRIES_TOTAL - self.failure_counter_total
    
    def create_driver(self, error = None):
        """Create or recreate the WebDriver. If error = True, take a screenshot of the page for debugging."""
        # Take screenshot if an error was found
        if error is True:
            self.screenshot()
        # Close driver if there was one open
        if error is not None:
            self.close()
            time.sleep(60) # Sleep for a minute
        # Create new webdriver
        self.driver = Chrome(executable_path = TrackingScraperConfig.DEFAULT_PATH_CHROME)
        self.driver.maximize_window()
        self.driver.set_page_load_timeout(TrackingScraperConfig.DEFAULT_TIMEOUT_LONG)
    
    def close(self):
        """Closes the web browser and the WebDriver."""
        try:
            self.driver.close()
        except AttributeError:
            pass # WebDriver did not exist
        except Exception as ex:
            print("WebDriver could not be closed:", str(ex))
    
    def screenshot(self):
        """Take a screenshot of the current page and save its HTML content, for debugging."""
        filename = "../errors/error_" + str(self.failure_counter_total)
        # Screenshot the current page
        try:
            self.driver.save_screenshot(filename + ".png")
        except Exception as ex:
            print("Screenshot could not be taken:", str(ex))
        # Save the page's HTML content
        try:
            with open(filename + ".html", "w") as file:
                file.write(self.driver.page_source)
        except Exception as ex:
            print("HTML source could not be saved:", str(ex))

    def send_mail(self, message, extra = None):
        """Send an email to the administrator."""
        try:
            TrackingScraperEmail(extra).send(message)
        except Exception as ex:
            print("Could not send mail to administrator:", str(ex))
    
    def __del__(self):
        self.close()

# Main execution
if __name__ == "__main__":
    TrackingScraperWrapper().execute()
