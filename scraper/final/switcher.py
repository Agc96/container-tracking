from converter import TrackingScraperConverter
from utils import TrackingScraperError, TrackingScraperConfig

from selenium.common.exceptions import (TimeoutException, ElementNotInteractableException,
NoAlertPresentException)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import logging
import re
import time

class TrackingScraperSwitcher:
    """
    Switcher for selecting and saving Web elements and subelements in a tracking-related document.
    """
    
    def __init__(self, driver, document, configuration, parent_command, parent_element = None):
        self.__driver         = driver
        self.__document       = document
        self.__configuration  = configuration
        self.__parent_command = parent_command
        self.__parent_element = driver if parent_element is None else parent_element
    
    @property
    def document(self):
        """Returns the stored tracking-related dictionary."""
        return self.__document
    
    ###############################################################################################
    
    def process(self):
        """
        Get Web elements based on the current configuration command, then process or return them
        accordingly. Returns True if all commands and subcommands were executed successfully,
        False if one command failed, or the list of Web elements if no subcommands were found.
        """
        # Get process type
        process_type = self.__parent_command.get("type")
        if process_type is None:
            raise TrackingScraperError("Process type not found")
        logging.info("Process type: %s", process_type)
        
        # Execute process based on process type
        try:
            method = getattr(self, "_process_" + process_type)
            return method()
        except AttributeError:
            raise TrackingScraperError("Process type " + process_type + " is not valid")
        except TypeError:
            raise TrackingScraperError("Process type " + process_type + " can't be directly invoked")
    
    ###############################################################################################
    
    def _process_id(self):
        return self._process_dom_elements(By.ID)
    def _process_class(self):
        return self._process_dom_elements(By.CLASS_NAME)
    def _process_css(self):
        return self._process_dom_elements(By.CSS_SELECTOR)
    def _process_name(self):
        return self._process_dom_elements(By.NAME)
    def _process_tag(self):
        return self._process_dom_elements(By.TAG_NAME)
    def _process_xpath(self):
        return self._process_dom_elements(By.XPATH)
    
    def _process_dom_elements(self, selector_type):
        # Get selector
        selector = self.__parent_command.get("selector")
        if selector is None:
            raise TrackingScraperError("Selector not found in process by " + selector_type)
        
        # Check assertions
        assertions = self.__check_assertions(selector_type, selector)
        if assertions is True:
            return True
        
        # Get DOM elements
        dom_elements = self.__parent_element.find_elements(selector_type, selector)
        
        # Check requirements
        required = self.__parent_command.get("required", TrackingScraperConfig.DEFAULT_KEY_REQUIRED)
        if len(dom_elements) == 0:
            logging.info("No elements found, using required")
            return not required
        
        # Get child command list and process them, if possible
        commands = self.__parent_command.get("commands")
        if isinstance(commands, list):
            return self.__process_child_commands(commands, dom_elements)
        
        # Get a child command for all elements and process them, if possible
        child_command = self.__parent_command.get("command")
        if child_command is not None:
            for child_element in dom_elements:
                result = self.__generate_child_process(child_command, child_element)
                if result is not True:
                    return result
            return True
        
        # If no single child command was found, return all DOM elements
        logging.info("No commands found, return")
        return dom_elements
    
    def __check_assertions(self, selector_type, selector):
        assertion = self.__parent_command.get("assert")
        
        # Assert at least one element found
        if assertion is True:
            try:
                WebDriverWait(self.__driver, TrackingScraperConfig.DEFAULT_TIMEOUT,
                              TrackingScraperConfig.DEFAULT_WAIT_SHORT).until(
                    EC.presence_of_all_elements_located((selector_type, selector)))
            except TimeoutException:
                raise TrackingScraperError("Assertion error: Elements unexpectedly not found")
            
            time.sleep(TrackingScraperConfig.DEFAULT_WAIT_SHORT)
            return True
        
        # Assert no elements found
        if assertion is False:
            try:
                WebDriverWait(self.__driver, TrackingScraperConfig.DEFAULT_TIMEOUT,
                              TrackingScraperConfig.DEFAULT_WAIT_SHORT).until_not(
                    EC.presence_of_all_elements_located((selector_type, selector)))
            except TimeoutException:
                raise TrackingScraperError("Assertion error: Elements unexpectedly found")
            
            time.sleep(TrackingScraperConfig.DEFAULT_WAIT_SHORT)
            return True
        
        return False
    
    def __process_child_commands(self, commands, elements):
        for child_command in commands:
            # Get index
            index = child_command.get("index")
            if index is None:
                raise TrackingScraperError("Child index command not found")
            
            # Check requirements
            if index >= len(elements):
                logging.info("Child element at index " + index + ", using required")
                return not child_command.get("required", TrackingScraperConfig.DEFAULT_KEY_REQUIRED)
            
            # Process child element at specified index
            logging.info("Child index: %d", index)
            result = self.__generate_child_process(child_command, elements[index])
            
            # If no subelements were found, return that element or element list
            # If a minor error occured (e.g. element not found), return False
            if result is not True:
                return result
        
        # If everything was fine, return True
        return True
    
    def __generate_child_process(self, child_command, child_element):
        return TrackingScraperSwitcher(self.__driver, self.__document, self.__configuration,
                                       child_command, child_element).process()
    
    ###############################################################################################
    
    def _process_split(self):
        # Get text to split
        parent_text = self.__get_parent_text()
        
        # Get text separator
        delimiter = self.__parent_command.get("delimiter")
        if delimiter is None:
            raise TrackingScraperError("No separator found")
        
        # Split text
        elements = parent_text.split(delimiter)
        
        # Get child command list and process them, if possible
        commands = self.__parent_command.get("commands")
        if isinstance(commands, list):
            return self.__process_child_commands(commands, elements)
        
        # If no single child command was found, return split list
        return elements
    
    def __get_parent_text(self):
        parent_text = self.__parent_element
        try:
            return parent_text.text.strip() # value is a DOM element, we need its inner text
        except AttributeError:
            return parent_text.strip() # value is already a string
    
    ###############################################################################################
    
    def _process_regex(self):
        # Get text
        text = self.__get_parent_text()
        
        # Get regular expression pattern
        pattern = self.__parent_command.get("pattern")
        if pattern is None:
            raise TrackingScraperError("No regular expression found")
        
        # Match expression with text
        regex    = re.search(pattern, text)
        required = self.__parent_command.get("required", TrackingScraperConfig.DEFAULT_KEY_REQUIRED)
        if regex is None:
            logging.info("Regular expression does not match text, using required")
            return not required
        
        # Get list of matched elements
        elements = list(regex.groups())
        
        # Get child command list and process them, if possible
        commands = self.__parent_command.get("commands")
        if isinstance(commands, list):
            return self.__process_child_commands(commands, elements)
        
        # If no single child command was found, return list of matched elements
        return elements
    
    ###############################################################################################
    
    def _process_save(self):
        attribute = self.__parent_command.get("key")
        if attribute is None:
            raise TrackingScraperError("Save key not found")
        
        # Get text to be saved, and verify if it's not empty
        value    = self.__get_parent_text()
        required = self.__parent_command.get("required", TrackingScraperConfig.DEFAULT_KEY_REQUIRED)
        if len(value) == 0:
            logging.info("Text to save is empty, using required")
            return not required
        
        # Format type if necessary
        format_type = self.__parent_command.get("format")
        if format_type is not None:
            value = TrackingScraperConverter(value, format_type, self.__configuration).convert()
        
        #  Save according to parent key and formatting value
        self.__document[attribute] = value
        
        # Return True to indicate everything was OK
        return True
    
    ###############################################################################################
    
    def _process_compare(self):
        # Get text to compare
        text = self.__get_parent_text()
        
        # Get values to compare
        values = self.__parent_command.get("values")
        if values is not None:
            raise TrackingScraperError("Values to compare not found")
        
        # Check if text equals to value, or if it is in value list, then act accordingly
        if text in values:
            commands = self.__parent_command.get("success")
            return self.__process_compare_commands(commands, "Success")
        else:
            commands = self.__parent_command.get("failure")
            return self.__process_compare_commands(commands, "Failure")
    
    def __process_compare_commands(self, commands, compare_result):
        # Check requirements
        required = self.__parent_command.get("required", TrackingScraperConfig.DEFAULT_KEY_REQUIRED)
        if commands is None:
            logging.info(compare_result + " commands not found, resorting to required")
            return not required
        
        # Process child commands
        for child_command in commands:
            result = self.__generate_child_process(child_command, self.__parent_element)
            if result is not True:
                return result
        return True
    
    ###############################################################################################
    
    def _process_write(self):
        # Get value
        value = self.__parent_command.get("value")
        if value is None:
            # Get value from attribute
            attribute = self.__parent_command.get("attribute")
            if attribute is None:
                raise TrackingScraperError("No value or attribute to use as input")
            value = self.__document.get(attribute)
        
        try:
            # Clear element if specified
            if self.__parent_command.get("clean", TrackingScraperConfig.DEFAULT_KEY_CLEAN):
                self.__parent_element.clear()
            # Write value
            self.__parent_element.send_keys(value)
            # Send enter if specified
            if self.__parent_command.get("enter", TrackingScraperConfig.DEFAULT_KEY_ENTER):
                self.__parent_element.send_keys(Keys.ENTER)
        except AttributeError:
            raise TrackingScraperError("Element is not interactable (attribute)")
        except ElementNotInteractableException:
            raise TrackingScraperError("Element is not interactable (selenium)")
        
        # Return True to indicate everything is OK
        time.sleep(TrackingScraperConfig.DEFAULT_WAIT_SHORT)
        return True
    
    ###############################################################################################
    
    def _process_alert(self):
        assertion = self.__parent_command.get("assertion")
        try:
            # Try to switch to alert
            alert = self.__driver.switch_to.alert
            if assertion is False:
                raise TrackingScraperError("Assertion failed: Alert unexpectedly found")
            # Accept or dismiss action depending on command
            if self.__parent_command.get("action", TrackingScraperConfig.DEFAULT_KEY_ACTION):
                alert.accept()
            else:
                alert.dismiss()
        except NoAlertPresentException:
            if assertion is True:
                raise TrackingScraperError("Assertion failed: Alert unexpectedly not found")
        
        # Return True to indicate everything is OK
        return True
    
    ###############################################################################################
    
    def _process_click(self):
        # Check requirements
        required = self.__parent_command.get("required", TrackingScraperConfig.DEFAULT_KEY_REQUIRED)
        if not self.__parent_element.is_displayed():
            return not required
        if not self.__parent_element.is_enabled():
            return not required
        
        try:
            # Try to click the element
            self.__parent_element.click()
            
            # Wait 2 or 5 seconds depending on "wait" attribute
            wait_time = self.__parent_command.get("wait", TrackingScraperConfig.DEFAULT_KEY_WAIT)
            if wait_time:
                time.sleep(TrackingScraperConfig.DEFAULT_WAIT_LONG)
            else:
                time.sleep(TrackingScraperConfig.DEFAULT_WAIT_SHORT)
                
            # Return True to indicate everything is OK
            return True
        except ElementNotInteractableException:
            return not required
    
    ###############################################################################################
    
    def _process_ocr(self):
        length = self.__parent_command.get("length")
        if length is None:
            raise TrackingScraperError("Text length not defined")
        
        # Request text
        text = input("Enter captcha text: ")
        if len(text) != length:
            raise TrackingScraperError("Text is not " + length + " characters long")
        
        # Save to attribute
        self.__document["ocr"] = text
        return True
