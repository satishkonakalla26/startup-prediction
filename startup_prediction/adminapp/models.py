from django.db import models


class Dataset(models.Model):
    data_id    = models.AutoField(primary_key=True)
    data_set   = models.FileField(upload_to='datasets/')

    # Gradient Boosting metrics
    gb_accuracy  = models.FloatField(null=True, blank=True)
    gb_precision = models.FloatField(null=True, blank=True)
    gb_recall    = models.FloatField(null=True, blank=True)
    gb_f1_score  = models.FloatField(null=True, blank=True)
    gb_algo      = models.CharField(max_length=100, null=True, blank=True)

    # AdaBoost metrics
    ad_accuracy  = models.FloatField(null=True, blank=True)
    ad_precision = models.FloatField(null=True, blank=True)
    ad_recall    = models.FloatField(null=True, blank=True)
    ad_f1_score  = models.FloatField(null=True, blank=True)
    ad_algo      = models.CharField(max_length=100, null=True, blank=True)

    # Random Forest metrics
    rf_accuracy  = models.FloatField(null=True, blank=True)
    rf_precision = models.FloatField(null=True, blank=True)
    rf_recall    = models.FloatField(null=True, blank=True)
    rf_f1_score  = models.FloatField(null=True, blank=True)
    rf_algo      = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Dataset {self.data_id}"
