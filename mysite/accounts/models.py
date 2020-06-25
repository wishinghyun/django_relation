from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.
class User(AbstractUser):
    followers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="follwings",
        blank=True
    )
    # 각종 필드를 추가
    # createsuperuser
    # DB를 날려야될 경우
    # shell_plus
    # create_user is_staff, 최고권한과 관련된 필드 True로 설정
    # User.objects.create_user(username='admin', password='1234', is_staff=True, is_superuser=True)