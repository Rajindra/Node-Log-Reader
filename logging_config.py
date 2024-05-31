import logging
import logging.config

def setup_logging(log_file='application.log'):
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            },
        },
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'formatter': 'standard',
                'class': 'logging.FileHandler',
                'filename': log_file,
            },
            'console': {
                'level': 'DEBUG',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['file', 'console'],
                'level': 'DEBUG',
                'propagate': True
            },
        }
    }

    logging.config.dictConfig(logging_config)

# Call setup_logging when this module is imported
setup_logging()
