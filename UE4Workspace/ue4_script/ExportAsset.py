import os
import json

from unreal import (
    AssetRegistryHelpers,
    FbxExportOption,
    FbxExportCompatibility,
    AssetExportTask,
    Exporter,

    AnimSequenceExporterFBX,
    SkeletalMeshExporterFBX,
    StaticMeshExporterFBX
)

# addon_path is Blender Unreal Engien 4 Workspace addon path
# node_id is unreal engine project instance

asset_registry = AssetRegistryHelpers.get_asset_registry()

load_imported_asset_list = open(os.path.normpath(os.path.join(addon_path, 'temp', 'imported_asset_list.json')), 'r')
original_imported_asset_list = json.loads(load_imported_asset_list.read())
load_imported_asset_list.close()

json_file = open(os.path.normpath(os.path.join(addon_path, 'temp', 'import_asset_setting.json')), 'r')
import_asset_setting = json.loads(json_file.read())
json_file.close()

assets = [(asset_path, index) for asset_node_id, asset_path, index in import_asset_setting['files'] if asset_node_id == node_id]

for asset_path, index in assets:
    asset = asset_registry.get_asset_by_object_path(asset_path)
    asset_object = asset.get_asset()

    if bool(asset_object):
        target_path = os.path.join(import_asset_setting['path'], 'temp_file_' + str(index) + '.fbx').replace(os.sep, '/')
        export_options = FbxExportOption()

        for prop, value in ([
            ('fbx_export_compatibility', getattr(FbxExportCompatibility, import_asset_setting['fbx_export_compatibility'])),
            ('ascii', import_asset_setting['ascii']),
            ('force_front_x_axis', import_asset_setting['force_front_x_axis']),
            ('vertex_color', import_asset_setting['vertex_color']),
            ('level_of_detail', import_asset_setting['level_of_detail']),
            ('collision', import_asset_setting['collision']),
            ('export_morph_targets', import_asset_setting['export_morph_targets']),
            ('export_preview_mesh', import_asset_setting['export_preview_mesh']),
            ('map_skeletal_motion_to_root', import_asset_setting['map_skeletal_motion_to_root']),
            ('export_local_time', import_asset_setting['export_local_time']),
        ]):
            export_options.set_editor_property(prop, value)

        export_task = AssetExportTask()

        for prop, value in [
            ('automated', True),
            ('object', asset_object),
            ('filename', target_path),
            ('exporter', {
                'StaticMesh': StaticMeshExporterFBX(),
                'SkeletalMesh': SkeletalMeshExporterFBX(),
                'AnimSequence': AnimSequenceExporterFBX()
                }[str(asset.asset_class)]),
            ('options', export_options),
            ('prompt', False),
            ('replace_identical', True),
        ]:
            export_task.set_editor_property(prop, value)

        is_export_success = Exporter.run_asset_export_task(export_task)
        if is_export_success:
            original_imported_asset_list.append([target_path, str(asset.asset_class), str(asset.asset_name)])

save_imported_asset_list = open(os.path.normpath(os.path.join(addon_path, 'temp', 'imported_asset_list.json')), 'w+')
save_imported_asset_list.write(json.dumps(original_imported_asset_list, indent=4))
save_imported_asset_list.close()