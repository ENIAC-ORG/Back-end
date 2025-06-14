from django.urls import path 
from .views import *

urlpatterns = [
    path( 'MBTI/' , GetMBTItest.as_view({'post' : 'create' , 'get' : 'retrieve'}) , name='MBTI') ,
    path('glasser/' , GlasserTestView.as_view({'post' : 'create' , 'get' : 'retrieve'}) , name='glasser') ,
    path('phq9/' , PHQ9test.as_view({'post' : 'create' , 'get' : 'retrieve'}) , name='phq9') ,
    path('tests/' , ThrepayTestsView.as_view({"get" : "get"}) , name="patient_tests") , 
    path('record/<int:id>/' , MedicalRecordView.as_view( { 'delete' : 'delete' , 'get' : 'get_record_by_id'}) , name='patient_record') , 
    path('record/' , MedicalRecordView.as_view({'post' : 'create' , 'put' : 'update' , 'get' : 'retrieve' }) , name='records_ops') , 
    path( 'record_doctor_month/' , MedicalRecordView.as_view({'get' : 'retrieve_list_last_30_day' }) , name='month_records_ops') ,
    path( 'record_doctor_year/' , MedicalRecordView.as_view({'get' : 'retrieve_list_last_year' }) , name='year_records_ops') ,
    path( 'record_all/' , MedicalRecordView.as_view( {'get' : 'retrieve_list_all'}),name='record_all') , 
    path( 'record/query/' , MedicalRecordView.as_view( {'post' : 'query_on_records'}),name='record_query') , 
    path('record_check/' , MedicalRecordView.as_view({'get' : 'retrieve_check'}) , name= 'record_check')
]