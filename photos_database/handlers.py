import os
from aiogram.types import Message
from man_project_2023.telegram_bot.config import Bot

BASE_DIR = "database"

class PhotosDB:

    def __init__(self, bot: Bot):
        self.bot = bot
        self.__BASE_DIR = self.join(base_dir=os.path.dirname(os.path.abspath(__file__)), dir="database")

    def join(self, base_dir, dir, absolute_path: bool = False):
        path = os.path.join(base_dir.__str__(), dir.__str__())
        if absolute_path:
            return os.path.abspath(path)
        return path

    async def register(self, telegram_id: int):
        user = self.join(self.__BASE_DIR, telegram_id)
        gigs = self.join(user, "gigs")
        profile = self.join(user, "profile")

        os.makedirs(user)
        os.makedirs(gigs)
        os.makedirs(profile)

    async def delete(self, telegram_id: int):
        user = self.join(self.__BASE_DIR, telegram_id)
        os.removedirs(user)


    async def save(self, telegram_id: int, file_id: str, gig_id: str):
        print(self.__BASE_DIR)
        photo_path = await self.bot.get_file(file_id=file_id)
        user = self.join(self.__BASE_DIR, telegram_id)
        gigs = self.join(user, "gigs")

        gig = self.join(gigs, gig_id)
        os.makedirs(gig, exist_ok=True)

        save_path = self.join(gig, "preview.jpg", absolute_path=True)
        print(photo_path.file_path)
        await self.bot.download_file(photo_path.file_path,
                                     save_path)

    async def get(self, telegram_id: int):
        pass

#
# import asyncio
#
# asyncio.run(PhotosDB().register(telegram_id=1125858430))

# def register(user_id):
#     user_dir = os.path.join(BASE_DIR, user_id.__str__())
#     gigs_dir = os.path.join(user_dir, "gigs")
#     profile_dir = os.path.join(user_dir, "profile")
#
#     os.makedirs(gigs_dir)
#     os.makedirs(profile_dir)
#
#
#
# def get_photo(user_id, photo_id):
#     user_dir = os.path.join(BASE_DIR, str(user_id))
#     photo_path = os.path.join(user_dir, "gigs", f"{photo_id}.jpg")
#
#     if os.path.exists(photo_path):
#         with open(photo_path, "rb") as file:
#             return file.read()
#     else:
#         return None
#
#
# def move_photo(user_id, photo_id, destination):
#     user_dir = os.path.join(BASE_DIR, str(user_id))
#     source_path = os.path.join(user_dir, "gigs", f"{photo_id}.jpg")
#     destination_path = os.path.join(user_dir, destination, f"{photo_id}.jpg")
#
#     if os.path.exists(source_path):
#         shutil.move(source_path, destination_path)
#         return True
#     else:
#         return False
#
#
# def add_photo(user_id, photo_id, photo_url):
#     user_dir = os.path.join(BASE_DIR, str(user_id))
#     photo_path = os.path.join(user_dir, "gigs", f"{photo_id}.jpg")
#
#
# # Пример использования функций
# user_id = 1233
# register_user(user_id)
#
# photo_id = 1
# photo_url = "https://example.com/photo.jpg"
# add_photo(user_id, photo_id, photo_url)
#
# photo_data = get_photo(user_id, photo_id)
# if photo_data:
#     # Делайте что-то с данными фотографии
#     pass
#
# move_photo(user_id, photo_id, "profile")
