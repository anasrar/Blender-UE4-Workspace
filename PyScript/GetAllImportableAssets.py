import os
import inspect
import json
from unreal import (
    AssetRegistryHelpers
)

asset_registry = AssetRegistryHelpers.get_asset_registry()
# get all assets
all_assets = asset_registry.get_assets_by_path('/Game', recursive=True)

# Fix Python PATH Script Issue #9
filename = inspect.getframeinfo(inspect.currentframe()).filename
currentPath = os.path.dirname(os.path.abspath(filename))

file = open(os.path.normpath(os.path.join(currentPath, "..", "Data", "assetsList.json")), "w+")
# filter for skeleton assets
file.write(json.dumps([(str(asset.object_path), str(asset.asset_name), {"StaticMesh": "MESH", "SkeletalMesh": "ARMATURE", "AnimSequence": "ACTION"}[str(asset.asset_class)]) for asset in all_assets if str(asset.asset_class) in ["StaticMesh", "SkeletalMesh", "AnimSequence"]]))
file.close()