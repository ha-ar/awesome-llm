#!/usr/bin/env python3
"""
Setup script to download complete Quran data once
Run this script before using the application
"""

import os
import sys
from pathlib import Path
from quran_api import QuranAPI

def main():
    print("🕌 Quran Data Setup")
    print("=" * 50)
    
    # Create data directory
    data_dir = "quran_data"
    Path(data_dir).mkdir(exist_ok=True)
    
    # Initialize API
    api = QuranAPI(data_dir)
    
    # Check if data already exists
    if api.is_data_available():
        stats = api.get_stats()
        if stats:
            print(f"📚 Quran data already exists!")
            print(f"   Surahs: {stats.get('total_surahs', 'Unknown')}")
            print(f"   Ayahs: {stats.get('total_ayahs', 'Unknown')}")
            print(f"   Size: {stats.get('file_size_mb', 'Unknown')} MB")
            print(f"   Downloaded: {stats.get('download_date', 'Unknown')}")
            
            choice = input("\n🔄 Re-download? (y/N): ").strip().lower()
            if choice != 'y':
                print("✅ Using existing data.")
                return True
    
    print("\n📥 Downloading Quran data...")
    print("This may take 1-2 minutes depending on your internet connection.")
    
    # Try different editions
    editions = [
        ("quran-uthmani", "Uthmani Script (with Tashkeel) - Recommended"),
        ("quran-simple", "Simple Arabic Text (without Tashkeel)"),
        ("quran-simple-enhanced", "Enhanced Simple Arabic")
    ]
    
    print("\n📖 Available editions:")
    for i, (edition, description) in enumerate(editions, 1):
        print(f"   {i}. {description}")
    
    # Get user choice
    while True:
        try:
            choice = input(f"\nSelect edition (1-{len(editions)}) [1]: ").strip()
            if not choice:
                choice = "1"
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(editions):
                selected_edition = editions[choice_idx][0]
                break
            else:
                print("❌ Invalid choice. Please try again.")
        except ValueError:
            print("❌ Please enter a number.")
    
    print(f"\n⬇️ Downloading {editions[choice_idx][1]}...")
    
    # Download the data
    success = api.download_complete_quran(selected_edition)
    
    if success:
        print("\n✅ Download completed successfully!")
        
        # Show statistics
        stats = api.get_stats()
        if stats:
            print(f"\n📊 Statistics:")
            print(f"   📚 Total Surahs: {stats.get('total_surahs')}")
            print(f"   📜 Total Ayahs: {stats.get('total_ayahs')}")
            print(f"   💾 File Size: {stats.get('file_size_mb')} MB")
            print(f"   📅 Downloaded: {stats.get('download_date')}")
        
        # Test a few verses
        print(f"\n🧪 Testing data integrity...")
        test_verses = [
            (1, 1),  # Al-Fatiha
            (2, 255),  # Ayat al-Kursi
            (112, 1)  # Al-Ikhlas
        ]
        
        for surah, ayah in test_verses:
            verse = api.get_verse(surah, ayah)
            if verse:
                print(f"   ✅ {surah}:{ayah} - {verse[:50]}...")
            else:
                print(f"   ❌ {surah}:{ayah} - Not found")
        
        print(f"\n🎉 Setup complete! You can now use the Quran recitation app.")
        print(f"📁 Data stored in: {os.path.abspath(data_dir)}/")
        
        return True
    else:
        print("\n❌ Download failed. Please check your internet connection and try again.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Download cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)