from django.shortcuts import render
from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from utils.therapy_tests import GetMBTIresults ,GlasserResults
from counseling.models import Pationt ,Psychiatrist
from .models import TherapyTests , GlasserTest , MedicalRecord , TreatementHistory , MedicalRecordPermission 
from rest_framework import status 
import json 
from datetime import datetime , date , timedelta 
from django.utils import timezone
from django.http.request import QueryDict
from .serializer import MedicalRecordSerializer ,MedicalGetRecord ,TreatementHistorySerializer , ThrapyTestSerializer , GlasserSerializer ,MedicalQueryRecord
from django.forms.models import model_to_dict
from fuzzywuzzy import fuzz
# https://www.youtube.com/watch?v=P2_j1P51dNI&list=RD1mZhwXMl8vc&index=27

class MedicalRecordView(viewsets.ModelViewSet ) : 
    permission_classes = [IsAuthenticated]
    queryset = MedicalRecord.objects.all()
    http_method_names = ['get','post','retrieve','put','patch' , 'delete']
    serializer_class = MedicalRecordSerializer
    def create(self , request ) : 
        user = request.user 
        pationt = Pationt.objects.filter(user = user ).first()
        serializer = self.serializer_class(data= request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.stored_validated_data 
        treatementHistory1 = None 
        treatementHistory2 = None 
        treatementHistory3 = None 
        if 'treatementHistory1' in validated_data.keys() : 
            treatementHistory1 = validated_data.get('treatementHistory1')
            tr1 = TreatementHistory.objects.create(
                end_date = treatementHistory1['end_date'] , 
                length = treatementHistory1['length'], 
                is_finished = treatementHistory1['is_finished'] , 
                reason_to_leave = treatementHistory1['reason_to_leave'] , 
                approach = treatementHistory1['approach'], 
                special_drugs = treatementHistory1['special_drugs']
            )
            treatementHistory1 = tr1
        if 'treatementHistory2' in validated_data.keys() : 
            treatementHistory2 = validated_data.get('treatementHistory2')
            tr2 = TreatementHistory.objects.create(
                end_date = treatementHistory2['end_date'] , 
                length = treatementHistory2['length'] , 
                is_finished = treatementHistory2['is_finished'], 
                reason_to_leave = treatementHistory2['reason_to_leave'], 
                approach = treatementHistory2['approach'], 
                special_drugs = treatementHistory2['special_drugs']
            )
            treatementHistory2 = tr2

        if 'treatementHistory3' in validated_data.keys() : 
            treatementHistory3 = validated_data.get("treatementHistory3")
            tr3 = TreatementHistory.objects.create(
                end_date = treatementHistory3['end_date'], 
                length = treatementHistory3['length'] , 
                is_finished = treatementHistory3['is_finished'], 
                reason_to_leave = treatementHistory3['reason_to_leave'], 
                approach = treatementHistory3['approach'], 
                special_drugs = treatementHistory3['special_drugs']
            )
            treatementHistory3 = tr3

        medical_record = MedicalRecord.objects.create(
            pationt = pationt , 
            child_num = validated_data.get('child_num') , 
            family_history= validated_data.get('family_history')  , 
            nationalID = validated_data.get('nationalID') , 
            treatementHistory1 = treatementHistory1 , 
            treatementHistory2 = treatementHistory2 , 
            treatementHistory3 = treatementHistory3
        )
    
        oi_dict = model_to_dict(medical_record)
        oi_serialized = json.dumps(oi_dict)
        data = {
            "medical_record" : oi_serialized , 
            "message" : "record has been successfully created."
        }
        return Response(data , status=status.HTTP_201_CREATED)
    

    def update(self , request ) : 
        user = request.user 
        pationt = Pationt.objects.filter(user = user ).first()
        serializer = self.serializer_class(data= request.data )
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.stored_validated_data 
        treatementHistory1 = None 
        treatementHistory2 = None 
        treatementHistory3 = None 
        old_record = MedicalRecord.objects.filter(pationt = pationt )

        if not old_record.exists() : 
            return Response({"message" : "this patient has not create a record yet."} , status=status.HTTP_400_BAD_REQUEST )
        
        old_record = old_record.first()

        if 'treatementHistory1' in validated_data.keys() : 
            treatementHistory1 = validated_data.get('treatementHistory1')
            if not old_record.treatementHistory1 : 
                tr1 = TreatementHistory.objects.create(
                    end_date = treatementHistory1['end_date'] , 
                    length = treatementHistory1['length'], 
                    is_finished = treatementHistory1['is_finished'] , 
                    reason_to_leave = treatementHistory1['reason_to_leave'] , 
                    approach = treatementHistory1['approach'], 
                    special_drugs = treatementHistory1['special_drugs']
                )
                old_record.treatementHistory1 = tr1
            else : 
                old_record.treatementHistory1.end_date = treatementHistory1['end_date'] 
                old_record.treatementHistory1.length = treatementHistory1['length']
                old_record.treatementHistory1.is_finished = treatementHistory1['is_finished'] 
                old_record.treatementHistory1.reason_to_leave = treatementHistory1['reason_to_leave'] 
                old_record.treatementHistory1.approach = treatementHistory1['approach']
                old_record.treatementHistory1.special_drugs = treatementHistory1['special_drugs']
            #     tr1 = old_record.treatementHistory1
            # treatementHistory1 = tr1
            old_record.treatementHistory1.save()

        if 'treatementHistory2' in validated_data.keys() : 
            treatementHistory2 = validated_data.get('treatementHistory2')
            if not old_record.treatementHistory2 : 
                tr2 = TreatementHistory.objects.create(
                    end_date = treatementHistory2['end_date'] , 
                    length = treatementHistory2['length'], 
                    is_finished = treatementHistory2['is_finished'] , 
                    reason_to_leave = treatementHistory2['reason_to_leave'] , 
                    approach = treatementHistory2['approach'], 
                    special_drugs = treatementHistory2['special_drugs']
                )
                old_record.treatementHistory2 = tr2 
            else : 
                old_record.treatementHistory2.end_date = treatementHistory2['end_date']
                old_record.treatementHistory2.length = treatementHistory2['length']
                old_record.treatementHistory2.is_finished = treatementHistory2['is_finished'] 
                old_record.treatementHistory2.reason_to_leave = treatementHistory2['reason_to_leave'] 
                old_record.treatementHistory2.approach = treatementHistory2['approach']
                old_record.treatementHistory2.special_drugs = treatementHistory2['special_drugs']
            #     tr2 = old_record.treatementHistory2

            old_record.treatementHistory2.save()
            # treatementHistory2 = tr2

        if 'treatementHistory3' in validated_data.keys() : 
            treatementHistory3 = validated_data.get('treatementHistory3')
            if not old_record.treatementHistory3 : 
                tr3 = TreatementHistory.objects.create(
                    end_date = treatementHistory2['end_date'] , 
                    length = treatementHistory2['length'], 
                    is_finished = treatementHistory2['is_finished'] , 
                    reason_to_leave = treatementHistory2['reason_to_leave'] , 
                    approach = treatementHistory2['approach'], 
                    special_drugs = treatementHistory2['special_drugs']
                )
                old_record.treatementHistory3 = tr3 
            else : 
                old_record.treatementHistory3.end_date = treatementHistory3['end_date'] 
                old_record.treatementHistory3.length = treatementHistory3['length']
                old_record.treatementHistory3.is_finished = treatementHistory3['is_finished']
                old_record.treatementHistory3.reason_to_leave = treatementHistory3['reason_to_leave'] 
                old_record.treatementHistory3.approach = treatementHistory3['approach']
                old_record.treatementHistory3.special_drugs = treatementHistory3['special_drugs']
            old_record.treatementHistory3.save()

        old_record.pationt = pationt 
        old_record.child_num = validated_data.get('child_num') 
        old_record.family_history= validated_data.get('family_history')  
        old_record.nationalID = validated_data.get('nationalID') 
        old_record.save()
        
        oi_dict = model_to_dict(old_record)
        oi_serialized = json.dumps(oi_dict)
        data = {
            "medical_record" : oi_serialized , 
            "message" : "record has been successfully updated."
        }

        return Response(data , status=status.HTTP_200_OK )
    
    def retrieve_list_all( self , request ) : 
        user = request.user
        if user.role == 'user' : 
            return Response({"message" : "ordinary user can not access this Information."} , status =status.HTTP_400_BAD_REQUEST )
        doctor = Psychiatrist.objects.filter( user = user).first()
        doctor_patients = MedicalRecordPermission.objects.filter(psychiatrist = doctor ).values_list('pationt', flat=True)
        if doctor_patients.exists() : 
            ress = MedicalRecord.objects.filter(pationt__in=doctor_patients)
            data_list = []
            for item in ress:
                datas = {
                    'child_num': item.child_num,
                    'family_history': item.family_history,
                    'nationalID': item.nationalID,
                    'id': item.id,
                    'name': item.name,
                    'age': item.age,
                    'gender': item.gender
                }
                if item.treatementHistory1 != None : 
                    datas['treatementHistory1']= TreatementHistorySerializer(item.treatementHistory1).data
                if item.treatementHistory2 != None : 
                    datas['treatementHistory2'] = TreatementHistorySerializer(item.treatementHistory2).data
                if item.treatementHistory3 != None : 
                    datas['treatementHistory3']= TreatementHistorySerializer(item.treatementHistory3).data
                if item.therapyTests != None :   
                    v = ThrapyTestSerializer(item.therapyTests).data
                    v['glasserTest'] = GlasserSerializer( item.therapyTests.glasserTest ).data
                    datas['therapyTests'] = v 
                data_list.append(datas)
            serializer = MedicalGetRecord(data=data_list,many=True)
            if serializer.is_valid():
                return Response({"records": serializer.validated_data}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else : 
            return Response({"message" : "you do not have permission."} , status=status.HTTP_200_OK )
        

    def retrieve_list_last_30_day( self , request ) : 
        user = request.user
        end = timezone.now().date()
        start = end - timedelta(days=30)
        if user.role == 'user' : 
            return Response({"message" : "ordinary user can not access this Information."} , status =status.HTTP_400_BAD_REQUEST )
        doctor = Psychiatrist.objects.filter( user = user).first()
        doctor_patients = MedicalRecordPermission.objects.filter(psychiatrist = doctor, created_date__range=[str(start) , str(end)] ).order_by('-created_date').values_list('pationt', flat=True)
        if doctor_patients.exists() : 
            ress = MedicalRecord.objects.filter(pationt__in=doctor_patients)
            data_list = []
            for item in ress:
                datas = {
                    'child_num': item.child_num,
                    'family_history': item.family_history,
                    'nationalID': item.nationalID,
                    'id': item.id,
                    'name': item.name,
                    'age': item.age,
                    'gender': item.gender
                }
                if item.treatementHistory1 != None : 
                    datas['treatementHistory1']= TreatementHistorySerializer(item.treatementHistory1).data
                if item.treatementHistory2 != None : 
                    datas['treatementHistory2'] = TreatementHistorySerializer(item.treatementHistory2).data
                if item.treatementHistory3 != None : 
                    datas['treatementHistory3']= TreatementHistorySerializer(item.treatementHistory3).data
                if item.therapyTests != None :   
                    v = ThrapyTestSerializer(item.therapyTests).data
                    v['glasserTest'] = GlasserSerializer( item.therapyTests.glasserTest ).data
                    datas['therapyTests'] = v 
                # print("datasssss " , datas )
                data_list.append(datas)
            serializer = MedicalGetRecord(data=data_list,many=True)
            if serializer.is_valid():
                return Response({"records": serializer.validated_data}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else : 
            return Response({"message" : "you do not have permission."} , status=status.HTTP_200_OK )
        
    def get_record_by_id(self , request , id ) : 
        # we consider id as patient id 
        user = request.user
        if user.role == 'user' : 
            return Response({"message" : "ordinary user can not access this Information."} , status =status.HTTP_400_BAD_REQUEST )
        # p = Pationt.objects.filter( id = id  ).first()
        ress = MedicalRecord.objects.filter( pationt = id )
        if not ress.exists() : 
            return Response({"message" : "there is no record with this id."} , status =status.HTTP_400_BAD_REQUEST )
        item = ress.first()
        datas = {
            'child_num': item.child_num,
            'family_history': item.family_history,
            'nationalID': item.nationalID,
            'id': item.id,
            'name': item.name,
            'age': item.age,
            'gender': item.gender
        }

        if item.treatementHistory1 != None : 
            datas['treatementHistory1']= TreatementHistorySerializer(item.treatementHistory1).data
        if item.treatementHistory2 != None : 
            datas['treatementHistory2'] = TreatementHistorySerializer(item.treatementHistory2).data
        if item.treatementHistory3 != None : 
            datas['treatementHistory3']= TreatementHistorySerializer(item.treatementHistory3).data
        if item.therapyTests != None :   
            v = ThrapyTestSerializer(item.therapyTests).data
            v['glasserTest'] = GlasserSerializer( item.therapyTests.glasserTest ).data
            datas['therapyTests'] = v 
        
        serializer = MedicalGetRecord(data= datas )
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def query_on_records(self , request ) : 
        query = request.data.get('name')
        user = request.user
        if user.role == 'user' : 
            return Response({"message" : "ordinary user can not access this Information."} , status =status.HTTP_400_BAD_REQUEST )
        doctor = Psychiatrist.objects.filter( user = user).first()
        doctor_patients = MedicalRecordPermission.objects.filter(psychiatrist = doctor ).values_list('pationt', flat=True)
        if doctor_patients.exists() : 
            data_list = []
            objects = MedicalRecord.objects.filter(pationt__in=doctor_patients)
            if query:    
                scores = []
                for obj in objects:
                    score = fuzz.ratio(query, obj.name)
                    if score < 50:
                        continue
                    partial_score = fuzz.partial_ratio(query, obj.name)
                    if partial_score < 60:
                        continue

                    scores.append((obj, score))

                scores.sort(key=lambda x: x[1], reverse=True)
                
                for obj , score in scores : 
                    if score> 45 : 
                        print( "sdflsfjdslfjdslfj " , obj.id )
                        datas = {
                            'id': obj.id,
                            'nationalID': obj.nationalID,
                            'name': obj.name,
                            'patient' : obj.pationt.id
                        }
                        datas['gender'] = 'F' if obj.gender == MedicalRecord.GENDER_Female else 'M'
                        data_list.append(datas)   

                if len(data_list) ==0 : 
                    return Response({"message": "not found any similar data."}, status=status.HTTP_400_BAD_REQUEST)
            else : 
                for obj in objects: 
                    datas = {
                        'nationalID': obj.nationalID,
                        'id': obj.id,
                        'name': obj.name,
                        'patient' : obj.pationt.id
                    }
                    datas['gender'] = 'F' if obj.gender == MedicalRecord.GENDER_Female else 'M'
                    data_list.append(datas)   
            serializer = MedicalQueryRecord(data=data_list,many=True)
            if serializer.is_valid():
                return Response({"records": serializer.validated_data}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else : 
            return Response({"message" : "you do not have permission."} , status=status.HTTP_200_OK )
        

    def retrieve_list_last_year( self , request ) : 
        user = request.user
        end = timezone.now().date()
        start = end - timedelta(days=360)
        if user.role == 'user' : 
            return Response({"message" : "ordinary user can not access this Information."} , status = status.HTTP_400_BAD_REQUEST)
    
        doctor = Psychiatrist.objects.filter( user = user).first()
        doctor_patients = MedicalRecordPermission.objects.filter(psychiatrist = doctor, created_date__range=[str(start) , str(end)] ).order_by('-created_date').values_list('pationt', flat=True)

        if doctor_patients.exists() : 
            ress = MedicalRecord.objects.filter(pationt__in=doctor_patients)
            data_list = []
            for item in ress:
                datas = {
                    'child_num': item.child_num,
                    'family_history': item.family_history,
                    'nationalID': item.nationalID,
                    'id': item.id,
                    'name': item.name,
                    'age': item.age,
                    'gender': item.gender
                }
                if item.treatementHistory1 != None : 
                    datas['treatementHistory1']= TreatementHistorySerializer(item.treatementHistory1).data
                if item.treatementHistory2 != None : 
                    datas['treatementHistory2'] = TreatementHistorySerializer(item.treatementHistory2).data
                if item.treatementHistory3 != None : 
                    datas['treatementHistory3']= TreatementHistorySerializer(item.treatementHistory3).data
                if item.therapyTests != None :   
                    v = ThrapyTestSerializer(item.therapyTests).data
                    v['glasserTest'] = GlasserSerializer( item.therapyTests.glasserTest ).data
                    datas['therapyTests'] = v 
                # print("datasssss " , datas )
                data_list.append(datas)
            serializer = MedicalGetRecord(data=data_list,many=True)
            if serializer.is_valid():
                return Response({"records": serializer.validated_data}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else : 
            return Response({"message" : "you do not have permission."} , status=status.HTTP_200_OK )
    
    def retrieve_check(self , request ) : 
        user = request.user 
        pationt = Pationt.objects.filter(user = user).first()
        records = self.queryset.filter( pationt = pationt )
        if not records.exists() : 
            return Response({"message" : False } , status=status.HTTP_200_OK )
        return Response({"message" : True } , status=status.HTTP_200_OK )

    def retrieve(self , request ) : 
        user = request.user 
        pationt = Pationt.objects.filter(user = user).first()
        records = self.queryset.filter( pationt = pationt )
        if not records.exists() : 
            return Response({"message" : "there is no any records for this user."} , status=status.HTTP_400_BAD_REQUEST )
        item  = records.first() 
        datas = {
            'child_num': item.child_num,
            'family_history': item.family_history,
            'nationalID': item.nationalID,
            'id': item.id,
            'name': item.name,
            'age': item.age,
            'gender': item.gender
        }
        if item.treatementHistory1 != None : 
            datas['treatementHistory1']= TreatementHistorySerializer(item.treatementHistory1).data
        if item.treatementHistory2 != None : 
            datas['treatementHistory2'] = TreatementHistorySerializer(item.treatementHistory2).data
        if item.treatementHistory3 != None : 
            datas['treatementHistory3']= TreatementHistorySerializer(item.treatementHistory3).data
        if item.therapyTests != None :   
            v = ThrapyTestSerializer(item.therapyTests).data
            v['glasserTest'] = GlasserSerializer( item.therapyTests.glasserTest ).data
            datas['therapyTests'] = v 
        
        serializer = MedicalGetRecord(data= datas )
        if serializer.is_valid():
            return Response(serializer.validated_data , status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    def delete(self , request ,id ) : 
        user = request.user 
        if user.role != 'admin' : 
            return Response({"message" : "only admin can access this Information."} , status =status.HTTP_400_BAD_REQUEST )
        ress = MedicalRecord.objects.filter( pationt = id )
        if not ress.exists() : 
            return Response({"message" : "there is no record with this pationt id."} , status =status.HTTP_400_BAD_REQUEST )
        record = ress.first()
        record.delete()
        return Response({"message" : "record deleted successfully"} , status=status.HTTP_204_NO_CONTENT )


class ThrepayTestsView(viewsets.ModelViewSet ) : 
    permission_classes = [IsAuthenticated]
    serializer_class = ThrapyTestSerializer
    def get( self , request ) : 
        user = request.user
        pationt = Pationt.objects.filter(user = user ).first()
        if not pationt : 
            Response({"message" : "there is not patient"} , status=status.HTTP_400_BAD_REQUEST )
        test = TherapyTests.objects.filter( pationt = pationt ).first()
        if not test : 
            Response({"message" : "this user hasn't take any tests!"} , status=status.HTTP_400_BAD_REQUEST)

        v = ThrapyTestSerializer(test).data
        v['glasserTest'] = GlasserSerializer( test.glasserTest ).data
    
        return Response( {"TherapTests" : v} , status=status.HTTP_200_OK )


class GlasserTestView(viewsets.ModelViewSet ) : 
    permission_classes = [IsAuthenticated]
    def create( self, request , *args , **kwargs ) : 
        req_data = {}
        d =  request.data["data"] 
        data = json.loads(d)
        for key in data.keys() : 
            print(data[key])
            req_data[key] = data[key]
            data[key]
        print( req_data )
        if not req_data : 
            return Response({"message" : "test's results could not be empty!!!"} , status=status.HTTP_400_BAD_REQUEST)
        categories = GlasserResults( data=req_data )
        glasser = GlasserTest.objects.create(
            love = categories["love"] , 
            survive = categories["survive"] , 
            freedom = categories["freedom"] , 
            power = categories["power"] , 
            fun = categories["fun"]
        )
        user = request.user
        pationt = Pationt.objects.filter(user = user).first()
        old_test = TherapyTests.objects.filter( pationt = pationt ).first()
        if old_test : 
            old_test.glasserTest = glasser
            old_test.save()
            data = {
                'message' : 'test`s results was successfullly updated' ,   
                "result" :  categories
            }
            return Response( data = data , status=status.HTTP_200_OK )
        else : 
            test = TherapyTests.objects.create( 
                pationt = pationt ,
                glasserTest = glasser 
            )
            data = {
                'message' : 'test`s results was successfullly registered' ,   
                "result" : categories
            }
            return Response(data=data  , status=status.HTTP_200_OK ) 
               

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        pationt = Pationt.objects.filter(user = user ).first()
        print(pationt)
        mbti = TherapyTests.objects.filter( pationt = pationt ).first()
        return Response( {"glasser" : mbti.glasserTest} , status=status.HTTP_200_OK )
            

class GetMBTItest(viewsets.ModelViewSet) : 
    permission_classes = [IsAuthenticated ]

    def create(self, request, *args, **kwargs):
        udata = request.data
        
        data = {}
        for key in udata.keys() : 
            data[int(key)] = udata[key]
        
        user = request.user
        pationt = Pationt.objects.filter(user = user).first()
        mbti = GetMBTIresults( data , user.gender )
        
        old_test = TherapyTests.objects.filter( pationt = pationt ).first()
        if old_test : 
            old_test.MBTItest = mbti['final']
            old_test.save()
            data = {
                'message' : 'test`s results was successfullly updated' , 
                "result" : mbti["final"] 
            }
            return Response( data= data , status=status.HTTP_200_OK )
        else : 
            test = TherapyTests.objects.create( 
                pationt = pationt ,
                MBTItest = mbti['final']
            )
            data = {
                'message' : 'test`s results was successfullly registered' , 
                "result" : mbti["final"] 
            }
            return Response( data= data , status=status.HTTP_200_OK )
    

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        pationt = Pationt.objects.filter(user = user ).first()
        print(pationt)
        # mbti = pationt.therapytests 
        mbti = TherapyTests.objects.filter( pationt = pationt ).first()
        return Response( {"type" : mbti.MBTItest} , status=status.HTTP_200_OK )

