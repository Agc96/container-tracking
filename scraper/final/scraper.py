from config import TrackingScraperConfig
from errors import (TrackingScraperAssertionError, TrackingScraperTimeoutError,
                    TrackingScraperSwitcherError, TrackingScraperError)
from switcher import TrackingScraperSwitcher

from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException

import datetime
import json
import logging
import time

class TrackingScraper:
    """Main class for the Tracking Web Scraper."""
    
    def __init__(self, driver, database, container):
        self.__driver          = driver
        self.__database        = database
        self.__container_table = database[TrackingScraperConfig.DEFAULT_CONTAINER_TABLE]
        self.__movement_table  = database[TrackingScraperConfig.DEFAULT_MOVEMENT_TABLE]
        self.__container       = container
        
        # Get configuration file
        try:
            with open("../config/" + self.__container["carrier"] + ".json", encoding = "UTF-8") as file:
                self.__configuration = json.load(file)
        except KeyError:
            raise TrackingScraperError("Carrier not found")
        except FileNotFoundError:
            raise TrackingScraperError("Configuration file not found")
        
        # Check if general configuration exists
        if "general" not in self.__configuration:
            raise TrackingScraperError("General configuration information not found")
    
    @property
    def container(self):
        """Returns the container information."""
        return self.__container
    
    ###############################################################################################
    
    def execute(self):
        """Execute commands."""
        
        input_result    = False
        single_result   = False
        multiple_result = False
        try:
            start = self._go_to_url()
            while True:
                # Check if we're still on time
                end = time.time()
                if (end - start) > TrackingScraperConfig.DEFAULT_TIMEOUT_LONG:
                    raise TrackingScraperTimeoutError(True)
                # Execute input
                input_result = self._execute_commands(input_result, "input")
                if input_result is not True:
                    logging.info("Input execution was unsuccessful, retrying...")
                    continue
                # Execute single output
                single_result = self._execute_commands(single_result, "single")
                if single_result is not True:
                    logging.info("Single output execution was unsuccessful, retrying...")
                    continue
                # Execute multiple output
                multiple_result = self._execute_multiple_output(multiple_result)
                if multiple_result is not True:
                    logging.info("Multiple output execution was unsuccessful, retrying...")
                    continue
                # Finish execution and save elements
                self._finish_execution()
                time.sleep(TrackingScraperConfig.DEFAULT_WAIT_SHORT)
                break
            return True
        # Check assertions
        except TrackingScraperAssertionError as ex:
            logging.warning(str(ex))
            if ex.assertion_type is False:
                return self._finish_execution()
            return False
        # Check timeout errors
        except TrackingScraperTimeoutError as ex:
            logging.error(str(ex))
            return False
        # Check switcher errors
        except TrackingScraperSwitcherError as ex:
            logging.error("Command: %s", TrackingScraperSwitcher.print_command(ex.command))
            logging.error(str(ex))
            return False
        # Check common errors
        except TrackingScraperError as ex:
            logging.error(str(ex))
            return False
        except Exception:
            logging.exception("Unknown exception ocurred in scraper")
            return None
    
    ###############################################################################################
    
    def _go_to_url(self):
        # Check if general configuration is declared
        general_config = self.__configuration.get("general")
        if general_config is None:
            raise TrackingScraperError("Configuration information not found")
        
        # Get configuration URL
        link = self.__configuration["general"].get("url")
        if link is None:
            raise TrackingScraperError("Configuration URL could not be found")
        
        # Go to desired URL
        try:
            self.__driver.get(link.format(**self.__container))
            time.sleep(TrackingScraperConfig.DEFAULT_WAIT_LONG)
        except TimeoutException:
            raise TrackingScraperTimeoutError(False)
        
        # Check if page is a Chrome error
        chrome_error = self.__driver.find_elements_by_id("main-frame-error")
        if len(chrome_error) > 0:
            logging.error("Chrome error detected: %s", chrome_error[0].text)
            raise TrackingScraperTimeoutError(False)
        
        # Start time counting
        return time.time()
    
    ###############################################################################################
    
    def _execute_commands(self, parent_result, key):
        # Check if commands were already executed
        if parent_result is True:
            return True
        
        # Get commands, if none found, return True
        commands = self.__configuration.get(key)
        if commands is None:
            return True
        
        # Process commands
        for command in commands:
            result = TrackingScraperSwitcher(self.__driver, self.__container, self.__configuration,
                                             command).process()
            if result is not True:
                return False
        
        # Return True if everything was OK
        return True
    
    ###############################################################################################
    
    def _execute_multiple_output(self, multiple_result):
        if multiple_result is True:
            return True
        
        # Get multiple command, if none found, return True
        multiple_command = self.__configuration.get("multiple")
        if multiple_command is None:
            return True
        
        # Get configuration key
        multiple_configuration = self.__configuration["general"].get("multiple")
        if multiple_configuration is None:
            return True
        
        # Create multiple document based on configuration file
        multiple_document = dict(multiple_configuration)
        for key in TrackingScraperConfig.DEFAULT_CONTAINER_COPY:
            multiple_document[key] = self.__container[key]
        
        # Generate and process multiple documents
        return self.__process_multiple_elements(multiple_command, multiple_document, self.__driver)
    
    def __process_multiple_elements(self, multiple_command, multiple_document, previous_element):
        # Get single subcommands
        multiple_single_commands = multiple_command.get("single")
        if not isinstance(multiple_single_commands, list):
            raise TrackingScraperError("Multiple command must have single commands key")
        
        # Get command to find parents, if none found, use driver to extract single commands
        multiple_parents = multiple_command.get("parents")
        if multiple_parents is None:
            multiple_elements = [previous_element]
        else:
            multiple_elements = TrackingScraperSwitcher(self.__driver, {}, self.__configuration,
                                                        multiple_parents, previous_element).process()
            if multiple_elements is False:
                return True # No elements found
            if multiple_elements is True:
                raise TrackingScraperError("Parent elements must be a list of web elements")
        
        # Get multiple subcomamnd
        multiple_multiple_command = multiple_command.get("multiple")
        
        # Process every single command for every multiple element
        for multiple_subelement in multiple_elements:
            subdocument = dict(multiple_document)
            for single_command in multiple_single_commands:
                single_result = TrackingScraperSwitcher(self.__driver, subdocument,
                                                        self.__configuration, single_command,
                                                        multiple_subelement).process()
                if single_result is not True:
                    logging.info("Multiple: single subcommand failed")
                    return False
            
            # Check if multiple subcommand exists, if it doesn't, save and continue.
            if multiple_multiple_command is None:
                self._insert_or_update(subdocument, self.__movement_table,
                                       TrackingScraperConfig.DEFAULT_MOVEMENT_QUERY)
                continue
            
            # If it exists, copy result document and iterate these new multiple elements with it
            multiple_result = self.__process_multiple_elements(multiple_multiple_command,
                                                               subdocument, multiple_subelement)
            if multiple_result is not True:
                logging.info("Multiple: multiple subcommand failed")
                return False
        
        # Return True to notify everything is OK
        return True
    
    ###############################################################################################
    
    def _finish_execution(self):
        # Get configuration for single element
        single_config = self.__configuration["general"].get("single")
        if single_config is None:
            return True
        
        # Get processed value to save
        processed_value = single_config.get("processed", TrackingScraperConfig.DEFAULT_KEY_PROCESSED)
        self.__container["processed"] = processed_value
        
        # Get collection and upsert container
        return self._insert_or_update(self.__container, self.__container_table,
                                      TrackingScraperConfig.DEFAULT_CONTAINER_QUERY)
    
    def _insert_or_update(self, document, collection, query_keys):
        # Create shallow copy of document, with specified keys, for query
        query_document = self._create_query_document(document, query_keys)
        logging.info("Query document: %s", query_document)
        
        # Try to update
        if "_id" in document:
            document.pop("_id")
        document["updated_at"] = datetime.datetime.utcnow()
        result = collection.update_many(query_document, {"$set": document})
        
        if result.matched_count > 0:
            logging.info("Updated: %s", query_document)
            return True
        
        # If update was unsuccessful, insert document
        document["created_at"] = datetime.datetime.utcnow()
        document["updated_at"] = None
        
        result = collection.insert_one(document)
        logging.info("Inserted: %s", query_document)
        return True
    
    def _create_query_document(self, document, query_keys):
        query_document = {}
        for key in query_keys:
            query_document[key] = document.get(key)
        return query_document
