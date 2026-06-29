-- Confirmed against bddk.org.tr/Kurulus/Liste/77 on 2026-06-29 (ADR 0001).
INSERT INTO banks (name, website, is_digital) VALUES
    ('Albaraka Türk Katılım Bankası', 'https://www.albarakaturk.com.tr', FALSE),
    ('Kuveyt Türk Katılım Bankası', 'https://www.kuveytturk.com.tr', FALSE),
    ('Türkiye Finans Katılım Bankası', 'https://www.turkiyefinans.com.tr', FALSE),
    ('Vakıf Katılım Bankası', 'https://www.vakifkatilim.com.tr', FALSE),
    ('Ziraat Katılım Bankası', 'https://www.ziraatkatilim.com.tr', FALSE),
    ('Türkiye Emlak Katılım Bankası', 'https://www.emlakbank.com.tr', FALSE),
    ('Dünya Katılım Bankası', 'https://www.dunyakatilim.com.tr', FALSE),
    ('Adil Katılım Bankası', 'https://www.adilkatilim.com.tr', TRUE),
    ('Hayat Finans Katılım Bankası', 'https://www.hayatfinans.com.tr', TRUE),
    ('T.O.M. Katılım Bankası', 'https://www.tombank.com.tr', TRUE)
ON CONFLICT (name) DO NOTHING;
