import logging
import os
from datetime import datetime
import app.style.better_print as better_print

log_path = 'logs'

if not os.path.exists(log_path):
    os.makedirs(log_path)

current_datetime = datetime.now().strftime('%Y-%m-%d')
log_filename = f'{log_path}/app_log_{current_datetime}.log'

logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

def log_info(info):
    better_print.try_print(info)
    logger.info(info)

def log_warning(warning):
    better_print.try_print(warning)
    logger.warning(warning)

def log_error(error):
    better_print.try_print(error)
    logger.error(error)