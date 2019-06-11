from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime

import pandas as pd
import numpy as np
import os
import csv

class TrackingDetailedPreprocessor:
    """
    Class that preprocesses every intermodal container movement information in the database.
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
        self.scraper_db_name    = database_name
        self.scraper_database   = MongoClient()[database_name]
        self.scraper_containers = self.scraper_database["containers"]
        self.scraper_movements  = self.scraper_database["container_movements"]
        self.scraper_statuses   = self.scraper_database["container_statuses"]
    
    def evaluate_carrier(self, carrier):
        """
        Preprocess all the container movement deltas for a specified carrier, and separate those in these categories:
        - Finished movement deltas suitable for training with machine learning (finished)
        - Finished movement deltas, but first and second movements have the same locations (repeated_locations)
        - Finished movement deltas, but first and second movements have the same statuses (repeated_statuses)
        - Finished movement deltas, but first or second movements don't have location geocode information (missing)
        - Estimated movement deltas (estimated)
        - Containers with only one movement (single)
        - Containers with no movements (empty)
        - Containers with finished movements before estimated movements (incoherent), this case should never happen.
        All those categories will be individually saved as files if there's at least one container movement delta
        that fits into that category.
        """
        finished, repeated_locations, repeated_statuses, repeated_delta, missing = [], [], [], [], []
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
            # Case more than one movement found
            for index, second_movement in enumerate(movements):
                if index == 0:
                    continue
                first_movement = movements[index - 1]
                self.preprocess_movements(finished, repeated_locations, repeated_statuses, repeated_delta, missing,
                                          estimated, incoherent, container, carrier, first_movement, second_movement)
        
        # Save container movement information
        self.save_information(carrier, [
            ("train", finished, "finished movement deltas", True),
            ("repeated-locations", repeated_locations, "finished movement deltas but with same locations", True),
            ("repeated-statuses", repeated_statuses, "finished movement deltas but with same statuses", True),
            ("repeated-delta", repeated_delta, "repeated finished movement deltas", True),
            ("missing", missing, "finished movement deltas but with missing geocodes", True),
            ("estimated", estimated, "estimated movement deltas", True),
            ("single", single, "containers with only one movement", True),
            ("empty", empty, "containers with no movements", False),
            ("incoherent", incoherent, "incoherent containers found!", True)
        ])
    
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
    
    def save_one_movement(self, movement_list, container, movement):
        """
        Save basic data from a single container movement onto a movement list.
        """
        movement_list.append({
            "container" : container,
            "date"      : movement["date"],
            "status"    : movement["status"],
            "location"  : movement["location"]
        })
    
    def preprocess_movements(self, finished, repeated_locations, repeated_statuses, repeated_delta, missing, estimated,
                             incoherent, container, carrier, first_movement, second_movement):
        # Case second movement is estimated
        if second_movement["estimated"] == True:
            self.save_movement_delta(estimated, container, carrier, first_movement, second_movement)
            return
        # Case first movement is estimated but second one is not. This case should never happen.
        if first_movement["estimated"] == True:
            self.save_movement_delta(incoherent, container, carrier, first_movement, second_movement)
            return
        # Case both movements are finished but are in the same location
        if first_movement["location"] == second_movement["location"]:
            self.save_movement_delta(repeated_locations, container, carrier, first_movement, second_movement)
            return
        # Case both movements are finished but have the same status
        if first_movement["status"] == second_movement["status"]:
            self.save_movement_delta(repeated_statuses, container, carrier, first_movement, second_movement)
            return
        # Case both movements are finished but one movement has no geocodes (save only the movement with the geocode missing)
        if ("latitude" not in first_movement) or ("longitude" not in first_movement):
            self.save_one_movement(missing, container, first_movement)
            return
        if ("latitude" not in second_movement) or ("longitude" not in second_movement):
            self.save_one_movement(missing, container, second_movement)
            return
        # Case both movements are already in the finished movement list
        for movement_delta in finished:
            if self.is_same_movement_delta(movement_delta, carrier, first_movement, second_movement):
                self.save_movement_delta(repeated_delta, container, carrier, first_movement, second_movement)
                return
        # Case both movements are finished and don't have any issues
        self.save_movement_delta(finished, container, carrier, first_movement, second_movement)
    
    def is_same_movement_delta(self, movement_delta, carrier, first_movement, second_movement):
        # Check carrier code
        if movement_delta["carrier"] != self.get_carrier_code(carrier):
            return False
        # Check elapsed days
        if movement_delta["elapsed_days"] != self.get_elapsed_days(first_movement, second_movement):
            return False
        # Check first movement geocode
        if movement_delta["first_latitude"] != first_movement.get("latitude"):
            return False
        if movement_delta["first_longitude"] != first_movement.get("longitude"):
            return False
        # Check second movement geocode
        if movement_delta["second_latitude"] != second_movement.get("latitude"):
            return False
        if movement_delta["second_longitude"] != second_movement.get("longitude"):
            return False
        # This is the same movement delta, save it onto the movement list
        return True
    
    def save_movement_delta(self, movement_list, container, carrier, first_movement, second_movement):
        movement_list.append({
            # General information
            "container"          : container,
            "carrier"            : self.get_carrier_code(carrier),
            "elapsed_days"       : self.get_elapsed_days(first_movement, second_movement),
            # First container information
            "first_date"         : first_movement.get("date"),
            "first_status"       : first_movement.get("status"),
            "first_status_code"  : self.get_status_code(first_movement, carrier),
            "first_location"     : first_movement.get("location"),
            "first_latitude"     : first_movement.get("latitude"),
            "first_longitude"    : first_movement.get("longitude"),
            "first_vehicle"      : self.get_vehicle_code(first_movement),
            # Second container information
            "second_date"        : second_movement.get("date"),
            "second_status"      : second_movement.get("status"),
            "second_status_code" : self.get_status_code(second_movement, carrier),
            "second_location"    : second_movement.get("location"),
            "second_latitude"    : second_movement.get("latitude"),
            "second_longitude"   : second_movement.get("longitude"),
            "second_vehicle"     : self.get_vehicle_code(second_movement)
        })
    
    def get_elapsed_days(self, first_movement, second_movement):
        """
        Get elapsed days between the first and second movements, in number of days (including decimals).
        """
        elapsed_days = second_movement["date"] - first_movement["date"]
        return elapsed_days.days + elapsed_days.seconds/(3600*24)
    
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
    
    def save_information(self, carrier, configuration):
        directory = self.create_parent_directory()
        print("{} information:".format(carrier))
        for category, movement_list, message, is_csv in configuration:
            # Get movement list count
            count = len(movement_list)
            if count == 0:
                continue
            # Print message
            print("-", count, message)
            # Save file to CSV or text
            method = self.save_to_csv if is_csv else self.save_to_text
            method(movement_list, directory, carrier, category)
    
    def create_parent_directory(self):
        """
        Create a directory for the preprocessed files.
        """
        directory = "preprocess-{}".format(datetime.now().strftime("%Y%m%d"))
        if not os.path.exists(directory):
            os.mkdir(directory)
        return directory
    
    def save_to_csv(self, movement_list, directory, carrier, category):
        """
        Save movement information to a CSV file in the specified directory.
        """
        filename = "{}/{}-{}.csv".format(directory, carrier, category)
        with open(filename, "w", newline = "") as file:
            writer = csv.DictWriter(file, movement_list[0].keys())
            writer.writeheader()
            writer.writerows(movement_list)
    
    def save_to_text(self, movement_list, directory, carrier, category):
        """
        Save movement information to a text file in the specified directory.
        """
        filename = "{}/{}-{}.txt".format(directory, carrier, category)
        with open(filename, "w") as file:
            for container in movement_list:
                file.write(container + "\n")

if __name__ == "__main__":
    preprocessor = TrackingDetailedPreprocessor("scraper2")
    preprocessor.evaluate_carrier("Evergreen")
    preprocessor.evaluate_carrier("Maersk")
    preprocessor.evaluate_carrier("Hapag-Lloyd")
