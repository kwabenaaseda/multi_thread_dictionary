import json
import os
import urllib.request
import urllib.error
import urllib.parse
import re  # Added for cleaning HTML tags from Wiktionary results

class DictionaryService:
    def __init__(self, filepath: str):
        self._local_dictionary = {}
        # Wiktionary uses language-specific subdomains
        self._api_template = "https://{lang}.wiktionary.org/api/rest_v1/page/definition"
        self._load(filepath)

    def _load(self, filepath: str):
        if not os.path.exists(filepath):
            return
        with open(filepath, "r", encoding="utf-8") as f:
            self._local_dictionary = json.load(f)

    def lookup(self, word: str, lang: str = "en") -> dict:
        word = word.strip().lower()
        lang = lang.strip().lower()

        if lang == "en" and word in self._local_dictionary:
            return {"definition": self._local_dictionary[word], "source": "local"}

        encoded_word = urllib.parse.quote(word)
        url = f"https://{lang}.wiktionary.org/api/rest_v1/page/definition/{encoded_word}"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "LexiconApp/1.0"})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))

            # --- DYNAMIC PARSING STRATEGY ---
            # 1. Get all keys (e.g., ['fr'], ['Noun'], or ['en'])
            keys = list(data.keys())
            if not keys: return None

            # 2. Get the first section
            first_section = data[keys[0]]
            
            # 3. Handle the nesting: Wiktionary data is usually:
            # Section (List) -> Object -> Definitions (List) -> Object -> 'definition'
            if isinstance(first_section, list) and len(first_section) > 0:
                item = first_section[0]
                if 'definitions' in item and len(item['definitions']) > 0:
                    raw_def = item['definitions'][0].get('definition', '')
                    
                    # Clean HTML tags (like <i> or <a>)
                    clean_def = re.sub(r'<[^>]+>', '', raw_def)
                    
                    return {
                        "definition": clean_def,
                        "source": f"Wiktionary ({lang.upper()})"
                    }
            return None

        except Exception as e:
            print(f"[DictionaryService] Error: {e}")
            return None