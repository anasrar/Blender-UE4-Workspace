import os
import json

from unreal import (
    EditorAssetLibrary,
    FbxImportUI,
    load_asset,
    AssetImportTask,
    AssetToolsHelpers,

    FBXImportContentType,
    VertexColorImportOption,
    Color,
    FBXNormalImportMethod,
    FBXNormalGenerationMethod,

    Vector,
    Rotator,

    MaterialSearchLocation
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

    if os.path.exists(source_file):
        import_options = FbxImportUI()

        unreal_engine_import_setting['vertex_override_color'] = [float(value) * 255 for value in unreal_engine_import_setting['vertex_override_color']]
        target_node_id, skeleton = file['skeleton'].split(':')

        for option, prop, value in ([
            (import_options, 'import_mesh', True),
            (import_options, 'import_as_skeletal', True),
            (import_options, 'import_animations', False),

            (import_options, 'skeleton', (None if file['skeleton'] == 'CREATE' else load_asset(skeleton))),

            (import_options.skeletal_mesh_import_data, 'import_content_type', getattr(FBXImportContentType, unreal_engine_import_setting['import_content_type'])),
            (import_options.skeletal_mesh_import_data, 'vertex_color_import_option', getattr(VertexColorImportOption, unreal_engine_import_setting['vertex_color_import_option'])),
            (import_options.skeletal_mesh_import_data, 'vertex_override_color', Color(r=unreal_engine_import_setting['vertex_override_color'][0], g=unreal_engine_import_setting['vertex_override_color'][1], b=unreal_engine_import_setting['vertex_override_color'][2], a=unreal_engine_import_setting['vertex_override_color'][3])),
            (import_options.skeletal_mesh_import_data, 'update_skeleton_reference_pose', unreal_engine_import_setting['update_skeleton_reference_pose']),
            (import_options.skeletal_mesh_import_data, 'use_t0_as_ref_pose', unreal_engine_import_setting['use_t0_as_ref_pose']),
            (import_options.skeletal_mesh_import_data, 'preserve_smoothing_groups', unreal_engine_import_setting['preserve_smoothing_groups']),
            (import_options.skeletal_mesh_import_data, 'import_meshes_in_bone_hierarchy', unreal_engine_import_setting['import_meshes_in_bone_hierarchy']),
            (import_options.skeletal_mesh_import_data, 'import_morph_targets', unreal_engine_import_setting['import_morph_targets']),
            (import_options.skeletal_mesh_import_data, 'import_mesh_lo_ds', unreal_engine_import_setting['import_mesh_lo_ds']),
            (import_options.skeletal_mesh_import_data, 'normal_import_method', getattr(FBXNormalImportMethod, 'FBXNIM_' + unreal_engine_import_setting['normal_import_method'])),
            (import_options.skeletal_mesh_import_data, 'normal_generation_method', getattr(FBXNormalGenerationMethod, unreal_engine_import_setting['normal_generation_method'])),
            (import_options.skeletal_mesh_import_data, 'compute_weighted_normals', unreal_engine_import_setting['compute_weighted_normals']),
            (import_options.skeletal_mesh_import_data, 'threshold_position', unreal_engine_import_setting['threshold_position']),
            (import_options.skeletal_mesh_import_data, 'threshold_tangent_normal', unreal_engine_import_setting['threshold_tangent_normal']),
            (import_options.skeletal_mesh_import_data, 'threshold_uv', unreal_engine_import_setting['threshold_uv']),
            (import_options, 'create_physics_asset', (unreal_engine_import_setting['create_physics_asset'] == 'CREATE')),

            # Transform

            (import_options.skeletal_mesh_import_data, 'import_translation', Vector(*unreal_engine_import_setting['import_translation'])),
            (import_options.skeletal_mesh_import_data, 'import_rotation', Rotator(*unreal_engine_import_setting['import_rotation'])),
            (import_options.skeletal_mesh_import_data, 'import_uniform_scale', unreal_engine_import_setting['import_uniform_scale']),

            # Misc.

            (import_options.skeletal_mesh_import_data, 'convert_scene', unreal_engine_import_setting['convert_scene']),
            (import_options.skeletal_mesh_import_data, 'force_front_x_axis', unreal_engine_import_setting['force_front_x_axis']),
            (import_options.skeletal_mesh_import_data, 'convert_scene_unit', unreal_engine_import_setting['convert_scene_unit']),
            (import_options, 'override_full_name', unreal_engine_import_setting['override_full_name']),

            # Material

            (import_options.texture_import_data, 'material_search_location', getattr(MaterialSearchLocation, unreal_engine_import_setting['material_search_location'])),
            (import_options, 'import_materials', unreal_engine_import_setting['import_materials']),
            (import_options, 'import_textures', unreal_engine_import_setting['import_textures']),
            (import_options.texture_import_data, 'invert_normal_maps', unreal_engine_import_setting['invert_normal_maps']),
            (import_options.skeletal_mesh_import_data, 'reorder_material_to_fbx_order', unreal_engine_import_setting['reorder_material_to_fbx_order']),
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
