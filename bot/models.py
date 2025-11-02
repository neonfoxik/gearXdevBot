from django.db import models


class User(models.Model):
    telegram_id = models.CharField(
        primary_key=True,
        max_length=50
    )
    user_tg_name = models.CharField(
        max_length=35,
        verbose_name='Имя аккаунта в телеграмм',
        null=True,
        blank=True,
        default="none",
    )
    user_name = models.CharField(
        max_length=35,
        verbose_name='Имя',
    )
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user_name)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

