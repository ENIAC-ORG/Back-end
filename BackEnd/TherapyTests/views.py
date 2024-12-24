from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from utils.therapy_tests import GetMBTIresults ,GlasserResults , phq9Results
from counseling.models import Pationt ,Psychiatrist
from .models import TherapyTests , GlasserTest , MedicalRecord , MedicalRecordPermission 
from rest_framework import status 
import json 
from datetime import timedelta 
from django.utils import timezone
from .serializer import *
from django.forms.models import model_to_dict
from fuzzywuzzy import fuzz
import logging 

logger = logging.getLogger(__name__)

class MedicalRecordView(viewsets.ModelViewSet ) : 
    permission_classes = [IsAuthenticated]
    queryset = MedicalRecord.objects.all()
    http_method_names = ['get','post','retrieve','put','patch' , 'delete']
    
    def create(self , request ) :
        user = request.user
        pationt = Pationt.objects.filter(user=user).first()
        if not pationt:
            return Response({"error": "Patient not found for the current user."}, status=status.HTTP_404_NOT_FOUND)
        request.data['pationt'] = pationt.id  
        serializer = MedicalRecordCreateSerializer(data=request.data)
        if serializer.is_valid():
            logger.warning("this is request and here : {}".format(request.data)  )
            medical_record = serializer.save()
            oi_dict = model_to_dict(medical_record)
            oi_serialized = json.dumps(oi_dict)
            data = {
                "medical_record" : oi_serialized , 
                "message" : "record has been successfully created."
            }
            logger.debug( "update  this is treatement histories ************** ... "  )

            return Response(data , status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request):
        user = request.user
        pationt = Pationt.objects.filter(user=user).first()
        
        if not pationt:
            return Response({"detail": "Patient not found."}, status=status.HTTP_404_NOT_FOUND)
        medical_record = get_object_or_404(MedicalRecord, pationt=pationt)

        serializer = MedicalRecordCreateSerializer(instance=medical_record, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve_list_all( self , request ) : 
        user = request.user
        if user.role == 'user' : 
            return Response({"message" : "ordinary user can not access this Information."} , status =status.HTTP_400_BAD_REQUEST )
        doctor = Psychiatrist.objects.filter( user = user)
        if not doctor.exists(): 
            return Response({"message" : "doctor does not exist."} , status =status.HTTP_400_BAD_REQUEST )
        doctor = doctor.first()
        doctor_patients = MedicalRecordPermission.objects.filter(psychiatrist = doctor ).values_list('pationt', flat=True)
        if doctor_patients.exists() : 
            ress = MedicalRecord.objects.filter(pationt__in=doctor_patients)
            serializer = MedicalRecordGetSerializer(instance=ress , many=True)
            return Response({"records": serializer.data}, status=status.HTTP_200_OK)
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
            serializer = MedicalRecordGetSerializer(instance=ress , many=True)
            return Response({"records": serializer.data}, status=status.HTTP_200_OK)
        else : 
            return Response({"message" : "you do not have permission."} , status=status.HTTP_200_OK )
        
    def get_record_by_id(self , request , id ) : 
        user = request.user
        if user.role == 'user':
            return Response(
                {"message": "Ordinary user cannot access this information."},
                status=status.HTTP_400_BAD_REQUEST
            )
        ress = MedicalRecord.objects.filter(pationt=id)
        if not ress.exists():
            return Response(
                {"message": "There is no record with this ID."},
                status=status.HTTP_400_BAD_REQUEST
            )
        item = ress.first()
        serializer = MedicalRecordGetSerializer(instance=item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

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
        doctor_patients = MedicalRecordPermission.objects.filter(psychiatrist = doctor, 
                                                                created_date__range=[str(start) , str(end)] ).order_by('-created_date').values_list('pationt', flat=True)
        if doctor_patients.exists() : 
            ress = MedicalRecord.objects.filter(pationt__in=doctor_patients)
            serializer = MedicalRecordGetSerializer(instance=ress , many=True)
            return Response({"records": serializer.data}, status=status.HTTP_200_OK)
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
        if not records.exists():
            return Response(
                {"message": "There is no record for this user."},
                status=status.HTTP_400_BAD_REQUEST
            )
        item  = records.first() 
       
        serializer = MedicalRecordGetSerializer(instance=item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
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
            
class PHQ9test(viewsets.ModelViewSet): 
    permission_classes = [IsAuthenticated]
    def create(self, request, *args, **kwargs):
        data = request.data 
        try: 
            for key in data.keys() : 
                data[int(key)] = data[key]
            user = request.user
            pationt = Pationt.objects.filter(user = user).first()
            phq = phq9Results(data)                    
            old_test = TherapyTests.objects.filter( pationt = pationt ).first()
            if old_test : 
                old_test.phq9 = phq
                old_test.phq9_created_at = timezone.now()
                old_test.save()
                data = {
                    'message' : 'test`s results was successfullly updated' , 
                    "result" : phq ,
                }
                return Response( data= data , status=status.HTTP_200_OK )
            else : 
                test = TherapyTests.objects.create( 
                    pationt = pationt ,
                    phq9 = phq , 
                    phq9_created_at = timezone.now(),
                )
                data = {
                    'message' : 'test`s results was successfullly registered' , 
                    "result" : phq
                }
                return Response( data= data , status=status.HTTP_200_OK )
    

        except KeyError as e:
            return Response(
                data={"message": f"Invalid data key: {e}."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError as e:
            return Response(
                data={"message": f"Value error encountered: {e}."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                data={"message": f"An unexpected error occurred: {str(e)}."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    def retrieve(self, request, *args, **kwargs):
        user = request.user
        pationt = Pationt.objects.filter(user = user ).first()
        # mbti = pationt.therapytests 
        test = TherapyTests.objects.filter( pationt = pationt ).first()
        return Response( {"type" : test.phq9 , "created_at" : test.phq9_created_at} , status=status.HTTP_200_OK )


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

