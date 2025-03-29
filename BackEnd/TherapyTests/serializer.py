from rest_framework import serializers 
from .models import TreatementHistory , MedicalRecord 
import json
from django.http import QueryDict
from django.forms.models import model_to_dict
from .models import TreatementHistory , TherapyTests , GlasserTest 
import logging 

logger = logging.getLogger(__name__)

class GlasserSerializer( serializers.ModelSerializer) : 
    class Meta : 
        model = GlasserTest
        fields = ['id' ,'love' , 'survive' , 'freedom' , 'power' , 'fun']

class ThrapyTestSerializer( serializers.ModelSerializer) : 
    glasserTest = GlasserSerializer()
    class Meta : 
        model = TherapyTests
        fields = ['id', 'pationt' , 'MBTItest' , 'glasserTest']
        extra_kwargs = {
            'glasserTest' : {'required': False},
        }

    def is_valid(self, *, raise_exception=False):
        return super().is_valid(raise_exception=raise_exception)

class MedicalQueryRecord(serializers.Serializer) : 
    id = serializers.IntegerField()
    nationalID = serializers.CharField(max_length = 10)
    name = serializers.CharField(max_length = 40 )
    patient= serializers.IntegerField()
    gender = serializers.CharField(max_length = 2 )

    class Meta:
        # model = MedicalRecord
        fields = [ 'id'  , 'nationalID' , 'name']
    
class TreatmentHistorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = TreatementHistory
        fields = ['id', 'end_date', 'length', 'is_finished', 'reason_to_leave', 'approach', 'special_drugs']
        # extra_kwargs = {'id': {'read_only': True ,
        #                         'required': True}}
class MedicalRecordCreateSerializer(serializers.ModelSerializer):
    treatment_histories = TreatmentHistorySerializer(many=True)
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'pationt', 'child_num', 'therapyTests', 'name', 'created_at', 
            'age', 'gender', 'family_history', 'nationalID', 'treatment_histories'
        ]
        
        extra_kwargs = {
            'pationt': {'required': False},  
        }

    def create(self, validated_data):
        treatment_histories_data = validated_data.pop('treatment_histories')
        medical_record = MedicalRecord.objects.create(**validated_data)
        
        for treatment_history_data in treatment_histories_data:
            TreatementHistory.objects.create(medical_record=medical_record, **treatment_history_data)
        return medical_record
    
    def update(self, instance, validated_data):
        treatment_histories_data = validated_data.pop('treatment_histories', None)

        logger.info(f"Initial data: {self.initial_data}")
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        if treatment_histories_data:
            for treatment_history_data in treatment_histories_data:
                logger.debug( "this is treatement history ... " , treatment_history_data )
                history_id = treatment_history_data.get('id', None)
                if history_id:
                
                    treatment_history = TreatementHistory.objects.get(id=history_id)
                    for attr, value in treatment_history_data.items():
                        setattr(treatment_history, attr, value)
                    treatment_history.save()
                else:
                    TreatementHistory.objects.create(medical_record=instance, **treatment_history_data)
        return instance


class MedicalRecordGetSerializer(serializers.ModelSerializer):
    treatment_histories = TreatmentHistorySerializer(many=True)
    therapyTests = ThrapyTestSerializer()
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'pationt', 'child_num', 'therapyTests', 'name', 'created_at', 
            'age', 'gender', 'family_history', 'nationalID', 'treatment_histories'
        ]

    def is_valid(self, *, raise_exception=False):
        return super().is_valid(raise_exception=raise_exception)
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        therapy_test = TherapyTests.objects.filter(pationt=instance.pationt).first()
        if therapy_test:
            representation['therapyTests'] = ThrapyTestSerializer(therapy_test).data
        return representation

    
