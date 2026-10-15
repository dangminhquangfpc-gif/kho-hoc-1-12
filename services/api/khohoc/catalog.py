def subjects_for_grade(grade: int) -> list[dict]:
    common = [
        ("toan", "Toán"),
        (
            "tieng_viet" if grade <= 5 else "ngu_van",
            "Tiếng Việt" if grade <= 5 else "Ngữ văn",
        ),
    ]
    if grade <= 5:
        names = common + [
            ("dao_duc", "Đạo đức"),
            ("the_chat", "Giáo dục thể chất"),
            ("nghe_thuat", "Nghệ thuật"),
            ("trai_nghiem", "Hoạt động trải nghiệm"),
        ]
        names += (
            [("tu_nhien_xa_hoi", "Tự nhiên và Xã hội")]
            if grade <= 3
            else [("khoa_hoc", "Khoa học"), ("lich_su_dia_li", "Lịch sử và Địa lí")]
        )
        if grade >= 3:
            names += [
                ("tieng_anh", "Tiếng Anh"),
                ("tin_hoc_cong_nghe", "Tin học và Công nghệ"),
            ]
        return [{"id": k, "name": v, "requirement": "required"} for k, v in names]
    names = common + [
        ("tieng_anh", "Tiếng Anh"),
        ("lich_su_dia_li", "Lịch sử và Địa lí"),
        ("khoa_hoc_tu_nhien", "Khoa học tự nhiên"),
        ("tin_hoc", "Tin học"),
        ("cong_nghe", "Công nghệ"),
        ("gdcd", "Giáo dục công dân"),
        ("the_chat", "Giáo dục thể chất"),
        ("nghe_thuat", "Nghệ thuật"),
        ("huong_nghiep", "Hoạt động trải nghiệm, hướng nghiệp"),
    ]
    if grade <= 9:
        return [{"id": k, "name": v, "requirement": "required"} for k, v in names]
    required = common + [
        ("tieng_anh", "Tiếng Anh"),
        ("lich_su", "Lịch sử"),
        ("the_chat", "Giáo dục thể chất"),
        ("quoc_phong", "Giáo dục quốc phòng và an ninh"),
        ("huong_nghiep", "Hoạt động trải nghiệm, hướng nghiệp"),
    ]
    elective = [
        ("dia_li", "Địa lí"),
        ("vat_li", "Vật lí"),
        ("hoa_hoc", "Hóa học"),
        ("sinh_hoc", "Sinh học"),
        ("tin_hoc", "Tin học"),
        ("cong_nghe", "Công nghệ"),
        ("kinh_te_phap_luat", "Giáo dục kinh tế và pháp luật"),
        ("am_nhac", "Âm nhạc"),
        ("mi_thuat", "Mĩ thuật"),
    ]
    return [
        {"id": k, "name": v, "requirement": req}
        for names, req in [(required, "required"), (elective, "elective")]
        for k, v in names
    ]
