from converter import ScraperConverter
from config import ScraperConfig
from errors import ScraperSwitcherError, ScraperAssertionError, ScraperTimeoutError
from image import ScraperImage

from selenium.common.exceptions import (TimeoutException, ElementNotInteractableException,
                                        NoAlertPresentException)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import datetime
import re
import time

class ScraperSwitcher:
    """
    Switcher for selecting and saving Web elements and subelements in a tracking-related document.
    """
    
    def __init__(self, scraper, document, parent_command, parent_element = None):
        self.database = scraper.database
        self.driver   = scraper.driver
        self.carrier  = scraper.carrier
        self.config   = scraper.config
        self.logger   = scraper.logger
        self.document = document
        self.parent_command = parent_command
        self.parent_element = self.driver if parent_element is None else parent_element
    
    ###############################################################################################
    
    def process(self):
        """
        Get Web elements based on the current configuration command, then process or return them
        accordingly. Returns True if all commands and subcommands were executed successfully,
        False if one command failed, or the list of Web elements if no subcommands were found.
        """
        # Get process type
        process_type = self.parent_command.get("type")
        if process_type is None:
            raise ScraperSwitcherError("Process type not found", self.parent_command)
        # self.logger.debug("Process type: %s", process_type)
        
        # Execute process based on process type
        try:
            method = getattr(self, "process_" + process_type)
        except AttributeError:
            raise ScraperSwitcherError("Process type {} is not valid".format(process_type),
                                        self.parent_command)
        try:
            return method()
        except TypeError:
            raise ScraperSwitcherError("Process type {} is not a function".format(process_type),
                                        self.parent_command)
    
    ###############################################################################################
    
    def process_id(self):
        return self.process_dom_elements(By.ID)
    def process_class(self):
        return self.process_dom_elements(By.CLASS_NAME)
    def process_css(self):
        return self.process_dom_elements(By.CSS_SELECTOR)
    def process_name(self):
        return self.process_dom_elements(By.NAME)
    def process_tag(self):
        return self.process_dom_elements(By.TAG_NAME)
    def process_xpath(self):
        return self.process_dom_elements(By.XPATH)
    
    def process_dom_elements(self, selector_type):
        # Get selector
        selector = self.parent_command.get("selector")
        if selector is None:
            raise ScraperSwitcherError("Selector not found in process by " + selector_type,
                                               self.parent_command)
        
        # Check assertions
        assertions = self.check_assertions(selector_type, selector)
        if assertions is True:
            # self.logger.debug("Assertions are correct")
            return True
        
        # Get DOM elements
        dom_elements = self.parent_element.find_elements(selector_type, selector)
        
        # Check requirements
        required = self.parent_command.get("required", ScraperConfig.DEFAULT_KEY_REQUIRED)
        if len(dom_elements) == 0:
            self.logger.debug("Command: %s", self.print_command(self.parent_command))
            self.logger.debug("No elements found, using required")
            return not required
        
        # Get child command list and process them, if possible
        commands = self.parent_command.get("commands")
        if isinstance(commands, list):
            return self.process_child_commands(commands, dom_elements)
        
        # Get a child command for all elements and process them, if possible
        child_command = self.parent_command.get("command")
        if isinstance(child_command, dict):
            for child_element in dom_elements:
                result = self.generate_child_process(child_command, child_element)
                if result is not True:
                    return result
            return True
        
        # If no single child command was found, return all DOM elements
        self.logger.debug("Command: %s", self.print_command(self.parent_command))
        self.logger.debug("No child commands found, return all elements")
        return dom_elements
    
    def check_assertions(self, selector_type, selector):
        assertion = self.parent_command.get("assert")
        
        if isinstance(assertion, bool):
            # Set expected conditions depending if we want to switch to a frame or not
            frame = self.parent_command.get("frame", ScraperConfig.DEFAULT_KEY_FRAME)
            if frame:
                conditions = EC.frame_to_be_available_and_switch_to_it((selector_type, selector))
            else:
                conditions = EC.presence_of_all_elements_located((selector_type, selector))
            
            # Prepare waiter
            waiter = WebDriverWait(self.driver, ScraperConfig.DEFAULT_TIMEOUT_SHORT)
            
            if assertion:
                # Assert at least one element found
                try:
                    waiter.until(conditions)
                except TimeoutException:
                    raise ScraperAssertionError(selector_type, True)
            else:
                # Assert no elements found
                try:
                    waiter.until_not(conditions)
                except TimeoutException:
                    result = False if self.parent_command.get("assert_save") else None
                    raise ScraperAssertionError(selector_type, result)
            
            # Wait a little bit and return
            time.sleep(ScraperConfig.DEFAULT_WAIT_SHORT)
            return True
        
        # self.logger.debug("Command: %s", self.print_command())
        # self.logger.debug("Assertions not found")
        return False
    
    def process_child_commands(self, commands, elements):
        for child_command in commands:
            # Get index
            index = child_command.get("index")
            if index is None:
                raise ScraperSwitcherError("Child index command not found", child_command)
            
            # Check requirements
            if index >= len(elements):
                self.logger.debug("Command: %s", self.print_command(child_command))
                self.logger.debug("Child element at index %d, using required", index)
                return not child_command.get("required", ScraperConfig.DEFAULT_KEY_REQUIRED)
            
            # Process child element at specified index
            # self.logger.debug("Child index: %d", index)
            result = self.generate_child_process(child_command, elements[index])
            
            # If no subelements were found, return that element or element list
            # If a minor error occured (e.g. element not found), return False
            if result is not True:
                return result
        
        # If everything was fine, return True
        return True
    
    def generate_child_process(self, child_command, child_element):
        return ScraperSwitcher(self, self.document, child_command, child_element).process()
    
    ###############################################################################################
    
    def process_split(self):
        """Split text from a DOM element based on a delimiter."""
        
        # Get text to split
        parent_text = self.get_parent_text()
        
        # Get text separator
        delimiter = self.parent_command.get("delimiter")
        if delimiter is None:
            raise ScraperSwitcherError("No separator found", self.parent_command)
        
        # Split text
        elements = parent_text.split(delimiter)
        
        # Get child command list and process them, if possible
        commands = self.parent_command.get("commands")
        if isinstance(commands, list):
            return self.process_child_commands(commands, elements)
        
        # If no single child command was found, return split list
        return elements
    
    def get_parent_text(self):
        parent_text = self.parent_element
        try:
            return parent_text.text.strip() # value is a DOM element, we need its inner text
        except AttributeError:
            return parent_text.strip() # value is already a string
    
    ###############################################################################################
    
    def process_regex(self):
        # Get text
        text = self.get_parent_text()
        
        # Get regular expression pattern
        pattern = self.parent_command.get("pattern")
        if pattern is None:
            raise ScraperSwitcherError("No regular expression found", self.parent_command)
        
        # Match expression with text
        regex    = re.search(pattern, text)
        required = self.parent_command.get("required", ScraperConfig.DEFAULT_KEY_REQUIRED)
        if regex is None:
            self.logger.debug("Command: %s", self.print_command(self.parent_command))
            self.logger.debug("Regular expression does not match text, using required")
            return not required
        
        # Get list of matched elements
        elements = list(regex.groups())
        
        # Get child command list and process them, if possible
        commands = self.parent_command.get("commands")
        if isinstance(commands, list):
            return self.process_child_commands(commands, elements)
        
        # If no single child command was found, return list of matched elements
        return elements
    
    ###############################################################################################
    
    def process_save(self):
        """Saves text or subtext from a DOM element, or an specified value."""
        
        attribute = self.parent_command.get("key")
        if attribute is None:
            raise ScraperSwitcherError("Save key not found", self.parent_command)
        
        # Get value if it was defined, else get from DOM text
        value = self.parent_command.get("value")
        if value is None:
            value = self.get_parent_text()
        
        # Verify if value is an empty string
        required = self.parent_command.get("required", ScraperConfig.DEFAULT_KEY_REQUIRED)
        if isinstance(value, str) and len(value) == 0:
            self.logger.debug("Command: %s", self.print_command(self.parent_command))
            self.logger.debug("Text to save is empty, using required")
            return not required
        
        # Format type if necessary
        format_type = self.parent_command.get("format")
        if format_type is not None:
            value = ScraperConverter(self, self.document, value, format_type).convert()
            # If a value already exists in the attribute and it's a datetime object, join them
            if self.join_datetimes_if_possible(attribute, value):
                return True
            
        # Save according to parent key and formatting value
        self.document[attribute] = value
        return True
    
    def join_datetimes_if_possible(self, attribute, new_value):
        # Check if attribute exists
        if attribute not in self.document:
            return False
        
        # Get value from attribute
        old_value = self.document[attribute]
        
        # Check if old value is a date and new value is a time
        if isinstance(old_value, datetime.datetime) and isinstance(new_value, datetime.time):
            self.document[attribute] = datetime.datetime.combine(old_value.date(), new_value)
            return True
        
        # Return False if nothing was found
        return False
    
    ###############################################################################################
    
    def process_attr(self):
        # Get attribute name
        attribute_name = self.parent_command.get("name")
        if attribute_name is None:
            raise ScraperSwitcherError("Attribute name not found", self.parent_command)
        
        # Get attribute value from parent element
        attribute = self.parent_element.get_attribute(attribute_name)
        
        # Get child command, if none found, return attribute
        child_command = self.parent_command.get("command")
        if child_command is not None:
            # self.logger.debug("ATTRIBUTE - Child command found")
            return self.generate_child_process(child_command, attribute)
        # print(attribute)
        # self.logger.debug("ATTRIBUTE - No child command found")
        return attribute
    
    ###############################################################################################
    
    def process_compare(self):
        # Get text to compare
        text = self.get_parent_text()
        
        # Get values to compare
        values = self.parent_command.get("values")
        if values is None:
            raise ScraperSwitcherError("Values to compare not found", self.parent_command)
        
        # Check if text equals to value, or if it is in value list, then act accordingly
        success_commands = self.parent_command.get("success")
        failure_commands = self.parent_command.get("failure")
        if success_commands is None and failure_commands is None:
            self.logger.debug("Command: %s", self.print_command(self.parent_command))
            self.logger.debug("No commands found, resorting to required")
            return not self.parent_command.get("required", ScraperConfig.DEFAULT_KEY_REQUIRED)
        
        return self.process_compare_commands(success_commands if text in values else failure_commands)
    
    def process_compare_commands(self, commands):
        # Check requirements
        if commands is None:
            return True
        
        # Process child commands
        for child_command in commands:
            result = self.generate_child_process(child_command, self.parent_element)
            if result is not True:
                return result
        return True
    
    ###############################################################################################
    
    def process_write(self):
        # Get value
        value = self.parent_command.get("value")
        if value is None:
            # Get value from attribute
            attribute = self.parent_command.get("attribute")
            if attribute is None:
                raise ScraperSwitcherError("No attribute to use as input", self.parent_command)
            value = self.document.get(attribute)
            if value is None:
                raise ScraperSwitcherError("No value to use as input", self.parent_command)
        
        try:
            # Clear element if specified
            if self.parent_command.get("clean", ScraperConfig.DEFAULT_KEY_CLEAN):
                self.parent_element.clear()
            # Write value
            self.parent_element.send_keys(value)
            # Send enter if specified
            if self.parent_command.get("enter", ScraperConfig.DEFAULT_KEY_ENTER):
                self.parent_element.send_keys(Keys.ENTER)
        except ElementNotInteractableException:
            raise ScraperSwitcherError("Element is not interactable (because of Selenium)",
                                               self.parent_command)
        except AttributeError:
            raise ScraperSwitcherError("Element is not interactable (because of attribute)",
                                               self.parent_command)
        
        # Return True to indicate everything is OK
        time.sleep(ScraperConfig.DEFAULT_WAIT_SHORT)
        return True
    
    ###############################################################################################
    
    def process_alert(self):
        assertion = self.parent_command.get("assert")
        # TODO: Usar waits
        try:
            # Try to switch to alert
            alert = self.driver.switch_to.alert
            # Accept or dismiss action depending on command
            if self.parent_command.get("action", ScraperConfig.DEFAULT_KEY_ACTION):
                alert.accept()
            else:
                alert.dismiss()
            # Check assertions
            if assertion is False:
                result = False if self.parent_command.get("assert_save") else None
                raise ScraperAssertionError("alert", result)
        except NoAlertPresentException:
            if assertion is True:
                raise ScraperAssertionError("alert", True)
        
        # Return True to indicate everything is OK
        return True
    
    ###############################################################################################
    
    def process_click(self):
        # Check requirements
        required = self.parent_command.get("required", ScraperConfig.DEFAULT_KEY_REQUIRED)
        if not self.parent_element.is_displayed():
            return not required
        if not self.parent_element.is_enabled():
            return not required
        
        try:
            # Try to click the element
            self.parent_element.click()
            
            # Wait 2 or 5 seconds depending on "wait" attribute
            wait_time = self.parent_command.get("wait", ScraperConfig.DEFAULT_KEY_WAIT)
            if wait_time:
                time.sleep(ScraperConfig.DEFAULT_WAIT_LONG)
            else:
                time.sleep(ScraperConfig.DEFAULT_WAIT_SHORT)
                
            # Return True to indicate everything is OK
            return True
        except ElementNotInteractableException:
            return not required
        except TimeoutException:
            raise ScraperTimeoutError(False)
    
    ###############################################################################################
    
    def process_image(self):
        # Reset image to default width and height
        self.set_element_attribute("width")
        self.set_element_attribute("height")
        
        # Get required
        required = self.parent_command.get("required", ScraperConfig.DEFAULT_KEY_REQUIRED)
        # Get filename
        filename = "image-{}.png".format(self.config.get("carrier"))
        
        start_time = time.time()
        while True:
            # Take screenshot of element and process it
            if not self.parent_element.screenshot(filename):
                raise ScraperSwitcherError("Process OCR failed, could not take screenshot",
                                                   self.parent_command)
            text = ScraperImage(self, self.parent_command, filename).execute()
            if text is not None:
                break
            
            # If image processing failed, search for failure commands
            failure_command = self.parent_command.get("failure")
            if failure_command is None:
                self.logger.warning("Process OCR failed, using required")
                return not required
            # If they exist, execute them and wait a bit
            result = self.generate_child_process(failure_command, self.driver)
            if result is not True:
                self.logger.warning("Process OCR failure commands failed, using required")
                return not required
            time.sleep(ScraperConfig.DEFAULT_WAIT_NORMAL)

            # Check if we're out of time
            if (time.time() - start_time) > ScraperConfig.DEFAULT_TIMEOUT_NORMAL:
                raise ScraperTimeoutError(True)
        
        # Find element to write image text to
        element_command = self.parent_command.get("write")
        if not isinstance(element_command, dict):
            raise ScraperSwitcherError("Process OCR write command not found",
                                               self.parent_command)
        elements = self.generate_child_process(element_command, self.driver)
        
        # Write to element
        write_command = {"type": "write", "value": text}
        for element in elements:
            result = self.generate_child_process(write_command, element)
            if result is not True:
                return result
        return True
    
    def set_element_attribute(self, attribute_name):
        # Get attribute value to set, if none found, value will be set to null
        attribute_value = self.parent_command.get(attribute_name)
        # Set element attribute with JavaScript
        self.driver.execute_script("arguments[0].setAttribute(arguments[1], arguments[2]);",
                                     self.parent_element, attribute_name, attribute_value)
    
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
