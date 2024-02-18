from domain.session_logger import SessionLogger as logger


def printTestResults(func):
    """Prints the test header & results to console in a readable format."""
    def wrapper(*args, **kwargs):
        logger.debug(kwargs.get("header"))

        result = func(*args, **kwargs)

        logger.debug(f'\t{result}')
        
        return result
    return wrapper
