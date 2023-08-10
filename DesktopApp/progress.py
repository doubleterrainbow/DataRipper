
class Progress:
    def __init__(self, message: str, current_progress = 0, max_progress = None, error = None, complete = False) -> None:
        self.current_progress = current_progress
        self.message = message
        self.max_progress = max_progress
        self.error = error
        self.complete = complete
        
