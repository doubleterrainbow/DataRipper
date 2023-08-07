

class LinkerFunction:
    def __init__(self, label, tags, callable):
        self.label = label
        self.output_filename = "".join(label.split(" ")) + ".txt"
        self.tags = tags
        self.callable = callable