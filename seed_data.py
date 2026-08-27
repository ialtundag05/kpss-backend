"""Seed data for KPSS Quest app - Turkish exam prep content."""

QUESTIONS = [
    # TARİH
    {"subject": "Tarih", "topic": "Osmanlı Kuruluş", "question_text": "Osmanlı Devleti hangi yıl kurulmuştur?",
     "option_a": "1299", "option_b": "1326", "option_c": "1389", "option_d": "1453",
     "correct_option": "a", "difficulty": 1, "is_frequently_asked": True},
    {"subject": "Tarih", "topic": "Fetih Dönemi", "question_text": "İstanbul hangi yıl fethedilmiştir?",
     "option_a": "1451", "option_b": "1453", "option_c": "1458", "option_d": "1461",
     "correct_option": "b", "difficulty": 1, "is_frequently_asked": True},
    {"subject": "Tarih", "topic": "Kurtuluş Savaşı", "question_text": "TBMM hangi tarihte açılmıştır?",
     "option_a": "19 Mayıs 1919", "option_b": "23 Nisan 1920", "option_c": "29 Ekim 1923", "option_d": "24 Temmuz 1923",
     "correct_option": "b", "difficulty": 2, "is_frequently_asked": True},

    # COĞRAFYA
    {"subject": "Coğrafya", "topic": "Türkiye Fiziki", "question_text": "Türkiye'nin en yüksek dağı hangisidir?",
     "option_a": "Erciyes", "option_b": "Kaçkar", "option_c": "Ağrı", "option_d": "Süphan",
     "correct_option": "c", "difficulty": 1, "is_frequently_asked": True},
    {"subject": "Coğrafya", "topic": "Türkiye Fiziki", "question_text": "Türkiye'nin en uzun nehri hangisidir?",
     "option_a": "Fırat", "option_b": "Kızılırmak", "option_c": "Sakarya", "option_d": "Dicle",
     "correct_option": "b", "difficulty": 1, "is_frequently_asked": True},

    # VATANDAŞLIK
    {"subject": "Vatandaşlık", "topic": "Anayasa", "question_text": "Türkiye Cumhuriyeti Anayasası hangi yıl kabul edilmiştir? (Mevcut)",
     "option_a": "1961", "option_b": "1971", "option_c": "1982", "option_d": "2007",
     "correct_option": "c", "difficulty": 1, "is_frequently_asked": True},
    {"subject": "Vatandaşlık", "topic": "Devlet Yapısı", "question_text": "TBMM üye sayısı kaçtır?",
     "option_a": "450", "option_b": "500", "option_c": "550", "option_d": "600",
     "correct_option": "d", "difficulty": 1, "is_frequently_asked": True},

    # MATEMATİK
    {"subject": "Matematik", "topic": "Temel İşlemler", "question_text": "3x + 5 = 20 denkleminde x kaçtır?",
     "option_a": "3", "option_b": "5", "option_c": "7", "option_d": "15",
     "correct_option": "b", "difficulty": 1, "is_frequently_asked": True},
    {"subject": "Matematik", "topic": "Yüzde", "question_text": "80'in %25'i kaçtır?",
     "option_a": "15", "option_b": "20", "option_c": "25", "option_d": "30",
     "correct_option": "b", "difficulty": 1, "is_frequently_asked": True},

    # TÜRKÇE (YENİ EKLENDİ)
    {"subject": "Türkçe", "topic": "Cümlede Anlam", "question_text": "Aşağıdaki cümlelerin hangisinde 'neden-sonuç' ilişkisi vardır?",
     "option_a": "Yağmur yağınca içeri girdik.", "option_b": "Güneş açsın diye dua ettik.", "option_c": "Çok çalışırsan başarırsın.", "option_d": "Akşam bize gelecekler.",
     "correct_option": "a", "difficulty": 1, "is_frequently_asked": True},
    
    # EĞİTİM BİLİMLERİ (YENİ EKLENDİ)
    {"subject": "Eğitim Bilimleri", "topic": "Gelişim Psikolojisi", "question_text": "Piaget'ye göre soyut işlemler dönemi hangi yaş aralığını kapsar?",
     "option_a": "0-2", "option_b": "2-7", "option_c": "7-11", "option_d": "11-18",
     "correct_option": "d", "difficulty": 2, "is_frequently_asked": True},

    # GÜNCEL BİLGİLER (YENİ EKLENDİ)
    {"subject": "Güncel Bilgiler", "topic": "2026 Olimpiyatları", "question_text": "2026 Kış Olimpiyatları hangi ülkede düzenlenecektir?",
     "option_a": "İtalya", "option_b": "Fransa", "option_c": "Japonya", "option_d": "Kanada",
     "correct_option": "a", "difficulty": 3, "is_frequently_asked": True},
]

FLASHCARDS = [
    # Eskiler
    {"subject": "Tarih", "front_text": "1453", "back_text": "İstanbul'un fethi"},
    {"subject": "Coğrafya", "front_text": "Ağrı Dağı", "back_text": "Türkiye'nin en yüksek dağı (5137 m)"},
    {"subject": "Vatandaşlık", "front_text": "600", "back_text": "TBMM milletvekili sayısı"},
    {"subject": "Matematik", "front_text": "Karenin alanı", "back_text": "Kenar × Kenar (a²)"},
    # Yeniler
    {"subject": "Türkçe", "front_text": "Ünsüz Benzeşmesi (Sertleşmesi)", "back_text": "Fıstıkçı Şahap harfleriyle biten kelimenin c,d,g ile başlayan ek alınca ç,t,k'ye dönüşmesi."},
    {"subject": "Eğitim Bilimleri", "front_text": "Klasik Koşullanma", "back_text": "Pavlov - Nötr uyarıcının koşullu uyarıcıya dönüşmesi süreci."},
    {"subject": "Güncel Bilgiler", "front_text": "NATO'ya katılan son ülke (2024)", "back_text": "İsveç"},
]

VIDEOS = [
    # TARİH (Senin İstediğin Özel Videolar)
    {"title": "İstanbul'un Fethi ve Fatih Sultan Mehmet", "video_url": "https://www.youtube.com/embed/wG4vpTjcJIw", "subject": "Tarih"},
    {"title": "Osmanlı Devleti'nin Kuruluşu Kısaca", "video_url": "https://www.youtube.com/embed/rZo3xkzTfrs", "subject": "Tarih"},
    
    # DİĞER DERSLER
    {"title": "Türkiye'nin Coğrafi Bölgeleri", "video_url": "https://www.youtube.com/embed/xW8xJXjKMdY", "subject": "Coğrafya"},
    {"title": "Anayasa Temel Kavramlar", "video_url": "https://www.youtube.com/embed/GfoUyv0Ie3Y", "subject": "Vatandaşlık"},
    {"title": "Yüzde Problemleri Pratik Çözüm", "video_url": "https://www.youtube.com/embed/8kK2zwjRV0M", "subject": "Matematik"},
    
    # YENİ EKLENEN DERSLERİN VİDEOLARI
    {"title": "Cümlede Anlam Taktikleri (Reels)", "video_url": "https://www.youtube.com/embed/jfKfPfyJRdk", "subject": "Türkçe"},
    {"title": "Gelişim Psikolojisi Hap Bilgiler", "video_url": "https://www.youtube.com/embed/jfKfPfyJRdk", "subject": "Eğitim Bilimleri"},
    {"title": "2026 KPSS Güncel Bilgiler Turu", "video_url": "https://www.youtube.com/embed/jfKfPfyJRdk", "subject": "Güncel Bilgiler"},
]
