# mongoexport -d tracking_scraper -c containers
# mongoexport -d tracking_scraper -c 

while True:
    containers = []
    query = {
        "carrier": "Hapag-Lloyd",
        "processed": False
    }
    for container in container_table.find(query).sort("_id", -1).limit(200):
        containers.append(container)
    if len(container) == 0:
        break

    fail_counter = 0
    start = time.time()
    driver = webdriver.Chrome(executable_path = TrackingScraperConfig.DEFAULT_PATH_CHROME)
    
    for container in containers:
        if fail_counter >= 10:
            print("Too much failures, aborting")
            break
        cont_start = time.time()
        try:
            scraper = TrackingScraper(driver, database, container)
            if not scraper.execute():
                fail_counter = fail_counter + 1
                logging.error("Scraper for container %s unsuccessful", container["container"])
        except TrackingScraperError as ex:
            fail_counter = fail_counter + 1
            logging.error("Error extracting container information: %s", str(ex))
            continue
        except Exception:
            fail_counter = fail_counter + 1
            logging.exception("Unknown exception ocurred when creating or executing scraper")
            break
        finally:
            cont_end = time.time()
            logging.info("Container time:", cont_end - cont_start, "seconds")
    # input("Press Enter to quit")
    driver.close()
    end = time.time()
    print("Total time:", end - start, "seconds")
    
    # Wait 1 minute to start again
    time.sleep(60)
