
def singleton(cls):
    """Ensures the class is only ever allowed to have one instance."""
    instances = {}
    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return get_instance()

