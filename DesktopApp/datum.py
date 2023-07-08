
class Datum:
    def __init__(self, pID, gID, name):
        self.pID = pID
        self.gID = gID
        self.name = name

    def __cmp__(self, other):
        if self.pID < other.pID:
            return -1
        elif self.pID > other.pID:
            return 1
        else:
            if self.gID < other.gID:
                return -1
            elif self.gID > other.gID:
                return 1
            else:
                if self.name < other.name:
                    return -1
                elif self.name > other.name:
                    return 1
                else:
                    return 0

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __str__(self):
        return f"{self.pID},{self.gID},{self.name}"
