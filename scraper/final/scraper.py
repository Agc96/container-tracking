from config import TrackingScraperConfig
from exception import TrackingScraperError
from switcher import TrackingScraperSwitcher

from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException

import datetime
import json
import logging
import time

class TrackingScraper:
    """Main class for the Tracking Web Scraper."""
    
    def __init__(self, driver, database, document):
        self.__driver   = driver
        self.__database = database
        self.__document = document
        
        # Get configuration file
        try:
            with open("../config/" + self.__document["carrier"] + ".json") as file:
                self.__configuration = json.load(file)
        except KeyError:
            raise TrackingScraperError("Carrier not found")
        except FileNotFoundError:
            raise TrackingScraperError("Configuration file not found")
        
        # Get general configuration
        if "general" not in self.__configuration:
            raise TrackingScraperError("General configuration information not found")
        
        # Get single and multiple tables
        self.__single_table, self.__single_query     = self._get_database_config(database, "single")
        self.__multiple_table, self.__multiple_query = self._get_database_config(database, "multiple")
    
    def _get_database_config(self, database, config_type):
        # Get configuration
        collection_configuration = self.__configuration["general"].get(config_type)
        if collection_configuration is None:
            return None
        
        # Get collection name
        table_name = collection_configuration.get("table")
        if table_name is None:
            raise TrackingScraperError("Table name for " + config_type + " entries not found")
        
        # Get collection query
        table_query_keys = collection_configuration.get("query")
        if not isinstance(table_query_keys, list):
            table_query_keys = []
        
        # Return database and query keys
        return database[table_name], table_query_keys
        
    @property
    def document(self):
        """Returns the container information."""
        return self.__document
    
    ###############################################################################################
    
    def execute(self):
        """Execute commands."""
        
        parent_result   = False
        input_result    = False
        single_result   = False
        multiple_result = False
        
        try:
            start = self._go_to_url()
            while True:
                # Check if we're still on time
                end = time.time()
                if (end - start) > TrackingScraperConfig.DEFAULT_TIMEOUT_LONG:
                    raise TrackingScraperError("Timeout exceeded, scraping was unsuccessful")
                
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
                parent_result = self._finish_execution()
                time.sleep(TrackingScraperConfig.DEFAULT_WAIT_SHORT)
                break
        except TrackingScraperError:
            logging.exception("Exception ocurred")
        except Exception:
            logging.exception("Unknown exception ocurred")
        finally:
            return parent_result
    
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
            self.__driver.get(link.format(**self.__document))
            time.sleep(TrackingScraperConfig.DEFAULT_WAIT_LONG)
        except TimeoutException:
            raise TrackingScraperError("Error loading Web page, timeout exceeded")
        
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
            result = TrackingScraperSwitcher(self.__driver, self.__document, self.__configuration,
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
        
        # Create multiple document based on single query items
        multiple_document = self._create_query_document(self.__document, self.__single_query)
        # Overwrite previous tracking items, if necessary
        # if multiple_command.get("overwrite", TrackingScraperConfig.DEFAULT_KEY_OVERWRITE):
            # self.__single_table.delete_many(multiple_document)
        
        # Generate and process multiple documents
        estimated = multiple_configuration.get("estimated", TrackingScraperConfig.DEFAULT_KEY_ESTIMATED)
        multiple_document["estimated"] = estimated
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
            if not isinstance(multiple_elements, list):
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
                self._insert_or_update(subdocument, self.__multiple_table, self.__multiple_query)
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
        self.__document["processed"] = processed_value
        
        # Get collection and upsert container
        return self._insert_or_update(self.__document, self.__single_table, self.__single_query)
    
    def _insert_or_update(self, document, collection, query_keys):
        # Create shallow copy of document, with specified keys, for query
        query_document = self._create_query_document(document, query_keys)
        logging.info("Query document: %s", query_document)
        
        # Try to update
        document["updated_at"] = datetime.datetime.utcnow()
        result = collection.update_one(query_document, {"$set": document})
        
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
