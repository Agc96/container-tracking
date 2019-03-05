// MAERSK

container = "MAEU6835658"
tracking = {
    "general": {},
    "container": {
        "code": container
    },
    "last_route": {},
    "routes": []
}

/////////////////////////////////////////////////

elements = $('.font--display-1--heavy')

// Origin point
tracking["general"]["origin"] = elements[0].innerText

// Destination point
tracking["general"]["destination"] = elements[1].innerText

/////////////////////////////////////////////////

elements = $('.expandable-table__wrapper td')

// Container description
subelements = $(elements[1]).find('span')
tracking["container"]["description"] = subelements[3].innerText

// Estimated arrival time
subelements = $(elements[2]).find('span')
tracking["general"]["est_arrival"] = subelements[3].innerText

// 

/////////////////////////////////////////////////

// HAPAG-LLOYD

tracking = {
    "container": container,
    "routes": []
}

elements = driver.find_element(By.CLASS, 'inputNonEdit')
// 
tracking["container"]["type"] = elements[0].text
tracking["container"]["description"] = elements[1].text
tracking[""]

/////////////////////////////////////////////////

elements = driver.find_elements(By.CSS_SELECTOR, '.hal-table tbody tr')
for (element in elements) {
    // Obtener items y definir nueva ruta
    items = element.find_elements(By.TAG_NAME, 'td')
    movement = {
        "transport": []
    }
    // Estado del contenedor
    movement["status"]              = items[0].text
    // Ubicación del contenedor 
    movement["location"]            = items[1].text
    // Fecha del movimiento del contenedor
    movement["date"]                = items[2].text
    // Hora del movimiento del contendor
    movement["time"]                = items[3].text
    movement["transport"]["ship"]   = items[4].text
    movement["transport"]["voyage"] = items[5].text
    tracking["movements"].append(movement)
}

///////////////////////////////////////////////

// EVERGREEN:
