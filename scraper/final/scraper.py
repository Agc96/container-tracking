from config import TrackingScraperConfig
from errors import (TrackingScraperAssertionError, TrackingScraperTimeoutError,
                    TrackingScraperSwitcherError, TrackingScraperError)
from switcher import TrackingScraperSwitcher

from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException

import datetime
import json
import time

class TrackingScraper:
    """Main class for the Tracking Web Scraper."""
    
    def __init__(self, driver, database, container, configuration, logger):
        self.driver          = driver
        self.database        = database
        self.container_table = database[TrackingScraperConfig.DEFAULT_CONTAINER_TABLE]
        self.movement_table  = database[TrackingScraperConfig.DEFAULT_MOVEMENT_TABLE]
        self.container       = container
        self.configuration   = configuration
        self.logger          = logger
        # Check if general configuration exists
        if "general" not in self.configuration:
            raise TrackingScraperError("General configuration information not found")
    
    ###############################################################################################
    
    def execute(self):
        """
        Execute a series of commands based on the configuration file specified in the initializer.
        """
        self.input_result    = False
        self.single_result   = False
        self.multiple_result = False
        self.start_time      = time.time()
        self.elapsed_time    = 0
        try:
            self.go_to_carrier_url()
            while True:
                # Check if we're still on time
                self.elapsed_time = time.time() - self.start_time
                if self.elapsed_time > TrackingScraperConfig.DEFAULT_TIMEOUT_LONG:
                    raise TrackingScraperTimeoutError(True)
                # Execute input commands
                self.input_result = self.execute_commands(self.input_result, "input")
                if self.input_result is not True:
                    self.log_retry("Input execution was unsuccessful, retrying...")
                    continue
                # Execute single output
                self.single_result = self.execute_commands(self.single_result, "single")
                if self.single_result is not True:
                    self.log_retry("Single output execution was unsuccessful, retrying...")
                    continue
                # Execute multiple output
                self.multiple_result = self.execute_multiple_output(self.multiple_result)
                if self.multiple_result is not True:
                    self.log_retry("Multiple output execution was unsuccessful, retrying...")
                    continue
                # Finish execution, save elements and wait
                self.finish_execution()
                return self.wait_until_timeout()
        except Exception as ex:
            return self.process_exceptions(ex)
    
    def log_retry(self, logging_message):
        self.logger.info(logging_message)
        time.sleep(TrackingScraperConfig.DEFAULT_WAIT_NORMAL)
    
    def wait_until_timeout(self):
        """
        Wait until we've reached the default timeout, to avoid saturating the servers.
        """
        self.elapsed_time = time.time() - self.start_time
        while (self.elapsed_time < TrackingScraperConfig.DEFAULT_TIMEOUT_SHORT):
            time.sleep(1)
            self.elapsed_time = time.time() - self.start_time
        # Return the benchmark
        return (True, self.elapsed_time)
        
    def process_exceptions(self, ex):
        self.elapsed_time = time.time() - self.start_time
        # Check assertions
        if isinstance(ex, TrackingScraperAssertionError):
            self.logger.warning(str(ex))
            value = self.finish_execution() if ex.assertion_type is False else False
            return (value, self.elapsed_time)
        # Check timeout errors
        if isinstance(ex, TrackingScraperTimeoutError):
            self.logger.warning(str(ex))
            return (False, self.elapsed_time)
        # Check scraper switcher errors
        if isinstance(ex, TrackingScraperSwitcherError):
            self.logger.error("Command: %s", TrackingScraperSwitcher.print_command(ex.command))
            self.logger.error(str(ex))
            return (False, self.elapsed_time)
        # Check common errors
        if isinstance(ex, TrackingScraperError):
            self.logger.error(str(ex))
            return (False, self.elapsed_time)
        # Check unknown errors
        self.logger.exception("Unknown exception ocurred in scraper")
        return (None, self.elapsed_time)
    
    ###############################################################################################
    
    def go_to_carrier_url(self):
        # Check if general configuration is declared
        general_config = self.configuration.get("general")
        if general_config is None:
            raise TrackingScraperError("Configuration information not found")
        
        # Get configuration URL
        link = self.configuration["general"].get("url")
        if link is None:
            raise TrackingScraperError("Configuration URL could not be found")
        
        # Go to desired URL
        try:
            self.driver.get(link.format(**self.container))
            time.sleep(TrackingScraperConfig.DEFAULT_WAIT_LONG)
        except TimeoutException:
            raise TrackingScraperTimeoutError(False)
        
        # Check if page is a Chrome error
        chrome_error = self.driver.find_elements_by_id("main-frame-error")
        if len(chrome_error) > 0:
            self.logger.error("Chrome error detected: %s", chrome_error[0].text)
            raise TrackingScraperTimeoutError(False)
    
    ###############################################################################################
    
    def execute_commands(self, parent_result, key):
        # Check if commands were already executed
        if parent_result is True:
            return True
        
        # Get commands, if none found, return True
        commands = self.configuration.get(key)
        if commands is None:
            return True
        
        # Process commands
        for command in commands:
            switcher = TrackingScraperSwitcher(self.driver, self.database, self.container,
                                               self.configuration, self.logger, command)
            if switcher.process() is not True:
                return False
        
        # Return True if everything was OK
        return True
    
    ###############################################################################################
    
    def execute_multiple_output(self, multiple_result):
        if multiple_result is True:
            return True
        
        # Get multiple command, if none found, return True
        multiple_command = self.configuration.get("multiple")
        if multiple_command is None:
            return True
        
        # Get configuration key
        multiple_configuration = self.configuration["general"].get("multiple")
        if multiple_configuration is None:
            return True
        
        # Create multiple document based on configuration file
        multiple_document = dict(multiple_configuration)
        for key in TrackingScraperConfig.DEFAULT_CONTAINER_COPY:
            multiple_document[key] = self.container[key]
        
        # Generate and process multiple documents
        return self.process_multiple_elements(multiple_command, multiple_document, self.driver)
    
    def process_multiple_elements(self, multiple_command, multiple_document, previous_element):
        # Get single subcommands
        multiple_single_commands = multiple_command.get("single")
        if not isinstance(multiple_single_commands, list):
            raise TrackingScraperError("Multiple command must have single commands key")
        
        # Get command to find parents, if none found, use driver to extract single commands
        multiple_parents = multiple_command.get("parents")
        if multiple_parents is None:
            multiple_elements = [previous_element]
        else:
            switcher = TrackingScraperSwitcher(self.driver, self.database, {}, self.configuration,
                                               self.logger, multiple_parents, previous_element)
            multiple_elements = switcher.process()
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
                switcher = TrackingScraperSwitcher(self.driver, self.database, subdocument,
                                                   self.configuration, self.logger, single_command,
                                                   multiple_subelement)
                if switcher.process() is not True:
                    self.logger.info("Multiple: single subcommand failed")
                    return False
            
            # Check if multiple subcommand exists, if it doesn't, save and continue.
            if multiple_multiple_command is None:
                self.insert_or_update(subdocument, self.movement_table,
                                       TrackingScraperConfig.DEFAULT_MOVEMENT_QUERY)
                continue
            
            # If it exists, copy result document and iterate these new multiple elements with it
            multiple_result = self.process_multiple_elements(multiple_multiple_command,
                                                             subdocument, multiple_subelement)
            if multiple_result is not True:
                self.logger.info("Multiple: multiple subcommand failed")
                return False
        
        # Return True to notify everything is OK
        return True
    
    ###############################################################################################
    
    def finish_execution(self):
        # Get configuration for single element
        single_config = self.configuration["general"].get("single")
        if single_config is None:
            return True
        
        # Get processed value to save
        processed_value = single_config.get("processed", TrackingScraperConfig.DEFAULT_KEY_PROCESSED)
        self.container["processed"] = processed_value
        
        # Get collection and upsert container
        return self.insert_or_update(self.container, self.container_table,
                                     TrackingScraperConfig.DEFAULT_CONTAINER_QUERY)
    
    def insert_or_update(self, document, collection, query_keys):
        # Create shallow copy of document, with specified keys, for query
        query_document = self.create_query_document(document, query_keys)
        self.logger.info("Query document: %s", query_document)
        
        # Try to update
        if "_id" in document:
            document.pop("_id")
        document["updated_at"] = datetime.datetime.utcnow()
        result = collection.update_many(query_document, {"$set": document})
        
        if result.matched_count > 0:
            self.logger.info("Updated: %s", query_document)
            return True
        
        # If update was unsuccessful, insert document
        document["created_at"] = datetime.datetime.utcnow()
        document["updated_at"] = None
        
        result = collection.insert_one(document)
        self.logger.info("Inserted: %s", query_document)
        return True
    
    def create_query_document(self, document, query_keys):
        query_document = {}
        for key in query_keys:
            query_document[key] = document.get(key)
        return query_document
