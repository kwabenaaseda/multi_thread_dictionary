import json
import os
import urllib.request
import urllib.error
import difflib

class DictionaryService:
    def __init__(self, filepath: str):
        self._local_dictionary = {}
        # Reverting to the stable V2 English API
        self._api_base = "https://api.dictionaryapi.dev/api/v2/entries/en/"
        self._load(filepath)

    def _load(self, filepath: str):
        if not os.path.exists(filepath): return
        with open(filepath, "r", encoding="utf-8") as f:
            self._local_dictionary = json.load(f)

    def get_suggestions(self, word: str) -> list:
        """Find the top 3 closest matches from the local dictionary."""
        all_local_words = list(self._local_dictionary.keys())
        # cutoff=0.7 means 70% similarity required
        return difflib.get_close_matches(word, all_local_words, n=3, cutoff=0.7)

    def lookup(self, word: str, lang: str = "en") -> dict:
        word = word.strip().lower()
        
        # --- Step 1: Language Gating ---
        if lang != "en":
            return {
                "definition": f"Support for {lang.upper()} is currently in development. Please try an English term.",
                "source": "System"
            }

        # --- Step 2: Local Cache ---
        if word in self._local_dictionary:
            return {"definition": self._local_dictionary[word], "source": "local"}

        # --- Step 3: Reliable English API ---
        url = self._api_base + urllib.parse.quote(word)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "LexiconApp/1.0"})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
            
            # Stable parsing for the Google-based Dictionary API
            definition = data[0]["meanings"][0]["definitions"][0]["definition"]
            return {"definition": definition, "source": "Free Dictionary API"}
            
        except Exception:
            return None