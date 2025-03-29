from typing import Iterable
from django.db import models
from counseling.models import Psychiatrist , Pationt 
from datetime import date

class Reservation(models.Model) : 
    DAY0 = 'شنبه'
    DAY1 = 'یکشنبه'
    DAY2 = 'دوشنبه'
    DAY3 = 'سه‌شنبه'
    DAY4 = 'چهارشنبه'
    DAY5 = 'پنج‌شنبه'
    DAY6 = 'جمعه'

    DAY_CHOICES = [
        (DAY0 , 'شنبه' ),
        (DAY1, 'یک‌شنبه'),
        (DAY2 ,'دو‌شنبه'),
        (DAY3 ,'سه‌شنبه'),
        (DAY4 ,'چهار‌شنبه'),
        (DAY5 , 'پنج‌شنبه'),
        (DAY6 ,'جمعه')
    ]

    REMOTE = 'مجازی'
    INPERSON = 'حضوری'
    RESERVE_CHOICES = [
        (INPERSON , 'حضوری') ,
        ( REMOTE , 'مجازی')
    ]
    
    psychiatrist = models.ForeignKey(Psychiatrist, on_delete=models.CASCADE, related_name='psychiatrist_reservations')
    pationt = models.ForeignKey(Pationt, on_delete=models.CASCADE, related_name='pationt_reservations')
    date = models.DateField()
    time = models.TimeField()

    MeetingLink= models.CharField(max_length=100,blank=True, null=True)
    type = models.CharField(max_length=15 ,choices=RESERVE_CHOICES)
    day = models.CharField(max_length=10, choices=DAY_CHOICES , blank=True  )
    feedback = models.TextField(blank=True, null=True)  # فیدبک از جلسه
    email_sent = models.BooleanField(default=False)  #ایمیل فیدبک ارسال شده یانه

    class Meta:
        unique_together = ['date', 'time' , 'pationt' , 'psychiatrist']

    def save(self, *args, **kwargs) :
        day_dict = {
            0 : self.DAY2 , 
            1 : self.DAY3  , 
            2 : self.DAY4 , 
            3 : self.DAY5 , 
            4 : self.DAY6 , 
            5 : self.DAY0 , 
            6 : self.DAY1 
        }
        
        if not self.day: 
            print( )
            day_num = self.date.weekday()
            # day_num = date.today().weekday()
            if day_dict[day_num] == self.DAY0 : 
                print("he1")
                self.day = self.DAY0
            elif day_dict[day_num] == self.DAY1 : 
                print("he2")
                self.day = self.DAY1
            elif day_dict[day_num] == self.DAY2 : 
                print("he3")
                self.day = self.DAY2
            elif day_dict[day_num] == self.DAY3 : 
                print("he4")
                self.day = self.DAY3
            elif day_dict[day_num] == self.DAY4 : 
                print("he5")
                self.day = self.DAY4
            elif day_dict[day_num] == self.DAY5 : 
                print("he6")
                self.day = self.DAY5
            else : 
                print("he7")
                self.day = self.DAY6

        return super().save()