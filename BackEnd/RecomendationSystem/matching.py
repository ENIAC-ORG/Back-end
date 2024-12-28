def match_patient_to_psychologists(patient, psychologists):
    """
    تطبیق بیمار با روانشناسان موجود، با اولویت‌بندی و مدیریت سوالات بدون پاسخ.
    
    Args:
        patient (Patient): اطلاعات بیمار.
        psychologists (QuerySet[Psychologist]): لیست روانشناسان.
        
    Returns:
        List[dict]: لیستی از روانشناسان مرتب شده بر اساس امتیاز تطبیق.
    """
    # وزن‌دهی معیارها
    WEIGHTS = {
        "specialties": 3,  # تطبیق تخصص‌ها
        "therapy_methods": 2,  # تطبیق روش‌های درمانی
        "age_groups": 2,  # تطبیق گروه سنی
        "gender": 1,  # جنسیت روانشناس
        "religion": 1,  # مذهبی بودن روانشناس
        "session_preference": 1,  # نوع جلسات
        "stress_level": 2,  # سطح استرس بیمار
        "energy_level": 1,  # سطح انرژی بیمار
        "physical_conditions": 2,  # تجربه کار با مشکلات جسمی
        "crisis_management": 2,  # تجربه مدیریت بحران
        "support_system": 2,  # حمایت عاطفی بیمار
        "sleep_hours": 1,  # ساعت خواب بیمار
        "medications": 2,  # داروهای خاص
        "suicidal_thoughts": 3,  # آخرین فکر خودکشی
        "treatment_duration": 1,  # تطبیق مدت زمان درمان
        "communication_preference": 1,  # روش ارتباط
    }

    # تطبیق علائم بیمار با تخصص‌های روانشناس
    symptom_to_specialty_map = {
        "اضطراب": ["اضطراب", "اختلالات روانی شدید"],
        "افسردگی": ["افسردگی", "اختلالات روانی شدید"],
        "مشکلات خواب": ["مشکلات خواب"],
        "مشکلات رفتاری": ["مشکلات رفتاری"],
        "اختلالات خوردن": ["اختلالات خوردن"],
        "مشکلات تمرکز": ["ADHD", "اختلالات شخصیت"],
        "مشکلات روابط": ["مشکلات روابط", "اختلالات شخصیت"],
        "ترس‌ها": ["اضطراب", "اختلالات روانی شدید"],
        "پارانویا": ["اختلالات روانی شدید"],
        "ADHD": ["ADHD"],
    }

    # روش‌های درمانی که بیمار ترجیح می‌دهد
    therapy_method_map = {
        "درمان شناختی-رفتاری (CBT)": "CBT",
        "آگاهی‌حاضر (Mindfulness)": "Mindfulness",
        "درمان خانواده": "Family Therapy",
        "درمان روان‌تحلیلی": "Psychoanalytic",
        "درمان هنری": "Art Therapy",
        "درمان گروهی": "Group Therapy",
    }

    matches = []

    for psychologist in psychologists:
        match_score = 0
        reasons = []

        # 1. تطبیق تخصص‌ها با علائم بیمار
        if patient.symptoms:
            matched_specialties = set()
            for symptom in patient.symptoms:
                if symptom in symptom_to_specialty_map:
                    matched_specialties.update(symptom_to_specialty_map[symptom])

            # بررسی تطبیق تخصص‌ها
            if matched_specialties:
                matched_specialties = matched_specialties.intersection(set(psychologist.specialties))
                if matched_specialties:
                    match_score += len(matched_specialties) * WEIGHTS["specialties"]
                    reasons.append(f"تطابق در تخصص‌ها: {', '.join(matched_specialties)}")

        # 2. تطبیق روش‌های درمانی
        if patient.preferred_therapy_methods:
            matched_methods = set(patient.preferred_therapy_methods).intersection(set(psychologist.therapy_methods))
            if matched_methods:
                match_score += len(matched_methods) * WEIGHTS["therapy_methods"]
                reasons.append(f"تطابق در روش‌های درمانی: {', '.join(matched_methods)}")

        # 3. تطبیق گروه سنی
        age_group_matched = False
        if patient.age:
            if patient.age < 18 and "کودکان" in psychologist.age_groups:
                age_group_matched = True
            elif 18 <= patient.age <= 24 and "نوجوانان" in psychologist.age_groups:
                age_group_matched = True
            elif 25 <= patient.age <= 64 and "بزرگ‌سالان" in psychologist.age_groups:
                age_group_matched = True
            elif patient.age > 64 and "سالمندان" in psychologist.age_groups:
                age_group_matched = True

        if age_group_matched:
            match_score += WEIGHTS["age_groups"]
            reasons.append("تطبیق در گروه سنی")

        # 4. تطبیق جنسیت روانشناس
        if psychologist.gender == patient.therapist_gender_preference or patient.therapist_gender_preference == "فرقی نمی‌کند":
            match_score += WEIGHTS["gender"]
            reasons.append("تطبیق در جنسیت")

        # 5. تطبیق مذهبی بودن
        if psychologist.religion == patient.religion_preference or patient.religion_preference == "فرقی نمی‌کند":
            match_score += WEIGHTS["religion"]
            reasons.append("تطبیق در مذهب")

        # 6. تطبیق نوع جلسه
        if psychologist.session_preference in [patient.presentation_preference, "هر دو"]:
            match_score += WEIGHTS["session_preference"]
            reasons.append("تطبیق در نوع جلسه")

        # 7. سطح استرس بیمار
        if patient.stress_level and 7 <= int(patient.stress_level) <= 10 and psychologist.crisis_management:
            match_score += WEIGHTS["stress_level"]
            reasons.append("روانشناس تجربه مدیریت بحران دارد")

        # 8. تطبیق مدت زمان درمان
        if patient.treatment_duration:
            if patient.treatment_duration == psychologist.treatment_duration:
                match_score += WEIGHTS["treatment_duration"]
                reasons.append(f"تطبیق در مدت زمان درمان: {patient.treatment_duration}")

        # 9. تطبیق داروهای خاص
        if patient.current_medications and psychologist.medication_experience:
            match_score += WEIGHTS["medications"]
            reasons.append("روانشناس تجربه مدیریت داروهای خاص دارد")

        # 10. تطبیق آخرین فکر خودکشی
        if patient.suicidal_thoughts == "بله" and psychologist.crisis_management:
            match_score += WEIGHTS["suicidal_thoughts"]
            reasons.append("روانشناس تجربه مدیریت خطر خودکشی دارد")

        # 11. تطبیق نوع ارتباط
        if patient.communication_preference in psychologist.communication_preferences or psychologist.communication_preferences == "هر دو":
            match_score += WEIGHTS["communication_preference"]
            reasons.append("تطبیق در نوع ارتباط")

        # 12. سطح انرژی بیمار (امکان تطبیق با سایر فاکتورها)
        if patient.energy_level:
            if patient.energy_level == "کم" and any(specialty in ["افسردگی", "اضطراب"] for specialty in psychologist.specialties):
                match_score += WEIGHTS["energy_level"]
                reasons.append("روانشناس تجربه کار با بیماران با انرژی کم دارد (افسردگی/اضطراب)")
            elif patient.energy_level == "زیاد" and "ADHD" in psychologist.specialties:
                match_score += WEIGHTS["energy_level"]
                reasons.append("روانشناس تجربه کار با بیماران با انرژی زیاد دارد (ADHD)")

        # 13. تجربه کار با مشکلات جسمی
        if patient.physical_conditions and psychologist.physical_condition_experience:
            match_score += WEIGHTS["physical_conditions"]
            reasons.append("روانشناس تجربه کار با مشکلات جسمی دارد")

        # 14. حمایت عاطفی بیمار
        if patient.support_system:
            # اگر بیمار حمایت عاطفی کم دارد، به دنبال روانشناس‌هایی با روش‌های درمانی مرتبط می‌گردیم
            if patient.support_system == "کم":
                # روش‌های درمانی که بیشتر با حمایت عاطفی مرتبط هستند
                preferred_methods = ["CBT", "Family Therapy", "Mindfulness"]

                # تطبیق با روش‌های درمانی (امتیاز تطابق نسبی از 0 تا 1)
                matched_methods = [method for method in psychologist.therapy_methods if method in preferred_methods]
                match_score_method = len(matched_methods) / len(preferred_methods) if preferred_methods else 0
                match_score += match_score_method * WEIGHTS["support_system"]
                if matched_methods:
                    reasons.append(f"تجربه در حمایت عاطفی از طریق روش‌های درمانی مناسب: {', '.join(matched_methods)}")
        

        # 15. ساعت خواب بیمار
        if patient.sleep_hours and psychologist.specialties:  # فرض بر این است که روانشناس تجربه مدیریت مشکلات خواب دارد
            if int(patient.sleep_hours) < 5 and "مشکلات خواب" in psychologist.specialties:
                match_score += WEIGHTS["sleep_hours"]
                reasons.append("روانشناس تجربه مدیریت مشکلات خواب دارد")

        matches.append({
            "psychologist": psychologist,
            "match_score": match_score,
            "reasons": reasons,
        })

    # مرتب‌سازی بر اساس امتیاز تطبیق
    matches = sorted(matches, key=lambda x: x["match_score"], reverse=True)
    return matches
