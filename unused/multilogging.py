from datetime import datetime
from multiprocessing import Process
from random import randint
from selenium.webdriver import Chrome, ChromeOptions

import logging
import time

def process_web_pages(carrier):
    logger = prepare_logger(carrier)
    logger.warning("No debería poder ver los mensajes del webdriver en %s", carrier)
    driver = Chrome(executable_path = "C:/WebDriver/chromedriver")
    driver.get("https://www.example.com/{}".format(carrier))
    time.sleep(randint(10, 15))
    logger.info("Fin de la naviera %s", carrier)
    logger.debug("Debería poder ver esto en %s con logger.setLevel(logging.DEBUG)", carrier)
    driver.quit()

def prepare_logger(carrier):
    # Prepare formatter
    formatter = logging.Formatter("[%(levelname)s %(asctime)s] %(message)s")
    # Prepare handler
    today = datetime.now().strftime("%Y%m%d")
    handler = logging.FileHandler("scraper-{}-{}.log".format(carrier, today))
    handler.setFormatter(formatter)
    # Prepare logger
    logger = logging.getLogger("scraper-{}".format(carrier))
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger

if __name__ == "__main__":
    carriers = ["Maersk", "Hapag-Lloyd", "Evergreen", "Textainer"]
    processes = []
    # Crear procesos
    for carrier in carriers:
        p = Process(target = process_web_pages, args = (carrier,))
        processes.append(p)
        p.start()
    # Esperar a que terminen
    for p in processes:
        p.join()
