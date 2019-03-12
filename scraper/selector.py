from error import TrackingScraperError
from selenium.webdriver.common.by import By

import re
import sys

class TrackingSelectorSwitcher:
    """
    Tracking Scraper switcher for selecting and saving DOM elements and subelements in a
    tracking-related document.
    """
    
    def __init__(self, container, carrier, driver, document, attribute_group, parent_command,
                 parent_element = None):
        self.__container = container
        self.__carrier = carrier
        self.__driver = driver
        self.__document = document
        self.__attribute_group = attribute_group
        self.__parent_command = parent_command
        self.__parent_element = driver if (parent_element is None) else parent_element
    
    @property
    def document(self):
        """
        Returns the stored tracking-related dictionary.
        """
        return self.__document
    
    ###############################################################################################
    
    def process(self):
        """
        Get DOM element(s) based on the configuration selector element declared in initialization,
        then process or return them accordingly. Returns True if all commands were executed
        successfully, False if one command failed, or DOM element(s) if no commands were found.
        """
        
        # Get selector type
        selector_type = self.__parent_command.get("type")
        if selector_type is None:
            self._close_driver("Selector type not found")
        
        # Execute process based on selector type
        try:
            method = getattr(self, "_process_" + selector_type)
            return method()
        except AttributeError:
            self._close_driver("Process: Selector type " + selector_type + " is not valid.")
    
    ###############################################################################################
    
    def _process_id(self):
        """
        Get DOM element by ID, then process it or return it depending on the parent command.
        """
        
        # Get selector value
        selector_value = self.__selector_command.get("value")
        if selector_value is None:
            self._close_driver("Process by ID: Selector value not found.")
        
        # Get DOM element by ID
        dom_element = self.__parent_element.find_element_by_id(selector_value)
            
        # Get child command, if it's not declared, return DOM element
        child_command = self.__parent_command.get("command")
        if child_command is None:
            return dom_element
        
        # Create child selector switcher and return its process result
        child_selector = TrackingSelectorSwitcher(self.__container, self.__carrier, self.__driver,
                                                  self.__document, self.__attribute_group,
                                                  child_command, dom_element)
        return child_selector.process()
    
    ###############################################################################################
    
    def _process_class(self):
        """
        Get DOM elements by class name, then process them or return them depending on the parent
        command.
        """
        return self._process_dom_elements(By.CLASS_NAME)
    
    def _process_css(self):
        """
        Get DOM elements by CSS selector, then process them or return them depending on the parent
        command.
        """
        return self._process_dom_elements(By.CSS_SELECTOR)
    
    def _process_tag(self):
        """
        Get DOM elements by tag name, then process them or return them depending on the parent
        command.
        """
        return self._process_dom_elements(By.TAG_NAME)
    
    def _process_name(self):
        """
        Get DOM elements by "name" attribute, then process them or return them depending on the
        parent command.
        """
        return self._process_dom_elements(By.NAME)
    
    def _process_xpath(self):
        """
        Get DOM elements by XPath, then process them or return them depending on the parent command.
        """
        return self._process_dom_elements(By.XPATH)
    
    def _process_dom_elements(self, by_attribute):
        """
        Get DOM elements by a specified By attribute, then process them or return them depending
        on the parent command.
        """
        
        # Get CSS selector
        selector = self.__parent_command.get("value")
        if selector is None:
            self._close_driver("Process by " + by_attribute + ": Selector value not found.")
        
        # Get DOM elements by specified attribute
        dom_elements = self.__parent_element.find_elements(by_attribute, selector)
        
        # Get subcommands, if none are declared, return DOM elements
        commands = self.__parent_command.get("commands")
        if commands is None:
            return dom_elements
        
        # Iterate through selector command elements
        for child_command in commands:
            print("Child command:", child_command)
            
            # Get element index to use
            dom_index = child_command.get("index")
            if dom_index is None:
                self._close_driver("Process by " + by_attribute + ": Child command index not found")
            
            # Get DOM element at index
            try:
                child_element = dom_elements[dom_index]
            except IndexError:
                # Write log message
                message = "Process by {0}: Child element at index {1} was not found"
                self._log_message(message.format(by_attribute, dom_index))
                # Return True if element was marked as not required, False otherwise
                return not child_command.get("required", True)
            
            # Create child selector switcher
            child_selector = TrackingSelectorSwitcher(self.__container, self.__carrier,
                                                      self.__driver, self.__document,
                                                      self.__attribute_group, child_command,
                                                      child_element)
            
            # Process child selector switcher
            child_result = child_selector.process()
            if child_result is not True:
                # if no subelements were found, return that element or element list
                # if a minor error occured (e.g. element not found), return False
                return child_result
        
        # If everything was fine, return True
        return True
    
    ###############################################################################################
    
    def _process_split(self):
        """
        Split parent element text by a string, then process them or return them depending on the
        parent command.
        """
        
        # Get parent element text
        try:
            text = self.__parent_element.text
        except AttributeError:
            self._close_driver("Process split: Element has no text")
        
        # Get text separator
        separator = self.__parent_command.get("value")
        if separator is None:
            self._close_driver("Process split: No separator found")
        
        items = text.split(separator)
        return True
    
    ###############################################################################################
    
    def _process_regex(self):
        """
        Match regex pattern with the parent element text, then process the groups or return them
        depending on the parent command.
        """
        return True
    
    ###############################################################################################
    
    def _process_save(self):
        """
        Saves element to the document, according to specified attribute and attribute group.
        """
        
        # Get attribute value to save to
        attribute = self.__parent_command.get("value")
        if attribute is None:
            self._close_driver("Process save: Attribute to save not found")
        
        # Get text to be saved
        saved_text = self.__parent_element
        try:
            # if value in "saved_text" is a DOM element, we need its text
            saved_text = saved_text.text
        except AttributeError:
            pass # value in "saved_text" is already a string
        
        # Verify if text is not empty
        if len(saved_text) == 0:
            # Write log message
            self._log_message("Process save: Text is empty")
            # Return True if element was marked as not required, False otherwise
            return not self.__parent_command.get("required", True)
        
        # Save text into the document
        try:
            self.__document[self.__attribute_group][attribute] = saved_text
            return True
        except KeyError:
            self._close_driver("Process save: Attribute group or attribute not found")
    
    ###############################################################################################
    
    def _log_message(self, message):
        """
        Logs a message to the standard error file.
        """
        try:
            self._raise_error(message)
        except TrackingScraperError as ex:
            print(ex, file = sys.stderr)
    
    def _close_driver(self, message):
        """
        Closes the Selenium Driver and raises an exception.
        """
        self.__driver.close()
        self._raise_error(message)
    
    def _raise_error(self, message):
        """
        Raises a TrackingScraperError with a custom message detailing the main attributes of the
        selector switcher object.
        """
        
        # Get needed attributes
        command_index = self.__parent_command.get("index")
        command_type  = self.__parent_command.get("type")
        command_value = self.__parent_command.get("value")
        
        # Format message
        log_message = ("Selector(attribute_group={0}, command_index={1}, command_type={2}, "
                       "command_value={3}): {4}")
        log_message = log_message.format(self.__attribute_group, command_index, command_type,
                                         command_value, message)
        
        # Raise exception
        raise TrackingScraperError(log_message, self.__container, self.__carrier)

