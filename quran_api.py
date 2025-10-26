import requests
import json
import os
from typing import Dict, Optional, List
import time
from pathlib import Path

class QuranAPI:
    """
    Downloads and caches complete Quran data from multiple API sources
    """
    
    def __init__(self, data_dir: str = "quran_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # API endpoints
        self.apis = {
            "alquran": "https://api.alquran.cloud/v1",
            "quranenc": "https://quranenc.com/api/v1",
            "jsdelivr": "https://cdn.jsdelivr.net/gh/risan/quran-json@main/dist"
        }
        
        # Cache files
        self.cache_files = {
            "complete": self.data_dir / "quran_complete.json",
            "metadata": self.data_dir / "quran_metadata.json",
            "surahs": self.data_dir / "surahs_info.json"
        }
    
    def download_complete_quran(self, edition: str = "quran-uthmani") -> bool:
        """
        Download complete Quran with Uthmani script (with tashkeel)
        
        Args:
            edition: API edition to use
            - "quran-uthmani" (with tashkeel)
            - "quran-simple" (without tashkeel)
            - "quran-simple-enhanced" (enhanced simple)
        """
        print(f"📖 Downloading complete Quran (edition: {edition})...")
        
        try:
            # Method 1: Try AlQuran.cloud API (most reliable)
            url = f"{self.apis['alquran']}/quran/{edition}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 200:
                    return self._save_complete_quran(data['data'])
            
            print("⚠️ Primary API failed, trying alternative...")
            
            # Method 2: Try downloading surah by surah
            return self._download_surah_by_surah(edition)
            
        except Exception as e:
            print(f"❌ Error downloading Quran: {e}")
            return False
    
    def _download_surah_by_surah(self, edition: str) -> bool:
        """Download each surah individually (fallback method)"""
        print("📚 Downloading surah by surah...")
        
        complete_quran = {
            "surahs": [],
            "edition": edition,
            "total_ayahs": 0
        }
        
        # Download surah info first
        surahs_info = self._get_surahs_info()
        if not surahs_info:
            return False
        
        for surah_num in range(1, 115):  # 114 surahs
            try:
                print(f"📋 Downloading Surah {surah_num}/114...")
                
                url = f"{self.apis['alquran']}/surah/{surah_num}/{edition}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('code') == 200:
                        surah_data = data['data']
                        complete_quran['surahs'].append(surah_data)
                        complete_quran['total_ayahs'] += len(surah_data['ayahs'])
                        
                        # Small delay to be respectful to API
                        time.sleep(0.1)
                    else:
                        print(f"⚠️ Failed to get Surah {surah_num}")
                else:
                    print(f"⚠️ HTTP {response.status_code} for Surah {surah_num}")
                    
            except Exception as e:
                print(f"⚠️ Error downloading Surah {surah_num}: {e}")
                continue
        
        if len(complete_quran['surahs']) >= 110:  # At least 110 surahs
            return self._save_complete_quran(complete_quran)
        else:
            print(f"❌ Only downloaded {len(complete_quran['surahs'])} surahs")
            return False
    
    def _get_surahs_info(self) -> Optional[List[Dict]]:
        """Get metadata about all surahs"""
        try:
            # Try to load from cache first
            if self.cache_files["surahs"].exists():
                with open(self.cache_files["surahs"], 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Download from API
            url = f"{self.apis['alquran']}/meta"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 200:
                    surahs_info = data['data']['surahs']['references']
                    
                    # Save to cache
                    with open(self.cache_files["surahs"], 'w', encoding='utf-8') as f:
                        json.dump(surahs_info, f, ensure_ascii=False, indent=2)
                    
                    return surahs_info
                    
        except Exception as e:
            print(f"⚠️ Error getting surahs info: {e}")
        
        return None
    
    def _save_complete_quran(self, data: Dict) -> bool:
        """Save complete Quran data to local file"""
        try:
            # Save complete data
            with open(self.cache_files["complete"], 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Create metadata
            metadata = {
                "total_surahs": len(data.get('surahs', [])),
                "total_ayahs": data.get('total_ayahs', 0),
                "edition": data.get('edition', 'unknown'),
                "download_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "file_size_mb": round(self.cache_files["complete"].stat().st_size / (1024*1024), 2)
            }
            
            with open(self.cache_files["metadata"], 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Quran data saved successfully!")
            print(f"📊 Total Surahs: {metadata['total_surahs']}")
            print(f"📊 Total Ayahs: {metadata['total_ayahs']}")
            print(f"💾 File Size: {metadata['file_size_mb']} MB")
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving Quran data: {e}")
            return False
    
    def load_local_quran(self) -> Optional[Dict]:
        """Load Quran data from local cache"""
        try:
            if self.cache_files["complete"].exists():
                with open(self.cache_files["complete"], 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print("📁 No local Quran data found. Run download first.")
                return None
                
        except Exception as e:
            print(f"❌ Error loading local Quran data: {e}")
            return None
    
    def get_verse(self, surah: int, ayah: int) -> Optional[str]:
        """Get specific verse from local data"""
        data = self.load_local_quran()
        if not data:
            return None
        
        try:
            surahs = data.get('surahs', [])
            if surah <= len(surahs):
                surah_data = surahs[surah - 1]  # 0-indexed
                ayahs = surah_data.get('ayahs', [])
                
                for ayah_data in ayahs:
                    if ayah_data.get('numberInSurah') == ayah:
                        return ayah_data.get('text', '')
            
        except Exception as e:
            print(f"❌ Error getting verse {surah}:{ayah}: {e}")
        
        return None
    
    def get_surah(self, surah: int) -> Optional[Dict]:
        """Get complete surah from local data"""
        data = self.load_local_quran()
        if not data:
            return None
        
        try:
            surahs = data.get('surahs', [])
            if surah <= len(surahs):
                return surahs[surah - 1]  # 0-indexed
                
        except Exception as e:
            print(f"❌ Error getting surah {surah}: {e}")
        
        return None
    
    def search_verses(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for verses containing specific text"""
        results = []
        data = self.load_local_quran()
        if not data:
            return results
        
        query = query.strip()
        if not query:
            return results
        
        try:
            surahs = data.get('surahs', [])
            
            for surah_data in surahs:
                surah_num = surah_data.get('number', 0)
                surah_name = surah_data.get('englishName', '')
                
                for ayah_data in surah_data.get('ayahs', []):
                    ayah_text = ayah_data.get('text', '')
                    ayah_num = ayah_data.get('numberInSurah', 0)
                    
                    if query in ayah_text:
                        results.append({
                            'surah': surah_num,
                            'ayah': ayah_num,
                            'surah_name': surah_name,
                            'text': ayah_text,
                            'reference': f"{surah_num}:{ayah_num}"
                        })
                        
                        if len(results) >= limit:
                            return results
            
        except Exception as e:
            print(f"❌ Error searching verses: {e}")
        
        return results
    
    def get_stats(self) -> Optional[Dict]:
        """Get statistics about local Quran data"""
        if self.cache_files["metadata"].exists():
            try:
                with open(self.cache_files["metadata"], 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ Error loading metadata: {e}")
        
        return None
    
    def is_data_available(self) -> bool:
        """Check if Quran data is available locally"""
        return self.cache_files["complete"].exists()

# Convenience functions
def download_quran_data(data_dir: str = "quran_data") -> bool:
    """Download complete Quran data"""
    api = QuranAPI(data_dir)
    return api.download_complete_quran()

def load_quran_data(data_dir: str = "quran_data") -> Optional[Dict]:
    """Load Quran data from local storage"""
    api = QuranAPI(data_dir)
    return api.load_local_quran()