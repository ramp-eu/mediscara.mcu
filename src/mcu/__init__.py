import coloredlogs
import logging

coloredlogs.install(fmt='%(asctime)s %(funcName)s %(levelname)s %(message)s', level=logging.INFO)