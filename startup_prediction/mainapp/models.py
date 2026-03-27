from django.db import models


class User(models.Model):
    STATUS_CHOICES = [
        ('pending',    'Pending'),
        ('accepted',   'Accepted'),
        ('rejected',   'Rejected'),
        ('restricted', 'Restricted'),
    ]

    user_id  = models.AutoField(primary_key=True)
    Fullname = models.CharField(max_length=200)
    Email    = models.EmailField(unique=True)
    Phone    = models.CharField(max_length=20)
    Password = models.CharField(max_length=200)
    city     = models.CharField(max_length=100, null=True, blank=True)
    industry = models.CharField(max_length=100, null=True, blank=True)
    state    = models.CharField(max_length=100, null=True, blank=True)
    image    = models.ImageField(upload_to='profiles/', null=True, blank=True)
    status   = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.Fullname
