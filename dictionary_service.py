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

    def _levenshtein_distance(self, s1, s2):
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]

    def get_suggestions(self, word: str, limit: int = 3):
        """Finds the closest matches in the local dictionary using Levenshtein distance."""
        words = list(self._local_dictionary.keys())
        # Calculate distance for each word and sort by smallest distance
        # We only suggest words with a distance of 3 or less to keep them relevant
        suggestions = []
        for w in words:
            dist = self._levenshtein_distance(word, w)
            if dist <= 3: 
                suggestions.append((w, dist))
        
        # Sort by distance (ascending) and return the top words
        suggestions.sort(key=lambda x: x[1])
        return [s[0] for s in suggestions[:limit]]
    
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