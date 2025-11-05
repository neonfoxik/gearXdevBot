from django.conf import settings
from django.urls import path

from bot import views

# Импортируем views для регистрации обработчиков бота
# Это происходит после полной инициализации Django
_ = views

app_name = 'bot'


urlpatterns = [
    path(settings.BOT_TOKEN, views.index, name="index"),
    path('', views.set_webhook, name="set_webhook"),
    path("status/", views.status, name="status"),
]
