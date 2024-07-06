import pickle


class BitmapCache:
    """
    BitmapCache handles loading and saving of character bitmaps.

    :param cache_file: Path to the cache file.
    """

    def __init__(self, cache_file: str = "font_cache.pkl"):
        self.cache_file = cache_file
        self.cache = self.load_cache()

    def load_cache(self) -> dict:
        """
        Load the character bitmap cache from a file.

        :return: Dictionary containing cached bitmaps.
        """
        try:
            with open(self.cache_file, "rb") as f:
                return pickle.load(f)
        except (FileNotFoundError, EOFError):
            return {}

    def save_cache(self):
        """
        Save the character bitmap cache to a file.
        """
        with open(self.cache_file, "wb") as f:
            pickle.dump(self.cache, f)
