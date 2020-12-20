import os
import json

from unreal import (
    EditorAssetLibrary,
    FbxImportUI,
    AssetImportTask,
    AssetToolsHelpers,

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

        for option, prop, value in ([
            (import_options, 'import_mesh', True),
            (import_options, 'import_as_skeletal', False),
            (import_options, 'import_animations', False),

            (import_options.static_mesh_import_data, 'auto_generate_collision', (True if file['custom_collision'] else unreal_engine_import_setting['auto_generate_collision'])),
            (import_options.static_mesh_import_data, 'vertex_color_import_option', getattr(VertexColorImportOption, unreal_engine_import_setting['vertex_color_import_option'])),
            (import_options.static_mesh_import_data, 'vertex_override_color', Color(r=unreal_engine_import_setting['vertex_override_color'][0], g=unreal_engine_import_setting['vertex_override_color'][1], b=unreal_engine_import_setting['vertex_override_color'][2], a=unreal_engine_import_setting['vertex_override_color'][3])),
            (import_options.static_mesh_import_data, 'remove_degenerates', unreal_engine_import_setting['remove_degenerates']),
            (import_options.static_mesh_import_data, 'build_adjacency_buffer', unreal_engine_import_setting['build_adjacency_buffer']),
            (import_options.static_mesh_import_data, 'build_reversed_index_buffer', unreal_engine_import_setting['build_reversed_index_buffer']),
            (import_options.static_mesh_import_data, 'generate_lightmap_u_vs', (False if file['custom_lightmap'] else unreal_engine_import_setting['generate_lightmap_u_vs'])),
            (import_options.static_mesh_import_data, 'one_convex_hull_per_ucx', unreal_engine_import_setting['one_convex_hull_per_ucx']),
            (import_options.static_mesh_import_data, 'combine_meshes', unreal_engine_import_setting['combine_meshes']),
            (import_options.static_mesh_import_data, 'transform_vertex_to_absolute', unreal_engine_import_setting['transform_vertex_to_absolute']),
            (import_options.static_mesh_import_data, 'bake_pivot_in_vertex', unreal_engine_import_setting['bake_pivot_in_vertex']),
            (import_options.static_mesh_import_data, 'import_mesh_lo_ds', (True if bool(file['lod']) else unreal_engine_import_setting['import_mesh_lo_ds'])),
            (import_options.static_mesh_import_data, 'normal_import_method', getattr(FBXNormalImportMethod, 'FBXNIM_' + unreal_engine_import_setting['normal_import_method'])),
            (import_options.static_mesh_import_data, 'normal_generation_method', getattr(FBXNormalGenerationMethod, unreal_engine_import_setting['normal_generation_method'])),
            (import_options.static_mesh_import_data, 'compute_weighted_normals', unreal_engine_import_setting['compute_weighted_normals']),

            # Transform

            (import_options.static_mesh_import_data, 'import_translation', Vector(*unreal_engine_import_setting['import_translation'])),
            (import_options.static_mesh_import_data, 'import_rotation', Rotator(*unreal_engine_import_setting['import_rotation'])),
            (import_options.static_mesh_import_data, 'import_uniform_scale', unreal_engine_import_setting['import_uniform_scale']),

            # Misc.

            (import_options.static_mesh_import_data, 'convert_scene', unreal_engine_import_setting['convert_scene']),
            (import_options.static_mesh_import_data, 'force_front_x_axis', unreal_engine_import_setting['force_front_x_axis']),
            (import_options.static_mesh_import_data, 'convert_scene_unit', unreal_engine_import_setting['convert_scene_unit']),
            (import_options, 'override_full_name', unreal_engine_import_setting['override_full_name']),

            # LODSetting

            (import_options, 'auto_compute_lod_distances', (file['auto_compute_lod_distances'] if bool(file['lod']) else unreal_engine_import_setting['auto_compute_lod_distances'])),
            (import_options, 'minimum_lod_number', unreal_engine_import_setting['minimum_lod_number']),
            (import_options, 'lod_number', unreal_engine_import_setting['lod_number']),

            # Material

            (import_options.texture_import_data, 'material_search_location', getattr(MaterialSearchLocation, unreal_engine_import_setting['material_search_location'])),
            (import_options, 'import_materials', unreal_engine_import_setting['import_materials']),
            (import_options, 'import_textures', unreal_engine_import_setting['import_textures']),
            (import_options.texture_import_data, 'invert_normal_maps', unreal_engine_import_setting['invert_normal_maps']),
            (import_options.static_mesh_import_data, 'reorder_material_to_fbx_order', unreal_engine_import_setting['reorder_material_to_fbx_order']),
        ]+[
            # LOD Screen Size
            (import_options, 'lod_distance' + str(index), screen_size) for index, screen_size in enumerate((file['lod']+[unreal_engine_import_setting['lod_distance' + str(index)] for index in range(8)][len(file['lod']):]))
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
