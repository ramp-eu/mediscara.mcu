import coloredlogs
import logging

coloredlogs.install(fmt='%(asctime)s %(hostname)s %(name)s[%(process)d] %(levelname)s %(message)s', level=logging.INFO)