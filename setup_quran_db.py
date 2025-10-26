#!/usr/bin/env python3
"""
Quick setup script to prepare the Quran recitation checker with a full Quran database.
"""

import json
import requests
from pathlib import Path

def download_full_quran():
    """Download the complete Quran text from API and save locally."""
    print("📥 Downloading complete Quran text...")
    
    quran_data = {}
    
    # Download all 114 surahs
    for surah_num in range(1, 115):
        try:
            print(f"  Downloading Surah {surah_num}/114...", end='\r')
            url = f"https://api.alquran.cloud/v1/surah/{surah_num}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data['code'] == 200:
                for ayah in data['data']['ayahs']:
                    ref = f"{surah_num}:{ayah['numberInSurah']}"
                    quran_data[ref] = ayah['text']
        except Exception as e:
            print(f"\n⚠️  Error downloading Surah {surah_num}: {e}")
            continue
    
    print(f"\n✅ Downloaded {len(quran_data)} verses")
    
    # Save to file
    output_file = Path(__file__).parent / "quran_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(quran_data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Saved to {output_file}")
    return quran_data

def update_checker_to_use_file():
    """Update quran_checker.py to load from the JSON file."""
    checker_file = Path(__file__).parent / "quran_checker.py"
    
    if not checker_file.exists():
        print("❌ quran_checker.py not found!")
        return
    
    # Read the file
    with open(checker_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already updated
    if 'quran_data.json' in content:
        print("✅ quran_checker.py already configured to use full database")
        return
    
    # Add import at top
    new_import = """import json
from pathlib import Path"""
    
    if new_import not in content:
        content = content.replace('from typing import List, Tuple, Dict', 
                                 f'from typing import List, Tuple, Dict\n{new_import}')
    
    # Replace _load_quran_sample method
    old_method = """    def _load_quran_sample(self) -> Dict[str, str]:
        \"\"\"
        Load sample Quranic verses. In production, use:
        - https://api.alquran.cloud/v1/surah/{surah_number}
        - Or local Quran database
        \"\"\"
        # Sample verses for testing (Al-Fatiha and beginning of Al-Baqarah)
        return {"""
    
    new_method = """    def _load_quran_sample(self) -> Dict[str, str]:
        \"\"\"
        Load Quranic verses from local database file.
        Falls back to sample verses if file not found.
        \"\"\"
        # Try to load from file
        quran_file = Path(__file__).parent / "quran_data.json"
        if quran_file.exists():
            try:
                with open(quran_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load quran_data.json: {e}")
        
        # Fallback to sample verses
        return {"""
    
    if old_method in content:
        content = content.replace(old_method, new_method)
        
        # Write back
        with open(checker_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Updated quran_checker.py to use full database")
    else:
        print("⚠️  Could not automatically update quran_checker.py")
        print("   The file may have been modified. Please update manually.")

def main():
    print("=" * 60)
    print("🕌 Quran Recitation Checker - Database Setup")
    print("=" * 60)
    print()
    
    # Check if data already exists
    quran_file = Path(__file__).parent / "quran_data.json"
    if quran_file.exists():
        print(f"📁 Found existing database: {quran_file}")
        response = input("   Do you want to re-download? (y/N): ").strip().lower()
        if response != 'y':
            print("   Skipping download...")
            quran_data = None
        else:
            quran_data = download_full_quran()
    else:
        quran_data = download_full_quran()
    
    print()
    
    # Update the checker file
    update_checker_to_use_file()
    
    print()
    print("=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run the app: python app.py")
    print("3. Start reciting Quran verses!")
    print()
    
    if quran_data:
        print(f"📊 Database contains {len(quran_data)} verses from all 114 surahs")
    
    print()

if __name__ == "__main__":
    main()
