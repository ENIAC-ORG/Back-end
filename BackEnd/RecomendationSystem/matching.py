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
        "stress_level": 1,  # سطح استرس بیمار
        "energy_level": 1,  # سطح انرژی بیمار
        "physical_conditions": 1,  # تجربه کار با مشکلات جسمی
        "crisis_management": 2,  # تجربه مدیریت بحران
        "support_system": 1,  # حمایت عاطفی بیمار
        "treatment_duration": 1,  # تطبیق مدت زمان درمان
        "communication_preference": 1,  # روش ارتباط
    }

    matches = []

    for psychologist in psychologists:
        match_score = 0
        reasons = []

        # 1. تطبیق تخصص‌ها
        if patient.symptoms:
            matched_specialties = set(patient.symptoms).intersection(set(psychologist.specialties))
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
            reasons.append("روانشناس تجربه مدیریت بیماران پر استرس را دارد")

        # 8. سطح انرژی بیمار
        if patient.energy_level and patient.energy_level == "کم" and psychologist.therapy_methods:
            match_score += WEIGHTS["energy_level"]
            reasons.append("تطابق در مدیریت بیماران با انرژی پایین")

        # 9. مشکلات جسمی
        if patient.physical_issues and psychologist.physical_conditions_experience:
            match_score += WEIGHTS["physical_conditions"]
            reasons.append("تجربه با بیماران دارای مشکلات جسمی")

        # 10. حمایت عاطفی
        if patient.has_support_system == "خیر" and "گروه‌درمانی" in psychologist.therapy_methods:
            match_score += WEIGHTS["support_system"]
            reasons.append("روانشناس می‌تواند بیمار را در گروه‌درمانی حمایت کند")

        # 11. تجربه مدیریت بحران
        if patient.suicidal_thoughts != "هرگز" and psychologist.crisis_management:
            match_score += WEIGHTS["crisis_management"]
            reasons.append("تجربه در مدیریت بحران")

        # 12. مدت زمان درمان
        if psychologist.max_sessions_per_week and patient.treatment_duration:
            if patient.treatment_duration == "کوتاه‌مدت" and psychologist.max_sessions_per_week >= 10:
                match_score += WEIGHTS["treatment_duration"]
                reasons.append("روانشناس توانایی مدیریت درمان کوتاه‌مدت را دارد")
            elif patient.treatment_duration == "بلندمدت" and psychologist.max_sessions_per_week < 10:
                match_score += WEIGHTS["treatment_duration"]
                reasons.append("روانشناس توانایی مدیریت درمان بلندمدت را دارد")

        # 13. روش‌های ارتباط
        if patient.communication_preference and psychologist.communication_preference:
            matched_communication = set(patient.communication_preference).intersection(set(psychologist.communication_preference))
            if matched_communication:
                match_score += len(matched_communication) * WEIGHTS["communication_preference"]
                reasons.append(f"تطابق در روش‌های ارتباط: {', '.join(matched_communication)}")

        # جمع‌آوری نتایج
        if match_score > 0:
            matches.append({
                "psychologist": psychologist,
                "match_score": match_score,
                "reasons": reasons,
            })

    # مرتب‌سازی بر اساس امتیاز تطبیق
    matches = sorted(matches, key=lambda x: x["match_score"], reverse=True)
    return matches
