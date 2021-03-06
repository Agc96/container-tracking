from pymongo import MongoClient, ASCENDING
from datetime import datetime

import csv
import os
import sys

class TrackingPreprocessor:
    """
    Class that preprocesses the intermodal container tracking-and-tracing information in database.
    """
    
    # TODO: No hardcodear esto
    CARRIERS = {
        "Maersk"      : 1,
        "Hapag-Lloyd" : 2,
        "Evergreen"   : 3
    }
    VEHICLES = {
        "Vessel" : 1,
        "Truck"  : 2,
        "Train"  : 3
    }
    
    def __init__(self, database_name):
        self.scraper_database   = MongoClient()[database_name]
        self.scraper_containers = self.scraper_database["containers"]
        self.scraper_movements  = self.scraper_database["container_movements"]
        self.scraper_statuses   = self.scraper_database["container_statuses"]
    
    def evaluate_carrier(self, carrier):
        """
        Preprocess all the containers for a specified carrier, and separate those in these categories:
        - Containers with no estimated movements, suitable for training with machine learning (finished)
        - Containers with finished movements, but first and last movements have the same locations (repeated_locations)
        - Containers with finished movements, but first and last movements have the same statuses (repeated_statuses)
        - Containers with finished movements, but first or last movements don't have location geocode information (missing)
        - Containers with estimated movements (estimated)
        - Containers with only one movement (single)
        - Containers with no movements (empty)
        - Containers with real movements before estimated movements (incoherent), this case should never happen.
        All those categories will be individually saved as files if there's at least one container that fits into that category.
        """
        finished, repeated_locations, repeated_statuses, missing = [], [], [], []
        estimated, single, empty, incoherent = [], [], [], []
        
        # Iterate through container query
        for container in self.query_containers(carrier):
            movements      = list(self.query_movements(container))
            movement_count = len(movements)
            
            # Case no movements found
            if movement_count == 0:
                empty.append(container)
                continue
            # Case only one movement found
            if movement_count == 1:
                self.save_one_movement(single, container, movements[0])
                continue
            
            # Get first and last movements
            first_movement = movements[0]
            last_movement  = movements[-1]
            # Case last movement is estimated
            if last_movement["estimated"] == True:
                self.save_movements(estimated, container, carrier, first_movement, last_movement, movement_count)
                continue
            # This case should never happen
            if first_movement["estimated"] == True:
                self.save_movements(incoherent, container, carrier, first_movement, last_movement, movement_count)
                continue
            # Case both movements contain real data
            self.preprocess_movements(finished, repeated_locations, repeated_statuses, missing, container,
                                      carrier, first_movement, last_movement, movement_count)
        
        # Create directory
        directory = self.create_parent_directory()
        print("{} information:".format(carrier))
        # Save containers ready for training
        if len(finished) > 0:
            self.save_to_csv(finished, directory, carrier, "train", "containers with finished movements")
        # Save containers with same locations in both extremes
        if len(repeated_locations) > 0:
            self.save_to_csv(repeated_locations, directory, carrier, "repeated-locations",
                             "containers with finished movements but same locations")
        # Save containers with same statuses in both extremes
        if len(repeated_statuses) > 0:
            self.save_to_csv(repeated_statuses, directory, carrier, "repeated-statuses",
                             "containers with finished movements but same statuses")
        # Save containers with missing locations
        if len(missing) > 0:
            self.save_to_csv(missing, directory, carrier, "missing",
                             "containers with finished movements but missing locations")
        
        # Save containers with estimated movements
        if len(estimated) > 0:
            self.save_to_csv(estimated, directory, carrier, "estimated", "containers with estimated movements")
        # Save containers with only one movement
        if len(single) > 0:
            self.save_to_csv(single, directory, carrier, "single", "containers with only one movement")
        # Save empty containers
        if len(empty) > 0:
            self.save_to_text(empty, directory, carrier, "empty", "containers with no movements")
        
        # Save incoherent containers
        if len(incoherent) > 0:
            self.save_to_csv(incoherent, directory, carrier, "incoherent", "incoherent containers found!")
    
    def query_containers(self, carrier):
        """
        Prepare the query for containers from the specified carrier.
        """
        query = {
            "carrier"   : carrier,
            "processed" : True
        }
        return self.scraper_containers.distinct("container", query)
    
    def query_movements(self, container):
        """
        Prepare the query for movements from the specified container.
        """
        query = {
            "container" : container
        }
        sort = [
            ("date", ASCENDING),
            ("_id",  ASCENDING)
        ]
        return self.scraper_movements.find(query).sort(sort)
    
    def save_one_movement(self, movements, container, movement):
        # Write header
        if len(movements) == 0:
            movements.append(["container", "date", "status", "location"])
        # Write content
        movements.append([container, movement["date"], movement["status"], movement["location"]])
    
    def preprocess_movements(self, finished, repeated_locations, repeated_statuses, missing, container, carrier,
                             first_movement, last_movement, movement_count):
        # Check if both movements are in the same location
        if first_movement["location"] == last_movement["location"]:
            self.save_movements(repeated_locations, container, carrier, first_movement, last_movement, movement_count)
            return
        # Check if both movements have the same status
        if first_movement["status"] == last_movement["status"]:
            self.save_movements(repeated_statuses, container, carrier, first_movement, last_movement, movement_count)
            return
        
        # Check if both movements have geocodes
        if ("latitude" not in first_movement) or ("longitude" not in first_movement):
            self.save_one_movement(missing, container, first_movement)
            return
        if ("latitude" not in last_movement) or ("longitude" not in last_movement):
            self.save_one_movement(missing, container, last_movement)
            return
        
        self.save_movements(finished, container, carrier, first_movement, last_movement, movement_count)
    
    def save_movements(self, movements, container, carrier, first_movement, last_movement, movement_count):
        # Write header
        if len(movements) == 0:
            movements.append(["container",
                             "carrier",
                             "timedelta",
                             "movement_count",
                             "first_date",
                             "first_status",
                             "first_status_code",
                             "first_location",
                             "first_latitude",
                             "first_longitude",
                             "first_vehicle",
                             "last_date",
                             "last_status",
                             "last_status_code",
                             "last_location",
                             "last_latitude",
                             "last_longitude",
                             "last_vehicle"])
        # Write content
        movements.append([
            # General information
            container,
            self.get_carrier_code(carrier),
            self.get_elapsed_days(first_movement, last_movement),
            movement_count,
            # First container information
            first_movement.get("date"),
            first_movement.get("status"),
            self.get_status_code(first_movement, carrier),
            first_movement.get("location"),
            first_movement.get("latitude"),
            first_movement.get("longitude"),
            self.get_vehicle_code(first_movement),
            # Last container information
            last_movement.get("date"),
            last_movement.get("status"),
            self.get_status_code(last_movement, carrier),
            last_movement.get("location"),
            last_movement.get("latitude"),
            last_movement.get("longitude"),
            self.get_vehicle_code(last_movement)
        ])
    
    def get_elapsed_days(self, first_movement, last_movement):
        """
        Get elapsed days between the first and last movements, in number of days (including decimals).
        """
        timedelta = last_movement["date"] - first_movement["date"]
        return timedelta.days + timedelta.seconds/(3600*24)
    
    def get_carrier_code(self, carrier):
        """
        Get the code associated with the carrier name.
        """
        return self.CARRIERS.get(carrier, 0)
    
    def get_status_code(self, movement, carrier):
        """
        Get the code associated with the status of the container in this movement.
        """
        if "status_code" in movement:
            return int(movement["status_code"])
        
        # Lookup in database
        query = {
            carrier : movement["status"]
        }
        result = self.scraper_statuses.find_one(query)
        
        # Return code as integer
        return int(result["code"]) if result else 0
    
    def get_vehicle_code(self, movement):
        """
        Get the code associated with the vehicle used in the container movement.
        """
        if "vehicle" not in movement:
            return 0
        if "vehicle_code" in movement:
            return movement["vehicle_code"]
        
        # Lookup in enumeration
        return self.VEHICLES.get(movement["vehicle"], 0)
    
    def create_parent_directory(self):
        """
        Create a directory for the preprocessed files.
        """
        directory = "preprocess/{}-{}".format(datetime.now().strftime("%Y%m%d"), self.scraper_database.name)
        if not os.path.exists(directory):
            os.mkdir(directory)
        return directory
    
    def save_to_csv(self, movements, directory, carrier, category, message = None):
        """
        Save movement information to a CSV file in the specified directory.
        """
        # Get filename
        filename = "{}/{}-{}.csv".format(directory, carrier, category)
        # Write CSV
        with open(filename, "w", newline = "") as file:
            writer = csv.writer(file)
            writer.writerows(movements)
        # Print message
        if message:
            print("-", len(movements) - 1, message)
    
    def save_to_text(self, containers, directory, carrier, category, message = None):
        """
        Save container information to a text file in the specified directory.
        """
        # Get filename
        filename = "{}/{}-{}.txt".format(directory, carrier, category)
        # Write text file
        with open(filename, "w") as file:
            for container in containers:
                file.write(container + "\n")
        # Print message
        if message:
            print("-", len(containers) - 1, message)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: {} <database_name>".format(sys.argv[0]))
        exit(1)
    preprocessor = TrackingPreprocessor(sys.argv[1])
    preprocessor.evaluate_carrier("Evergreen")
    preprocessor.evaluate_carrier("Maersk")
    preprocessor.evaluate_carrier("Hapag-Lloyd")
