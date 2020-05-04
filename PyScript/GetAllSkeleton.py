import json
from unreal import (
    AssetRegistryHelpers
)

asset_registry = AssetRegistryHelpers.get_asset_registry()
# get all assets
all_assets = asset_registry.get_assets_by_path('/Game', recursive=True)
# filter for skeleton assets
print(json.dumps([(str(asset.package_name ), str(asset.asset_name)) for asset in all_assets if str(asset.asset_class) == "Skeleton"]))