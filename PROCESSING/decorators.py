

def printTestResults(func):
    def wrapper(*args, **kwargs):
        if kwargs.get("print_out"): print(kwargs.get("header"))
        result = func(*args, **kwargs)
        if kwargs.get("print_out"): print('\t', result, sep='')
        return result
    return wrapper