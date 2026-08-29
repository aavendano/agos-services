"""
Technology Asset Catalog and Repository Management.
"""

import os
import json
import glob
from typing import List, Optional, Dict
from analyzer.models import TechAsset


class TechnologyCatalog:
    """Catalog manager that indexes, validates, and persists organization technology assets."""

    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, "data", "technologies")
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def list_all(self) -> List[TechAsset]:
        """Loads and parses all technology asset manifests from disk."""
        assets: List[TechAsset] = []
        pattern = os.path.join(self.data_dir, "*.json")
        for filepath in sorted(glob.glob(pattern)):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    assets.append(TechAsset.model_validate(data))
            except Exception as e:
                print(f"[WARN] Error loading tech manifest {filepath}: {e}")
        return assets

    def get_by_id(self, tech_id: str) -> Optional[TechAsset]:
        """Fetches a specific technology asset by its ID."""
        for asset in self.list_all():
            if asset.id.lower() == tech_id.lower():
                return asset
        return None

    def save_asset(self, asset: TechAsset) -> str:
        """Saves or updates a technology asset manifest JSON file."""
        filename = f"{asset.id.replace('-', '_').lower()}.json"
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(asset.model_dump_json(indent=2))
        return filepath

    def delete_asset(self, tech_id: str) -> bool:
        """Removes an asset manifest by ID."""
        asset = self.get_by_id(tech_id)
        if not asset:
            return False
        filename = f"{asset.id.replace('-', '_').lower()}.json"
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
