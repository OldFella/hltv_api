
class DomainError(Exception):
    pass

class NotFoundError(DomainError):
    def __init__(self, item:str):
        self.item = item
        super().__init__(f"{item} not found")


