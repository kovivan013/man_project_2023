import uuid
from pydantic import BaseModel

class Utils:

    def get_uuid(self):
        return str(uuid.uuid4())

    # delete
    def as_dict(self, data: dict = None):
        if data is None:
            data = vars(self).copy()
        for i, v in data.items():
            try:
                data[i] = v.__dict__
                self.as_dict(data=data[i])
            except Exception as err:
                continue

        return data

# class BaseUser(Utils):
#     def __init__(self):
#         self.telegram_id: int = 0
#         self.username: str = ""
#         self.user_data = self.UserData()
#         self.gigs = self.Gigs()
#
#     class UserData:
#         def __init__(self):
#             self.description: str = ""
#             self.badges: list = []
#
#     class Gigs:
#         def __init__(self):
#             self.active: dict = {}
#             self.completed: dict = {}
#             self.archived: dict = {}
#             self.pending: dict = {}
#
#     def as_class(self, data: dict, path: str = ""):
#
#         for i, v in data.items():
#             if isinstance(v, dict) and v:
#                 path += f" {i}" if path else f"{i}"
#                 self.as_class(data=v,
#                               path=path)
#                 continue
#
#             keys = path.split()
#             name = i
#             value = v
#
#             if keys:
#                 attribute = getattr(self, keys[0])
#                 if len(keys) > 1:
#                     for i in keys[1:]:
#                         attribute = getattr(self, i)
#                 setattr(attribute, name, value)
#             else:
#                 setattr(self, name, value)



# u = BaseUser()
# data = {'telegram_id': 5633345, 'username': 'gffdgdgf', 'user_data': {'description': 'sfgsfgs', 'badges': []}, 'gigs': {'active': {}, 'completed': {}, 'archived': {}, 'pending': {}}}
#
# u.as_class(data=data)
#
# print(u.as_dict())
