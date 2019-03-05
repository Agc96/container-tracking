class ContainerScraper:
    
    selector_types = {
        "id":      By.ID,
        "class":   By.CLASS_NAME,
        "css":     By.CSS_SELECTOR,
        "tag":     By.TAG_NAME,
        "xpath":   By.XPATH
    }
    
    def __init__(self, carrier, container):
        self.driver = webdriver.Firefox()
        self.config = json.dumps(carrier + ".json")
        self.container = container
    
    def go_to_page (self):
        url = self.config["url"].format(container = self.container)
        self.driver.get(url)

    def save_general_info (self):
        general_info = self.config["output"]["general_info"]
        # Obtener el tipo de búsqueda
        selector_type = selector_types.get(general_info["type"])
        if (selector_type is None):
            return False
        # Obtener la lista de elementos
        elements = self.driver.find_elements(selector_type, general_info["selector"])
        # Guardar cada atributo definido según la información del elemento
        for attribute, index in general_info["attributes"].items():
            try:
                tracking[attribute] = elements[index].text
            except IndexError:
                return False
        return True
