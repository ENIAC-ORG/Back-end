from rest_framework import serializers
from .models import Profile


class DoctorProfileSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = Profile
        fields = '__all__'

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image: 
            return request.build_absolute_uri(f'/backend/media/{obj.image}')
        return None 
