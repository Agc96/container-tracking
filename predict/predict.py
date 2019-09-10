import datetime
import logging
import os
import time

import joblib
import numpy as np
import pandas as pd
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

class TrackingPredictor:
    """Predictor for the Container Tracking."""

    PROCESSED = 2
    ESTIMATED = 3
    FILENAME = "predict.joblib"
    FOLDER = "preprocess-detailed"
    X_COLUMNS = ["carrier", "first_latitude", "first_longitude", "second_latitude", "second_longitude"]
    Y_COLUMN = "elapsed_days"
    SLEEP = 60 # seconds
    PRECISION = 0.0001
    LOG_LEVEL = logging.INFO

    def __init__(self):
        self.logger = self.get_logger()
        self.database = self.get_database()
        if os.path.exists(self.FILENAME):
            self.logger.info("Loading regressor from file...")
            self.regr = joblib.load(self.FILENAME)
        else:
            self.logger.info("Regressor file not found, starting training...")
            self.regr = self.get_regressor()

    def get_logger(self):
        """Initialize the logging file."""
        logger = logging.getLogger("TrackingPredictor")
        logger.setLevel(self.LOG_LEVEL)
        handler = logging.FileHandler("predict.log")
        handler.setLevel(self.LOG_LEVEL)
        formatter = logging.Formatter("[%(levelname)s %(asctime)s] %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def get_database(self):
        """Initialize the PostgreSQL connection."""
        return psycopg2.connect(cursor_factory=psycopg2.extras.DictCursor,
                                host=os.getenv("DB_HOST", "localhost"),
                                dbname=os.getenv("DB_NAME", "tracking"),
                                user=os.getenv("DB_USER", "predictor"),
                                password=os.getenv("DB_PASS"))

    def get_regressor(self):
        """Initialize and save the regressor if there was no persistance file available."""
        try:
            # Read datasets
            datasets = []
            for filename in os.listdir(self.FOLDER):
                datasets.append(pd.read_csv(self.FOLDER + "/" + filename))
            # Join datasets
            dataset = pd.concat(datasets)
            self.logger.info("%d containers found", len(dataset))
            # Get X and Y
            X = dataset[self.X_COLUMNS].values
            Y = dataset[self.Y_COLUMN].values
            self.logger.info("X shape = %s, Y shape = %s", X.shape, Y.shape)
            # Split into train and test
            X_train, X_test, Y_train, Y_test = train_test_split(X, Y)
            self.logger.info("%d to train, %d to test", len(X_train), len(X_test))
            # Train regressor
            regr = RandomForestRegressor(n_estimators=1000, random_state=0)
            regr.fit(X_train, Y_train)
            score = regr.score(X_test, Y_test)
            self.logger.info("Regressor score: %f", score)
            # Save regressor to disk
            joblib.dump(regr, self.FILENAME)
            return regr
        except:
            self.logger.exception("Exception occured while training/saving regressor")
            raise

    def predict(self):
        """Predict arrival dates for recently processed containers."""
        print("Starting prediction...")
        while True:
            try:
                with self.database as conn:
                    # Get the container
                    container = self.get_container(conn)
                    if container is None:
                        continue
                    self.logger.info("Container: %s (ID %d)", container["code"], container["id"])
                    # Get origin and destination point
                    origin = self.get_location(conn, container["origin_id"])
                    destination = self.get_location(conn, container["destination_id"])
                    self.logger.debug("Origin point: %s", origin)
                    self.logger.debug("Destination point: %s", destination)
                    # Get movements and compact them into deltas
                    movements = self.get_movements(conn, container["id"])
                    if self.check_movements(conn, container["id"], movements):
                        continue
                    # Compact movement into deltas
                    deltas = self.get_movement_deltas(origin, movements, destination)
                    if self.check_movement_deltas(conn, container["id"], deltas):
                        continue
                    # Predict arrival date for deltas marked as estimated
                    total_time, arrival_date = self.calculate_time(deltas, container["carrier_id"])
                    self.set_container(conn, container["id"], total_time, arrival_date)
            except KeyboardInterrupt:
                print()
                break
            except:
                self.logger.exception("Exception occured while predicting container")
                break
        print("Finished prediction.")

    def get_container(self, conn):
        """Get a container from the database, with status PROCESSED. If no container was found,
            sleep some time to allow other database connections to load more containers."""
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tracking_container WHERE status_id = %s LIMIT 1", (self.PROCESSED,))
            container = cur.fetchone()
        if container is None:
            self.logger.info("No containers found, sleeping...")
            time.sleep(self.SLEEP)
        return container

    def get_movements(self, conn, movement):
        """Get movement deltas from the container movements, the origin port and the destination port."""
        with conn.cursor() as cur:
            cur.execute("""SELECT latitude, longitude, date, estimated FROM tracking_movement mov
                           LEFT JOIN tracking_location loc ON mov.location_id = loc.id
                           WHERE container_id = %s ORDER BY date ASC""", (movement,))
            movements = cur.fetchall()
        # Log movement data if debugging is enabled
        self.logger.debug("Movement list:")
        for movement in movements:
            self.logger.debug(movement)
        return movements

    def get_location(self, conn, location):
        """Get a location from the database."""
        with conn.cursor() as cur:
            cur.execute("SELECT latitude, longitude FROM tracking_location WHERE id = %s", (location,))
            return cur.fetchone()

    def check_movements(self, conn, container, movements):
        """Check if the movement list is appropiate to continue. Returns True if movement list length
            has less than two movements, False otherwise."""
        if len(movements) == 0:
            self.logger.warning("No movements found in container")
            self.set_container(conn, container, 0, None)
            return True
        if len(movements) == 1:
            self.logger.warning("Only one movement found in container")
            self.set_container(conn, container, 0, movements[0]["date"])
            return True
        return False

    def get_movement_deltas(self, origin, movements, destination):
        """Get a list of timedeltas between locations between the movements."""
        deltas = []
        # Check if we should prepend the origin port to the movement deltas
        if origin is not None and not self.same_location(movements[0], origin):
            deltas.append(self.make_delta(origin, None, movements[0], True))
        # Iterate through movements
        for movement in movements:
            if len(deltas) > 0:
                last_delta = deltas[-1]
                # Set previous delta end date as this delta's start date
                last_delta["end_date"] = movement["date"]
                last_delta["timedelta"] = movement["date"] - last_delta["start_date"]
                # Do not save a new delta if it has the same location and estimated status
                if self.same_location(movement, last_delta, True):
                    continue
            # Save delta as [latitude, longitude, start_date, end_date, timedelta, estimated]
            deltas.append(self.make_delta(movement, movement, None, movement["estimated"]))
        # Check if we should append the origin port to the movement deltas
        if destination is not None and not self.same_location(movements[-1], destination):
            deltas.append(self.make_delta(destination, movements[-1], None, True))
        # Log movement delta data if debugging is enabled
        self.logger.debug("Movement deltas:")
        for delta in deltas:
            self.logger.debug(delta)
        return deltas

    def same_location(self, first, second, check_estimated=False):
        """Checks if two documents have the same location (approximate latitude and longitude).
            If `check_estimated` is enabled, also check if both have the same estimated status."""
        return (self.aprox_float(first["latitude"], second["latitude"]) and
                self.aprox_float(first["longitude"], second["longitude"]) and
                (not check_estimated or (first["estimated"] == second["estimated"])))

    def aprox_float(self, first, second):
        """Assumes two floats are the same if they are None or only differ in a specified precision."""
        return first is None or second is None or (abs(first - second) < self.PRECISION)

    def make_delta(self, location, start_movement=None, end_movement=None, estimated=True):
        """Makes a movement delta."""
        # Initialize values
        start_date = start_movement["date"] if start_movement else None
        end_date = end_movement["date"] if end_movement else None
        timedelta = (end_date - start_date) if (start_date and end_date) else None
        # Make the dictionary
        return {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "start_date": start_date,
            "end_date": end_date,
            "timedelta": timedelta,
            "estimated": estimated
        }

    def check_movement_deltas(self, conn, container, deltas):
        if len(deltas) == 0:
            self.logger.warning("No movement deltas found in container")
            self.set_container(conn, container, 0, None)
            return True
        if len(deltas) == 1:
            self.logger.warning("Less than two movement deltas found in container")
            self.set_container(conn, container, deltas[0]["timedelta"], deltas[0]["end_date"])
            return True
        return False

    def calculate_time(self, deltas, carrier):
        # Calculate total elapsed days
        total_days = datetime.timedelta(0)
        for index, delta in enumerate(deltas):
            # This should not happen
            if delta["start_date"] is None and delta["end_date"] is None:
                self.logger.error("Both start date and end date are None, skipping...")
                continue
            # Case 1: Start date does not exist but end date does (origin point)
            elif delta["start_date"] is None:
                delta["timedelta"] = self.estimate_time(carrier, delta, deltas[index + 1])
                delta["start_date"] = delta["end_date"] - delta["timedelta"]
            # Case 2: Start date exists but end date doesn't (destination point)
            elif delta["end_date"] is None:
                delta["timedelta"] = self.estimate_time(carrier, deltas[index - 1], delta)
                delta["end_date"] = delta["start_date"] + delta["timedelta"]
            # Add timedelta to total days
            if delta["timedelta"]:
                total_days += delta["timedelta"]
        # Estimate arrival date
        arrival_date = deltas[0]["start_date"]
        if arrival_date is None:
            self.logger.error("Start date is None after calculating elapsed days...")
        else:
            arrival_date += total_days
            self.logger.debug("Elapsed days: %s", total_days)
            self.logger.debug("Arrival date: %s", arrival_date)
        return total_days, arrival_date

    def estimate_time(self, carrier, first, second):
        """Create an input vector for the regressor and estimate the elapsed days for that
            movement delta."""
        vector = [carrier, first["latitude"], first["longitude"], second["latitude"], second["longitude"]]
        self.logger.debug("Creating input vector %s", vector)
        result = self.regr.predict([vector])
        if result:
            self.logger.debug("Predicted value was %f days", result[0])
            return datetime.timedelta(result[0])
        self.logger.error("No estimated value was found for the vector")
        return None

    def set_container(self, conn, container, total_time, arrival_date):
        """Set the estimated time and the arrival date for the container."""
        with conn.cursor() as cur:
            cur.execute("""UPDATE tracking_container SET arrival_date = %s, status_id = %s
                            WHERE id = %s""", (arrival_date, self.ESTIMATED, container))

if __name__ == "__main__":
    load_dotenv()
    TrackingPredictor().predict()
