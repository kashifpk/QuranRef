"QuranRef Libarary package"

from .surah_info import surah_info

translation_aliases = {
    'ur': 'ur.maududi',
    'en': 'en.maududi',
}

def get_surah_number_by_name(surah_name):
    "Given a surah name in English or other languages (Urdu), returns the Sura number"
    
    for surah_idx, surah in enumerate(surah_info):
        if surah:
            if surah_name==surah['english_name'] or surah_name==surah['arabic_name']:
                return surah_idx

    return False
