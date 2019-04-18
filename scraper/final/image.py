from config import TrackingScraperConfig
from errors import TrackingScraperError, TrackingScraperSwitcherError

from io import BytesIO
from PIL import Image

import logging
import pytesseract

class TrackingScraperImageProcessor:
    """Image processor for the Tracking Scraper."""
    
    def __init__(self, parent_command, image_data):
        self.parent_command = parent_command
        try:
            self.image = Image.open(BytesIO(image_data))
        except Exception as ex:
            raise TrackingScraperSwitcherError("Image could not be opened: " + str(ex),
                                               self.parent_command)
    
    def execute(self):
        """Process image with an OCR, depending on command configuration."""
        
        # Execute image child commands
        commands = self.parent_command.get("commands")
        if isinstance(commands, list):
            for child_command in commands:
                self._find_command(child_command)
        
        # Process text with an OCR
        text = self._image_to_text()
        
        # Check if it has the desired length
        length = self.parent_command.get("length", TrackingScraperConfig.DEFAULT_KEY_LENGTH)
        if len(text) != length:
            logging.info("Text does not have desired length, retrying...")
            return None
        
        # Check for possible problems in text
        filter_words = self.parent_command.get("filters")
        if not isinstance(filter_words, list):
            return text
        for word in filter_words:
            if word in text:
                logging.info("Text has dangerous characters, retrying...")
                return None
        return text
    
    def _find_command(self, command):
        try:
            # Get command type
            command_type = command["type"]
            # Get command based on command type
            method = getattr(self, "_command_" + command_type)
            # Execute command
            return method(command)
        except KeyError:
            raise TrackingScraperSwitcherError("Image command type not found", self.parent_command)
        except AttributeError:
            raise TrackingScraperSwitcherError("Image command type " + command_type + " is not valid",
                                               self.parent_command)
    
    def _command_bnw(self, command):
        """Converts image to black and white."""
        
        # Get pixel pivot value, if it doesn't exist, assume default
        pivot = command.get("pivot", TrackingScraperConfig.DEFAULT_BNW_PIVOT)
        if not isinstance(pivot, int):
            raise TrackingScraperError("Image to black and white: pivot must be an integer")
        if pivot < 0 or pivot > 255:
            raise TrackingScraperError("Image to black and white: pivot must be between [0, 255]")
        
        # Convert image to black and white
        self.image = Image.eval(self.image, lambda pixel: 0 if pixel <= pivot else 255)
    
    def _image_to_text(self):
        config = "--psm 7"
        whitelist = ""
        
        # Check if we should include alphabetical letters
        if self.parent_command.get("alphabet", TrackingScraperConfig.DEFAULT_KEY_ALPHABET):
            whitelist += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        # Check if we should include numeric letters
        if self.parent_command.get("numbers", TrackingScraperConfig.DEFAULT_KEY_NUMBERS):
            whitelist += "1234567890"
        
        # Process image according to whitelist
        if whitelist:
            config += " -c tessedit_char_whitelist=" + whitelist
        print(config)
        
        # Clean whitespace and return
        text = pytesseract.image_to_string(self.image, config = config)
        return text.replace(" ", "")
