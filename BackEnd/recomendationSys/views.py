from rest_framework import viewsets , status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from Profile.serializer import DoctorProfileSerializer
from Profile.models import Profile
from counseling.models import Psychiatrist
from rest_framework.permissions import IsAuthenticated
from .serializer import DoctorInfoSerializer
from .models import DoctorPersonalityInfo
from .bge_m3 import getting_similarities , process_patient_answeres , process_doctor_answeres

# https://www.youtube.com/watch?v=P2_j1P51dNI&list=RD1mZhwXMl8vc&index=2


class RecomendationSysView(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated]
    # @action(detail=False, methods=['post'])
    def get_recomended_doctors(self, request):
        udata = request.data
        data = {}
        for key in udata.keys() : 
            data[int(key)] = udata[key]
        user = request.user
        user_process_text = process_patient_answeres(data)
        print("data              " , data )
        print("usr process text *********** " , user_process_text )
        doctor_process_text = [ d.text_info for d in DoctorPersonalityInfo.objects.all() ]
        doctor_ids =  [ d.psychiatrist for d in DoctorPersonalityInfo.objects.all() ]
        similars = getting_similarities( user_process_text , 
                                                doctor_process_text , doctor_ids )
        print( similars )
        similar_doctors = [ Profile.objects.filter( id = x[1].id).first() for x in similars ][:3]
        if similars == None : 
            return Response({"message" : "there is no matching for this user."} , status=status.HTTP_400_BAD_REQUEST)
        return Response ( {"doctors" :DoctorProfileSerializer(similar_doctors , many=True ).data } , status=status.HTTP_200_OK)
        
        
    def doctor_info_api(self , request ) : 
        udata = request.data
        doctor = Psychiatrist.objects.filter(user = request.user ).first()
        if request.user.role != 'doctor' : 
            return Response({"message" : "only doctors could access this Information."} , status =status.HTTP_400_BAD_REQUEST )
        if doctor != None : 
            data = {}
            for key in udata.keys() : 
                data[int(key)] = udata[key]
            user = request.user
            doctor_process_text = process_doctor_answeres(data ,user.gender , user.date_of_birth )
            doctorInfo = DoctorPersonalityInfo.objects.create( 
                psychiatrist = doctor,
                text_info = doctor_process_text 
            )
            return Response({"message" : "successfully data added" , "data" : DoctorInfoSerializer(doctorInfo).data } , status= status.HTTP_200_OK)
        return Response({"message" : "there is no doctor with this id ."} , status =status.HTTP_400_BAD_REQUEST )
