from django.db import models
from counseling.models import Psychiatrist,Pationt

class Rating(models.Model):
    CHOICES = (
        (1, '1 star'),
        (2, '2 stars'),
        (3, '3 stars'),
        (4, '4 stars'),
        (5, '5 stars')
    )
    psychiatrist = models.ForeignKey(Psychiatrist, on_delete=models.CASCADE)
    pationt = models.ForeignKey(Pationt, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=0, choices=CHOICES)
    comments = models.TextField(blank=True)
    date = models.DateField(null=True)
    class Meta:
        unique_together = ('psychiatrist', 'pationt')
