import logging
import os

# Create a logs directory if it doesn't exist
logs_dir = 'logs'
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

def setup_logging():
    loggers = {
        'map': {'filename': 'map.log', 'level': logging.DEBUG},
        'combat': {'filename': 'combat.log', 'level': logging.INFO},
        'boot': {'filename': 'boot.log', 'level': logging.DEBUG},
        'connector': {'filename': 'connector.log', 'level': logging.DEBUG}
    }

    for logger_name, logger_info in loggers.items():
        log_file = os.path.join(logs_dir, logger_info['filename'])
        setup_logger(logger_name, log_file, logger_info['level'])

def setup_logger(name, log_file, level=logging.DEBUG):
    handler = logging.FileHandler(log_file, mode='w')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)