from django.db import models

class Message(models.Model):
    """
    Модель для хранения сообщений от пользователей.

    Attributes:
        user_id (int): Идентификатор пользователя, отправившего сообщение.
        chat_id (int): Идентификатор чата, в котором было отправлено сообщение.
        text (str): Текст сообщения.
        command (str, optional): Команда, указанная в сообщении (если есть). Поле может быть пустым.
        date (datetime, auto_now_add=True): Дата и время создания записи (автоматически добавляется при сохранении).

    Methods:
        __str__(): Возвращает строковое представление объекта сообщения.
    """

    user_id = models.IntegerField()
    chat_id = models.IntegerField()
    text = models.TextField()
    command = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Возвращает строковое представление объекта сообщения.

        Returns:
            str: Строковое представление объекта сообщения, содержащее идентификатор сообщения, пользователя и чата.
        """
        return f"Message {self.pk} from User {self.user_id} in Chat {self.chat_id}"
