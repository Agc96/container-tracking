from switcher import TrackingScraperSwitcher
from utils import TrackingScraperError, TrackingScraperConfig

from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException

import json
import logging
import time

class TrackingScraper:
    """Main class for the Tracking Web Scraper."""
    
    def __init__(self, document):
        self.__document = document
        
        # Initialize WebDriver
        try:
            self.__driver = webdriver.Chrome(executable_path = "../driver/chromedriver")
        except WebDriverException as ex:
            raise TrackingScraperError("Error creating Selenium driver. " + str(ex))
            
        # Get configuration file
        try:
            with open("../config/" + self.__document["carrier"] + ".json") as file:
                self.__configuration = json.load(file)
        except KeyError:
            self.__driver.close()
            raise TrackingScraperError("Carrier not found")
        except FileNotFoundError:
            self.__driver.close()
            raise TrackingScraperError("Configuration file not found")
        except json.JSONDecodeError as ex:
            self.__driver.close()
            raise TrackingScraperError("Configuration file could not be read: " + str(ex))
    
    ###############################################################################################
    
    def execute(self):
        parent_result   = False
        input_result    = False
        single_result   = False
        multiple_result = False
        
        try:
            self._go_to_url()
            start = time.time()
            
            while True:
                # Check if we're still on time
                end = time.time()
                if (end - start) > TrackingScraperConfig.DEFAULT_TIMEOUT:
                    raise TrackingScraperError("Timeout exceeded, scraping was unsuccessful")
                
                # Execute input
                input_result = self._execute_input(input_result)
                if input_result is not True:
                    logging.info("Input execution was unsuccessful, retrying...")
                    continue
                
                # Execute single output
                single_result = self._execute_single_output(single_result)
                if single_result is not True:
                    logging.info("Single output execution was unsuccessful, retrying...")
                    continue
                
                # Execute multiple output
                multiple_result = self._execute_multiple_output(multiple_result)
                break
            
            # Return True if everything executed correctly
            parent_result = True
        
        # Exception handling
        except TrackingScraperError:
            logging.exception("Error occured while executing scraper")
        except Exception:
            logging.exception("Unknown exception occured")
        finally:
            self.__driver.close()
            return parent_result
    
    ###############################################################################################
    
    def _go_to_url(self):
        try:
            link = self.__configuration["general"]["url"]
            self.__driver.get(link.format(**self.__document))
            time.sleep(TrackingScraperConfig.DEFAULT_WAIT_LONG)
        except KeyError:
            raise TrackingScraperError("Configuration URL could not be found")
        except TimeoutException:
            raise TrackingScraperError("Error loading Web page, timeout exceeded")
    
    ###############################################################################################
    
    def _execute_input(self, input_result):
        # Check if input was already executed
        if input_result is True:
            return True
        
        # Get input commands, if none found, return True
        input_commands = self.__configuration["input"]
        if input_commands is None:
            return True
        
        # Process parent input commands
        for input_command in input_commands:
            result = TrackingScraperSwitcher(self.__driver, self.__document, self.__configuration,
                                             input_command).process()
            if result is not True:
                return result
        
        # Return True if everything was OK
        return True
    
    ###############################################################################################
    
    def _execute_single_output(self, single_result):
        # Check if single output was already executed
        if single_result is True:
            return True
        
        # Get output commands, if none found, return True
        single_commands = self.__configuration["single"]
        if single_commands is None:
            return True
        
        # Process parent input commands
        for single_command in single_commands:
            result = TrackingScraperSwitcher(self.__driver, self.__document, self.__configuration,
                                             single_command).process()
            if result is not True:
                return result
        
        # Return True if everything was OK
        return True
    
    def _execute_multiple_output(self, multiple_result):
        return True
