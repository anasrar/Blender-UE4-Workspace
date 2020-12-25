import os
import math
import re
import json
import bpy
from bpy.types import Panel as OriginalPanel, Operator as OriginalOperator
from mathutils import Matrix
from . connect import remote

def create_matrix_scale_from_vector(vec):
    return Matrix.Scale(vec[0], 4, (1.0, 0.0, 0.0)) @ Matrix.Scale(vec[1], 4, (0.0, 1.0, 0.0)) @ Matrix.Scale(vec[2], 4, (0.0, 0.0, 1.0))

class Panel(OriginalPanel):
    bl_category = 'UE4Workspace'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.mode == 'OBJECT')

class ExperimentalPanel(OriginalPanel):
    bl_category = 'UE4Workspace'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        preferences = context.preferences.addons['UE4Workspace'].preferences
        misc = preferences.misc
        return (context.mode == 'OBJECT' and misc.experimental_features)

class ObjectPanel(OriginalPanel):
    bl_category = 'UE4Workspace'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

class ObjectSubPanel(Panel):
    bl_parent_id = 'UE4WORKSPACE_PT_ObjectPanel'

class ExportOptionPanel(Panel):

    def draw_property(self, data, properties):
        layout = self.layout

        for tab, data_properties in properties.items():
            layout.prop(data, tab, icon=('TRIA_DOWN' if getattr(data, tab, False) else 'TRIA_RIGHT'), emboss=False)
            if getattr(data, tab, False):
                box = layout.box()

                for label_str, property_str in data_properties:
                    row = box.row()
                    split = row.split(factor=0.6)
                    col = split.column()
                    col.alignment = 'RIGHT'
                    col.label(text=label_str)
                    col = split.column()
                    if property_str == 'frame_import_range':
                        col.enabled = data.animation_length == 'FBXALIT_SET_RANGE'
                        col.prop(data, property_str, text='Min', index=0)
                        col.prop(data, property_str, text='Max', index=1)
                    elif property_str == 'material_curve_suffixes':
                        material_curve_suffixes = getattr(data, property_str, '').split('|') if bool(getattr(data, property_str, '')) else []

                        row = col.row(align=True)
                        row.label(text=str(len(material_curve_suffixes)) + ' Array' if bool(material_curve_suffixes) else '0 Array')

                        row.operator('ue4workspace.add_material_curve_suffix',icon='PLUS', text='')
                        row.operator('ue4workspace.clear_material_curve_suffix',icon='TRASH', text='')

                        if bool(material_curve_suffixes):
                            for index, surffix in enumerate(material_curve_suffixes):
                                row = box.row()
                                split = row.split(factor=0.6)
                                col = split.column()
                                col.alignment = 'RIGHT'
                                col.label(text=str(index))
                                row = split.row(align=True)
                                row.label(text=surffix)
                                op = row.operator('ue4workspace.edit_material_curve_suffix',icon='GREASEPENCIL', text='')
                                op.index = index
                                op.val = surffix
                                row.operator('ue4workspace.remove_material_curve_suffix_index',icon='TRASH', text='').index = index
                    else:
                        col.prop(data, property_str, text='')

class ExportOperator(OriginalOperator):

    ext_file = ''
    collections_dict = {}
    temp_attach_mute_state = False
    temp_custom_collision = []
    temp_socket = []
    temp_lod = []
    temp_main_lod_matrix_and_parent = None
    temp_skeletal_meshes = []
    temp_hair_particle = []

    @classmethod
    def description(cls, context, properties):
        preferences = context.preferences.addons['UE4Workspace'].preferences
        description = ''

        if preferences.export.type in ['FILE', 'BOTH']:
            return '' if bool(preferences.export.export_folder.strip()) else 'File folder not valid'
        return '' if bool(preferences.export.temp_folder.strip()) else 'Temporary folder not valid'

    @classmethod
    def poll(cls, context):
        preferences = context.preferences.addons['UE4Workspace'].preferences

        if preferences.export.type in ['FILE', 'BOTH']:
            return bool(preferences.export.export_folder.strip()) and context.mode == 'OBJECT'
        return bool(preferences.export.temp_folder.strip()) and context.mode == 'OBJECT'

    def safe_string_path(self, string):
        return re.sub("[\\/:<>\'\"|?*&]", '', string).strip()

    def create_string_directory(self, root, subfolder):
        subfolder_safe_string = self.safe_string_path(subfolder)
        return os.path.join(root, subfolder_safe_string)

    def create_directory_if_not_exist(self, directory, subfolder):
        if not os.path.isdir(directory) and subfolder:
            os.mkdir(directory)

    def is_file_exist(self, *args):
        return os.path.isfile(os.path.join(*args))

    def unhide_collection(self, *args):
        self.collections_dict = {}
        for collection, state in args:
            collection_data = bpy.data.collections.get(collection, False)
            self.collections_dict[collection] = {
                'render': None,
                'select': None,
                'viewport': None
            }
            if collection_data and state:
                for key in self.collections_dict[collection]:
                    self.collections_dict[collection][key] = getattr(collection_data, 'hide_' + key)
                    setattr(collection_data, 'hide_' + key, False)

    def restore_collection(self, *args):
        for collection, state in args:
            collection_data = bpy.data.collections.get(collection, False)
            if collection_data and state:
                for key, val in self.collections_dict[collection].items():
                    setattr(collection_data, 'hide_' + key, val)
        self.collections_dict = {}

    def unreal_engine_exec_script(self, script='ImportStaticMesh.py', unreal_engine_import_setting={}):
        preferences = bpy.context.preferences.addons['UE4Workspace'].preferences
        if preferences.export.type in ['UNREAL', 'BOTH'] and remote.remote_nodes:
            unreal_engine_import_setting_path = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'temp', 'unreal_engine_import_setting.json')).replace(os.sep, '/')

            file = open(unreal_engine_import_setting_path, 'w+')
            file.write(json.dumps(unreal_engine_import_setting, indent=4))
            file.close()

            remote.exec_script(script)
    
    def prepare_custom_collision(self, obj):
        self.temp_custom_collision = []
        base_collision_name = 'UCX_' + obj.name + '_'
        collision_collection = bpy.data.collections.get('UE4CustomCollision', False)
        if collision_collection:
            for index, collision_object in enumerate([collision_object for collision_object in collision_collection.objects if collision_object.parent is obj and collision_object.type == 'MESH' and collision_object.data.is_custom_collision], start=1):
                self.temp_custom_collision.append((collision_object, collision_object.name, collision_object.hide_get(), collision_object.hide_select, collision_object.hide_viewport))

                collision_object.hide_set(False)
                collision_object.hide_select = False
                collision_object.hide_viewport = False
                collision_object.select_set(state=True)

                collision_object.name = base_collision_name + ('0' if index <= 9 else '') + str(index)

    def restore_custom_collision(self):
        for collision_object, original_name, hide, hide_select, hide_viewport in self.temp_custom_collision:
            collision_object.hide_set(hide)
            collision_object.hide_select = hide_select
            collision_object.hide_viewport = hide_viewport
            collision_object.select_set(state=False)

            collision_object.name = original_name

        self.temp_custom_collision = []

    def prepare_socket(self, obj):
        self.temp_socket = []
        socket_collection = bpy.data.collections.get('UE4Socket', False)
        if socket_collection:
            for socket_object in [socket_object for socket_object in socket_collection.objects if socket_object.parent is obj and socket_object.type == 'EMPTY' and socket_object.is_socket]:
                self.temp_socket.append((socket_object, socket_object.hide_get(), socket_object.hide_select, socket_object.hide_viewport))

                socket_object.hide_set(False)
                socket_object.hide_select = False
                socket_object.hide_viewport = False
                socket_object.select_set(state=True)

                socket_object.scale /= 100

                socket_object.rotation_euler.x += math.radians(90)

                socket_object.name = 'SOCKET_' + socket_object.name

    def restore_socket(self):
        for socket_object, hide, hide_select, hide_viewport in self.temp_socket:
            socket_object.hide_set(hide)
            socket_object.hide_select = hide_select
            socket_object.hide_viewport = hide_viewport
            socket_object.select_set(state=False)

            socket_object.scale *= 100
            socket_object.rotation_euler.x -= math.radians(90)

            socket_object.name = socket_object.name[7:]

        self.temp_socket = []

    def prepare_lod(self, obj):
        self.temp_lod = []
        lods_data = [(lod.obj, lod.screen_size) for lod in obj.data.lods if lod.obj is not None]
        if bool(lods_data):
            lod_parent = bpy.data.objects.new('LOD_' + obj.name, None)

            for collection in obj.users_collection:
                collection.objects.link(lod_parent)

            lod_parent.matrix_world.translation = obj.matrix_world.copy().translation
            lod_parent.empty_display_size = 2
            lod_parent.empty_display_type = 'ARROWS'
            lod_parent['fbx_type'] = 'LodGroup'
            lod_parent.select_set(state=True)

            self.temp_main_lod_matrix_and_parent = (lod_parent, obj, obj.matrix_world.copy(), obj.parent)

            obj.parent = lod_parent

            obj.matrix_parent_inverse = lod_parent.matrix_world.inverted()

            bpy.context.view_layer.update()

            for lod_obj, screen_size in lods_data:
                lod_obj_copy = lod_obj.copy()
                lod_obj_copy.parent = lod_parent
                lod_obj_copy.matrix_world = obj.matrix_world.copy()

                for collection in lod_obj.users_collection:
                    collection.objects.link(lod_obj_copy)

                lod_obj_copy.hide_set(False)
                lod_obj_copy.hide_select = False
                lod_obj_copy.hide_viewport = False
                lod_obj_copy.select_set(state=True)

                self.temp_lod.append(lod_obj_copy)

    def restore_lod(self):
        if bool(self.temp_lod):
            lod_parent, obj, obj_matrix_world, obj_original_parent = self.temp_main_lod_matrix_and_parent

            obj.parent = obj_original_parent
            obj.matrix_world = obj_matrix_world

            for lod_obj_copy in self.temp_lod:
                bpy.data.objects.remove(lod_obj_copy)

            bpy.data.objects.remove(lod_parent)
        self.temp_lod = []
        self.temp_main_lod_matrix_and_parent = None

    def mute_attach_constraint(self, obj):
        constraint = obj.constraints.get('attach_to')
        if constraint:
            self.temp_attach_mute_state = constraint.mute
            constraint.mute = True

    def unmute_attach_constraint(self, obj):
        constraint = obj.constraints.get('attach_to')
        if constraint:
            constraint.mute = self.temp_attach_mute_state

    def prepare_skeletal_meshes(self, obj):
        self.temp_skeletal_meshes = []
        meshes = [children_obj for children_obj in obj.children if children_obj.type == 'MESH' and children_obj.data.is_export_skeletal_mesh_part]
        if bool(meshes):
            for skeletal_mesh_object in meshes:
                self.temp_skeletal_meshes.append((skeletal_mesh_object, skeletal_mesh_object.hide_get(), skeletal_mesh_object.hide_select, skeletal_mesh_object.hide_viewport))

                skeletal_mesh_object.hide_set(False)
                skeletal_mesh_object.hide_select = False
                skeletal_mesh_object.hide_viewport = False
                skeletal_mesh_object.select_set(state=True)

    def restore_skeletal_meshes(self, obj):
        for skeletal_mesh_object, hide, hide_select, hide_viewport in self.temp_skeletal_meshes:

            skeletal_mesh_object.hide_set(hide)
            skeletal_mesh_object.hide_select = hide_select
            skeletal_mesh_object.hide_viewport = hide_viewport
            skeletal_mesh_object.select_set(state=False)

        self.temp_skeletal_meshes = []

    def prepare_groom(self, obj):
        self.temp_hair_particle = [obj.show_instancer_for_render, obj.show_instancer_for_viewport]
        obj.show_instancer_for_render, obj.show_instancer_for_viewport = [False, True]

    def restore_groom(self, obj):
        obj.show_instancer_for_render, obj.show_instancer_for_viewport = self.temp_hair_particle
        self.temp_hair_particle = []