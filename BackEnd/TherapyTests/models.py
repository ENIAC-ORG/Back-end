from typing import Iterable
from django.db import models
from counseling.models import Pationt , Psychiatrist
from django.core.exceptions import ValidationError 
import datetime
from django.core.validators import MinValueValidator, MaxValueValidator

# نیاز به بقا	
# نیاز به عشق و تعلق خاطر	
# نیاز به آزادی	
# نیاز به قدرت	
# نیاز به تفریح

class GlasserTest(models.Model) : 
    love = models.FloatField( default=0.0 )
    survive = models.FloatField( default=0.0 )
    freedom = models.FloatField( default=0.0 )
    power = models.FloatField( default=0.0 )
    fun = models.FloatField( default=0.0 )

class TherapyTests(models.Model) : 
    pationt = models.OneToOneField(Pationt , on_delete=models.CASCADE )
    MBTItest = models.CharField( max_length=6 , blank=True , null=True  )
    glasserTest = models.ForeignKey( GlasserTest , on_delete=models.DO_NOTHING  , blank=True , null=True)
    phq9 = models.IntegerField(
	    validators=[MinValueValidator(0), MaxValueValidator(27)],
	    blank=True,
	    null=True
	)
    phq9_created_at = models.DateTimeField(auto_now_add=True)

class MedicalRecord(models.Model) : 
    GENDER_Male = 'مرد'
    GENDER_Female = 'زن'
    GENDER_CHOICES = [
        (GENDER_Female, 'زن'),
        (GENDER_Male, 'مرد')
    ]
    # fields :  ['child_num' , 'family_history' , 'nationalID' , 'treatementHistory1' , 'treatementHistory2' , 'treatementHistory3' ]
    pationt = models.OneToOneField(Pationt , on_delete=models.CASCADE)
    child_num = models.IntegerField(blank=False , null=False )
    therapyTests = models.OneToOneField( TherapyTests , on_delete=models.DO_NOTHING , blank=True , null=True )
    name = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    age = models.IntegerField(range(12 , 80 ))
    # treatementHistory1 = models.ForeignKey(TreatementHistory , on_delete=models.DO_NOTHING , null=True,blank=True , related_name="treatement_history1")
    # treatementHistory2 = models.ForeignKey(TreatementHistory , on_delete=models.DO_NOTHING , null=True , blank=True ,related_name="treatement_history2")
    # treatementHistory3 = models.ForeignKey(TreatementHistory , on_delete=models.DO_NOTHING , null=True , blank=True ,related_name="treatement_history3")
    gender = models.CharField(max_length=5 , choices=GENDER_CHOICES ,null=True )
    family_history = models.BooleanField(default=False )
    nationalID = models.CharField(max_length=10 , blank=False )

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not isinstance(self.pationt , Pationt):
            raise ValidationError('Invalid value for content_object')
        self.name = self.determine_name()
        self.age = self.determine_age()
        self.gender = self.determine_gender()
        self.therapyTests = TherapyTests.objects.filter(pationt = self.pationt ).first()
        super().save(*args, **kwargs)

    def determine_gender(self ) : 
        gender = ''
        if self.pationt.user.gender == 'F' :
            gender = self.GENDER_Female
        else : 
            gender = self.GENDER_Male
        return gender 
    
    def determine_name(self):
        return self.pationt.get_fullname()
    
    def determine_age(self ) : 
        now_year = datetime.datetime.now().year
        print("now " ,  now_year , "your age : " ,self.pationt.user.date_of_birth.year  )
        return now_year - self.pationt.user.date_of_birth.year 
    
class TreatementHistory(models.Model): 
    end_date = models.DateField()
    length = models.IntegerField() # based on month 
    is_finished = models.BooleanField(default=True )
    reason_to_leave = models.TextField(blank=True , max_length= 500 )
    approach = models.TextField( max_length= 30 ,blank=True , null=True)
    special_drugs = models.TextField(max_length=200 , blank=True )
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='treatment_histories')
    def to_dict(self):
        return {
            'end_date': self.end_date,
            'length': self.length,
            'is_finished': self.is_finished,
            'reason_to_leave': self.reason_to_leave,
            'approach': self.approach,
            'special_drugs': self.special_drugs
        }
      
class MedicalRecordPermission( models.Model ) : 
    pationt = models.ForeignKey( Pationt , on_delete=models.CASCADE ) 
    psychiatrist = models.ForeignKey(Psychiatrist , on_delete=models.CASCADE)
    created_date = models.DateField()

    def save(self, *args, **kwargs):
        """
        Check if there's already a Psychiatrist object associated with this User
        """ 
        if MedicalRecordPermission.objects.filter(pationt = self.pationt ,psychiatrist=self.psychiatrist ).exists() == False :
            self.created_date =datetime.date.today()
            return super().save(*args, **kwargs)


