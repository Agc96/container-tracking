from config import ScraperConfig
from errors import ScraperAssertionError, ScraperTimeoutError, ScraperSwitcherError, ScraperError
from switcher import ScraperSwitcher

from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException

import datetime
import json
import time

class Scraper:
    """Main class for the Tracking Web Scraper."""
    
    PROCESSED = 2
    ERROR = 0
    
    def __init__(self, process, container):
        self.database  = process.database
        self.driver    = process.driver
        self.carrier   = process.carrier
        self.config    = process.config
        self.logger    = process.logger
        self.container = container
        self.movements = []
        # Check if general configuration exists
        if "general" not in self.config:
            raise ScraperError("General configuration information not found")
    
    ###############################################################################################
    
    def execute(self):
        """Execute a series of commands based on the configuration file for this carrier."""
        self.input_result     = False
        self.container_result = False
        self.movements_result = False
        self.start_time       = time.time()
        self.elapsed_time     = 0
        try:
            self.go_to_carrier_url()
            while True:
                # Check if we're still on time
                self.elapsed_time = time.time() - self.start_time
                if self.elapsed_time > ScraperConfig.DEFAULT_TIMEOUT_LONG:
                    raise ScraperTimeoutError(True)
                # Execute input commands
                self.input_result = self.execute_commands(self.input_result, "input")
                if self.input_result is not True:
                    self.log_retry("Input execution was unsuccessful, retrying...")
                    continue
                # Execute container commands
                self.container_result = self.execute_commands(self.container_result, "container")
                if self.container_result is not True:
                    self.log_retry("Single output execution was unsuccessful, retrying...")
                    continue
                # Execute movement commands
                self.movements_result = self.execute_movements(self.movements_result)
                if self.movements_result is not True:
                    self.log_retry("Multiple output execution was unsuccessful, retrying...")
                    continue
                # Finish execution, save elements and wait
                self.finish_execution()
                return self.wait_until_timeout()
        except Exception as ex:
            return self.process_exceptions(ex)
    
    def log_retry(self, logging_message):
        self.logger.info(logging_message)
        time.sleep(ScraperConfig.DEFAULT_WAIT_NORMAL)
    
    def wait_until_timeout(self):
        """Wait until we've reached the default timeout, to avoid saturating the servers."""
        self.elapsed_time = time.time() - self.start_time
        while (self.elapsed_time < ScraperConfig.DEFAULT_TIMEOUT_SHORT):
            time.sleep(1)
            self.elapsed_time = time.time() - self.start_time
        # Return the benchmark
        return (True, self.elapsed_time)
        
    def process_exceptions(self, ex):
        self.elapsed_time = time.time() - self.start_time
        # Check assertions
        if isinstance(ex, ScraperAssertionError):
            self.logger.warning(str(ex))
            value = self.finish_execution() if ex.assertion_type is False else False # No guardar error!
            return (value, self.elapsed_time)
        # Check timeout errors
        if isinstance(ex, ScraperTimeoutError):
            self.logger.warning(str(ex))
            return (self.save_error(), self.elapsed_time)
        # Check scraper switcher errors
        if isinstance(ex, ScraperSwitcherError):
            self.logger.error("Command: %s", ScraperSwitcher.print_command(ex.command))
            self.logger.error(str(ex))
            return (self.save_error(), self.elapsed_time)
        # Check common errors
        if isinstance(ex, ScraperError):
            self.logger.error(str(ex))
            return (self.save_error(), self.elapsed_time)
        # Check any webdriver-related errors
        if isinstance(ex, WebDriverException):
            self.logger.exception("An error error ocurred while using the WebDriver")
            # Don't save the error, reprocess it
            return (False, self.elapsed_time)
        # Check unknown errors
        self.logger.exception("Unknown exception ocurred in scraper")
        return (None, self.elapsed_time)
    
    ###############################################################################################
    
    def go_to_carrier_url(self):
        # Get configuration URL
        link = self.config["general"].get("url")
        if link is None:
            raise ScraperError("Configuration URL could not be found")
        
        # Go to desired URL
        try:
            self.driver.get(link.format(container=self.container['code']))
            time.sleep(ScraperConfig.DEFAULT_WAIT_LONG)
        except TimeoutException:
            raise ScraperTimeoutError(False)
        
        # Check if page is a Chrome error
        chrome_error = self.driver.find_elements_by_id("main-frame-error")
        if len(chrome_error) > 0:
            self.logger.error("Chrome error detected: %s", chrome_error[0].text)
            raise ScraperTimeoutError(False)
    
    ###############################################################################################
    
    def execute_commands(self, result, key):
        # Check if commands were already executed
        if result is True:
            return True
        # Get commands, if none found, return True
        commands = self.config.get(key)
        if commands is None:
            return True
        # Process commands
        for command in commands:
            switcher = ScraperSwitcher(self, self.container, command)
            if switcher.process() is not True:
                return False
        # Return True if everything was OK
        return True
    
    ###############################################################################################
    
    def execute_movements(self, result):
        if result is True:
            return True
        # Get multiple command, if none found, return True
        command = self.config.get("movements")
        if command is None:
            return True
        # Create movement based on configuration file
        estimated = self.config["general"].get("estimated", ScraperConfig.DEFAULT_KEY_ESTIMATED)
        movement = {
            "container": self.container["id"],
            "estimated": estimated
        }
        # Generate and process multiple documents
        return self.process_movements(command, movement, self.driver)
    
    def process_movements(self, command, document, previous):
        # Get single subcommands
        single_commands = command.get("single")
        if not isinstance(single_commands, list):
            raise ScraperError("Multiple command must have single commands key")
        
        # Get command to find parents, if none found, use driver to extract single commands
        parents = command.get("parents")
        if parents is None:
            multiple_elements = [previous]
        else:
            multiple_elements = ScraperSwitcher(self, {}, parents, previous).process()
            if multiple_elements is False:
                return True # No elements found
            if multiple_elements is True:
                raise ScraperError("Parent elements must be a list of web elements")
        
        # Get multiple subcomamnd
        multiple_subcommand = command.get("multiple")
        
        # Process every single command for every multiple element
        for multiple_subelement in multiple_elements:
            subdocument = dict(document)
            for single_command in single_commands:
                switcher = ScraperSwitcher(self, subdocument, single_command, multiple_subelement)
                if switcher.process() is not True:
                    self.logger.info("Movements: single subcommand failed")
                    return False
            
            # Check if multiple subcommand exists, if it doesn't, save and continue.
            if multiple_subcommand is None:
                self.movements.append(subdocument)
                continue
            
            # If it exists, copy result document and iterate these new multiple elements with it
            multiple_result = self.process_movements(multiple_subcommand, subdocument,
                                                     multiple_subelement)
            if multiple_result is not True:
                self.logger.info("Movements: multiple subcommand failed")
                return False
        
        # Return True to notify everything is OK
        return True
    
    ###############################################################################################
    
    def finish_execution(self):
        with self.database as conn:
            with conn.cursor() as cur:
                # Actualizar contenedor
                self.prepare_container_for_save()
                cur.execute("""UPDATE tracking_container SET status_id = %(status_id)s,
                    arrival_date = %(arrival_date)s, priority = %(priority)s
                    WHERE id = %(id)s;""", self.container)
                # Guardar movimientos de los contenedores
                for movement in self.movements:
                    self.prepare_movement_for_save(movement)
                    # Verificar si el movimiento ya existe
                    cur.execute("""SELECT id FROM tracking_movement WHERE container_id =
                        %(container)s AND status_id = %(status)s AND location_id = %(location)s
                        LIMIT 1;""", movement)
                    result = cur.fetchone()
                    if result is None:
                        # Caso 1: El movimiento no existe, crear uno nuevo
                        cur.execute("""INSERT INTO tracking_movement (container_id, location_id,
                            status_id, date, vehicle_id, vessel, voyage, estimated) VALUES
                            (%(container)s, %(location)s, %(status)s, %(date)s, %(vehicle)s,
                            %(vessel)s,  %(voyage)s, %(estimated)s)""", movement)
                    else:
                        # Caso 2: El movimiento ya existe, actualizarlo
                        movement["id"] = result["id"]
                        cur.execute("""UPDATE tracking_movement SET date = %(date)s, vehicle_id =
                            %(vehicle)s, vessel = %(vessel)s, voyage = %(voyage)s, estimated =
                            %(estimated)s WHERE id = %(id)s;""", movement)
            # conn.commit() TODO: Ver si es necesario
        return True
    
    def prepare_container_for_save(self):
        """Updates the container data before saving to database."""
        # Aumentar en 1 la prioridad
        self.container["priority"] += 1
        # Colocar si fue procesado o no, dependiendo de la configuración
        if self.config.get("processed", ScraperConfig.DEFAULT_KEY_PROCESSED):
            self.container["status_id"] = self.PROCESSED
    
    def prepare_movement_for_save(self, movement):
        """Updates the container movement data before saving to database."""
        estimated = self.config.get("estimated", ScraperConfig.DEFAULT_KEY_ESTIMATED)
        if "estimated" not in movement:
            movement["estimated"] = estimated
        if "vessel" not in movement:
            movement["vessel"] = None
        if "voyage" not in movement:
            movement["voyage"] = None
        if "vehicle" not in movement:
            movement["vehicle"] = None
    
    def save_error(self):
        with self.database as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE tracking_container SET status_id = %s WHERE id = %s",
                            (self.ERROR, self.container["id"]))
        return False
