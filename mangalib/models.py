from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Manga(models.Model):
    id = models.CharField(max_length=200, primary_key=True, db_index=True)
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    cover = models.CharField(max_length=200)
    synopsis = models.TextField()
    def __str__(self):
        return self.title

class Profile(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    name = models.CharField(max_length=200)
    library = models.ManyToManyField(Manga)
    def __str__(self):
        return self.name