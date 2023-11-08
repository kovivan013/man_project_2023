# class MessageReporter:
#     """Отправляет сообщения об ошибках"""
#
#     def __init__(self, answer: dict = None, telegram_id: str = ''):
#         self._answer: dict = answer if answer else {}
#         self._status: int = answer.get("status", 0) if answer else 0
#         self._answer_data: str = answer.get("answer_data", {}) if answer else {}
#         self._telegram_id: str = telegram_id if telegram_id else ''
#         self._code: Optional[int] = None
#         self._answer_data_dict: dict = {}
#
#     @logger.catch
#     async def handle_errors(self) -> dict:
#         """Parse status and data from answer"""
#
#         data = {}
#         if self._answer_data and not self._answer_data.startswith('<!'):
#             try:
#                 data: dict = json.loads(self._answer_data)
#                 if isinstance(data, dict):
#                     self._code = data.get("code", 0)
#                     self._answer_data_dict = data
#             except JSONDecodeError as err:
#                 logger.error(
#                     f"ErrorsSender: answer_handling: JSON ERROR: {err}"
#                     f"\nStatus: {self._status}"
#                     f"\nAnswer data: {self._answer_data}"
#                 )
#         self._answer.update(answer_data=data)
#         if self._status not in range(200, 300):
#             await self.send_message_check_token()
#         return self._answer