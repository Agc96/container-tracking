from converter import TrackingScraperConverter
from config import TrackingScraperConfig
from errors import (TrackingScraperSwitcherError, TrackingScraperAssertionError,
                    TrackingScraperTimeoutError)
from image import TrackingScraperImageProcessor

from selenium.common.exceptions import (TimeoutException, ElementNotInteractableException,
                                        NoAlertPresentException)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import datetime
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
            raise TrackingScraperSwitcherError("Process type not found", self.__parent_command)
        # logging.info("Process type: %s", process_type)
        
        # Execute process based on process type
        try:
            method = getattr(self, "_process_" + process_type)
            return method()
        except AttributeError:
            raise TrackingScraperSwitcherError("Process type " + process_type + " is not valid",
                                               self.__parent_command)
    
    ###############################################################################################
    
    def _process_id(self):
        return self.__process_dom_elements(By.ID)
    def _process_class(self):
        return self.__process_dom_elements(By.CLASS_NAME)
    def _process_css(self):
        return self.__process_dom_elements(By.CSS_SELECTOR)
    def _process_name(self):
        return self.__process_dom_elements(By.NAME)
    def _process_tag(self):
        return self.__process_dom_elements(By.TAG_NAME)
    def _process_xpath(self):
        return self.__process_dom_elements(By.XPATH)
    
    def __process_dom_elements(self, selector_type):
        # Get selector
        selector = self.__parent_command.get("selector")
        if selector is None:
            raise TrackingScraperSwitcherError("Selector not found in process by " + selector_type,
                                               self.__parent_command)
        
        # Check assertions
        assertions = self.__check_assertions(selector_type, selector)
        if assertions is True:
            # logging.info("Assertions are correct")
            return True
        
        # Get DOM elements
        dom_elements = self.__parent_element.find_elements(selector_type, selector)
        
        # Check requirements
        required = self.__parent_command.get("required", TrackingScraperConfig.DEFAULT_KEY_REQUIRED)
        if len(dom_elements) == 0:
            logging.info("Command: %s", self.print_command(self.__parent_command))
            logging.info("No elements found, using required")
            return not required
        
        # Get child command list and process them, if possible
        commands = self.__parent_command.get("commands")
        if isinstance(commands, list):
            return self.__process_child_commands(commands, dom_elements)
        
        # Get a child command for all elements and process them, if possible
        child_command = self.__parent_command.get("command")
        if isinstance(child_command, dict):
            for child_element in dom_elements:
                result = self.__generate_child_process(child_command, child_element)
                if result is not True:
                    return result
            return True
        
        # If no single child command was found, return all DOM elements
        logging.info("Command: %s", self.print_command(self.__parent_command))
        logging.info("No child commands found, return all elements")
        return dom_elements
    
    def __check_assertions(self, selector_type, selector):
        assertion = self.__parent_command.get("assert")
        
        if isinstance(assertion, bool):
            # Set expected conditions depending if we want to switch to a frame or not
            frame = self.__parent_command.get("frame", TrackingScraperConfig.DEFAULT_KEY_FRAME)
            if frame:
                conditions = EC.frame_to_be_available_and_switch_to_it((selector_type, selector))
            else:
                conditions = EC.presence_of_all_elements_located((selector_type, selector))
            
            # Prepare waiter
            waiter = WebDriverWait(self.__driver, TrackingScraperConfig.DEFAULT_TIMEOUT_SHORT)
            
            if assertion:
                # Assert at least one element found
                try:
                    waiter.until(conditions)
                except TimeoutException:
                    raise TrackingScraperAssertionError(selector_type, True)
            else:
                # Assert no elements found
                try:
                    waiter.until_not(conditions)
                except TimeoutException:
                    result = False if self.__parent_command.get("assert_save") else None
                    raise TrackingScraperAssertionError(selector_type, result)
            
            # Wait a little bit and return
            time.sleep(TrackingScraperConfig.DEFAULT_WAIT_SHORT)
            return True
        
        # logging.info("Command: %s", self.print_command())
        # logging.info("Assertions not found")
        return False
    
    def __process_child_commands(self, commands, elements):
        for child_command in commands:
            # Get index
            index = child_command.get("index")
            if index is None:
                raise TrackingScraperSwitcherError("Child index command not found", child_command)
            
            # Check requirements
            if index >= len(elements):
                logging.info("Command: %s", self.print_command(child_command))
                logging.info("Child element at index %d, using required", index)
                return not child_command.get("required", TrackingScraperConfig.DEFAULT_KEY_REQUIRED)
            
            # Process child element at specified index
            # logging.info("Child index: %d", index)
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
        """Split text from a DOM element based on a delimiter."""
        
        # Get text to split
        parent_text = self.__get_parent_text()
        
        # Get text separator
        delimiter = self.__parent_command.get("delimiter")
        if delimiter is None:
            raise TrackingScraperSwitcherError("No separator found", self.__parent_command)
        
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
            raise TrackingScraperSwitcherError("No regular expression found", self.__parent_command)
        
        # Match expression with text
        regex    = re.search(pattern, text)
        required = self.__parent_command.get("required", TrackingScraperConfig.DEFAULT_KEY_REQUIRED)
        if regex is None:
            logging.info("Command: %s", self.print_command(self.__parent_command))
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
        """Saves text or subtext from a DOM element, or an specified value."""
        
        attribute = self.__parent_command.get("key")
        if attribute is None:
            raise TrackingScraperSwitcherError("Save key not found", self.__parent_command)
        
        # Get value if it was defined, else get from DOM text
        value = self.__parent_command.get("value")
        if value is None:
            value = self.__get_parent_text()
        
        # Verify if value is an empty string
        required = self.__parent_command.get("required", TrackingScraperConfig.DEFAULT_KEY_REQUIRED)
        if isinstance(value, str) and len(value) == 0:
            logging.info("Command: %s", self.print_command(self.__parent_command))
            logging.info("Text to save is empty, using required")
            return not required
        
        # Format type if necessary
        format_type = self.__parent_command.get("format")
        if format_type is not None:
            value = TrackingScraperConverter(self.__document, value, format_type,
                                             self.__configuration).convert()
            # If a value already exists in the attribute and it's a datetime object, join them
            if self.__join_datetimes_if_possible(attribute, value):
                return True
            
        # Save according to parent key and formatting value
        self.__document[attribute] = value
        return True
    
    def __join_datetimes_if_possible(self, attribute, new_value):
        # Check if attribute exists
        if attribute not in self.__document:
            return False
        
        # Get value from attribute
        old_value = self.__document[attribute]
        
        # Check if old value is a date and new value is a time
        if isinstance(old_value, datetime.datetime) and isinstance(new_value, datetime.time):
            self.__document[attribute] = datetime.datetime.combine(old_value.date(), new_value)
            return True
        
        # Return False if nothing was found
        return False
    
    ###############################################################################################
    
    def _process_attr(self):
        # Get attribute name
        attribute_name = self.__parent_command.get("name")
        if attribute_name is None:
            raise TrackingScraperSwitcherError("Attribute name not found", self.__parent_command)
        
        # Get attribute value from parent element
        attribute = self.__parent_element.get_attribute(attribute_name)
        
        # Get child command, if none found, return attribute
        child_command = self.__parent_command.get("command")
        if child_command is not None:
            # logging.info("ATTRIBUTE - Child command found")
            return TrackingScraperSwitcher(self.__driver, self.__document, self.__configuration,
                                           child_command, attribute).process()
        # print(attribute)
        # logging.info("ATTRIBUTE - No child command found")
        return attribute
    
    ###############################################################################################
    
    def _process_compare(self):
        # Get text to compare
        text = self.__get_parent_text()
        
        # Get values to compare
        values = self.__parent_command.get("values")
        if values is None:
            raise TrackingScraperSwitcherError("Values to compare not found", self.__parent_command)
        
        # Check if text equals to value, or if it is in value list, then act accordingly
        success_commands = self.__parent_command.get("success")
        failure_commands = self.__parent_command.get("failure")
        if success_commands is None and failure_commands is None:
            logging.info("Command: %s", self.print_command(self.__parent_command))
            logging.info("No commands found, resorting to required")
            return not self.__parent_command.get("required", TrackingScraperConfig.DEFAULT_KEY_REQUIRED)
        
        return self.__process_compare_commands(success_commands if text in values else failure_commands)
    
    def __process_compare_commands(self, commands):
        # Check requirements
        if commands is None:
            return True
        
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
                raise TrackingScraperSwitcherError("No value or attribute to use as input",
                                                   self.__parent_command)
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
        except ElementNotInteractableException:
            raise TrackingScraperSwitcherError("Element is not interactable (because of Selenium)",
                                               self.__parent_command)
        except AttributeError:
            raise TrackingScraperSwitcherError("Element is not interactable (because of attribute)",
                                               self.__parent_command)
        
        # Return True to indicate everything is OK
        time.sleep(TrackingScraperConfig.DEFAULT_WAIT_SHORT)
        return True
    
    ###############################################################################################
    
    def _process_alert(self):
        assertion = self.__parent_command.get("assert")
        # TODO: Usar waits
        try:
            # Try to switch to alert
            alert = self.__driver.switch_to.alert
            # Accept or dismiss action depending on command
            if self.__parent_command.get("action", TrackingScraperConfig.DEFAULT_KEY_ACTION):
                alert.accept()
            else:
                alert.dismiss()
            # Check assertions
            if assertion is False:
                result = False if self.__parent_command.get("assert_save") else None
                raise TrackingScraperAssertionError("alert", result)
        except NoAlertPresentException:
            if assertion is True:
                raise TrackingScraperAssertionError("alert", True)
        
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
        except TimeoutException:
            raise TrackingScraperTimeoutError(False)
    
    ###############################################################################################
    
    def _process_ocr(self):
        # Reset image to default width and height
        self.__set_element_attribute("width")
        self.__set_element_attribute("height")
        
        # Get required
        required = self.__parent_command.get("required", TrackingScraperConfig.DEFAULT_KEY_REQUIRED)

        start_time = time.time()
        while True:
            # Take screenshot of element and process it
            image_bytes = self.__parent_element.screenshot_as_png
            text = TrackingScraperImageProcessor(self.__parent_command, image_bytes).execute()
            if text is not None:
                break
            
            # If image processing failed, search for failure commands
            failure_command = self.__parent_command.get("failure")
            if failure_command is None:
                logging.warning("Process OCR failed, using required")
                return not required
            # If they exist, execute them and wait a bit
            result = self.__generate_child_process(failure_command, self.__driver)
            if result is not True:
                logging.warning("Process OCR failure commands failed, using required")
                return not required
            time.sleep(TrackingScraperConfig.DEFAULT_WAIT_NORMAL)

            # Check if we're out of time
            if (time.time() - start_time) > TrackingScraperConfig.DEFAULT_TIMEOUT_NORMAL:
                raise TrackingScraperTimeoutError(True)
        
        # Find element to write image text to
        element_command = self.__parent_command.get("write")
        if not isinstance(element_command, dict):
            raise TrackingScraperSwitcherError("Process OCR write command not found",
                                               self.__parent_command)
        elements = self.__generate_child_process(element_command, self.__driver)
        
        # Write to element
        write_command = {"type": "write", "value": text}
        for element in elements:
            result = self.__generate_child_process(write_command, element)
            if result is not True:
                return result
        return True
    
    def __set_element_attribute(self, attribute_name):
        # Get attribute value to set, if none found, value will be set to null
        attribute_value = self.__parent_command.get(attribute_name)
        # Set element attribute with JavaScript
        self.__driver.execute_script("arguments[0].setAttribute(arguments[1], arguments[2]);",
                                     self.__parent_element, attribute_name, attribute_value)
    
    ###############################################################################################
    
    @staticmethod
    def print_command(command):
        command_texts = []
        for key, value in command.items():
            if isinstance(value, list):
                command_texts.append('"{0}": list({1})'.format(key, len(value)))
            elif isinstance(value, dict):
                command_texts.append('"{0}": dict({1})'.format(key, len(value)))
            elif isinstance(value, str):
                command_texts.append('"{0}": "{1}"'.format(key, value))
            else:
                command_texts.append('"{0}": {1}'.format(key, value))
        return "{" + ", ".join(command_texts) + "}"
