import audioop

class Coder:

    def __init__(self, width=2):
        self.width = width
        self.state = None

    def code(self, data):
        data, self.state = audioop.lin2adpcm(data, self.width, self.state)
        return data

class Decoder:

    def __init__(self, width=2):
        self.width = width
        self.state = None

    def decode(self, data):
        data, self.state = audioop.adpcm2lin(data, self.width, self.state)
        return data

