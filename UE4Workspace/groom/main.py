import bpy
from bpy.utils import register_class, unregister_class
from .. utils.base import ExportOperator, ExperimentalPanel

class OP_ExportGroom(ExportOperator):
    bl_idname = 'ue4workspace.export_groom'
    bl_label = 'Export Groom'
    bl_description = 'Export Hair Modifiers To Groom'

    ext_file = 'abc'

    def execute(self, context):
        preferences = context.preferences.addons['UE4Workspace'].preferences
        groom = preferences.groom

        selected_objects = context.selected_objects
        objects = context.scene.objects if groom.option == 'ALL' else selected_objects
        objects = [obj for obj in objects if obj.type == 'MESH' and 'HAIR' in [mod.particle_system.settings.type for mod in obj.modifiers if mod.type == 'PARTICLE_SYSTEM'] and not obj.data.mesh_as_lod]

        directory = self.create_string_directory(preferences.export.export_folder if preferences.export.type in ['FILE','BOTH'] else preferences.export.temp_folder, groom.subfolder)

        self.create_directory_if_not_exist(directory, groom.subfolder)

        list_name_objects = []
        unreal_engine_import_setting = {
            'files': [],
            'main_folder': self.safe_string_path(preferences.connect_unreal_engine.main_folder),
            'subfolder': self.safe_string_path(groom.subfolder),
            'overwrite_file': groom.overwrite_file,
            'temporary': preferences.export.type == 'UNREAL'
        }

        bpy.ops.object.select_all(action='DESELECT')

        for obj in objects:
            filename = self.safe_string_path(obj.name)
            check_duplicate = len([obj_name for obj_name in list_name_objects if obj_name.startswith(filename)])
            list_name_objects.append(filename)

            filename += '_' + str(check_duplicate) if bool(check_duplicate) else ''
            filename_ext = filename + '.' + self.ext_file

            if not self.is_file_exist(directory, filename_ext) or groom.overwrite_file:

                self.mute_attach_constraint(obj)

                original_location = obj.matrix_world.to_translation()
                if groom.origin == 'OBJECT':
                    obj.matrix_world.translation = (0, 0, 0)

                original_rotation = obj.rotation_quaternion.copy() if obj.rotation_mode == 'QUATERNION' else obj.rotation_euler.copy()
                if not groom.apply_rotation:
                    if obj.rotation_mode == 'QUATERNION':
                        obj.rotation_quaternion = (1, 0, 0, 0)
                    else:
                        obj.rotation_euler = (0, 0, 0)

                self.prepare_groom(obj)

                obj.select_set(state=True)

                export_setting = {
                    'filepath': self.create_string_directory(directory, filename_ext),
                    'check_existing': False,
                    'filter_blender': False,
                    'filter_backup': False,
                    'filter_image': False,
                    'filter_movie': False,
                    'filter_python': False,
                    'filter_font': False,
                    'filter_sound': False,
                    'filter_text': False,
                    'filter_archive': False,
                    'filter_btx': False,
                    'filter_collada': False,
                    'filter_alembic': True,
                    'filter_usd': False,
                    'filter_volume': False,
                    'filter_folder': True,
                    'filter_blenlib': False,
                    'filemode': 8,
                    'display_type': 'DEFAULT',
                    'sort_method': 'FILE_SORT_ALPHA',
                    'start': 1,
                    'end': 1,
                    'xsamples': 1,
                    'gsamples': 1,
                    'sh_open': 0.0,
                    'sh_close': 1.0,
                    'selected': True,
                    'renderable_only': False,
                    'visible_objects_only': True,
                    'flatten': False,
                    'uvs': True,
                    'packuv': True,
                    'normals': True,
                    'vcolors': False,
                    'face_sets': False,
                    'subdiv_schema': False,
                    'apply_subdiv': False,
                    'curves_as_mesh': False,
                    'use_instancing': True,
                    'global_scale': 100.0,
                    'triangulate': False,
                    'quad_method': 'SHORTEST_DIAGONAL',
                    'ngon_method': 'BEAUTY',
                    'export_hair': True,
                    'export_particles': False,
                    'export_custom_properties': groom.use_custom_props,
                    'as_background_job': False,
                    'init_scene_frame_range': False
                }

                # EXPORT
                bpy.ops.wm.alembic_export(**export_setting)

                unreal_engine_import_setting['files'].append({
                    'path': export_setting['filepath']
                })

                self.restore_groom(obj)

                obj.select_set(state=False)

                if groom.origin == 'OBJECT':
                    obj.matrix_world.translation = original_location

                if not groom.apply_rotation:
                    if obj.rotation_mode == 'QUATERNION':
                        obj.rotation_quaternion = original_rotation
                    else:
                        obj.rotation_euler = original_rotation

                self.unmute_attach_constraint(obj)

        for obj in selected_objects:
            obj.select_set(state=True)

        # self.unreal_engine_exec_script('ImportGroom.py', unreal_engine_import_setting)

        self.report({'INFO'}, 'export ' + str(len(unreal_engine_import_setting['files'])) + ' groom success')

        return {'FINISHED'}

class PANEL(ExperimentalPanel):
    bl_idname = 'UE4WORKSPACE_PT_GroomPanel'
    bl_label = '[Experimental] Groom'

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons['UE4Workspace'].preferences
        groom = preferences.groom

        col_data = [
            ('Subfolder', 'subfolder'),
            ('Overwrite File', 'overwrite_file'),
            ('Custom Properties', 'use_custom_props'),
            ('Apply Rotation', 'apply_rotation'),
            ('Export Groom Option', 'option'),
            ('Origin', 'origin'),
        ]

        for label_str, property_str in col_data:
            row = layout.row()
            split = row.split(factor=0.6)
            col = split.column()
            col.alignment = 'RIGHT'
            col.label(text=label_str)
            col = split.column()
            col.prop(groom, property_str, text='')

        col = layout.column()
        col.scale_y = 1.5
        col.operator('ue4workspace.export_groom',icon='OUTLINER_OB_HAIR')

        box = layout.box()
        col = box.column(align=True)

        row = col.row()
        row.alignment = 'CENTER'
        row.label(text='Not Support Export')

        row = col.row()
        row.alignment = 'CENTER'
        row.label(text='Directly To Unreal Engine')

        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator('wm.url_open',icon='URL', text='Unreal Engine Setting').url='https://github.com/anasrar/Blender-UE4-Workspace/issues/22'

list_class_to_register = [
    OP_ExportGroom,
    PANEL
]

def register():
    for x in list_class_to_register:
        register_class(x)

def unregister():
    for x in list_class_to_register[::-1]:
        unregister_class(x)