import os
import json
import pickle
import tempfile
import hashlib
from datetime import datetime


class MetricCache:
    """Cache system for computed dataset metrics."""

    def __init__(self, cache_dir=None, expiry_days=30, max_size_gb=10):
        self.cache_dir = cache_dir or os.path.join(tempfile.gettempdir(), "metric_cache")
        self.expiry_days = expiry_days
        self.max_size_gb = max_size_gb

        os.makedirs(self.cache_dir, exist_ok=True)

        self.index_path = os.path.join(self.cache_dir, "cache_index.json")
        self.cache_index = self._load_index()

        self._cleanup_cache()

    def _load_index(self):
        """Load cache index from disk."""
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"entries": {}, "size_bytes": 0, "last_cleanup": None}

    def _save_index(self):
        """Save cache index to disk."""
        try:
            with open(self.index_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache_index, f, indent=2)
        except Exception as e:
            print(f"Error saving cache index: {e}")

    def _cleanup_cache(self):
        """Remove expired entries and trim cache if too large."""
        now = datetime.now()
        entries = self.cache_index["entries"]
        expired_keys = []

        for key, entry in list(entries.items()):
            last_accessed = datetime.fromisoformat(entry.get("last_accessed", "2000-01-01T00:00:00"))
            if (now - last_accessed).days > self.expiry_days:
                expired_keys.append(key)

        for key in expired_keys:
            self._remove_entry(key)

        while self.cache_index["size_bytes"] > (self.max_size_gb * 1024 * 1024 * 1024):
            if not entries:
                break
            lru_key = min(entries, key=lambda k: datetime.fromisoformat(entries[k].get("last_accessed", "2000-01-01T00:00:00")))
            self._remove_entry(lru_key)

        self.cache_index["last_cleanup"] = now.isoformat()
        self._save_index()

    def _remove_entry(self, key):
        """Remove a cache entry."""
        entry = self.cache_index["entries"].get(key)
        if not entry:
            return

        self.cache_index["size_bytes"] -= entry.get("size_bytes", 0)
        file_path = os.path.join(self.cache_dir, entry.get("file_name", ""))
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

        self.cache_index["entries"].pop(key, None)

    def get(self, key):
        """Retrieve an item from cache."""
        entry = self.cache_index["entries"].get(key)
        if not entry:
            return None

        file_path = os.path.join(self.cache_dir, entry.get("file_name", ""))
        if not os.path.exists(file_path):
            self._remove_entry(key)
            self._save_index()
            return None

        entry["last_accessed"] = datetime.now().isoformat()
        self._save_index()

        try:
            with open(file_path, 'rb') as f:
                return pickle.load(f)
        except Exception:
            self._remove_entry(key)
            self._save_index()
            return None

    def set(self, key, value, metadata=None):
        """Store an item in cache."""
        file_name = f"{hashlib.md5(key.encode()).hexdigest()}.cache"
        file_path = os.path.join(self.cache_dir, file_name)

        try:
            with open(file_path, 'wb') as f:
                pickle.dump(value, f)
        except Exception as e:
            print(f"Failed to write cache file: {e}")
            return

        size_bytes = os.path.getsize(file_path)
        now_str = datetime.now().isoformat()
        self.cache_index["entries"][key] = {
            "file_name": file_name,
            "created": now_str,
            "last_accessed": now_str,
            "size_bytes": size_bytes,
            "metadata": metadata or {}
        }
        self.cache_index["size_bytes"] += size_bytes
        self._save_index()

        if self.cache_index["size_bytes"] > (self.max_size_gb * 1024 * 1024 * 1024):
            self._cleanup_cache()
