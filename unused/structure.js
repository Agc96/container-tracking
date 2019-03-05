// MAERSK:

general["origin"]
general["destination"]
general["estimated_arrival"]
container["code"] // dato
container["description"]
last_route["status"]
last_route["location"]
last_route["date"]
movements[0]["location"]
movements[0]["date"]
movements[0]["time"]
movements[0]["status"]
movements[0]["transport_ship"]
movements[0]["transport_voyage"]
movements[0]["is_estimated"] // calculado

// HAPAG LLOYD:

container["code"] // dato
container["type"]
container["description"]
container["tare"]
last_route["location"]
last_route["date"]
routes[0]["status"]
routes[0]["location"]
routes[0]["date"]
routes[0]["time"]
routes[0]["transport"]["ship"]
routes[0]["transport"]["voyage"]
routes[0]["is_estimated"] // calculado

// EVERGREEN:

container["code"] // dato
container["type"]
routes[0]["status"]
routes[0]["location"]
routes[0]["date"]
routes[0]["transport"]["voyage"]
routes[0]["is_estimated"] = false // always false
