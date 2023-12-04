class Utils:

    def as_dict(self, data: dict = None):
        if data is None:
            data = self.__dict__
        for i, v in data.items():
            try:
                value = v.__dict__
                data[i] = value
                self.as_dict(data=data[i])
            except:
                continue

        return data