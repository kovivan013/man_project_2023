import uuid


class Utils:

    @staticmethod
    def get_uuid():
        return str(uuid.uuid4())

    @classmethod
    def sort_by(cls, obj: dict, path: list,
                reverse: bool = True):
        sorted_obj = dict(sorted(
            obj.items(),
            key=lambda x: cls.get_value(x[1], path=path),
            reverse=reverse
        ))

        return sorted_obj

    @classmethod
    def get_value(cls, obj: dict, path: list):
        for i in path:
            obj = obj.setdefault(i)
        return obj