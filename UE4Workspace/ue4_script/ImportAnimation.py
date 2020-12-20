import os
import inspect
import json

from unreal import (
    EditorAssetLibrary,
    FbxImportUI,
    AssetImportTask,
    AssetToolsHelpers,
    load_asset,

    FBXAnimationLengthImportType,
    Int32Interval,
    Vector,
    Rotator,
)

# addon_path is Blender Unreal Engien 4 Workspace addon path
# node_id is unreal engine project instance

json_file = open(os.path.normpath(os.path.join(addon_path, 'temp', 'unreal_engine_import_setting.json')), 'r')
unreal_engine_import_setting = json.loads(json_file.read())
json_file.close()

target_path = '/' + os.path.join('Game', unreal_engine_import_setting['main_folder'], unreal_engine_import_setting['subfolder']).replace(os.sep, '/')

if EditorAssetLibrary.does_directory_exist(directory_path=target_path):
    EditorAssetLibrary.make_directory(directory_path=target_path)

for file in unreal_engine_import_setting['files']:
    source_file = file['path'].replace(os.sep, '/')
    target_node_id, skeleton_path = file['skeleton'].split(':')

    skeleton_asset = load_asset(skeleton_path) if skeleton_path != 'NONE' else None

    if os.path.exists(source_file) and bool(skeleton_asset):
        import_options = FbxImportUI()

        frame_import_range_min, frame_import_range_max = unreal_engine_import_setting['frame_import_range']
        frame_import_range = Int32Interval()

        for option, prop, value in ([
            (import_options, 'import_mesh', False),
            (import_options, 'import_as_skeletal', False),
            (import_options, 'import_animations', True),

            (import_options, 'skeleton', skeleton_asset),

            (import_options.anim_sequence_import_data, 'animation_length', getattr(FBXAnimationLengthImportType, unreal_engine_import_setting['animation_length'])),
            (import_options.anim_sequence_import_data, 'import_meshes_in_bone_hierarchy', unreal_engine_import_setting['import_meshes_in_bone_hierarchy']),
            (frame_import_range, 'min', frame_import_range_min),
            (frame_import_range, 'max', frame_import_range_max),
            (import_options.anim_sequence_import_data, 'frame_import_range', frame_import_range),
            (import_options.anim_sequence_import_data, 'use_default_sample_rate', unreal_engine_import_setting['use_default_sample_rate']),
            (import_options.anim_sequence_import_data, 'custom_sample_rate', unreal_engine_import_setting['custom_sample_rate']),
            (import_options.anim_sequence_import_data, 'import_custom_attribute', unreal_engine_import_setting['import_custom_attribute']),
            (import_options.anim_sequence_import_data, 'delete_existing_custom_attribute_curves', unreal_engine_import_setting['delete_existing_custom_attribute_curves']),
            (import_options.anim_sequence_import_data, 'import_bone_tracks', unreal_engine_import_setting['import_bone_tracks']),
            (import_options.anim_sequence_import_data, 'set_material_drive_parameter_on_custom_attribute', unreal_engine_import_setting['set_material_drive_parameter_on_custom_attribute']),
            (import_options.anim_sequence_import_data, 'material_curve_suffixes', unreal_engine_import_setting['material_curve_suffixes']),
            (import_options.anim_sequence_import_data, 'remove_redundant_keys', unreal_engine_import_setting['remove_redundant_keys']),
            (import_options.anim_sequence_import_data, 'delete_existing_morph_target_curves', unreal_engine_import_setting['delete_existing_morph_target_curves']),
            (import_options.anim_sequence_import_data, 'do_not_import_curve_with_zero', unreal_engine_import_setting['do_not_import_curve_with_zero']),
            (import_options.anim_sequence_import_data, 'preserve_local_transform', unreal_engine_import_setting['preserve_local_transform']),

            # Transform

            (import_options.anim_sequence_import_data, 'import_translation', Vector(*unreal_engine_import_setting['import_translation'])),
            (import_options.anim_sequence_import_data, 'import_rotation', Rotator(*unreal_engine_import_setting['import_rotation'])),
            (import_options.anim_sequence_import_data, 'import_uniform_scale', unreal_engine_import_setting['import_uniform_scale']),

            # Misc.

            (import_options.anim_sequence_import_data, 'convert_scene', unreal_engine_import_setting['convert_scene']),
            (import_options.anim_sequence_import_data, 'force_front_x_axis', unreal_engine_import_setting['force_front_x_axis']),
            (import_options.anim_sequence_import_data, 'convert_scene_unit', unreal_engine_import_setting['convert_scene_unit']),
            (import_options, 'override_full_name', unreal_engine_import_setting['override_full_name']),
        ]):
            option.set_editor_property(prop, value)

        # Task

        import_task = AssetImportTask()

        for prop, value in [
            ('automated', True),
            ('destination_name', ''),
            ('destination_path', target_path),
            ('filename', source_file),
            ('replace_existing', unreal_engine_import_setting['overwrite_file']),
            ('save', False),
            ('options', import_options),
        ]:
            import_task.set_editor_property(prop, value)

        AssetToolsHelpers.get_asset_tools().import_asset_tasks([import_task])

        if unreal_engine_import_setting['temporary']:
            try:
                os.remove(source_file)
            except:
                print('Failed to Remove Temporary File, Location : ' + source_file)
