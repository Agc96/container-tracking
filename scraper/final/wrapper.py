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
        self.database = MongoClient()[TrackingScraperConfig.DEFAULT_DATABASE_NAME]
        self.containers_table = self.database[TrackingScraperConfig.DEFAULT_CONTAINER_TABLE]
        # TODO: Replace this with reading from config collection
        self.carriers = ["Maersk", "Hapag-Lloyd", "Evergreen", "Textainer"]
        # Initialize failure counters
        self.fail_counter_carrier = [False] * len(self.carriers)
        self.fail_counter_total   = 0
        # Initialize driver
        self.create_driver()
        self.finish = False
    
    def execute(self):
        total_start = time.time()

        while not self.finish:
            no_containers = True
            # Extract one container for every carrier
            for index, carrier in enumerate(self.carriers):
                # Check if carrier failure counter is too much:
                if self.fail_counter_carrier[index]:
                    continue
                # Check if total failure counter is too much
                if self.fail_counter_total >= TrackingScraperConfig.DEFAULT_RETRIES_ALL:
                    print("Too much failures in total, aborting...")
                    no_containers = False
                    self.finish = True
                    break
                # Get container
                container = self.containers_table.find_one({ "carrier": carrier, "processed": False })
                if container is None:
                    continue
                # Execute scraper
                no_containers = False
                self.execute_scraper(container, index)
            # Check if we have containers left:
            if no_containers:
                print("Finished scraping! Will everything be OK?")
                self.finish = True
        
        total_end = time.time() 
        print("Total time:", total_end - total_start, "seconds")

        # Finish execution by closing driver and sending mail
        self.send_mail(TrackingScraperEmail.FINISH_MESSAGE)
        self.close()
    
    def execute_scraper(self, container, index):
        container_start = time.time()
        result = TrackingScraper(self.driver, self.database, container).execute()

        # In case an unknown exception ocurred, finish execution
        if result is None:
            self.finish = True
            return False
        
        # In case there was an error scraping a container, restart the driver
        if result is False:
            # Add to failure count
            self.fail_counter_carrier[index] = True
            self.fail_counter_total += 1
            print("Scraper for container", container["container"], "was unsuccessful.",
                  "Total failure count:", self.fail_counter_total)
            # Create new driver
            self.create_driver(True)
        
        # Calculate time
        container_end = time.time()
        while (time.time() - container_start) < TrackingScraperConfig.DEFAULT_TIMEOUT_SHORT:
            time.sleep(1)
        # Print container time
        print("Container", container["container"], "time:", container_end - container_start, "seconds")
        return True
    
    def retries(self):
        """Get the number of retries left."""
        return TrackingScraperConfig.DEFAULT_RETRIES_ALL - self.fail_counter_total
    
    def create_driver(self, error = False):
        # Take screenshot if an error was found
        if error:
            self.screenshot()
            self.close()
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
        except:
            print("WebDriver could not be closed")
    
    def screenshot(self):
        """Take a screenshot of the current page and save its HTML content, for debugging."""
        filename = "../errors/error_" + str(self.fail_counter_total)
        # Screenshot the current page
        try:
            self.driver.save_screenshot(filename + ".png")
        except Exception as ex:
            print("Screenshot could not be taken:", str(ex))
        # Save the page's HTML content
        try:
            document = self.driver.find_element_by_tag_name("html")
            with open(filename + ".html", "w") as file:
                file.write(document.get_attribute("innerHTML"))
        except NoSuchElementException:
            print("No HTML in Hapag-Lloyd error (what?)")
        except Exception as ex:
            print("HTML could not be saved:", str(ex))

    def send_mail(self, message):
        """Send an email to the administrator."""
        try:
            TrackingScraperEmail(self.fail_counter).send(message)
        except:
            print("Could not send mail to administrator")
    
    def __del__(self):
        self.close()

# Main execution
if __name__ == "__main__":
    TrackingScraperWrapper().execute()
