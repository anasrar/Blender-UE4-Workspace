import os
import json
from unreal import (
    AssetRegistryHelpers
)

# addon_path is Blender Unreal Engien 4 Workspace addon path
# node_id is unreal engine project instance

asset_registry = AssetRegistryHelpers.get_asset_registry()

all_assets = asset_registry.get_assets_by_path('/Game', recursive=True)

skeleton_list = [(node_id, str(asset.package_name), str(asset.asset_name)) for asset in all_assets if str(asset.asset_class) == 'Skeleton']

load_skeleton_list = open(os.path.normpath(os.path.join(addon_path, 'temp', 'skeleton_list.json')), 'r')
original_skeleton_list = json.loads(load_skeleton_list.read())
load_skeleton_list.close()

original_skeleton_list.extend(skeleton_list)

save_skeleton_list = open(os.path.normpath(os.path.join(addon_path, 'temp', 'skeleton_list.json')), 'w+')
save_skeleton_list.write(json.dumps(original_skeleton_list, indent=4))
save_skeleton_list.close()