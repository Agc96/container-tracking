# from error

class TrackingSelectorSwitcher:
    """Tracking Scraper switcher for selecting"""

    def __init__(self, selector, parent_element):
        """Constructor."""
        self.__selector = selector
        self.__parent_element = parent_element

    def asd(cls):
        pass

    def process(self):
        """
        Get DOM node(s) based on the configuration selector element
        declared in initialization, then process them accordingly.
        """

        # Get selector type
        selector_type = self.__selector.get("type")
        if selector_type is None:
            raise TrackingScraperError("")

        # Execute based on type
        try:
            method = getattr(self, "_process_by_" + selector_type)
            self.method(selector_value)
        except KeyError:
            print("")
            return False

        return True
    
    def _process_by_id(self, selector):
        # Get selector value
        selector_value = self.__selector.get("value")
        if selector_value is None:
            return False

        element = self.__parent_element.find_element_by_id(selector_value)
        pass

    def _process_by_class(self, selector):
        # Get selector value
        selector_value = self.__selector.get("value")
        if selector_value is None:
            return False

        elements = self.__parent_element.find_elements_by_class(selector_value)
        pass

    def _process_elements_by_css_selector(self):
        print("css")
        pass

