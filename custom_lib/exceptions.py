class MyException(Exception):
    def __init__(self, message, status=500):
        super().__init__(message)
        self.status = status

    def to_dict(self):
        return {
            'message': str(self),
            'status': self.status,
        }