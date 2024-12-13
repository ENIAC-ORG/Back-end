from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from utils.google_api_helper import create_meet_event
from utils.email import send_GoogleMeet_Link

class GoogleMeetLinkAPIView(APIView):
    def post(self, request):
        data = request.data
        host_email = data.get("host_email")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        patient_email = data.get("patient_email")  
        psychiatrist_name = data.get("psychiatrist_name")  
        appointment_date = start_time.split('T')[0]  
        appointment_time = start_time.split('T')[1].split('Z')[0]  

        if not all([host_email, start_time, end_time, patient_email, psychiatrist_name]):
            return Response(
                {"error": "host_email, start_time, end_time, patient_email, and psychiatrist_name are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            event = create_meet_event(host_email, start_time, end_time)
            meet_link = event["hangoutLink"]

            # Send email to the patient
            subject = "لینک جلسه مجازی "
            send_GoogleMeet_Link(subject, [patient_email], psychiatrist_name, appointment_date, appointment_time, meet_link)

            return Response(
                {
                    "message": "Google Meet link created and sent successfully.",
                    "meet_link": meet_link,
                    "event_details": event,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
