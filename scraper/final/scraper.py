from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import *

import json
import re
import sys

class TrackingScraper:
	"""Web scraper for container information extraction."""

	def __init__(self, container, carrier):
		"""
		Initializes Selenium WebDriver, the container tracking object,
		and configuration for the shipping carrier.
		"""
		# Open the Firefox WebDriver
		try:
			self.__driver = webdriver.Firefox()
		except WebDriverException as ex:
			raise TrackingScraperError("Error creating Selenium driver.",
				container, carrier, ex)

		# Save container number in a variable
		self.__container = container

		# Define tracking information
		self.__tracking = {
			"general": {
				"container_number": container
			},
			"movements": []
		}

		# Get tracking configuration information
		try:
			with open("../config/" + carrier + ".json") as config:
				self.__config = json.load(config)
		except FileNotFoundError:
			print("")

	###################################################################

	def _go_to_url(self):
		"""Go to the URL specified in the configuration file."""

		# Get URL from configuration file
		url = self.config["general"]["url"]

		# Parse container if necessary, and go to page
		try:
			self.__driver.get(url.format(container = self.container))
		except WebDriverException as ex:
			print("Error ocurred while going to URL: ", ex)
			self.__driver.close()

	selector_types = {
		# Selector types
		"id": process_element_by_id,
		"class": process_elements_by_class,
		"css": process_elements_by_css_selector,
		"tag": process_elements_by_tag_name,
		# Text processing types
		"text": save_text_to_attribute,
		"regex": process_text_by_regex,
		"split": process_text_by_splitting
	}

	###################################################################

	def do_input_asserts(self):
		"""Executes assertions before input commands."""

		# Get input assertion commands
		input_assert = self.config.get("input_assert")
		if input_assert is None:
			return
		
		# Iterate through input assertion commands
		for input_assert in input_asserts:
			input_selector_type  = input_assert["type"]
			input_selector_value = 
			try:
				callback = selector_types[input_type]
			except KeyError:
				
	"""
	Realiza comandos al inicio del programa.
	"""
	def do_input_general_commands(self):
		try:
			input_commands = self.config["input"]
			wait_for_last_input = False
		except:
			pass

	def __del__(self):
		try:
			self.__driver.close()
		except AttributeError:
			pass # Driver was not declared, no need to close
		except InvalidSessionIdException:
			pass # Driver already closed
