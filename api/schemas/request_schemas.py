from pydantic import BaseModel

class BaseUser(BaseModel):
    telegram_id: int

class UserCreate(BaseUser):
    username: str
    description: str

    def as_dict(self) -> dict:
        return self.__dict__

class UpdateUser(BaseUser):
    username: str = ""
    description: str = ""


class GigCreate(BaseModel):
    # id: int
    # status: int
    # name: str
    # description: str
    # # image = None
    # location: dict
    # date: int

    # id: int
    # status: int
    # tags: list

    def as_dict(self) -> dict:
        return self.__dict__

#   СТОЛБЕЦ ОГОЛОШЕННЯ
# kovivan013
# {
#     "time": "yyyy_MM_dd"
#     "time"
# }
# dct = {
#     "users": {
#         "user": {
#             "telegram_id": 24735627,
#             "username": "test",
#             "gigs": {
#                 0: {
#                     "active": {
#                         "sdHF84jfhd78": {
#                             "id": 576455,
#                             "status": 1
#                         }
#                     },
#                     "completed": {
#                         "s3dfF45678jfhd78": {
#
#                         }
#                     }
#                 },
#                 1: {
#                     "active": {
#                         "sdHF84jfhd78": {
#
#                         }
#                     },
#                     "completed": {
#                         "s3dfF45678jfhd78": {
#
#                         }
#                     }
#                 }
#                 }
#             }
#         }
#     }



# {
#     "document": {
#         "id": 2427893,
#         "name": "Алгебра 11 Клас",
#         "status": 2,
#         "slug": "algebra-11-klas-2427893",
#         "private": 1,
#         "enable_cloning": 1,
#         "subject_id": 1,
#         "grade_id": 7,
#         "image": "",
#         "description": "",
#         "questions": 2
#     },
#     "questions": [
#         {
#             "id": "26372656",
#             "document_id": "2427893",
#             "content": "<p>A b or c?</p>",
#             "image": null,
#             "type": "quiz",
#             "point": "1",
#             "hint": "0",
#             "hint_penalty": "2",
#             "hint_description": "",
#             "order": "1",
#             "clone_id": null,
#             "options": [
#                 {
#                     "id": "102675098",
#                     "question_id": "26372656",
#                     "value": "<p>1</p>",
#                     "image": null,
#                     "correct": "0",
#                     "order": null
#                 },
#                 {
#                     "id": "102675099",
#                     "question_id": "26372656",
#                     "value": "<p>2</p>",
#                     "image": null,
#                     "correct": "1",
#                     "order": null
#                 },
#                 {
#                     "id": "102675100",
#                     "question_id": "26372656",
#                     "value": "<p>3</p>",
#                     "image": null,
#                     "correct": "0",
#                     "order": null
#                 },
#                 {
#                     "id": "102675101",
#                     "question_id": "26372656",
#                     "value": "<p>4</p>",
#                     "image": null,
#                     "correct": "0",
#                     "order": null
#                 }
#             ]
#         },
#         {
#             "id": "26372671",
#             "document_id": "2427893",
#             "content": "<p>A b or c? </p>",
#             "image": null,
#             "type": "quiz",
#             "point": "1",
#             "hint": "0",
#             "hint_penalty": "2",
#             "hint_description": "",
#             "order": "1",
#             "clone_id": null,
#             "options": [
#                 {
#                     "id": "102675146",
#                     "question_id": "26372671",
#                     "value": "<p>451</p>",
#                     "image": null,
#                     "correct": "0",
#                     "order": null
#                 },
#                 {
#                     "id": "102675147",
#                     "question_id": "26372671",
#                     "value": "<p>345</p>",
#                     "image": null,
#                     "correct": "0",
#                     "order": null
#                 },
#                 {
#                     "id": "102675148",
#                     "question_id": "26372671",
#                     "value": "<p>356</p>",
#                     "image": null,
#                     "correct": "1",
#                     "order": null
#                 },
#                 {
#                     "id": "102675149",
#                     "question_id": "26372671",
#                     "value": "<p>467</p>",
#                     "image": null,
#                     "correct": "0",
#                     "order": null
#                 }
#             ]
#         }
#     ],
#     "subjects": [
#         {
#             "id": "1",
#             "name": "Алгебра"
#         },
#         {
#             "id": "34",
#             "name": "Англійська мова"
#         },
#         {
#             "id": "40",
#             "name": "Астрономія"
#         },
#         {
#             "id": "3",
#             "name": "Біологія"
#         },
#         {
#             "id": "9",
#             "name": "Всесвітня історія"
#         },
#         {
#             "id": "4",
#             "name": "Географія"
#         },
#         {
#             "id": "5",
#             "name": "Геометрія"
#         },
#         {
#             "id": "50",
#             "name": "Громадянська освіта"
#         },
#         {
#             "id": "41",
#             "name": "Екологія"
#         },
#         {
#             "id": "37",
#             "name": "Економіка"
#         },
#         {
#             "id": "45",
#             "name": "Етика"
#         },
#         {
#             "id": "6",
#             "name": "Зарубіжна література"
#         },
#         {
#             "id": "43",
#             "name": "Захист України"
#         },
#         {
#             "id": "7",
#             "name": "Інформатика"
#         },
#         {
#             "id": "53",
#             "name": "Інші іноземні мови"
#         },
#         {
#             "id": "44",
#             "name": "Іспанська мова"
#         },
#         {
#             "id": "8",
#             "name": "Історія України"
#         },
#         {
#             "id": "52",
#             "name": "Креслення"
#         },
#         {
#             "id": "26",
#             "name": "Літературне читання"
#         },
#         {
#             "id": "38",
#             "name": "Людина і світ"
#         },
#         {
#             "id": "10",
#             "name": "Математика"
#         },
#         {
#             "id": "30",
#             "name": "Мистецтво"
#         },
#         {
#             "id": "29",
#             "name": "Мови національних меншин"
#         },
#         {
#             "id": "11",
#             "name": "Музичне мистецтво"
#         },
#         {
#             "id": "12",
#             "name": "Навчання грамоти"
#         },
#         {
#             "id": "35",
#             "name": "Німецька мова"
#         },
#         {
#             "id": "31",
#             "name": "Образотворче мистецтво"
#         },
#         {
#             "id": "13",
#             "name": "Основи здоров’я"
#         },
#         {
#             "id": "48",
#             "name": "Польська мова"
#         },
#         {
#             "id": "33",
#             "name": "Правознавство"
#         },
#         {
#             "id": "49",
#             "name": "Природничі науки"
#         },
#         {
#             "id": "27",
#             "name": "Природознавство"
#         },
#         {
#             "id": "42",
#             "name": "Технології"
#         },
#         {
#             "id": "32",
#             "name": "Трудове навчання"
#         },
#         {
#             "id": "15",
#             "name": "Українська література"
#         },
#         {
#             "id": "14",
#             "name": "Українська мова"
#         },
#         {
#             "id": "2",
#             "name": "Фізика"
#         },
#         {
#             "id": "17",
#             "name": "Фізична культура"
#         },
#         {
#             "id": "36",
#             "name": "Французька мова"
#         },
#         {
#             "id": "16",
#             "name": "Хімія"
#         },
#         {
#             "id": "39",
#             "name": "Художня культура"
#         },
#         {
#             "id": "28",
#             "name": "Я досліджую світ"
#         }
#     ],
#     "grades": [
#         {
#             "id": null,
#             "name": "---"
#         },
#         {
#             "id": "1",
#             "name": "1 клас"
#         },
#         {
#             "id": "2",
#             "name": "2 клас"
#         },
#         {
#             "id": "3",
#             "name": "3 клас"
#         },
#         {
#             "id": "4",
#             "name": "4 клас"
#         },
#         {
#             "id": "5",
#             "name": "5 клас"
#         },
#         {
#             "id": "6",
#             "name": "6 клас"
#         },
#         {
#             "id": "7",
#             "name": "7 клас"
#         },
#         {
#             "id": "8",
#             "name": "8 клас"
#         },
#         {
#             "id": "9",
#             "name": "9 клас"
#         },
#         {
#             "id": "10",
#             "name": "10 клас"
#         },
#         {
#             "id": "11",
#             "name": "11 клас"
#         }
#     ],
#     "types": [
#         {
#             "id": "quiz",
#             "name": "Одна правильна"
#         },
#         {
#             "id": "multiquiz",
#             "name": "Декілька правильних"
#         }
#     ]
# }

