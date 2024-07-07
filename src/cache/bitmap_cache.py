import pickle
from typing import Dict, Any


class BitmapCache:
    """
    Handles loading and saving of character bitmaps.

    :param cache_file: [str] Path to the cache file.
    """

    def __init__(self, cache_file: str = "font_cache.pkl"):
        """
        Initializes the BitmapCache with the specified cache file path.

        :param cache_file: [str] Path to the cache file.
        """
        self.cache_file = cache_file
        self.cache = self.load_cache()

    def load_cache(self) -> Dict[str, Any]:
        """
        Loads the character bitmap cache from a file.

        :return: [Dict[str, Any]] Dictionary containing cached bitmaps.
        """
        try:
            with open(self.cache_file, "rb") as f:
                return pickle.load(f)
        except (FileNotFoundError, EOFError):
            return {}

    def save_cache(self) -> None:
        """
        Saves the character bitmap cache to a file.
        """
        with open(self.cache_file, "wb") as f:
            pickle.dump(self.cache, f)
