from config import TrackingScraperConfig
from mail import TrackingScraperEmail
from scraper import TrackingScraper

from multiprocessing import Process
from selenium.webdriver import Chrome, ChromeOptions
from pymongo import MongoClient

import datetime
import json
import logging
import os
import time

class TrackingScraperProcess():
    """Process wrapper for an automatic extraction using the Tracking Web Scraper for containers."""
    
    def __init__(self, database, carrier):
        # Initialize database
        self.database   = database
        self.containers = self.database[TrackingScraperConfig.DEFAULT_CONTAINER_TABLE]
        # Get carrier configuration
        self.carrier = carrier.split(".")[0]
        with open(carrier, "w", encoding = "UTF-8") as file:
            self.configuration = json.load(file)
        # Initialize counters
        self.total_counter = 0
        self.round_counter = 0
        self.fail_counter  = 0
        self.fail_backoff  = 1
        # Initialize driver
        self.create_driver()
    
    def execute(self):
        # Get container until no containers are found or there's an unknown exception
        start = time.time()
        while True:
            # Get container, if no container is found, finish execution
            container = self.containers.find_one({
                "carrier"   : self.carrier,
                "processed" : False
            })
            if container is None:
                self.send_mail(TrackingScraperEmail.FINISH_MESSAGE, self.total_counter)
                break
            # Extract container information with the Tracking Scraper
            if not self.execute_scraper(container):
                break
        end = time.time()
        
        # Print usage time
        print("Finished scraping carrier {}!".format(self.carrier))
        print("Total time: {} seconds. Extracted {} containers".format(end - start, self.total_counter))
    
    def execute_scraper(self, container):
        result, time = TrackingScraper(self.driver, self.database, container, self.configuration).execute()
        print("Container", container["container"], "time:", time, "seconds")

        # In case an unknown exception ocurred, finish execution
        if result is None:
            return False
        
        # In case there was an error scraping a container, restart the driver
        if result is False:
            # Add to failure count and send mail
            print("Scraper for container", container["container"], "was unsuccessful")
            self.fail_counter += 1
            self.send_mail(TrackingScraperEmail.ERROR_MESSAGE, self.fail_counter)
            # Create new driver
            self.create_driver(True)
            self.fail_backoff *= 2
            # Continue execution
            return True
        
        # In case no error was found, add to scraper count and restart failure backoff
        self.fail_backoff = 1
        self.total_counter += 1
        if self.round_counter >= TrackingScraperConfig.DEFAULT_RESTART_ROUNDS:
            self.create_driver(False)
            self.round_counter = 0
        else:
            self.round_counter += 1
        return True
    
    def create_driver(self, error = None):
        """Create or recreate the WebDriver. If error = True, take a screenshot of the page for debugging."""
        # Take screenshot if an error was found
        if error is True:
            self.screenshot()
        # Close driver if there was one open
        if error is not None:
            self.close_driver()
            time.sleep(TrackingScraperConfig.DEFAULT_FAILURE_WAIT * self.fail_backoff)
        
        # Create new webdriver
        # chromeoptions = ChromeOptions()
        # chromeoptions.headless = True
        self.driver = Chrome(executable_path = TrackingScraperConfig.DEFAULT_PATH_CHROME) # Chrome(options = chromeoptions)
        self.driver.maximize_window()
        self.driver.set_page_load_timeout(TrackingScraperConfig.DEFAULT_TIMEOUT_LONG)
    
    def close_driver(self):
        """Closes the web browser and the WebDriver."""
        try:
            self.driver.quit()
        except:
            pass # Doesn't matter
    
    def screenshot(self):
        """Take a screenshot of the current page and save its HTML content, for debugging."""
        filename = "../errors/error-{}-{}".format(self.carrier, self.fail_counter)
        # Screenshot the current page
        try:
            self.driver.save_screenshot(filename + ".png")
        except Exception as ex:
            print("Screenshot could not be taken:", str(ex))
        # Save the page's HTML content
        try:
            with open(filename + ".html", "w", encoding = "UTF-8") as file:
                file.write(self.driver.page_source)
        except Exception as ex:
            print("HTML source could not be saved:", str(ex))
    
    def send_mail(self, message, counter = None):
        """Send an email to the administrator."""
        try:
            TrackingScraperEmail(counter = counter, carrier = self.carrier).send(message)
        except Exception as ex:
            print("Could not send mail to administrator:", str(ex))
    
    def __del__(self):
        self.close_driver()


"""
This is the main process of the Tracking Scraper for Containers.
It creates a list of processes, each one scraping a container from an assigned carrier every 30 seconds.
"""

def execute_process(database, carrier):
    TrackingScraperProcess(database, carrier).execute()

if __name__ == "__main__":
    # Initialize logging
    logging.basicConfig(filename = TrackingScraperConfig.DEFAULT_LOGGING_FILE,
                        level    = TrackingScraperConfig.DEFAULT_LOGGING_LEVEL,
                        format   = TrackingScraperConfig.DEFAULT_LOGGING_FORMAT)
    # Get database
    database = MongoClient()[TrackingScraperConfig.DEFAULT_DATABASE_NAME]
    # TODO: Get carriers from the database instead of the config folder
    carriers = os.listdir()
    # Open a process for every carrier
    processes = []
    for carrier in carriers:
        p = Process(target = execute_process, args = (database, carrier))
        processes.append(p)
        p.start()
    # Wait until all processes
    for p in processes:
        p.join()
    print("Finished execution!")
