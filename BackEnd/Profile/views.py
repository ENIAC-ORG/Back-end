from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Profile
from .serializers import DoctorProfileSerializer 


class DoctorProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = DoctorProfileSerializer

    @action(detail=False, methods=['get'])
    def filter_by_profile_type(self, request):
        profile_type = request.query_params.get('profile_type')
        if profile_type:
            queryset = self.queryset.filter(profile_type=profile_type)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "profile_type parameter is required"}, status=400)

