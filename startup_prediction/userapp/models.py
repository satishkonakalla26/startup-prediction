from django.db import models
from mainapp.models import User


class Predict(models.Model):
    predict_id    = models.AutoField(primary_key=True)
    user          = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    company_name  = models.CharField(max_length=200, null=True, blank=True)
    investors     = models.CharField(max_length=200, null=True, blank=True)
    Competitors   = models.IntegerField(null=True, blank=True)
    Partnerships  = models.CharField(max_length=200, null=True, blank=True)
    Founders      = models.CharField(max_length=200, null=True, blank=True)
    Time          = models.CharField(max_length=10, null=True, blank=True)
    Market        = models.CharField(max_length=10, null=True, blank=True)
    Relationships = models.IntegerField(null=True, blank=True)
    relationships = models.IntegerField(null=True, blank=True)
    funding_rounds = models.IntegerField(null=True, blank=True)
    funding_total_usd = models.FloatField(null=True, blank=True)
    Funding       = models.IntegerField(null=True, blank=True)
    Software      = models.IntegerField(null=True, blank=True)
    Web           = models.IntegerField(null=True, blank=True)
    Mobile        = models.IntegerField(null=True, blank=True)
    enterprise    = models.IntegerField(null=True, blank=True)
    Advertising   = models.IntegerField(null=True, blank=True)
    Games         = models.IntegerField(null=True, blank=True)
    commerce      = models.IntegerField(null=True, blank=True)
    Biotech       = models.IntegerField(null=True, blank=True)
    Consulting    = models.IntegerField(null=True, blank=True)
    Other         = models.IntegerField(null=True, blank=True)
    Vc            = models.IntegerField(null=True, blank=True)
    Angel         = models.IntegerField(null=True, blank=True)
    a             = models.IntegerField(null=True, blank=True)
    b             = models.IntegerField(null=True, blank=True)
    c             = models.IntegerField(null=True, blank=True)
    d             = models.IntegerField(null=True, blank=True)
    Participents  = models.FloatField(null=True, blank=True)
    top           = models.IntegerField(null=True, blank=True)
    result        = models.CharField(max_length=50, null=True, blank=True)
    conclusion    = models.TextField(null=True, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"Prediction {self.predict_id} - {self.result}"
