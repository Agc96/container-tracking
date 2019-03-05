# MAERSK

container = "MAEU6835658"
tracking = {
    "general": {},
    "container": {
        "code": container
    },
    "last_route": {},
    "routes": []
}

#################################################

elements = $('.font--display-1--heavy')

# Origin point
tracking["general"]["origin"] = elements[0].innerText

# Destination point
tracking["general"]["destination"] = elements[1].innerText

#################################################

elements = $('.expandable-table__wrapper td')

# Container description
subelements = $(elements[1]).find('span')
tracking["container"]["description"] = subelements[3].innerText

# Estimated arrival time
subelements = $(elements[2]).find('span')
tracking["general"]["est_arrival"] = subelements[3].innerText

# 

#################################################

# HAPAG-LLOYD

container = "FSCU5670046"
tracking = {
    "container": {
        "type": container
    },
    "movements": []
}


#################################################


###############################################

# EVERGREEN:
