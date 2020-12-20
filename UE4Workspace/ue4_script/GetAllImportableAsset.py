import os
import json
from unreal import (
    AssetRegistryHelpers
)

# addon_path is Blender Unreal Engien 4 Workspace addon path
# node_id is unreal engine project instance

asset_registry = AssetRegistryHelpers.get_asset_registry()

all_assets = asset_registry.get_assets_by_path('/Game', recursive=True)

asset_list = [(node_id, str(asset.object_path), str(asset.asset_name), str(asset.asset_class)) for asset in all_assets if str(asset.asset_class) in ['StaticMesh', 'SkeletalMesh', 'AnimSequence']]

load_import_asset_list = open(os.path.normpath(os.path.join(addon_path, 'temp', 'import_asset_list.json')), 'r')
original_asset_list = json.loads(load_import_asset_list.read())
load_import_asset_list.close()

original_asset_list.extend(asset_list)

save_import_asset_list = open(os.path.normpath(os.path.join(addon_path, 'temp', 'import_asset_list.json')), 'w+')
save_import_asset_list.write(json.dumps(original_asset_list, indent=4))
save_import_asset_list.close()