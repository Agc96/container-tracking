import json
import logging
import os
import shutil
import time
from multiprocessing import Process

import psycopg2
from dotenv import load_dotenv
from selenium.webdriver import Chrome, ChromeOptions

from config import ScraperConfig
from errors import ScraperError
from mail import ScraperEmail
from scraper import Scraper

class ScraperProcess():
    """Process wrapper for an automatic extraction using the Tracking Web Scraper for containers."""
    
    PENDING = 1 # Estado pendiente
    SLEEP_TIME = 60 # seconds
    MAX_BACKOFF = 128 # minutes (assuming ScraperConfig.ROUNDS_FAILURE_WAIT is 60 seconds)
    MIN_FAIL_TO_SEND_EMAIL = 5 # after 5 errors, send an email
    
    def __init__(self, carrier):
        # Get carrier configuration
        self.carrier = carrier
        with open("../config/{}.json".format(self.carrier["id"]), encoding="UTF-8") as file:
            self.config = json.load(file)
        # Get database instance
        self.database = ScraperConfig.get_database()
        # Initialize logger
        self.logger = ScraperConfig.getlogger(self.carrier["id"])
        # Initialize counters
        self.total_counter, self.round_counter, self.fail_counter, self.fail_backoff = 0, 0, 0, 1
        # Initialize driver
        self.create_driver()
    
    def execute(self):
        # Get container until no containers are found or there's an unknown exception
        start = time.time()
        while True:
            try:
                # Get container, if no container is found, finish execution
                with self.database:
                    with self.database.cursor() as cur:
                        cur.execute(""" SELECT * FROM tracking_container
                                        WHERE carrier_id = %s AND status_id IN %s
                                        ORDER BY priority
                                        LIMIT 1; """,
                                        (self.carrier["id"], (self.PENDING,)))
                        container = cur.fetchone()
                # Verify if container exists
                if container is None:
                    self.logger.info("Waiting a minute to find a container...")
                    time.sleep(self.SLEEP_TIME)
                    continue
                    # self.send_mail(ScraperEmail.FINISH_MESSAGE, self.total_counter)
                    # break
                # Extract container information with the Tracking Scraper
                if not self.execute_scraper(container):
                    break
            except KeyboardInterrupt:
                break
        end = time.time()
        
        # Print usage time
        print("Finished scraping carrier {}!".format(self.carrier["name"]))
        print("Total time: {} seconds. Extracted {} containers".format(end - start, self.total_counter))
        # Send message
        self.send_mail(ScraperEmail.FINISH_MESSAGE, self.total_counter)
    
    def execute_scraper(self, container):
        try:
            result = Scraper(self, container).execute()
        except:
            self.logger.exception("Unknown exception ocurred in scraper")
            return False
        print("Container {} extracted in {} seconds.".format(container['code'], result[1]))
        
        # In case an unknown exception ocurred, finish execution
        if result[0] is None:
            return False
        
        # In case there was an error scraping a container, restart the driver
        if result[0] is False:
            # Add to failure count
            print("Scraper for container {} was unsuccessful".format(container['code']))
            self.fail_counter += 1
            # Create new driver
            self.create_driver(True)
            if self.fail_backoff <= self.MAX_BACKOFF:
                self.fail_backoff *= 2
            # Continue execution
            return True
        
        # In case no error was found, add to scraper count and restart failure backoff
        self.fail_backoff = 1
        self.total_counter += 1
        self.round_counter += 1
        if self.round_counter >= ScraperConfig.ROUNDS_RESTART:
            self.create_driver(False)
            self.round_counter = 0
        return True
    
    def create_driver(self, error = None):
        """Create or recreate the WebDriver. If error = True, take a screenshot of the page for debugging."""
        # Send mail and take screenshot if an error was found
        if error is True:
            if self.fail_counter >= self.MIN_FAIL_TO_SEND_EMAIL:
                self.send_mail(ScraperEmail.ERROR_MESSAGE, self.fail_counter)
            self.screenshot()
            self.save_ocr_image()
        # Close driver if there was one open
        if error is not None:
            self.close_driver()
            time.sleep(ScraperConfig.ROUNDS_FAILURE_WAIT * self.fail_backoff)
        
        # Create new webdriver
        options = ChromeOptions()
        try:
            options.headless = True
        except:
            options.set_headless(True)
        self.driver = Chrome(executable_path=ScraperConfig.PATH_CHROME, options=options)
        self.driver.maximize_window()
        self.driver.set_page_load_timeout(ScraperConfig.DEFAULT_TIMEOUT_LONG)
    
    def close_driver(self):
        """Closes the web browser and the WebDriver."""
        try:
            self.driver.quit()
        except:
            pass # Doesn't matter
    
    def screenshot(self):
        """Take a screenshot of the current page and save its HTML content, for debugging."""
        filename = "../errors/error-{}-{}".format(self.carrier["id"], self.fail_counter)
        # Screenshot the current page
        try:
            self.driver.save_screenshot(filename + ".png")
        except Exception as ex:
            print("Screenshot could not be taken:", str(ex))
        # Save the page's HTML content
        try:
            with open(filename + ".html", "w", encoding="UTF-8") as file:
                file.write(self.driver.page_source)
        except Exception as ex:
            print("HTML source could not be saved:", str(ex))
    
    def send_mail(self, message, counter = None):
        """Send an email to the administrator."""
        try:
            ScraperEmail(counter=counter, carrier=self.carrier["name"]).send(message)
        except Exception as ex:
            print("Could not send mail to administrator:", str(ex))
    
    def save_ocr_image(self):
        source = "image-{}.png".format(self.carrier["id"])
        dest   = "../errors/error-{}-{}-ocr.png".format(self.carrier["id"], self.fail_counter)
        if os.path.exists(source):
            shutil.copyfile(source, dest)
    
    def __del__(self):
        self.close_driver()
        self.database.close()

"""
This is the main process of the Tracking Scraper for Containers.
It creates a list of processes, each one scraping a container from an assigned carrier every 30 seconds.
"""

def execute_process(carrier):
    ScraperProcess(carrier).execute()

if __name__ == "__main__":
    load_dotenv()
    # Get carriers from database
    with ScraperConfig.get_database() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM tracking_enterprise WHERE carrier = true;")
            carriers = cur.fetchall()
    conn.close()
    # Open a process for every carrier
    processes = []
    for carrier in carriers:
        p = Process(target = execute_process, args = (carrier,))
        processes.append(p)
        p.start()
    # Wait until all processes finish
    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        for p in processes:
            p.join()
    print("Finished execution!")
