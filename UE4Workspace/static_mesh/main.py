import bpy
from bpy.utils import register_class, unregister_class
from bpy.types import Operator
from .. utils.base import ExportOperator, Panel, ExportOptionPanel

class OP_ExportStaticMesh(ExportOperator):
    bl_idname = 'ue4workspace.export_static_mesh'
    bl_label = 'Export Static Mesh'
    bl_description = 'Export Mesh To Static Mesh'

    ext_file = 'fbx'

    def execute(self, context):
        preferences = context.preferences.addons['UE4Workspace'].preferences
        static_mesh = preferences.static_mesh
        fbx_setting = static_mesh.fbx
        unreal_engine_setting = static_mesh.unreal_engine

        selected_objects = context.selected_objects
        objects = context.scene.objects if static_mesh.option == 'ALL' else selected_objects
        objects = [obj for obj in objects if obj.type == 'MESH' and not 'ARMATURE' in [mod.type for mod in obj.modifiers] and not obj.data.mesh_as_lod]

        directory = self.create_string_directory(preferences.export.export_folder if preferences.export.type in ['FILE','BOTH'] else preferences.export.temp_folder, static_mesh.subfolder)

        self.create_directory_if_not_exist(directory, static_mesh.subfolder)

        list_unhide_collection_name = [('UE4CustomCollision', static_mesh.custom_collision), ('UE4Socket', static_mesh.socket)]

        self.unhide_collection(*list_unhide_collection_name)

        list_name_objects = []
        unreal_engine_import_setting = {
            'files': [],
            'main_folder': self.safe_string_path(preferences.connect_unreal_engine.main_folder),
            'subfolder': self.safe_string_path(static_mesh.subfolder),
            'overwrite_file': static_mesh.overwrite_file,
            'temporary': preferences.export.type == 'UNREAL'
        }

        unreal_engine_import_setting.update(unreal_engine_setting.to_dict())

        bpy.ops.object.select_all(action='DESELECT')

        for obj in objects:
            filename = self.safe_string_path(obj.name)
            check_duplicate = len([obj_name for obj_name in list_name_objects if obj_name.startswith(filename)])
            list_name_objects.append(filename)

            filename += '_' + str(check_duplicate) if bool(check_duplicate) else ''
            filename_ext = filename + '.' + self.ext_file

            if not self.is_file_exist(directory, filename_ext) or static_mesh.overwrite_file:

                is_object_has_custom_collision = bool([True for children_object in obj.children if children_object.type == 'MESH' and children_object.data.is_custom_collision])
                if static_mesh.custom_collision and is_object_has_custom_collision:
                    self.prepare_custom_collision(obj)

                is_object_has_socket = bool([True for children_object in obj.children if children_object.type == 'EMPTY' and children_object.is_socket])
                if static_mesh.socket and is_object_has_socket:
                    self.prepare_socket(obj)

                self.mute_attach_constraint(obj)

                original_location = obj.matrix_world.to_translation()
                if static_mesh.origin == 'OBJECT':
                    obj.matrix_world.translation = (0, 0, 0)

                original_rotation = obj.rotation_quaternion.copy() if obj.rotation_mode == 'QUATERNION' else obj.rotation_euler.copy()
                if not static_mesh.apply_rotation:
                    if obj.rotation_mode == 'QUATERNION':
                        obj.rotation_quaternion = (1, 0, 0, 0)
                    else:
                        obj.rotation_euler = (0, 0, 0)

                if static_mesh.lod:
                    self.prepare_lod(obj)

                obj.select_set(state=True)

                export_setting = {
                    'filepath': self.create_string_directory(directory, filename_ext),
                    'check_existing': False,
                    'filter_glob': '*.fbx',
                    'use_selection': True,
                    'use_active_collection': False,
                    'object_types': {'MESH', 'EMPTY'},
                    'use_custom_props': static_mesh.use_custom_props,
                    'bake_anim': False,
                    'path_mode': 'AUTO',
                    'embed_textures': False,
                    'batch_mode': 'OFF'
                }

                export_setting.update(fbx_setting.to_dict())

                # EXPORT
                bpy.ops.export_scene.fbx(**export_setting)

                unreal_engine_import_setting['files'].append({
                    'path': export_setting['filepath'],
                    'custom_lightmap': 'lightmap' in [uv.name.lower() for uv in obj.data.uv_layers],
                    'custom_collision': (static_mesh.custom_collision and is_object_has_custom_collision),
                    'auto_compute_lod_distances': obj.data.auto_compute_lod_screen_size,
                    'lod': (([obj.data.lod_0_screen_size] + [lod.screen_size for lod in obj.data.lods if lod.obj is not None]) if (static_mesh.lod and bool([True for lod in obj.data.lods if lod.obj is not None])) else [])
                })

                obj.select_set(state=False)

                if static_mesh.custom_collision and is_object_has_custom_collision:
                    self.restore_custom_collision()

                if static_mesh.socket and is_object_has_socket:
                    self.restore_socket()

                if static_mesh.lod:
                    self.restore_lod()

                if static_mesh.origin == 'OBJECT':
                    obj.matrix_world.translation = original_location

                if not static_mesh.apply_rotation:
                    if obj.rotation_mode == 'QUATERNION':
                        obj.rotation_quaternion = original_rotation
                    else:
                        obj.rotation_euler = original_rotation

                self.unmute_attach_constraint(obj)

        self.restore_collection(*list_unhide_collection_name)

        for obj in selected_objects:
            obj.select_set(state=True)

        self.unreal_engine_exec_script('ImportStaticMesh.py', unreal_engine_import_setting)

        self.report({'INFO'}, 'export ' + str(len(unreal_engine_import_setting['files'])) + ' static mesh success')

        return {'FINISHED'}

class PANEL(Panel):
    bl_idname = 'UE4WORKSPACE_PT_StaticMeshPanel'
    bl_label = 'Static Mesh'

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons['UE4Workspace'].preferences
        static_mesh = preferences.static_mesh

        col_data = [
            ('Subfolder', 'subfolder'),
            ('Overwrite File', 'overwrite_file'),
            ('Custom Properties', 'use_custom_props'),
            ('Apply Rotation', 'apply_rotation'),
            ('Custom Collision', 'custom_collision'),
            ('Socket', 'socket'),
            ('Level of Detail', 'lod'),
            ('Export Static Mesh Option', 'option'),
            ('Origin', 'origin'),
        ]

        for label_str, property_str in col_data:
            row = layout.row()
            split = row.split(factor=0.6)
            col = split.column()
            col.alignment = 'RIGHT'
            col.label(text=label_str)
            col = split.column()
            col.prop(static_mesh, property_str, text='')

        col = layout.column()
        col.scale_y = 1.5
        col.operator('ue4workspace.export_static_mesh',icon='MESH_CUBE')

class SUB_PANEL_1(ExportOptionPanel):
    bl_idname = 'UE4WORKSPACE_PT_StaticMeshFBXOption'
    bl_parent_id = 'UE4WORKSPACE_PT_StaticMeshPanel'
    bl_label = 'FBX Export Setting'

    def draw(self, context):
        preferences = context.preferences.addons['UE4Workspace'].preferences
        fbx_setting = preferences.static_mesh.fbx
        self.draw_property(fbx_setting, {
            'tab_transform': [
                ('Scale', 'global_scale'),
                ('Apply Scalings', 'apply_unit_scale'),
                ('Forward', 'axis_forward'),
                ('Up', 'axis_up'),
                ('Apply Unit', 'apply_unit_scale'),
                ('Apply Transform', 'bake_space_transform'),
            ],
            'tab_geometry': [
                ('Smoothing', 'mesh_smooth_type'),
                ('Export Subdivision Surface', 'use_subsurf'),
                ('Apply Modifiers', 'use_mesh_modifiers'),
                ('Loose Edges', 'use_mesh_edges'),
                ('Tangent Space', 'use_tspace'),
            ]
        })

class SUB_PANEL_2(ExportOptionPanel):
    bl_idname = 'UE4WORKSPACE_PT_StaticMeshUnrealEnginePanel'
    bl_parent_id = 'UE4WORKSPACE_PT_StaticMeshPanel'
    bl_label = 'Unreal Engine Export Setting'

    def draw(self, context):
        preferences = context.preferences.addons['UE4Workspace'].preferences
        unreal_engine_setting = preferences.static_mesh.unreal_engine

        setting_data = {
            'tab_mesh': [
                ('Auto Generate Collision', 'auto_generate_collision'),
                ('Vertex Color Import Option', 'vertex_color_import_option'),
                ('Vertex Override Color', 'vertex_override_color'),
                ('Remove Degenerates', 'remove_degenerates'),
                ('Build Adjacency Buffer', 'build_adjacency_buffer'),
                ('Build Reversed Index Buffer', 'build_reversed_index_buffer'),
                ('Generate Lightmaps UVs', 'generate_lightmap_u_vs'),
                ('One Convex Hull Per UCX', 'one_convex_hull_per_ucx'),
                ('Combine Meshes', 'combine_meshes'),
                ('Transform Vertex to Absolute', 'transform_vertex_to_absolute'),
                ('Bake Pivot in Vertex', 'bake_pivot_in_vertex'),
                ('Import Mesh LODs', 'import_mesh_lo_ds'),
                ('Normal Import Method', 'normal_import_method'),
                ('Normal Generation Method', 'normal_generation_method'),
                ('Compute Weighted Normals', 'compute_weighted_normals'),
            ],
            'tab_transform': [
                ('Import Translation', 'import_translation'),
                ('Import Rotation', 'import_rotation'),
                ('Import Uniform Scale', 'import_uniform_scale'),
            ],
            'tab_misc': [
                ('Convert Scene', 'convert_scene'),
                ('Force Front XAxis', 'force_front_x_axis'),
                ('Convert Scene Unit', 'convert_scene_unit'),
                ('Override Full Name', 'override_full_name'),
            ],
        }

        if unreal_engine_setting.import_mesh_lo_ds:
            setting_data['tab_lod'] = [
                ('Auto Compute LOD Screen Size', 'auto_compute_lod_distances')
            ]

            for index in range(8):
                setting_data['tab_lod'].append(('LOD ' + str(index) + ' Screen Size', 'lod_distance' + str(index)))

            setting_data['tab_lod'].append(('Minimum LOD', 'minimum_lod_number'))
            setting_data['tab_lod'].append(('Number of LODs', 'lod_number'))

        setting_data['tab_material'] = [
            ('Search Location', 'material_search_location'),
            ('Import Material', 'import_materials'),
            ('Import Texture', 'import_textures'),
            ('Invert Normal Maps', 'invert_normal_maps'),
            ('Reorder Material To FBX Order', 'reorder_material_to_fbx_order'),
        ]

        self.draw_property(unreal_engine_setting, setting_data)

list_class_to_register = [
    OP_ExportStaticMesh,
    PANEL,
    SUB_PANEL_1,
    SUB_PANEL_2
]

def register():
    for x in list_class_to_register:
        register_class(x)

def unregister():
    for x in list_class_to_register[::-1]:
        unregister_class(x)