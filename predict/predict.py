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
    FILENAME = "predict.joblib"
    FOLDER = "preprocess-detailed"
    X_COLUMNS = ["carrier", "first_latitude", "first_longitude", "second_latitude", "second_longitude"]
    Y_COLUMN = "elapsed_days"
    SLEEP = 60 # seconds
    LOG_LEVEL = logging.DEBUG

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
                    self.logger.debug("Container ID: %d", container["id"])
                    # Get origin and destination point
                    origin = self.get_location(conn, container["origin_id"])
                    destination = self.get_location(conn, container["destination_id"])
                    self.logger.debug("Origin point: %s", origin)
                    self.logger.debug("Destination point: %s", destination)
                    # Get movements and compact them into deltas
                    movements = self.get_movements(conn, container["id"])
                    deltas = self.get_movement_deltas(origin, movements, destination)
                    # Predict arrival date for deltas marked as estimated
                    break
                    # Predict arrival date
                    # X = [container["carrier"], origin[0], origin[1], destination[0], destination[1]]
                    # Y = self.regr.predict(X)
                    # Save the container
                    # self.set_container(conn, container, arrival)
            except KeyboardInterrupt:
                print()
                break
            except:
                self.logger.exception("Exception occured while predicting container")
                break
        print("Finished prediction.")

    def get_container(self, conn):
        """ Get a container from the database, with status PROCESSED. If no container was found,
            sleep some time to allow other database connections to load more containers. """
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tracking_container WHERE status_id = %s LIMIT 1", (self.PROCESSED,))
            container = cur.fetchone()
        if container is None:
            self.logger.info("No containers found, sleeping...")
            time.sleep(self.SLEEP)
        return container

    def get_movements(self, conn, id):
        """Get movement deltas from the container movements, the origin port and the destination port."""
        with conn.cursor() as cur:
            cur.execute("""SELECT latitude, longitude, date, estimated FROM tracking_movement mov
                           LEFT JOIN tracking_location loc ON mov.location_id = loc.id
                           WHERE container_id = %s ORDER BY date ASC""", (id,))
            movements = cur.fetchall()
        # Log movement data if debugging is enabled
        self.logger.debug("Movement list:")
        for movement in movements:
            self.logger.debug(movement)
        return movements

    def get_location(self, conn, id):
        """Get a location from the database."""
        with conn.cursor() as cur:
            cur.execute("SELECT latitude, longitude FROM tracking_location WHERE id = %s", (id,))
            return cur.fetchone()

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
                last_delta[3] = movement[2]
                last_delta[4] = movement[2] - last_delta[2]
                # Do not save a new delta if it's the same location, edit the last one instead
                if self.same_location(movement, last_delta) and movement[3] == last_delta[5]:
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

    def same_location(self, first, second, check_estimated=True):
        """Checks if two documents with location information have the same location (approximate latitude and
           approximate longitude)."""
        def aprox_float(first, second, precision=0.0001):
            return abs(first - second) < precision
        return aprox_float(first[0], second[0]) and aprox_float(first[1], second[1])

    def make_delta(self, location, start_movement=None, end_movement=None, estimated=True):
        """Makes a movement delta with the format `[latitude, longitude, start date, end date, time delta,
           estimated]`."""
        # Initialize values
        start_date = start_movement["date"] if start_movement else None
        end_date = end_movement["date"] if end_movement else None
        timedelta = (end_date - start_date) if (start_date and end_date) else None
        # Make the dictionary
        return [location["latitude"], location["longitude"], start_date, end_date, timedelta, estimated]

    def set_container(self, conn, container, arrival):
        """Set the estimated time and the arrival date for the container."""
        with conn.cursor() as cur:
            cur.execute("UPDATE tracking_container SET arrival_date = %s WHERE container_id = %s",
                (arrival, container["id"]))

if __name__ == "__main__":
    load_dotenv()
    TrackingPredictor().predict()
