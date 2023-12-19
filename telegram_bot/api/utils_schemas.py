from pydantic import BaseModel

# class PayloadStructure:
#
#     def add(self,
#             telegram_id: int = 0,
#             username: str = "",
#             name: str = "",
#             description: str = "",
#             photo: str = "",
#             tags: list = [],
#             location: dict = {},
#             address: dict = {},
#             date: int = 0
#             ):
#         data: dict = locals()
#         data.pop("self")
#         for i, v in data.items():
#             if v:
#                 setattr(self, i, v)
#
#         print(self.as_dict())
#
#     def as_dict(self) -> dict:
#         return self.__dict__

class StateProxy(BaseModel):
    file_id: str = ""

class ResponseStructure:
    def __init__(self, status: int, data: dict):
        self.status = status
        self.data = data

    def as_dict(self) -> dict:
        return self.__dict__

class StateStructure:
    def __init__(self, caption: str, media):
        self.caption = caption
        self.media = media

    def as_dict(self) -> dict:
        return self.__dict__

class LocationStructure:

    def __init__(self, location: dict) -> None:
        self.location = location

    async def get_city(self, with_type: bool = False):
        address: dict = self.location["address"]

        keys: dict = {"city": {"type": "місто"},
                      "town": {"type": "місто"},
                      "village": {"type": "село"},
                      "municipality": {"type": ""}}

        for i, v in keys.items():
            if i in address.keys():
                city: dict = {
                    "type": v['type'] if with_type and v['type'] else '',
                    "name": address[i]
                }
                # city: dict = [v['type'] + ' ' if with_type and v['type'] else '', address[i]]
                return city




