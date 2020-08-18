class Common:
    TYPE_CONVERSION = {}

    def __init__(self):
        self.TYPE_CONVERSION = {
            "INT": "Int64",
            "FLOAT": 'float64',
            "DISTRIB": 'object',
            "PERCENT": 'float64',
            "MILLISEC": 'float64',
            "DATA": 'object',
            "BOOL": 'bool',
            "STRING": 'object',
            "WORK_DUR": 'float64',
            "RATING": 'float64',
            "LEVEL": 'float64'
        }
