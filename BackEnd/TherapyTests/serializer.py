from rest_framework import serializers 
from .models import TreatementHistory , MedicalRecord 
import json
from django.http import QueryDict
from django.forms.models import model_to_dict
from .models import TreatementHistory , TherapyTests , GlasserTest 


class MedicalQueryRecord(serializers.Serializer) : 
    
    id = serializers.IntegerField()
    nationalID = serializers.CharField(max_length = 10)
    name = serializers.CharField(max_length = 40 )
    patient= serializers.IntegerField()
    gender = serializers.CharField(max_length = 2 )
    # class Meta:
    #     # model = MedicalRecord
    #     fields = [ 'id'  , 'nationalID' , 'name']


class TreatementHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatementHistory
        fields = ('end_date' , 'length' , 'is_finished' , 'reason_to_leave' , 'approach' , 'special_drugs' , 'id') 


class GlasserSerializer( serializers.ModelSerializer) : 
    class Meta : 
        model = GlasserTest
        fields = ('love' , 'survive' , 'freedom' , 'power' , 'fun') 

class ThrapyTestSerializer( serializers.ModelSerializer) : 
    glasserTest = GlasserSerializer()

    class Meta : 
        model = TherapyTests
        fields = ['id' , 'MBTItest' , 'glasserTest']
        extra_kwargs = {
            'glasserTest' : {'required': False},
        }
    
    def is_valid(self, *, raise_exception=False):
        print("in therapy test is valid ")
        return super().is_valid(raise_exception=raise_exception)

class MedicalGetRecord(serializers.ModelSerializer) : 
    treatementHistory1 = TreatementHistorySerializer(required=False)
    treatementHistory2 = TreatementHistorySerializer(required=False)
    treatementHistory3 = TreatementHistorySerializer(required=False)
    therapyTests = ThrapyTestSerializer(required=False)
    
    class Meta:
        model = MedicalRecord
        fields = ['child_num' , 'family_history' , 'nationalID' , 'id' , 'name' , 'age' , 'gender' , 'treatementHistory1' , 'treatementHistory2' , 'treatementHistory3' , 'therapyTests' ]
        

class MedicalRecordSerializer(serializers.ModelSerializer):
    
    def __init__(self, instance=None, data=..., **kwargs):
        self.treatementHistory1 = TreatementHistorySerializer()
        self.treatementHistory2 = TreatementHistorySerializer()
        self.treatementHistory3 = TreatementHistorySerializer()
        self.stored_validated_data = None
        super().__init__(instance, data, **kwargs)

    class Meta:
        model = MedicalRecord
        fields = ['child_num' , 'family_history' , 'nationalID' , 'id' , 'name' , 'age' , 'gender' ] # , 'treatementHistory1' , 'treatementHistory2' , 'treatementHistory3' 
        extra_kwargs = {
            'treatementHistory1': {'required': False}, 
            'treatementHistory2': {'required': False},
            'treatementHistory3': {'required': False}
        }
    
    def is_valid(self, *, raise_exception=False):
        validated_data = self.run_validation(self.initial_data)
        self.stored_validated_data = validated_data
        valid = super().is_valid(raise_exception=raise_exception)
        return valid
    

    def run_validation(self, data=...):
        
        data_dict = None 
        if type(data) is dict : 
            data_dict = data
        else : 
            data_dict = {key: value[0] for key, value in data.lists()}
        
        serializer = self.__class__()
        child_num = data.get('child_num')
        family_history = data.get('family_history')
        nationalID = data.get('nationalID')
        medical_record = {}
        # Validate child_num
        try:
            validated_child_num = serializer.fields['child_num'].run_validation(child_num)
            medical_record['child_num'] = validated_child_num
        except serializers.ValidationError as exc:
            raise serializers.ValidationError({'child_num': exc.detail})

        # Validate family_history
        try:
            validated_family_history = serializer.fields['family_history'].run_validation(family_history)
            medical_record['family_history']  = validated_family_history
        except serializers.ValidationError as exc:
            raise serializers.ValidationError({'family_history': exc.detail})

        # Validate nationalID
        try:
            validated_nationalID = serializer.fields['nationalID'].run_validation(nationalID)
            medical_record['nationalID'] = validated_nationalID
        except serializers.ValidationError as exc:
            raise serializers.ValidationError({'nationalID': exc.detail})


        if 'treatementHistory1' in data_dict.keys() :             
            treatementHistory1 = json.loads(data_dict['treatementHistory1']) 
            seializer1 = TreatementHistorySerializer(data= treatementHistory1 )
            seializer1.is_valid(raise_exception=True )
            value = seializer1.validated_data
            medical_record['treatementHistory1'] = dict(value)
           
        if 'treatementHistory2' in data_dict.keys() : 
            treatementHistory2 = json.loads(data_dict['treatementHistory2']) 
            seializer2 = TreatementHistorySerializer(data= treatementHistory2 )
            seializer2.is_valid(raise_exception=True )
            value = (seializer2.validated_data)
            medical_record['treatementHistory2'] = dict(value)


        if 'treatementHistory3' in data_dict.keys() : 
            treatementHistory3 = json.loads(data_dict['treatementHistory3'])
            data_dict.pop('treatementHistory3')
            seializer3 = TreatementHistorySerializer(data= treatementHistory3 )
            seializer3.is_valid(raise_exception=True )
            value = seializer3.validated_data
            value = (seializer3.validated_data)
            medical_record['treatementHistory3'] = dict(value)
        return medical_record
    
    
