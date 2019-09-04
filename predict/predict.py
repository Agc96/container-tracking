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

    FILENAME = "predict.joblib"
    FOLDER = "preprocess-detailed"
    X_COLUMNS = ["carrier", "first_latitude", "first_longitude", "second_latitude", "second_longitude"]
    Y_COLUMN = "elapsed_days"
    SLEEP = 60 # seconds

    def __init__(self):
        self.logger = self.get_logger()
        self.database = self.get_database()
        if os.path.exists(self.FILENAME):
            self.logger.info("Loading regressor from file...")
            self.regr = joblib.load(self.FILENAME)
        else:
            self.logger.warning("Regressor file not found, starting training...")
            self.regr = self.get_regressor()

    def get_logger(self):
        """Initialize the logging file."""
        logger = logging.getLogger("TrackingPredictor")
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler("predict.log")
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("[%(levelname)s %(asctime)s] %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def get_database(self):
        """Initialize the PostgreSQL connection."""
        dsn = {
            "cursor_factory": psycopg2.extras.DictCursor,
            "host": os.getenv("DB_HOST", "localhost"),
            "dbname": os.getenv("DB_NAME", "tracking"),
            "user": os.getenv("DB_USER", "predictor"),
            "password": os.getenv("DB_PASS")
        }
        return psycopg2.connect(**dsn)

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
            logging.exception("Exception occured while training/saving regressor")
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
                    # Get location data
                    origin = self.get_location(conn, container["origin_id"])
                    destination = self.get_location(conn, container["destination_id"])
                    # Predict arrival date
                    X = [container["carrier"], origin[0], origin[1], destination[0], destination[1]]
                    Y = self.regr.predict(X)
                    # TODO
                    arrival = datetime.datetime.now()
                    # Save the container
                    with conn.cursor() as cur:
                        cur.execute("UPDATE tracking_container SET arrival_date = %s WHERE container_id = %s",
                            (arrival, container["id"]))
            except KeyboardInterrupt:
                print()
                break
            except:
                logging.exception("Exception occured while predicting container")
                break
        print("Finished prediction.")

    def get_container(self, conn):
        """
        Get a container from the database, with status 1 (PROCESSED). If no container was found, sleep a
        minute to allow other database instances to load more containers.
        """
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tracking_container WHERE status = 1 LIMIT 1")
            container = cur.fetchone()
        if container is None:
            self.logger.info("No containers found, sleeping for a minute.")
            time.sleep(self.SLEEP)
        return container

    def get_location(self, conn, id):
        """Get the location from the database, with the specified ID."""
        with conn.cursor() as cur:
            cur.execute("SELECT latitude, longitude FROM tracking_location WHERE id = %s", (id,))
            return cur.fetchone()

    def set_container(self, container, arrival):
        """Set the arrival date for the container."""
        pass

if __name__ == "__main__":
    load_dotenv()
    TrackingPredictor().predict()
