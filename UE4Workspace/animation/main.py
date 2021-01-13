import bpy
from bpy.utils import register_class, unregister_class
from bpy.types import Operator, UIList
from .. utils.base import ExportOperator, Panel, ExportOptionPanel

class ANIMATION_UL_action_list(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, 'name', text='', icon='ACTION', emboss=False)
        layout.prop(item, 'is_export', text='')

class OP_SelectExportAction(Operator):
    bl_idname = 'ue4workspace.select_export_action'
    bl_label = 'Select Action To Export'
    bl_options = {'UNDO'}

    type: bpy.props.StringProperty(default='')

    def execute(self, context):
        if self.type:
            for action in bpy.data.actions:
                action.is_export = {'SELECT': True, 'DESELECT': False, 'INVERT': not action.is_export}[self.type]
        return {'FINISHED'}

class OP_AddMaterialCurveSuffix(Operator):
    bl_idname = 'ue4workspace.add_material_curve_suffix'
    bl_label = 'Add Suffix'
    bl_description = 'Add Suffix on Animation Export Setting'
    bl_options = {'UNDO'}

    val: bpy.props.StringProperty()

    def execute(self, context):
        preferences = context.preferences.addons['UE4Workspace'].preferences
        unreal_engine_setting = preferences.animation.unreal_engine

        material_curve_suffixes = unreal_engine_setting.material_curve_suffixes.split('|') if bool(unreal_engine_setting.material_curve_suffixes) else []
        material_curve_suffixes.append(self.val.replace('|', ''))

        unreal_engine_setting.material_curve_suffixes = '|'.join(material_curve_suffixes)

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 250)

    def draw(self, context):
        col = self.layout.column()
        row = col.row()
        split = row.split(factor=0.5)
        col = split.column()
        col.alignment = 'RIGHT'
        col.label(text='Value :')
        col = split.column()
        col.prop(self, 'val', text='')

class OP_ClearMaterialCurveSuffixes(Operator):
    bl_idname = 'ue4workspace.clear_material_curve_suffix'
    bl_label = 'Clear Suffixes'
    bl_description = 'Clear Suffixes on Animation Export Setting'
    bl_options = {'UNDO'}

    def execute(self, context):
        preferences = context.preferences.addons['UE4Workspace'].preferences
        unreal_engine_setting = preferences.animation.unreal_engine

        unreal_engine_setting.material_curve_suffixes = ''
        return {'FINISHED'}

class OP_RemoveMaterialCurveSuffixIndex(Operator):
    bl_idname = 'ue4workspace.remove_material_curve_suffix_index'
    bl_label = 'Remove Suffix'
    bl_description = 'Remove Suffix Base on Index Animation Export Setting'
    bl_options = {'UNDO'}

    index: bpy.props.IntProperty()

    def execute(self, context):
        preferences = context.preferences.addons['UE4Workspace'].preferences
        unreal_engine_setting = preferences.animation.unreal_engine

        material_curve_suffixes = unreal_engine_setting.material_curve_suffixes.split('|') if bool(unreal_engine_setting.material_curve_suffixes) else []
        material_curve_suffixes.pop(self.index)

        unreal_engine_setting.material_curve_suffixes = '|'.join(material_curve_suffixes)
        return {'FINISHED'}

class OP_EditMaterialCurveSuffix(Operator):
    bl_idname = 'ue4workspace.edit_material_curve_suffix'
    bl_label = 'Edit Value Suffix'
    bl_description = 'Edit Value Suffix on Animation Export Setting'
    bl_options = {'UNDO'}

    val: bpy.props.StringProperty()
    index: bpy.props.IntProperty()

    def execute(self, context):
        preferences = context.preferences.addons['UE4Workspace'].preferences
        unreal_engine_setting = preferences.animation.unreal_engine

        material_curve_suffixes = unreal_engine_setting.material_curve_suffixes.split('|') if bool(unreal_engine_setting.material_curve_suffixes) else []
        material_curve_suffixes[self.index] = self.val.replace('|', '')

        unreal_engine_setting.material_curve_suffixes = '|'.join(material_curve_suffixes)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 250)

    def draw(self, context):
        col = self.layout.column()
        row = col.row()
        split = row.split(factor=0.5)
        col = split.column()
        col.alignment = 'RIGHT'
        col.label(text='Value :')
        split = split.split()
        col = split.column()
        col.prop(self, 'val', text='')

class OP_ExportAnimationMesh(ExportOperator):
    bl_idname = 'ue4workspace.export_animation_mesh'
    bl_label = 'Export Animation'
    bl_description = 'Export Action To Animation'

    ext_file = 'fbx'

    @classmethod
    def poll(cls, context):
        preferences = context.preferences.addons['UE4Workspace'].preferences

        if context.mode == 'OBJECT' and context.active_object is not None and context.active_object.type == 'ARMATURE':
            if preferences.export.type == 'UNREAL' and preferences.animation.skeleton != 'NONE':
                return bool(preferences.export.temp_folder.strip())
            elif preferences.export.type == 'BOTH' and preferences.animation.skeleton != 'NONE':
                return bool(preferences.export.export_folder.strip())
            elif preferences.export.type == 'FILE':
                return bool(preferences.export.export_folder.strip())
        return False

    def execute(self, context):
        preferences = context.preferences.addons['UE4Workspace'].preferences
        animation = preferences.animation
        fbx_setting = animation.fbx
        unreal_engine_setting = animation.unreal_engine

        active_object = context.active_object
        selected_objects = context.selected_objects

        directory = self.create_string_directory(preferences.export.export_folder if preferences.export.type in ['FILE','BOTH'] else preferences.export.temp_folder, animation.subfolder)

        self.create_directory_if_not_exist(directory, animation.subfolder)

        list_name_animations = []
        unreal_engine_import_setting = {
            'files': [],
            'main_folder': self.safe_string_path(preferences.connect_unreal_engine.main_folder),
            'subfolder': self.safe_string_path(animation.subfolder),
            'overwrite_file': animation.overwrite_file,
            'temporary': preferences.export.type == 'UNREAL'
        }

        unreal_engine_import_setting.update(unreal_engine_setting.to_dict())

        bpy.ops.object.select_all(action='DESELECT')

        self.mute_attach_constraint(active_object)

        active_object.select_set(True)

        original_action = active_object.animation_data.action
        original_frame_start = context.scene.frame_start
        original_frame_end = context.scene.frame_end

        original_object_name = active_object.name
        is_armature_has_root_bone = active_object.data.bones.get('root', False)

        if animation.root_bone == 'ARMATURE':
            active_object.name = 'Armature'
        elif animation.root_bone == 'AUTO':
            if is_armature_has_root_bone:
                active_object.name = 'Armature'
            else:
                active_object.name = 'root'
        elif animation.root_bone == 'OBJECT':
            pass

        export_actions = [action for action in bpy.data.actions if action.is_export]

        for export_action in export_actions:
            filename = self.safe_string_path(export_action.name)
            check_duplicate = len([animation_name for animation_name in list_name_animations if animation_name.startswith(filename)])
            list_name_animations.append(filename)

            filename += '_' + str(check_duplicate) if bool(check_duplicate) else ''
            filename_ext = filename + '.' + self.ext_file

            if not self.is_file_exist(directory, filename_ext) or animation.overwrite_file:

                original_location = active_object.matrix_world.to_translation()
                if animation.origin == 'OBJECT':
                    active_object.matrix_world.translation = (0, 0, 0)

                original_rotation = active_object.rotation_quaternion.copy() if active_object.rotation_mode == 'QUATERNION' else active_object.rotation_euler.copy()
                if not animation.apply_rotation:
                    if active_object.rotation_mode == 'QUATERNION':
                        active_object.rotation_quaternion = (1, 0, 0, 0)
                    else:
                        active_object.rotation_euler = (0, 0, 0)

                active_object.animation_data.action = export_action

                if fbx_setting.bake_anim_force_startend_keying:
                    context.scene.frame_start, context.scene.frame_end = export_action.frame_range

                export_setting = {
                    'filepath': self.create_string_directory(directory, filename_ext),
                    'check_existing': False,
                    'filter_glob': '*.fbx',
                    'use_selection': True,
                    'use_active_collection': False,
                    'object_types': {'ARMATURE'},
                    'use_custom_props': animation.use_custom_props,
                    'bake_anim': True,
                    'bake_anim_use_nla_strips': False,
                    'bake_anim_use_all_actions': False,
                    'path_mode': 'AUTO',
                    'embed_textures': False,
                    'batch_mode': 'OFF'
                }

                export_setting.update(fbx_setting.to_dict())

                # EXPORT
                bpy.ops.export_scene.fbx(**export_setting)

                unreal_engine_import_setting['files'].append({
                    'path': export_setting['filepath'],
                    'skeleton': animation.skeleton
                })

                if animation.origin == 'OBJECT':
                    active_object.matrix_world.translation = original_location

                if not animation.apply_rotation:
                    if active_object.rotation_mode == 'QUATERNION':
                        active_object.rotation_quaternion = original_rotation
                    else:
                        active_object.rotation_euler = original_rotation

        self.unmute_attach_constraint(active_object)

        active_object.select_set(False)

        active_object.animation_data.action = original_action
        context.scene.frame_start = original_frame_start
        context.scene.frame_end = original_frame_end

        if animation.root_bone == 'ARMATURE':
            active_object.name = original_object_name
        elif animation.root_bone == 'AUTO':
            active_object.name = original_object_name
        elif animation.root_bone == 'OBJECT':
            pass

        for obj in selected_objects:
            obj.select_set(state=True)

        self.unreal_engine_exec_script('ImportAnimation.py', unreal_engine_import_setting)

        self.report({'INFO'}, 'export ' + str(len(unreal_engine_import_setting['files'])) + ' animation success')

        return {'FINISHED'}

class PANEL(Panel):
    bl_idname = 'UE4WORKSPACE_PT_AnimationPanel'
    bl_label = 'Animation'

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons['UE4Workspace'].preferences
        animation = preferences.animation

        col_data = [
            ('Subfolder', 'subfolder'),
            ('Overwrite File', 'overwrite_file'),
            ('Custom Properties', 'use_custom_props'),
            ('Apply Rotation', 'apply_rotation'),
            ('Root Bone', 'root_bone'),
            ('Origin', 'origin'),
            ('Frame Rate', 'fps'),
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
            if property_str == 'fps':
                col.prop(context.scene.render, property_str, text='')
            else:
                col.prop(animation, property_str, text='')

            if property_str == 'skeleton':
                row = layout.row()
                row.scale_y = 1.5
                row.operator('ue4workspace.update_skeletons',icon='ARMATURE_DATA')

        if context.active_object is not None and context.active_object.type == 'ARMATURE':
            row = layout.row()
            row.template_list('ANIMATION_UL_action_list', '', bpy.data, 'actions', context.active_object, 'ANIMATION_index_action')

            row = layout.row(align=True)
            row.scale_y = 1.5
            row.operator('ue4workspace.select_export_action', text='SELECT').type = 'SELECT'
            row.operator('ue4workspace.select_export_action', text='DESELECT').type = 'DESELECT'
            row.operator('ue4workspace.select_export_action', text='INVERT').type = 'INVERT'

        col = layout.column()
        col.scale_y = 1.5
        col.operator('ue4workspace.export_animation_mesh',icon='RENDER_ANIMATION')

class SUB_PANEL_1(ExportOptionPanel):
    bl_idname = 'UE4WORKSPACE_PT_AnimationFBXOption'
    bl_parent_id = 'UE4WORKSPACE_PT_AnimationPanel'
    bl_label = 'FBX Export Setting'

    def draw(self, context):
        preferences = context.preferences.addons['UE4Workspace'].preferences
        fbx_setting = preferences.animation.fbx
        self.draw_property(fbx_setting, {
            'tab_transform': [
                ('Scale', 'global_scale'),
                ('Apply Scalings', 'apply_unit_scale'),
                ('Forward', 'axis_forward'),
                ('Up', 'axis_up'),
                ('Apply Unit', 'apply_unit_scale'),
                ('Apply Transform', 'bake_space_transform'),
            ],
            'tab_armature': [
                ('Primary Bone Axis', 'primary_bone_axis'),
                ('Secondary Bone Axis', 'secondary_bone_axis'),
                ('Armature FBXNode Type', 'armature_nodetype'),
                ('Only Deform Bones', 'use_armature_deform_only'),
                ('Add Leaf Bones', 'add_leaf_bones'),
            ],
            'tab_bake_animation': [
                ('Key All Bones', 'bake_anim_use_all_bones'),
                ('Force Start/End Keying', 'bake_anim_force_startend_keying'),
                ('Sampling Rate', 'bake_anim_step'),
                ('Simplify', 'bake_anim_simplify_factor'),
            ],
        })

class SUB_PANEL_2(ExportOptionPanel):
    bl_idname = 'UE4WORKSPACE_PT_AnimationUnrealEnginePanel'
    bl_parent_id = 'UE4WORKSPACE_PT_AnimationPanel'
    bl_label = 'Unreal Engine Export Setting'

    def draw(self, context):
        preferences = context.preferences.addons['UE4Workspace'].preferences
        unreal_engine_setting = preferences.animation.unreal_engine

        setting_data = {
            'tab_animation': [
                ('Animation Length', 'animation_length'),
                ('Import Meshes in Bone Hierarchy', 'import_meshes_in_bone_hierarchy'),
                ('Frame Import Range', 'frame_import_range'),
                ('Use Default Sample Rate', 'use_default_sample_rate'),
                ('Custom Sample Rate', 'custom_sample_rate'),
                ('Import Custom Attribute', 'import_custom_attribute'),
                ('Delete Existing Custom Attribute Curves', 'delete_existing_custom_attribute_curves'),
                ('Import Bone Tracks', 'import_bone_tracks'),
                ('Set Material Curve Type', 'set_material_drive_parameter_on_custom_attribute'),
                ('Material Curve Suffixes', 'material_curve_suffixes'),
                ('Remove Redundant Keys', 'remove_redundant_keys'),
                ('Delete Existing Morph Target Curves', 'delete_existing_morph_target_curves'),
                ('Do not Import Curve With 0 Values', 'do_not_import_curve_with_zero'),
                ('Preserve Local Transform', 'preserve_local_transform'),
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
            ]
        }

        self.draw_property(unreal_engine_setting, setting_data)

list_class_to_register = [
    ANIMATION_UL_action_list,
    OP_SelectExportAction,
    OP_AddMaterialCurveSuffix,
    OP_ClearMaterialCurveSuffixes,
    OP_RemoveMaterialCurveSuffixIndex,
    OP_EditMaterialCurveSuffix,
    OP_ExportAnimationMesh,
    PANEL,
    SUB_PANEL_1,
    SUB_PANEL_2
]

def register():
    bpy.types.Action.is_export = bpy.props.BoolProperty(
        name='Export action',
        default=False
    )

    bpy.types.Object.ANIMATION_index_action = bpy.props.IntProperty(
        default=-1
    )

    for x in list_class_to_register:
        register_class(x)

def unregister():
    del bpy.types.Action.is_export
    del bpy.types.Object.ANIMATION_index_action

    for x in list_class_to_register[::-1]:
        unregister_class(x)