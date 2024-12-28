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
import json

class PatientFormAPIView(APIView):
    def get(self, request):
        """
        ارسال سوالات فرم بیمار.
        """
        questions = [
            {"id": 1, "text": "سن شما چند سال است؟", "type": "number"},
            {"id": 2, "text": "سطح انرژی خود را چگونه ارزیابی می‌کنید؟ (کم، متوسط، زیاد)", "type": "choice", "options": ["کم", "متوسط", "زیاد"]},
            {"id": 3, "text": "آیا داروی خاصی مصرف می‌کنید؟ اگر بله، لطفاً نام ببرید.", "type": "text"},
            {"id": 4, "text": "آیا مشکلات جسمی خاصی دارید که روی روان شما تأثیر می‌گذارد؟", "type": "text"},
            {"id": 5, "text": "چه علائمی دارید؟", "type": "multiple_choice", "options": ["اضطراب", "افسردگی", "مشکلات خواب", "مشکلات رفتاری", "اختلالات خوردن", "مشکلات تمرکز", "مشکلات روابط", "ترس‌ها", "پارانویا", "ADHD", "هیچ‌کدام"]},
            {"id": 6, "text": "آیا قبلاً درمان روانشناختی یا روان‌پزشکی انجام داده‌اید؟ اگر بله، توضیح دهید.", "type": "text"},
            {"id": 7, "text": "آخرین باری که به خودکشی فکر کردید، چه زمانی بود؟", "type": "choice", "options": ["هرگز", "یک ماه پیش", "هفته گذشته", "همین حالا"]},
            {"id": 8, "text": "سطح استرس روزانه خود را از 1 تا 10 ارزیابی کنید.", "type": "number"},
            {"id": 9, "text": "به طور متوسط چند ساعت در شبانه‌روز می‌خوابید؟", "type": "number"},
            {"id": 10, "text": "آیا به طور منظم در فعالیت‌های اجتماعی یا گروهی شرکت می‌کنید؟ (بله یا خیر)", "type": "boolean"},
            {"id": 11,"text": "چقدر از حمایت اجتماعی و عاطفی اطرافیان خود برخوردار هستید؟","type": "choice","options": ["کم", "متوسط", "زیاد"]},
            {"id": 12, "text": "مدت زمان درمان مورد انتظار شما چیست؟", "type": "choice", "options": ["کوتاه‌مدت", "بلندمدت"]},
            {"id": 13, "text": "آیا شما خود را مذهبی می‌دانید؟", "type": "choice", "options": ["مذهبی", "غیرمذهبی", "فرقی نمی‌کند"]},
            {"id": 14, "text": "ترجیح شما برای جنسیت درمانگر چیست؟", "type": "choice", "options": ["زن", "مرد", "فرقی نمی‌کند"]},
            {"id": 15, "text": "ترجیح شما برای نوع جلسات چیست؟", "type": "choice", "options": ["حضوری", "مجازی", "فرقی نمی‌کند"]},
            {"id": 16,"text": "چه روش درمانی را ترجیح می‌دهید؟","type": "multiple_choice","options": ["درمان شناختی-رفتاری (CBT)","آگاهی‌حاضر (Mindfulness)","درمان خانواده","درمان روان‌تحلیلی","درمان هنری","درمان گروهی"]},
            {"id": 17, "text": "چه روش‌هایی را برای ارتباط با درمانگر خود ترجیح می‌دهید؟", "type": "multiple_choice", "options": ["تماس تلفنی", "ایمیل", "پیام‌رسانی"]},
            {"id": 18, "text": "چه انتظاری از درمانگر خود دارید؟", "type": "text"},
            {"id": 19, "text": "هر توضیح اضافی که می‌تواند کمک کند، در اینجا وارد کنید.", "type": "text"}
        ]
        return Response({"questions": questions}, status=status.HTTP_200_OK)



    def post(self, request):
        """
        دریافت و ذخیره یا به‌روزرسانی پاسخ‌های فرم بیمار.
        """
        user = request.user

        # پردازش داده‌های ورودی و تبدیل به نوع مناسب
        processed_data = {}

        for key, value in request.data.items():
            if key in ["age", "stress_level", "sleep_hours"]:  # فیلدهای عددی
                try:
                    processed_data[key] = int(value)
                except ValueError:
                    return Response({"error": f"مقدار وارد شده برای فیلد {key} باید عدد صحیح باشد."}, status=status.HTTP_400_BAD_REQUEST)

            elif key in ["energy_level", "suicidal_thoughts", "religion_preference", "therapist_gender_preference", "presentation_preference", "support_system", "treatment_duration"]:  # فیلدهایی با گزینه‌های از پیش تعریف شده
                processed_data[key] = value

            elif key in ["social_activities"]:  # فیلد بولین
                processed_data[key] = True if value == "بله" else False

            elif key in ["preferred_therapy_methods", "communication_preference", "symptoms"]:  # فیلدهای چند گزینه‌ای
                if isinstance(value, list):
                    processed_data[key] = value
                else:
                    try:
                        processed_data[key] = json.loads(value) if value else []
                    except json.JSONDecodeError:
                        return Response({"error": f"مقدار وارد شده برای فیلد {key} باید لیست باشد."}, status=status.HTTP_400_BAD_REQUEST)

            elif key in ["additional_notes", "past_treatments", "current_medications", "physical_issues", "expectations"]:  # فیلدهای متنی
                processed_data[key] = value

            else:
                return Response({"error": f"فیلد {key} غیرمجاز است."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            patient_form = PatientFormResponse.objects.get(user=user)
            serializer = PatientFormResponseSerializer(patient_form, data=processed_data)
        except PatientFormResponse.DoesNotExist:
            serializer = PatientFormResponseSerializer(data=processed_data)

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
            {"id": 1, "text": "تخصص‌های شما چیست؟", "type": "multiple_choice", "options": ["اضطراب", "افسردگی", "مشکلات خواب", "اختلالات خوردن", "مشکلات روابط", "مشکلات رفتاری", "ADHD", "اختلالات شخصیت", "اختلالات روانی شدید"]},
            {"id": 2, "text": "چه روش‌های درمانی را استفاده می‌کنید؟", "type": "multiple_choice", "options": ["CBT", "Mindfulness", "Family Therapy", "Psychoanalytic", "Art Therapy", "Group Therapy"]},
            {"id": 3, "text": "با کدام گروه‌های سنی کار می‌کنید؟", "type": "multiple_choice", "options": ["کودکان", "نوجوانان", "بزرگ‌سالان", "سالمندان"]},
            {"id": 4, "text": "چه نوع جلساتی را ارائه می‌دهید؟", "type": "choice", "options": ["حضوری", "مجازی", "هر دو"]},
            {"id": 5, "text": "آیا شما خود را مذهبی می‌دانید؟", "type": "choice", "options": ["مذهبی", "غیرمذهبی", "فرقی نمی‌کند"]},
            {"id": 6, "text": "جنسیت شما چیست؟", "type": "choice", "options": ["زن", "مرد"]},
            {"id": 7, "text": "چند سال سابقه کاری دارید؟", "type": "number"},
            {"id": 8, "text": "حداکثر تعداد جلسات در هفته که می‌توانید ارائه دهید؟", "type": "number"},
            {"id": 9, "text": "حداکثر مدت زمان درمان که می‌توانید ارائه دهید چیست؟","type": "choice","options": ["کوتاه مدت", "میانه مدت", "بلند مدت"]},
            {"id": 10, "text": " (بله یا خیر) آیا تجربه کار با بیمارانی که مشکلات جسمی دارند را دارید؟", "type": "boolean"},
            {"id": 11, "text": " (بله یا خیر) آیا در مدیریت بحران (مانند بیماران با خطر خودکشی) تجربه دارید؟", "type": "boolean"},
            {"id": 12,"text": " (بله یا خیر) آیا تجربه کار با بیمارانی که داروهای خاص مصرف می‌کنند را دارید؟","type": "boolean"},
            {"id": 13, "text": "آیا تمایل دارید با بیماران مذهبی یا غیرمذهبی کار کنید؟", "type": "choice", "options": ["مذهبی", "غیرمذهبی", "فرقی نمی‌کند"]},
            {"id": 14, "text": "آیا ترجیح خاصی برای جنسیت بیمار دارید؟", "type": "choice", "options": ["زن", "مرد", "فرقی نمی‌کند"]},
            {"id": 15, "text": "ترجیح شما برای ارتباط با بیماران چیست؟","type": "multiple_choice", "options": ["تماس تلفنی", "ایمیل", "پیام‌رسانی"]},
            {"id": 16, "text": "هر توضیح اضافی که می‌خواهید اضافه کنید.", "type": "text"}
           

        ]
        return Response({"questions": questions}, status=status.HTTP_200_OK)

    def post(self, request):
        """
        دریافت و ذخیره یا به‌روزرسانی پاسخ‌های فرم روانشناس.
        """
        user = request.user

        # پردازش داده‌های ورودی و تبدیل به نوع مناسب
        processed_data = {}

        for key, value in request.data.items():
            if key in ["physical_conditions_experience", "crisis_management", "medications_experience"]:  # فیلدهای بولین
                processed_data[key] = True if value == "بله" else False

            elif key in ["experience_years", "max_sessions_per_week"]:  # فیلدهای عددی
                try:
                    processed_data[key] = int(value)
                except ValueError:
                    return Response({"error": f"مقدار وارد شده برای فیلد {key} باید عدد صحیح باشد."}, status=status.HTTP_400_BAD_REQUEST)

            elif key in ["specialties", "therapy_methods", "age_groups", "communication_preference"]:  # فیلدهای چند گزینه‌ای
                if isinstance(value, list):
                    processed_data[key] = value
                else:
                    try:
                        processed_data[key] = json.loads(value) if value else []
                    except json.JSONDecodeError:
                        return Response({"error": f"مقدار وارد شده برای فیلد {key} باید لیست باشد."}, status=status.HTTP_400_BAD_REQUEST)

            elif key in ["session_preference", "religion", "gender", "prefers_gender", "treatment_duration", "prefers_religious_patients"]:  # فیلدهای انتخابی
                processed_data[key] = value

            elif key in ["additional_notes"]:  # فیلدهای متنی
                processed_data[key] = value

            else:
                return Response({"error": f"فیلد {key} غیرمجاز است."}, status=status.HTTP_400_BAD_REQUEST)

        # بررسی وجود یا عدم وجود فرم روانشناس برای کاربر
        try:
            psychologist_form = PsychologistFormResponse.objects.get(user=user)
            serializer = PsychologistFormResponseSerializer(psychologist_form, data=processed_data)
        except PsychologistFormResponse.DoesNotExist:
            serializer = PsychologistFormResponseSerializer(data=processed_data)

        # ذخیره یا به‌روزرسانی داده‌ها
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
