import json
import os
import urllib.request
import urllib.error

class DictionaryService:
    def __init__(self, filepath: str):
        self._local_dictionary = {}
        self._api_base = "https://api.dictionaryapi.dev/api/v2/entries/en/"
        self._load(filepath)

    def _load(self, filepath: str):
        """Load the local JSON dictionary into memory at startup."""
        if not os.path.exists(filepath):
            print(f"[DictionaryService] WARNING: No local dictionary found at {filepath}")
            return

        with open(filepath, "r") as f:
            self._local_dictionary = json.load(f)

        print(f"[DictionaryService] Loaded {len(self._local_dictionary)} local words.")

    def lookup(self, word: str) -> dict:
        """
        Lookup strategy:
        1. Check local JSON first (fast, offline)
        2. Fall back to Free Dictionary API (online, larger vocabulary)
        3. Return not-found if both fail
        
        Returns a dict: { "definition": str, "source": str } or None
        """
        word = word.strip().lower()

        # --- Step 1: Check local dictionary ---
        if word in self._local_dictionary:
            print(f"[DictionaryService] '{word}' found in local dictionary.")
            return {
                "definition": self._local_dictionary[word],
                "source": "local"
            }

        # --- Step 2: Try the online API ---
        print(f"[DictionaryService] '{word}' not local. Querying API...")
        api_result = self._fetch_from_api(word)

        if api_result:
            return {
                "definition": api_result,
                "source": "api"
            }

        # --- Step 3: Both failed ---
        return None

    def _fetch_from_api(self, word: str) -> str:
        """
        Call the Free Dictionary API and extract the first definition.
        Returns the definition string, or None if anything goes wrong.
        """
        url = self._api_base + word

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "DictionaryServer/1.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                raw = response.read().decode("utf-8")
                data = json.loads(raw)

            # Navigate the API response structure to get first definition
            # Structure: list → meanings → definitions → definition
            definition = (
                data[0]
                ["meanings"][0]
                ["definitions"][0]
                ["definition"]
            )
            return definition

        except urllib.error.HTTPError as e:
            # 404 means the word genuinely doesn't exist in their database
            if e.code == 404:
                print(f"[DictionaryService] '{word}' not found in API.")
            else:
                print(f"[DictionaryService] API HTTP error: {e.code}")
            return None

        except urllib.error.URLError:
            # No internet connection or API is down
            print(f"[DictionaryService] API unreachable. Using local only.")
            return None

        except (KeyError, IndexError):
            # API responded but structure was unexpected
            print(f"[DictionaryService] API response parsing failed for '{word}'.")
            return None

        except Exception as e:
            print(f"[DictionaryService] Unexpected error: {e}")
            return None