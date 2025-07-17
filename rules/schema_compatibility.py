from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class SchemaCompatibilityConfig:
    allow_type_narrowing: bool = False
    allow_column_drop: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SchemaCompatibilityConfig":
        return cls(
            allow_type_narrowing=data.get("allow_type_narrowing", False),
            allow_column_drop=data.get("allow_column_drop", False)
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allow_type_narrowing": self.allow_type_narrowing,
            "allow_column_drop": self.allow_column_drop
        }
