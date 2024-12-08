import time

def pure_import():
    start_time = time.time()
    import dateparser
    end_time = time.time()
    print(f"Time taken to import dateparser for the first time: {end_time - start_time} seconds")

def some_function():
    start_time = time.time()
    import dateparser
    end_time = time.time()
    print(f"Time taken to import dateparser for the second time: {end_time - start_time} seconds")
