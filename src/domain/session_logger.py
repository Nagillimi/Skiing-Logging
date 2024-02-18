import logging
import os
from utilities.decorators.singleton import singleton


@singleton
class SessionLogger(logging.Logger):
    def __init__(self) -> None:
        super().__init__('session')
        formatter = logging.Formatter('%(levelname)s: %(asctime)s - %(message)s')

        self.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        console_handler.setFormatter(formatter)
        self.addHandler(console_handler)

        file_handler = logging.FileHandler(os.path.join(os.getcwd().split('src')[0], 'logs/session-error.log'), 'w')
        file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(formatter)
        self.addHandler(file_handler)

        file_handler = logging.FileHandler(os.path.join(os.getcwd().split('src')[0], 'logs/session-debug.log'), 'w')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.addHandler(file_handler)

        file_handler = logging.FileHandler(os.path.join(os.getcwd().split('src')[0], 'logs/session-info.log'), 'w')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.addHandler(file_handler)
