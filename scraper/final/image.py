from config import ScraperConfig
from errors import ScraperError, ScraperSwitcherError

from io import BytesIO
from PIL import Image

import pytesseract

class ScraperImage:
    """Image processor for the Tracking Scraper."""
    
    def __init__(self, switcher, parent_command, filename):
        self.logger = switcher.logger
        self.parent_command = parent_command
        try:
            self.image = Image.open(filename)
        except Exception as ex:
            message = "Image could not be opened: " + str(ex)
            raise ScraperSwitcherError(message, self.parent_command)
    
    def execute(self):
        """Process image with an OCR, depending on command configuration."""
        # Execute image child commands
        commands = self.parent_command.get("commands")
        if isinstance(commands, list):
            for child_command in commands:
                self.find_command(child_command)
        # Process text with an OCR
        text = self.image_to_text()
        # Check if it has the desired length
        length = self.parent_command.get("length", ScraperConfig.DEFAULT_KEY_LENGTH)
        if len(text) != length:
            self.logger.debug("Text does not have desired length, retrying...")
            return None
        # Check for possible problems in text
        filter_words = self.parent_command.get("filters")
        if not isinstance(filter_words, list):
            return text
        for word in filter_words:
            if word in text:
                self.logger.debug("Text has dangerous characters, retrying...")
                return None
        return text
    
    def find_command(self, command):
        try:
            # Get command type
            command_type = command.get("type")
            # Get command based on command type
            method = getattr(self, "command_" + command_type)
            # Execute command
            return method(command)
        except KeyError:
            raise ScraperSwitcherError("Image command type not found", self.parent_command)
        except AttributeError:
            raise ScraperSwitcherError("Image command type " + command_type + " is not valid",
                                               self.parent_command)
    
    def command_bnw(self, command):
        """Converts image to black and white."""
        # Get pixel pivot value, if it doesn't exist, assume default
        pivot = command.get("pivot", ScraperConfig.DEFAULT_BNW_PIVOT)
        if not isinstance(pivot, int):
            raise ScraperError("Image to black and white: pivot must be an integer")
        if pivot < 0 or pivot > 255:
            raise ScraperError("Image to black and white: pivot must be between [0, 255]")
        
        # Convert image to black and white
        self.image = Image.eval(self.image, lambda pixel: 0 if pixel <= pivot else 255)
    
    def image_to_text(self):
        config = "--psm 7"
        whitelist = ""
        
        # Check if we should include alphabetical letters
        if self.parent_command.get("alphabet", ScraperConfig.DEFAULT_KEY_ALPHABET):
            whitelist += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        # Check if we should include numeric letters
        if self.parent_command.get("numbers", ScraperConfig.DEFAULT_KEY_NUMBERS):
            whitelist += "1234567890"
        
        # Process image according to whitelist
        if whitelist:
            config += " -c tessedit_char_whitelist=" + whitelist
        
        # Clean whitespace and return
        text = pytesseract.image_to_string(self.image, config = config)
        return text.replace(" ", "")
