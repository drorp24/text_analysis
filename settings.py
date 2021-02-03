import os
import logging
from dotenv import load_dotenv
# Env
load_dotenv(verbose=True)

# Logger
format_ = '%(asctime)s - %(module)s - %(levelname)s: %(message)s'
log_level = os.getenv('LOG_LEVEL') if os.getenv('LOG_LEVEL') is not None else logging.DEBUG
logging.basicConfig(level=log_level, format=format_, datefmt="%Y-%m-%d %H:%M:%S")
