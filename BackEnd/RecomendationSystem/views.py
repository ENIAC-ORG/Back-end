from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PatientFormResponse, PsychologistFormResponse
from .serializers import PatientFormResponseSerializer, PsychologistFormResponseSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PatientFormResponse, PsychologistFormResponse
from .matching import match_patient_to_psychologists

class PatientFormAPIView(APIView):
    def get(self, request):
        """
        ارسال سوالات فرم بیمار.
        """
        questions = [
            {"id": 1, "text": "چه علائمی دارید؟", "type": "multiple_choice", "options": [
                "اضطراب", "افسردگی", "مشکلات خواب", "مشکلات رفتاری", "اختلالات خوردن", 
                "مشکلات تمرکز", "مشکلات روابط", "ترس‌ها", "پارانویا", "ADHD", "هیچ‌کدام"]},
            {"id": 2, "text": "سطح استرس روزانه خود را از 1 تا 10 ارزیابی کنید.", "type": "integer"},
            {"id": 3, "text": "سطح انرژی خود را چگونه ارزیابی می‌کنید؟", "type": "choice", "options": ["کم", "متوسط", "زیاد"]},
            {"id": 4, "text": "آیا شما خود را مذهبی می‌دانید؟", "type": "choice", "options": ["مذهبی", "غیرمذهبی", "فرقی نمی‌کند"]},
            {"id": 5, "text": "ترجیح شما برای جنسیت درمانگر چیست؟", "type": "choice", "options": ["زن", "مرد", "فرقی نمی‌کند"]},
            {"id": 6, "text": "ترجیح شما برای نوع جلسات چیست؟", "type": "choice", "options": ["حضوری", "مجازی", "فرقی نمی‌کند"]},
            {"id": 7, "text": "مدت زمان درمان مورد انتظار شما چیست؟", "type": "choice", "options": ["کوتاه‌مدت", "بلندمدت"]},
            {"id": 8, "text": "آیا داروی خاصی مصرف می‌کنید؟ اگر بله، لطفاً نام ببرید.", "type": "text"},
            {"id": 9, "text": "آیا قبلاً درمان روانشناختی یا روان‌پزشکی انجام داده‌اید؟ اگر بله، توضیح دهید.", "type": "text"},
            {"id": 10, "text": "آخرین باری که به خودکشی فکر کردید، چه زمانی بود؟", "type": "choice", "options": ["هرگز", "یک ماه پیش", "هفته گذشته", "همین حالا"]},
            {"id": 11, "text": "آیا مشکلات جسمی خاصی دارید که روی روان شما تأثیر می‌گذارد؟", "type": "text"},
            {"id": 12, "text": "به طور متوسط چند ساعت در شبانه‌روز می‌خوابید؟", "type": "integer"},
            {"id": 13, "text": "آیا به طور منظم در فعالیت‌های اجتماعی یا گروهی شرکت می‌کنید؟", "type": "boolean"},
            {"id": 14, "text": "چه انتظاری از درمانگر خود دارید؟", "type": "text"},
            {"id": 15, "text": "هر توضیح اضافی که می‌تواند کمک کند، در اینجا وارد کنید.", "type": "text"},
        ]
        return Response({"questions": questions}, status=status.HTTP_200_OK)

    def post(self, request):
        """
        دریافت و ذخیره یا به‌روزرسانی پاسخ‌های فرم بیمار.
        """
        user = request.user
        try:
            patient_form = PatientFormResponse.objects.get(user=user)
            serializer = PatientFormResponseSerializer(patient_form, data=request.data)
        except PatientFormResponse.DoesNotExist:
            serializer = PatientFormResponseSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=user)
            return Response({"message": "اطلاعات فرم بیمار با موفقیت ذخیره یا به‌روزرسانی شد."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PsychologistFormAPIView(APIView):
    def get(self, request):
        """
        ارسال سوالات فرم روانشناس.
        """
        questions = [
            {"id": 1, "text": "تخصص‌های شما چیست؟", "type": "multiple_choice", "options": [
                "اضطراب", "افسردگی", "مشکلات خواب", "اختلالات خوردن", "مشکلات روابط",
                "مشکلات رفتاری", "ADHD", "اختلالات شخصیت", "اختلالات روانی شدید"]},
            {"id": 2, "text": "چه روش‌های درمانی را استفاده می‌کنید؟", "type": "multiple_choice", "options": [
                "CBT", "Mindfulness", "Family Therapy", "Psychoanalytic", "Art Therapy", "Group Therapy"]},
            {"id": 3, "text": "با کدام گروه‌های سنی کار می‌کنید؟", "type": "multiple_choice", "options": [
                "کودکان", "نوجوانان", "بزرگ‌سالان", "سالمندان"]},
            {"id": 4, "text": "چه نوع جلساتی را ارائه می‌دهید؟", "type": "choice", "options": ["حضوری", "مجازی", "هر دو"]},
            {"id": 5, "text": "آیا شما خود را مذهبی می‌دانید؟", "type": "choice", "options": ["مذهبی", "غیرمذهبی", "فرقی نمی‌کند"]},
            {"id": 6, "text": "جنسیت شما چیست؟", "type": "choice", "options": ["زن", "مرد", "فرقی نمی‌کند"]},
            {"id": 7, "text": "چند سال سابقه کاری دارید؟", "type": "integer"},
            {"id": 8, "text": "حداکثر تعداد جلسات در هفته که می‌توانید ارائه دهید؟", "type": "integer"},
            {"id": 9, "text": "آیا تجربه کار با بیمارانی که مشکلات جسمی دارند را دارید؟", "type": "boolean"},
            {"id": 10, "text": "آیا در مدیریت بحران (مانند بیماران با خطر خودکشی) تجربه دارید؟", "type": "boolean"},
            {"id": 11, "text": "آیا تمایل دارید با بیماران مذهبی یا غیرمذهبی کار کنید؟", "type": "choice", "options": ["مذهبی", "غیرمذهبی", "فرقی نمی‌کند"]},
            {"id": 12, "text": "آیا ترجیح خاصی برای جنسیت بیمار دارید؟", "type": "choice", "options": ["زن", "مرد", "فرقی نمی‌کند"]},
            {"id": 13, "text": "هر توضیح اضافی که می‌خواهید اضافه کنید.", "type": "text"},
        ]
        return Response({"questions": questions}, status=status.HTTP_200_OK)

    def post(self, request):
        """
        دریافت و ذخیره یا به‌روزرسانی پاسخ‌های فرم روانشناس.
        """
        user = request.user
        try:
            psychologist_form = PsychologistFormResponse.objects.get(user=user)
            serializer = PsychologistFormResponseSerializer(psychologist_form, data=request.data)
        except PsychologistFormResponse.DoesNotExist:
            serializer = PsychologistFormResponseSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=user)
            return Response({"message": "اطلاعات فرم روانشناس با موفقیت ذخیره یا به‌روزرسانی شد."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class MatchPatientToPsychologistsAPIView(APIView):
    def get(self, request):
        """
        یافتن پزشکان مناسب برای بیمار.
        """
        user = request.user

        # بررسی اینکه بیمار فرم را پر کرده باشد
        try:
            patient_form = PatientFormResponse.objects.get(user=user)
        except PatientFormResponse.DoesNotExist:
            return Response({"error": "لطفاً ابتدا فرم بیمار را تکمیل کنید."}, status=status.HTTP_400_BAD_REQUEST)

        # دریافت تمامی پزشکانی که فرم خود را تکمیل کرده‌اند
        psychologists = PsychologistFormResponse.objects.all()
        if not psychologists.exists():
            return Response({"error": "هیچ روانشناسی در سیستم ثبت نشده است."}, status=status.HTTP_404_NOT_FOUND)

        # استفاده از الگوریتم تطبیق
        matches = match_patient_to_psychologists(patient_form, psychologists)

        # ساخت پاسخ
        result = [
            {
                "psychologist_id": match["psychologist"].user.id,
                "psychologist_name": match["psychologist"].user.firstname + " " + match["psychologist"].user.lastname,
                "match_score": match["match_score"],
                "reasons": match["reasons"],
            }
            for match in matches
        ]

        return Response({"matches": result}, status=status.HTTP_200_OK)
