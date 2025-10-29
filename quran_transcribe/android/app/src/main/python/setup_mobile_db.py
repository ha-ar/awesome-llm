# assets/python/setup_mobile_db.py
"""
Setup local SQLite database for mobile app
Optimized for fast access and small size
"""

import sqlite3
import requests
import json
from pathlib import Path

def setup_quran_database(db_path: str = "quran.db"):
    """Setup complete Quran database for mobile"""
    
    print("🔧 Setting up local Quran database...")
    
    # Create database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create optimized tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verses (
            surah INTEGER,
            ayah INTEGER,
            text TEXT,
            text_simple TEXT,
            words_count INTEGER,
            PRIMARY KEY (surah, ayah)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS surahs (
            number INTEGER PRIMARY KEY,
            name TEXT,
            english_name TEXT,
            total_ayahs INTEGER,
            revelation_type TEXT
        )
    ''')
    
    # Download and insert data
    print("📥 Downloading Quran data...")
    
    total_verses = 0
    
    for surah_num in range(1, 115):  # 114 surahs
        try:
            print(f"   Surah {surah_num}/114...", end='\r')
            
            url = f"https://api.alquran.cloud/v1/surah/{surah_num}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data['code'] == 200:
                surah_data = data['data']
                
                # Insert surah info
                cursor.execute('''
                    INSERT OR REPLACE INTO surahs 
                    (number, name, english_name, total_ayahs, revelation_type)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    surah_data['number'],
                    surah_data['name'],
                    surah_data['englishName'],
                    surah_data['numberOfAyahs'],
                    surah_data['revelationType']
                ))
                
                # Insert verses
                for ayah in surah_data['ayahs']:
                    text = ayah['text']
                    text_simple = remove_diacritics(text)
                    words_count = len(text.split())
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO verses 
                        (surah, ayah, text, text_simple, words_count)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        surah_num,
                        ayah['numberInSurah'], 
                        text,
                        text_simple,
                        words_count
                    ))
                    
                    total_verses += 1
        
        except Exception as e:
            print(f"\n⚠️ Error downloading Surah {surah_num}: {e}")
            continue
    
    # Create indexes for fast searches
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_verse_text ON verses(text)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_verse_simple ON verses(text_simple)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_surah_ayah ON verses(surah, ayah)')
    
    # Create FTS (Full Text Search) table for fast verse search
    cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS verses_fts 
        USING fts5(surah, ayah, text, text_simple)
    ''')
    
    # Populate FTS table
    cursor.execute('''
        INSERT INTO verses_fts (surah, ayah, text, text_simple)
        SELECT surah, ayah, text, text_simple FROM verses
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Database setup complete!")
    print(f"   📚 Total verses: {total_verses}")
    print(f"   💾 Database size: {Path(db_path).stat().st_size / (1024*1024):.1f} MB")
    
    return True

def remove_diacritics(text: str) -> str:
    """Remove Arabic diacritics for simple matching"""
    import re
    return re.sub(r'[َُِّْٰٱًٌٍ]', '', text)

if __name__ == "__main__":
    setup_quran_database()