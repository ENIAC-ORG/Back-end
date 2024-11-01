from django.db import models
from counseling.models import Psychiatrist
from counseling.models import Pationt
from reservation.models import Reservation

class FreeTime(models.Model):
    DAY0 = 'شنبه'
    DAY1 = 'یکشنبه'
    DAY2 = 'دوشنبه'
    DAY3 = 'سه‌شنبه'
    DAY4 = 'چهارشنبه'
    DAY5 = 'پنج‌شنبه'
    DAY6 = 'جمعه'

    DAY_CHOICES = [
        (DAY0 , 'شنبه'),
        (DAY1, 'یک‌شنبه'),
        (DAY2 ,'دو‌شنبه'),
        (DAY3 ,'سه‌شنبه'),
        (DAY4 ,'چهار‌شنبه'),
        (DAY5 , 'پنج‌شنبه'),
        (DAY6 ,'جمعه')
    ]

    Month0 = 'January' 
    Month1 = 'February'
    Month2 = 'March'
    Month3 = 'April'
    Month4 = 'May'
    Month5 = 'June'
    Month6 = 'July'
    Month7 = 'August' 
    Month8 = 'September'
    Month9 = 'October'
    Month10 ='November'
    Month11 ='December'

    MONTH_CHOICES = [
        (Month0 , 'January' ),
        (Month1, 'February'),
        (Month2 ,'March'),
        (Month3 ,'April'),
        (Month4 ,'May'),
        (Month5 , 'June'),
        (Month6 ,'July'),
        (Month7 , 'August' ),
        (Month8, 'September'),
        (Month9 ,'October'),
        (Month10 ,'November'),
        (Month11 ,'December'),
    ]

    psychiatrist = models.ForeignKey(Psychiatrist, on_delete=models.CASCADE)
    date = models.DateField(null=True)
    day = models.CharField(max_length=10, choices=DAY_CHOICES , blank=True)
    HOUR_CHOICES = [
    (f'{i:02d}:00', f'{i:02d}:00') for i in range(24)]

    month = models.CharField(max_length=10,choices=MONTH_CHOICES,blank=True)
    time = models.TimeField(choices=HOUR_CHOICES, null=True)

    def __str__(self):
        return f"{self.psychiatrist} - {self.day} {self.month} at {self.time}"
