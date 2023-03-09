from django.db import models


class PrismeDown(models.Model):
    down = models.BooleanField(default=False)

    @classmethod
    def set(cls, state: bool):
        cls.objects.all().update(down=state)

    @classmethod
    def get(cls) -> bool:
        # return cls.objects.first().down
        return cls.objects.all().values("down")[0]["down"]

    def __str__(self):
        return "Downtime: " + ("DOWN" if self.down else "UP")
