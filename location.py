class Location:
    def __init__(self, start_line, end_line, start_char, end_char):
        self.start_line = start_line
        self.end_line = end_line
        self.start_char = start_char
        self.end_char = end_char

    def __repr__(self):
        return str(self.start_line) + ":" + str(self.start_char) + "-" \
            + str(self.end_line) + ":" + str(self.end_char)
