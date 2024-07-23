class CustomParametersException(Exception):
    def __init__(self, message="Required parameters are missing.", code=400):
        self.message = message
        self.code = code
        super().__init__(self.message)
