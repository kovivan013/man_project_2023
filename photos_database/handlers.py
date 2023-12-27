import os
from aiogram.types import Message
from man_project_2023.telegram_bot.config import Bot, bot

BASE_DIR = "database"

class PhotosDB:

    # def __init__(self, bot: Bot = bot):
    #     self.bot = bot
    #     self.__BASE_DIR = self.join(base_dir=os.path.dirname(os.path.abspath(__file__)), dir="database")

    @staticmethod
    def join(base_dir, dir, absolute_path: bool = False):
        path = os.path.join(base_dir.__str__(), dir.__str__())
        if absolute_path:
            return os.path.abspath(path)
        return path

    __BASE_DIR = join(base_dir=os.path.dirname(os.path.abspath(__file__)), dir="database")

    @classmethod
    async def register(cls, telegram_id: int):
        user = cls.join(cls.__BASE_DIR, telegram_id)
        gigs = cls.join(user, "gigs")
        profile = cls.join(user, "profile")

        os.makedirs(user)
        os.makedirs(gigs)
        os.makedirs(profile)

    @classmethod
    async def delete(cls, telegram_id: int):
        user = cls.join(cls.__BASE_DIR, telegram_id)
        os.removedirs(user)

    @classmethod
    async def save(cls, telegram_id: int, file_id: str, gig_id: str):
        photo_path = await bot.get_file(file_id=file_id)
        user = cls.join(cls.__BASE_DIR, telegram_id)
        gigs = cls.join(user, "gigs")

        gig = cls.join(gigs, gig_id)
        os.makedirs(gig, exist_ok=True)

        save_path = cls.join(gig, "preview.jpg", absolute_path=True)
        print(photo_path.file_path)
        await bot.download_file(photo_path.file_path,
                                     save_path)

    @classmethod
    def get(cls, telegram_id: int, gig_id: str):
        user = cls.join(cls.__BASE_DIR, telegram_id, absolute_path=True)
        gigs = cls.join(user, "gigs")

        gig = cls.join(gigs, gig_id)
        print(gig)
        return open(f"{gig}\preview.jpg", "rb")

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
