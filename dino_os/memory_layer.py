"""Memory Layer - Simplified SQLite-backed persistent memory for Dino Dynasty OS."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class MemoryLayer:
    """Simplified SQLite-based memory layer (key-value with metadata)."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the memory layer.
        
        Args:
            db_path: Path to SQLite database file.
        """
        if db_path is None:
            db_path = str(Path(__file__).parent.parent / "dino_memory.db")
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the SQLite database - simplified schema."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            # Simplified: single table with key-value + metadata
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    metadata TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            # Index for faster lookups
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(key)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_memories_updated ON memories(updated_at)
            """)
            conn.commit()

    def add(self, key: str, value: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add or update a memory entry.
        
        Args:
            key: Unique memory key
            value: Memory value
            metadata: Optional metadata dictionary
            
        Returns:
            True if successful.
        """
        now = datetime.utcnow().isoformat()
        metadata_json = json.dumps(metadata) if metadata else None
        
        # Check if key exists to preserve created_at
        existing = self.get(key)
        created_at = existing['created_at'] if existing else now
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT OR REPLACE INTO memories 
                       (key, value, metadata, created_at, updated_at) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (key, value, metadata_json, created_at, now)
                )
                conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a memory entry.
        
        Args:
            key: Memory key
            
        Returns:
            Memory dict with value, metadata, created_at, updated_at or None.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT key, value, metadata, created_at, updated_at FROM memories WHERE key = ?",
                (key,)
            )
            row = cursor.fetchone()
            if row:
                return {
                    "key": row["key"],
                    "value": row["value"],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else None,
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                }
        return None

    def delete(self, key: str) -> bool:
        """Delete a memory entry.
        
        Args:
            key: Memory key
            
        Returns:
            True if deleted.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM memories WHERE key = ?", (key,))
            conn.commit()
            return cursor.rowcount > 0

    def list_keys(self, prefix: Optional[str] = None, limit: int = 100) -> List[str]:
        """List memory keys, optionally with prefix filter.
        
        Args:
            prefix: Optional key prefix filter
            limit: Maximum keys to return
            
        Returns:
            List of matching keys.
        """
        with sqlite3.connect(self.db_path) as conn:
            if prefix:
                cursor = conn.execute(
                    "SELECT key FROM memories WHERE key LIKE ? ORDER BY updated_at DESC LIMIT ?",
                    (f"{prefix}%", limit)
                )
            else:
                cursor = conn.execute(
                    "SELECT key FROM memories ORDER BY updated_at DESC LIMIT ?",
                    (limit,)
                )
            return [row[0] for row in cursor.fetchall()]

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Simple text search in memory values.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching memories.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """SELECT key, value, metadata, created_at, updated_at 
                   FROM memories 
                   WHERE value LIKE ? 
                   ORDER BY updated_at DESC LIMIT ?""",
                (f"%{query}%", limit)
            )
            return [
                {
                    "key": row["key"],
                    "value": row["value"],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else None,
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                }
                for row in cursor.fetchall()
            ]

    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recently updated memories.
        
        Args:
            limit: Maximum entries to return
            
        Returns:
            List of recent memories.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """SELECT key, value, metadata, created_at, updated_at 
                   FROM memories 
                   ORDER BY updated_at DESC LIMIT ?""",
                (limit,)
            )
            return [
                {
                    "key": row["key"],
                    "value": row["value"],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else None,
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                }
                for row in cursor.fetchall()
            ]

    def count(self) -> int:
        """Get total number of memory entries.
        
        Returns:
            Count of entries.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM memories")
            return cursor.fetchone()[0]

    def export(self) -> List[Dict[str, Any]]:
        """Export all memories.
        
        Returns:
            List of all memory entries.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT key, value, metadata, created_at, updated_at FROM memories"
            )
            return [
                {
                    "key": row["key"],
                    "value": row["value"],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else None,
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                }
                for row in cursor.fetchall()
            ]

    def clear(self) -> None:
        """Clear all memories."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM memories")
            conn.commit()
