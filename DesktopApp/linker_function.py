

class LinkerFunction:
    def __init__(self, label, tag, callable):
        self.label = label
        self.output_filename = "".join(label.split(" ")) + ".txt"
        self.tag = tag
        self.callable = callable