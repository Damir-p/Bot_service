from django.db import models

class Message(models.Model):
    user_id = models.IntegerField()
    chat_id = models.IntegerField()
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.pk} from User {self.user_id} in Chat {self.chat_id}"
