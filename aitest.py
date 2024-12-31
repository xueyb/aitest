import os
import logging
from core import engine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    engine.Engine(os.getcwd()).start()
