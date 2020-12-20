import os
import json
import bpy
from bpy.utils import register_class, unregister_class
from bpy.types import Operator
from .. utils.base import ExportOperator, Panel, ExportOptionPanel
from .. utils.connect import remote, skeletons

class OP_UpdateSkeleton(Operator):
    bl_idname = 'ue4workspace.update_skeletons'
    bl_label = 'Update Skeleton'
    bl_description = 'Update Skeleton From Unreal Engine'

    @classmethod
    def poll(self, context):
        preferences = context.preferences.addons['UE4Workspace'].preferences
        return preferences.export.type in ['UNREAL', 'BOTH'] and bool(remote.remote_nodes)

    def execute(self, context):
        preferences = context.preferences.addons['UE4Workspace'].preferences

        reset_skeleton_list = open(os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'temp', 'skeleton_list.json')), 'w+')
        reset_skeleton_list.write(json.dumps([]))
        reset_skeleton_list.close()

        remote.exec_script('GetAllSkeleton.py')

        load_skeleton_list = open(os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'temp', 'skeleton_list.json')), 'r')
        skeleton_list = json.loads(load_skeleton_list.read())
        load_skeleton_list.close()

        skeletons.clear()

        for node_id, package_name, asset_name in skeleton_list:
            skeletons.append((node_id + ':' + package_name, asset_name, package_name))

        self.report({'INFO'}, 'Update asset list success')

        return {'FINISHED'}

class OP_ExportSkeletalMesh(ExportOperator):
    bl_idname = 'ue4workspace.export_skeletal_mesh'
    bl_label = 'Export Skeletal Mesh'
    bl_description = 'Export Armature To Skeletal Mesh'

    ext_file = 'fbx'

    def execute(self, context):
        preferences = context.preferences.addons['UE4Workspace'].preferences
        skeletal_mesh = preferences.skeletal_mesh
        fbx_setting = skeletal_mesh.fbx
        unreal_engine_setting = skeletal_mesh.unreal_engine

        selected_objects = context.selected_objects
        objects = context.scene.objects if skeletal_mesh.option == 'ALL' else selected_objects
        objects = [obj for obj in objects if obj.type == 'ARMATURE']

        directory = self.create_string_directory(preferences.export.export_folder if preferences.export.type in ['FILE','BOTH'] else preferences.export.temp_folder, skeletal_mesh.subfolder)

        self.create_directory_if_not_exist(directory, skeletal_mesh.subfolder)

        list_name_objects = []
        unreal_engine_import_setting = {
            'files': [],
            'main_folder': self.safe_string_path(preferences.connect_unreal_engine.main_folder),
            'subfolder': self.safe_string_path(skeletal_mesh.subfolder),
            'overwrite_file': skeletal_mesh.overwrite_file,
            'temporary': preferences.export.type == 'UNREAL'
        }

        unreal_engine_import_setting.update(unreal_engine_setting.to_dict())

        bpy.ops.object.select_all(action='DESELECT')

        for obj in objects:
            if skeletal_mesh.mesh == 'COMBINE':
                filename = self.safe_string_path(obj.name)
                check_duplicate = len([obj_name for obj_name in list_name_objects if obj_name.startswith(filename)])
                list_name_objects.append(filename)

                filename += '_' + str(check_duplicate) if bool(check_duplicate) else ''
                filename_ext = filename + '.' + self.ext_file

                if not self.is_file_exist(directory, filename_ext) or skeletal_mesh.overwrite_file:

                    self.mute_attach_constraint(obj)

                    original_location = obj.matrix_world.to_translation()
                    if skeletal_mesh.origin == 'OBJECT':
                        obj.matrix_world.translation = (0, 0, 0)

                    original_rotation = obj.rotation_quaternion.copy() if obj.rotation_mode == 'QUATERNION' else obj.rotation_euler.copy()
                    if not skeletal_mesh.apply_rotation:
                        if obj.rotation_mode == 'QUATERNION':
                            obj.rotation_quaternion = (1, 0, 0, 0)
                        else:
                            obj.rotation_euler = (0, 0, 0)

                    original_object_name = obj.name
                    is_armature_has_root_bone = obj.data.bones.get('root', False)

                    if skeletal_mesh.root_bone == 'ARMATURE':
                        obj.name = 'Armature'
                    elif skeletal_mesh.root_bone == 'AUTO':
                        if is_armature_has_root_bone:
                            obj.name = 'Armature'
                        else:
                            obj.name = 'root'
                    elif skeletal_mesh.root_bone == 'OBJECT':
                        pass

                    self.prepare_skeletal_meshes(obj)

                    obj.select_set(state=True)

                    export_setting = {
                        'filepath': self.create_string_directory(directory, filename_ext),
                        'check_existing': False,
                        'filter_glob': '*.fbx',
                        'use_selection': True,
                        'use_active_collection': False,
                        'object_types': {'MESH', 'ARMATURE'},
                        'use_custom_props': skeletal_mesh.use_custom_props,
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
                        'skeleton': skeletal_mesh.skeleton
                    })

                    self.restore_skeletal_meshes(obj)

                    obj.select_set(state=False)

                    if skeletal_mesh.root_bone == 'ARMATURE':
                        obj.name = original_object_name
                    elif skeletal_mesh.root_bone == 'AUTO':
                        obj.name = original_object_name
                    elif skeletal_mesh.root_bone == 'OBJECT':
                        pass

                    if skeletal_mesh.origin == 'OBJECT':
                        obj.matrix_world.translation = original_location

                    if not skeletal_mesh.apply_rotation:
                        if obj.rotation_mode == 'QUATERNION':
                            obj.rotation_quaternion = original_rotation
                        else:
                            obj.rotation_euler = original_rotation

                    self.unmute_attach_constraint(obj)
            else:
                self.mute_attach_constraint(obj)

                original_location = obj.matrix_world.to_translation()
                if skeletal_mesh.origin == 'OBJECT':
                    obj.matrix_world.translation = (0, 0, 0)

                original_rotation = obj.rotation_quaternion.copy() if obj.rotation_mode == 'QUATERNION' else obj.rotation_euler.copy()
                if not skeletal_mesh.apply_rotation:
                    if obj.rotation_mode == 'QUATERNION':
                        obj.rotation_quaternion = (1, 0, 0, 0)
                    else:
                        obj.rotation_euler = (0, 0, 0)

                original_object_name = obj.name
                is_armature_has_root_bone = obj.data.bones.get('root', False)

                if skeletal_mesh.root_bone == 'ARMATURE':
                    obj.name = 'Armature'
                elif skeletal_mesh.root_bone == 'AUTO':
                    if is_armature_has_root_bone:
                        obj.name = 'Armature'
                    else:
                        obj.name = 'root'
                elif skeletal_mesh.root_bone == 'OBJECT':
                    pass

                obj.select_set(state=True)

                for skeletal_mesh_object, hide, hide_select, hide_viewport in [(children_obj, children_obj.hide_get(), children_obj.hide_select, children_obj.hide_viewport) for children_obj in obj.children if children_obj.type == 'MESH' and children_obj.data.is_export_skeletal_mesh_part]:
                    filename = self.safe_string_path(obj.name + '_' + skeletal_mesh_object.name)
                    check_duplicate = len([obj_name for obj_name in list_name_objects if obj_name.startswith(filename)])
                    list_name_objects.append(filename)

                    filename += '_' + str(check_duplicate) if bool(check_duplicate) else ''
                    filename_ext = filename + '.' + self.ext_file

                    if not self.is_file_exist(directory, filename_ext) or skeletal_mesh.overwrite_file:
                        skeletal_mesh_object.hide_set(False)
                        skeletal_mesh_object.hide_select = False
                        skeletal_mesh_object.hide_viewport = False

                        skeletal_mesh_object.select_set(state=True)

                        export_setting = {
                            'filepath': self.create_string_directory(directory, filename_ext),
                            'check_existing': False,
                            'filter_glob': '*.fbx',
                            'use_selection': True,
                            'use_active_collection': False,
                            'object_types': {'MESH', 'ARMATURE'},
                            'use_custom_props': False,
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
                            'skeleton': skeletal_mesh.skeleton
                        })

                        skeletal_mesh_object.select_set(state=False)

                        skeletal_mesh_object.hide_set(hide)
                        skeletal_mesh_object.hide_select = hide_select
                        skeletal_mesh_object.hide_viewport = hide_viewport

                obj.select_set(state=False)

                if skeletal_mesh.root_bone == 'ARMATURE':
                    obj.name = original_object_name
                elif skeletal_mesh.root_bone == 'AUTO':
                    obj.name = original_object_name
                elif skeletal_mesh.root_bone == 'OBJECT':
                    pass

                if skeletal_mesh.origin == 'OBJECT':
                    obj.matrix_world.translation = original_location

                if not skeletal_mesh.apply_rotation:
                    if obj.rotation_mode == 'QUATERNION':
                        obj.rotation_quaternion = original_rotation
                    else:
                        obj.rotation_euler = original_rotation

                self.unmute_attach_constraint(obj)

        for obj in selected_objects:
            obj.select_set(state=True)

        self.unreal_engine_exec_script('ImportSkeletalMesh.py', unreal_engine_import_setting)

        self.report({'INFO'}, 'export ' + str(len(unreal_engine_import_setting['files'])) + ' skeletal mesh success')

        return {'FINISHED'}

class PANEL(Panel):
    bl_idname = 'UE4WORKSPACE_PT_SkeletalMeshPanel'
    bl_label = 'Skeletal Mesh'

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons['UE4Workspace'].preferences
        skeletal_mesh = preferences.skeletal_mesh

        col_data = [
            ('Subfolder', 'subfolder'),
            ('Overwrite File', 'overwrite_file'),
            ('Custom Properties', 'use_custom_props'),
            ('Apply Rotation', 'apply_rotation'),
            ('Root Bone', 'root_bone'),
            ('Export Skeletal Mesh Option', 'option'),
            ('Origin', 'origin'),
            ('Mesh Option', 'mesh'),
        ]

        if preferences.export.type in ['UNREAL','BOTH']:
            col_data.append(('Skeleton', 'skeleton'))

        for label_str, property_str in col_data:
            row = layout.row()
            split = row.split(factor=0.6)
            col = split.column()
            col.alignment = 'RIGHT'
            col.label(text=label_str)
            col = split.column()
            col.prop(skeletal_mesh, property_str, text='')

            if property_str == 'skeleton':
                row = layout.row()
                row.scale_y = 1.5
                row.operator('ue4workspace.update_skeletons',icon='ARMATURE_DATA')

        col = layout.column()
        col.scale_y = 1.5
        col.operator('ue4workspace.export_skeletal_mesh',icon='OUTLINER_OB_ARMATURE')

class SUB_PANEL_1(ExportOptionPanel):
    bl_idname = 'UE4WORKSPACE_PT_SkeletalMeshFBXOption'
    bl_parent_id = 'UE4WORKSPACE_PT_SkeletalMeshPanel'
    bl_label = 'FBX Export Setting'

    def draw(self, context):
        preferences = context.preferences.addons['UE4Workspace'].preferences
        fbx_setting = preferences.skeletal_mesh.fbx
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
            ],
            'tab_armature': [
                ('Primary Bone Axis', 'primary_bone_axis'),
                ('Secondary Bone Axis', 'secondary_bone_axis'),
                ('Armature FBXNode Type', 'armature_nodetype'),
                ('Only Deform Bones', 'use_armature_deform_only'),
                ('Add Leaf Bones', 'add_leaf_bones'),
            ],
        })

class SUB_PANEL_2(ExportOptionPanel):
    bl_idname = 'UE4WORKSPACE_PT_SkeletalMeshUnrealEnginePanel'
    bl_parent_id = 'UE4WORKSPACE_PT_SkeletalMeshPanel'
    bl_label = 'Unreal Engine Export Setting'

    def draw(self, context):
        preferences = context.preferences.addons['UE4Workspace'].preferences
        unreal_engine_setting = preferences.skeletal_mesh.unreal_engine

        setting_data = {
            'tab_mesh': [
                ('Import Content Type', 'import_content_type'),
                ('Vertex Color Import Option', 'vertex_color_import_option'),
                ('Vertex Override Color', 'vertex_override_color'),
                ('Update Skeleton Reference Pose', 'update_skeleton_reference_pose'),
                ('Use T0 As Ref Pose', 'use_t0_as_ref_pose'),
                ('Preserve Smoothing Groups', 'preserve_smoothing_groups'),
                ('Import Meshes In Bone Hierarchy', 'import_meshes_in_bone_hierarchy'),
                ('Import Morph Targets', 'import_morph_targets'),
                ('Import Mesh LODs', 'import_mesh_lo_ds'),
                ('Normal Import Method', 'normal_import_method'),
                ('Normal Generation Method', 'normal_generation_method'),
                ('Compute Weighted Normals', 'compute_weighted_normals'),
                ('Threshold Position', 'threshold_position'),
                ('Threshold Tangent Normal', 'threshold_tangent_normal'),
                ('Threshold UV', 'threshold_uv'),
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
            'tab_material': [
                ('Search Location', 'material_search_location'),
                ('Import Material', 'import_materials'),
                ('Import Texture', 'import_textures'),
                ('Invert Normal Maps', 'invert_normal_maps'),
                ('Reorder Material To FBX Order', 'reorder_material_to_fbx_order'),
            ]
        }

        self.draw_property(unreal_engine_setting, setting_data)

list_class_to_register = [
    OP_UpdateSkeleton,
    OP_ExportSkeletalMesh,
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