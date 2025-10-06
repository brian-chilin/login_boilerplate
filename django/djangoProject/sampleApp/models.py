from django.db import models

# Create your models here.
class User(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    raw_password = models.CharField(max_length=255, null=True)

    class Meta:
        managed = False  # 🔑 Do NOT let Django create or change this table
        db_table = "users"