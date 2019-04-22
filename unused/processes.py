from multiprocessing import Process
from random import randint
from selenium.webdriver import Chrome, ChromeOptions

import os
import time

def process_web_pages(name, number, iterations):
    # Create WebDriver
    options = ChromeOptions()
    options.add_argument("--start-maximized")
    driver = Chrome(executable_path = "../../scraper/driver/chromedriver", options = options)
    # Load page "iterations" times
    for i in range(iterations):
        print("{}: iteration {} of {}".format(name, i+1, iterations))
        driver.get("http://localhost/pytests/page-{}.html".format(number))
        time.sleep(10)
    # Notify finishing and close driver
    print("Finished with", name)
    driver.quit()

if __name__ == "__main__":
    names = ["Maersk", "Hapag-Lloyd", "Evergreen", "Textainer"]
    # Create processes
    processes = []
    for index in range(4):
        iterations = randint(5, 10)
        p = Process(target = process_web_pages, args = (names[index], index + 1, iterations))
        processes.append(p)
        p.start()
    # Wait for processes
    for p in processes:
        p.join()
    print("Finished execution!")
