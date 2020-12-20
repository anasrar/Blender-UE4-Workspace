import os
import json
import bpy
from mathutils import Vector
from bpy.utils import register_class, unregister_class
from bpy.types import Panel, Operator, PropertyGroup,UIList
from .. utils.base import ExportOptionPanel
from .. utils.connect import remote

class PG_ImportAsset(PropertyGroup):
    name: bpy.props.StringProperty(default='asset')
    path: bpy.props.StringProperty(default='path')
    is_import: bpy.props.BoolProperty(default=False)
    node_id: bpy.props.StringProperty(default=':)')

class IMPORTASSET_UL_AssetList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.name)
        row.prop(item, 'is_import', text='')

class OP_UpdateAssetList(Operator):
    bl_idname = 'ue4workspace.update_asset_list'
    bl_label = 'Update Asset List'
    bl_description = 'Update Asset List From Unreal Engine Project'
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        preferences = context.preferences.addons['UE4Workspace'].preferences
        return preferences.export.type in ['BOTH', 'UNREAL'] and bool(remote.remote_nodes)

    def execute(self, context):
        collections = {
            'StaticMesh': context.scene.import_asset_static_mesh,
            'SkeletalMesh': context.scene.import_asset_skeletal_mesh,
            'AnimSequence': context.scene.import_asset_animation
        }

        reset_import_asset_list = open(os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'temp', 'import_asset_list.json')), 'w+')
        reset_import_asset_list.write(json.dumps([]))
        reset_import_asset_list.close()

        remote.exec_script('GetAllImportableAsset.py')

        load_import_asset_list = open(os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'temp', 'import_asset_list.json')), 'r')
        asset_list = json.loads(load_import_asset_list.read())
        load_import_asset_list.close()

        for collection in collections.values():
            collection.clear()

        context.scene.index_static_mesh = -1
        context.scene.index_skeletal_mesh = -1
        context.scene.index_animation = -1

        for node_id, object_path, asset_name, asset_class in asset_list:
            collection = collections[asset_class]
            asset = collection.add()
            asset.node_id = node_id
            asset.path = object_path
            asset.name = asset_name

        self.report({'INFO'}, 'Update asset list success')

        return {'FINISHED'}

class OP_SelectImportAsset(Operator):
    bl_idname = 'ue4workspace.select_import_asset'
    bl_label = 'Select Asset To Import'
    bl_description = 'Select Asset To Import'
    bl_options = {'UNDO'}

    type: bpy.props.StringProperty(default='')

    def execute(self, context):
        collections = {
            'STATIC_MESH': context.scene.import_asset_static_mesh,
            'SKELETAL_MESH': context.scene.import_asset_skeletal_mesh,
            'ANIMATION': context.scene.import_asset_animation
        }
        if self.type:
            for collection in collections[context.scene.import_asset_tab]:
                collection.is_import = {'SELECT': True, 'DESELECT': False, 'INVERT': not collection.is_import}[self.type]
        return {'FINISHED'}

class OP_ImportAsset(Operator):
    bl_idname = 'ue4workspace.import_asset'
    bl_label = 'Import Asset'
    bl_description = 'Import Asset From Unreal Engine Project'
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        preferences = context.preferences.addons['UE4Workspace'].preferences
        if preferences.export.type in ['FILE', 'BOTH'] and context.mode == 'OBJECT':
            return bool(preferences.export.export_folder.strip()) and bool(remote.remote_nodes)
        return bool(preferences.export.temp_folder.strip()) and bool(remote.remote_nodes)

    def execute(self, context):
        preferences = context.preferences.addons['UE4Workspace'].preferences
        import_asset = preferences.import_asset
        fbx_setting = import_asset.fbx
        unreal_engine_setting = import_asset.unreal_engine

        collection = {
            'STATIC_MESH': context.scene.import_asset_static_mesh,
            'SKELETAL_MESH': context.scene.import_asset_skeletal_mesh,
            'ANIMATION': context.scene.import_asset_animation
        }[context.scene.import_asset_tab]

        assets = [(asset.node_id, asset.path, index) for index, asset in enumerate([x for x in collection if x.is_import])]

        unreal_engine_export_setting = {
            'path': preferences.export.export_folder if preferences.export.type in ['FILE', 'BOTH'] else preferences.export.temp_folder,
            'files': assets,
        }

        unreal_engine_export_setting.update(unreal_engine_setting.to_dict())

        import_asset_setting = open(os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'temp', 'import_asset_setting.json')), 'w+')
        import_asset_setting.write(json.dumps(unreal_engine_export_setting, indent=4))
        import_asset_setting.close()

        reset_imported_asset_list = open(os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'temp', 'imported_asset_list.json')), 'w+')
        reset_imported_asset_list.write(json.dumps([]))
        reset_imported_asset_list.close()

        remote.exec_script('ExportAsset.py')

        load_imported_asset_list = open(os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'temp', 'imported_asset_list.json')), 'r')
        imported_asset_list = json.loads(load_imported_asset_list.read())
        load_imported_asset_list.close()

        for asset_path, asset_type, asset_name in imported_asset_list:
            if os.path.isfile(asset_path):
                bpy.ops.object.select_all(action='DESELECT')
                import_fbx_setting = {
                    'filepath': asset_path,
                    'directory': '',
                    'filter_glob': '*.fbx',
                    'ui_tab': 'MAIN'
                }
                import_fbx_setting.update(fbx_setting.to_dict())

                bpy.ops.import_scene.fbx(**import_fbx_setting)

                selected_objects = context.selected_objects

                if asset_type == 'StaticMesh':
                    collision_objects = [obj for obj in selected_objects if obj.name.startswith('UCX_')]
                    if unreal_engine_setting.collision and bool(collision_objects):
                        for collision_object in collision_objects:
                            main_object = bpy.data.objects.get(collision_object.name[4:])
                            if main_object and main_object.type == 'MESH':
                                context.view_layer.objects.active = main_object
                                context.scene.collision_picker = collision_object
                                bpy.ops.ue4workspace.collision_picker()

                    main_lod_object = next(iter([obj for obj in selected_objects if obj.name.endswith('_LOD0')]), None)
                    if unreal_engine_setting.level_of_detail and bool(main_lod_object):
                        main_lod_object_matrix_world = main_lod_object.matrix_world.copy()
                        main_lod_object_world_location = main_lod_object_matrix_world.to_translation()

                        lod_objects = [obj for obj in selected_objects if obj.type == 'MESH' and obj.name.startswith(main_lod_object.name[:-5]) and obj != main_lod_object]
                        for index, lod_object in enumerate(lod_objects, start=1):
                            lod_object.matrix_world.translation = main_lod_object_world_location + ((main_lod_object.dimensions * Vector((1.0, 0.0, 0.0))) * index) + (Vector((1.0, 0.0, 0.0)) * index)

                            lod_object_matrix_world = lod_object.matrix_world.copy()
                            lod_object.data.mesh_as_lod = True
                            lod_object.parent = main_lod_object
                            lod_object.matrix_world = lod_object_matrix_world

                            lod_data = main_lod_object.data.lods.add()
                            lod_data.obj = lod_object

                        empty_parent = main_lod_object.parent
                        main_lod_object.parent = None
                        main_lod_object.matrix_world = main_lod_object_matrix_world

                        bpy.data.objects.remove(empty_parent)

                elif asset_type == 'SkeletalMesh':
                    main_object = next(iter([obj for obj in selected_objects if obj.type == 'ARMATURE']), None)
                    if main_object is not None:
                        main_object_matrix_world = main_object.matrix_world.copy()
                        empty_parent = main_object.parent

                        main_object.parent = None
                        main_object.matrix_world = main_object_matrix_world

                        lod_group_empty = next(iter([obj for obj in selected_objects if obj.type == 'EMPTY' and obj.name.endswith('_LodGroup')]), None)
                        if unreal_engine_setting.level_of_detail and bool(lod_group_empty):
                            bpy.data.objects.remove(lod_group_empty)

                        bpy.data.objects.remove(empty_parent)

                elif asset_type == 'AnimSequence':
                    main_object = next(iter([obj for obj in selected_objects if obj.type == 'ARMATURE']), None)
                    if main_object is not None:
                        action = main_object.animation_data.action
                        action.name = asset_name
                        action.use_fake_user = True

                        for obj in selected_objects:
                            bpy.data.objects.remove(obj)

                os.remove(asset_path)

        bpy.ops.object.select_all(action='DESELECT')

        self.report({'INFO'}, 'Import asset success')

        return {'FINISHED'}

class PANEL(Panel):
    bl_idname = 'UE4WORKSPACE_PT_ImportAssetPanel'
    bl_label = 'Import Asset'
    bl_category = 'UE4Workspace'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        preferences = context.preferences.addons['UE4Workspace'].preferences
        return preferences.export.type in ['BOTH', 'UNREAL'] and context.mode == 'OBJECT'

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons['UE4Workspace'].preferences

        row = layout.row()
        row.scale_y = 1.5
        row.operator('ue4workspace.update_asset_list', icon='FILE_REFRESH', text='Update Asset List')

        row = layout.row()
        row.scale_y = 1.5
        row.prop(context.scene, 'import_asset_tab', expand=True)

        layout.template_list('IMPORTASSET_UL_AssetList', '', context.scene, {
            'STATIC_MESH': 'import_asset_static_mesh',
            'SKELETAL_MESH': 'import_asset_skeletal_mesh',
            'ANIMATION': 'import_asset_animation'
        }[context.scene.import_asset_tab], context.scene, {
            'STATIC_MESH': 'index_static_mesh',
            'SKELETAL_MESH': 'index_skeletal_mesh',
            'ANIMATION': 'index_animation'
        }[context.scene.import_asset_tab], rows=4)

        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator('ue4workspace.select_import_asset', text='SELECT').type = 'SELECT'
        row.operator('ue4workspace.select_import_asset', text='DESELECT').type = 'DESELECT'
        row.operator('ue4workspace.select_import_asset', text='INVERT').type = 'INVERT'

        row = layout.row()
        row.scale_y = 1.5
        row.operator('ue4workspace.import_asset', icon='IMPORT')

class BaseSubPanel(ExportOptionPanel):
    bl_parent_id = 'UE4WORKSPACE_PT_ImportAssetPanel'
    bl_category = 'UE4Workspace'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}

class SUB_PANEL_1(BaseSubPanel):
    bl_idname = 'UE4WORKSPACE_PT_ImportAssetFBXOptionPanel'
    bl_label = 'FBX Import Setting'

    def draw(self, context):
        preferences = context.preferences.addons['UE4Workspace'].preferences
        fbx_setting = preferences.import_asset.fbx
        self.draw_property(fbx_setting, {
            'tab_include': [
                ('Custom Normals', 'use_custom_normals'),
                ('Subdivision Data', 'use_subsurf'),
                ('Custom Properties', 'use_custom_props'),
                ('Import Enums As Strings', 'use_custom_props_enum_as_string'),
                ('Image Search', 'use_image_search'),
            ],
            'tab_transform': [
                ('Scale', 'global_scale'),
                ('Decal Offset', 'decal_offset'),
                ('Apply Transform', 'bake_space_transform'),
                ('Use Pre/Post Rotation', 'use_prepost_rot'),
            ],
            'tab_orientation': [
                ('Manual Orientation', 'use_manual_orientation'),
                ('Forward', 'axis_forward'),
                ('Up', 'axis_up'),
            ],
            'tab_animation': [
                ('Import Animation', 'use_anim'),
                ('Animation Offset', 'anim_offset'),
            ],
            'tab_armature': [
                ('Ignore Leaf Bones', 'ignore_leaf_bones'),
                ('Force Connect Children', 'force_connect_children'),
                ('Automatic Bone Orientation', 'automatic_bone_orientation'),
                ('Primary Bone Axis', 'primary_bone_axis'),
                ('Secondary Bone Axis', 'secondary_bone_axis'),
            ],
        })

class SUB_PANEL_2(BaseSubPanel):
    bl_idname = 'UE4WORKSPACE_PT_ImportAssetUnrealEnginePanel'
    bl_label = 'Unreal Engine Import Setting'

    def draw(self, context):
        preferences = context.preferences.addons['UE4Workspace'].preferences
        unreal_engine_setting = preferences.import_asset.unreal_engine
        self.draw_property(unreal_engine_setting, {
            'tab_exporter': [
                ('FBX Export Compatibility', 'fbx_export_compatibility'),
                ('ASCII', 'ascii'),
                ('Force Front X Axis', 'force_front_x_axis'),
            ],
            'tab_mesh': [
                ('Vertex Color', 'vertex_color'),
                ('Level Of Detail', 'level_of_detail'),
            ],
            'tab_static_mesh': [
                ('Collision', 'collision'),
            ],
            'tab_skeletal_mesh': [
                ('Export Morph Targets', 'export_morph_targets'),
            ],
            'tab_animation': [
                ('Export Preview Mesh', 'export_preview_mesh'),
                ('Map Skeletal Motion To Root', 'map_skeletal_motion_to_root'),
                ('Export Local Time', 'export_local_time'),
            ],
        })

list_class_to_register = [
    PG_ImportAsset,
    IMPORTASSET_UL_AssetList,
    OP_UpdateAssetList,
    OP_SelectImportAsset,
    OP_ImportAsset,
    PANEL,
    SUB_PANEL_1,
    SUB_PANEL_2
]

def register():

    bpy.types.Scene.import_asset_tab = bpy.props.EnumProperty(
        name='Import Asset Tab',
        items=[
            ('STATIC_MESH', 'Static Mesh', 'Static Mesh Tab'),
            ('SKELETAL_MESH', 'Skeletal Mesh', 'Skeletal Mesh Tab'),
            ('ANIMATION', 'Animation', 'Animation Tab')
            ],
        default='STATIC_MESH'
    )

    bpy.types.Scene.index_static_mesh = bpy.props.IntProperty(default=-1)
    bpy.types.Scene.index_skeletal_mesh = bpy.props.IntProperty(default=-1)
    bpy.types.Scene.index_animation = bpy.props.IntProperty(default=-1)

    for x in list_class_to_register:
        register_class(x)

    bpy.types.Scene.import_asset_static_mesh = bpy.props.CollectionProperty(type=PG_ImportAsset)
    bpy.types.Scene.import_asset_skeletal_mesh = bpy.props.CollectionProperty(type=PG_ImportAsset)
    bpy.types.Scene.import_asset_animation = bpy.props.CollectionProperty(type=PG_ImportAsset)

def unregister():
    del bpy.types.Scene.import_asset_tab

    del bpy.types.Scene.index_static_mesh
    del bpy.types.Scene.index_skeletal_mesh
    del bpy.types.Scene.index_animation

    del bpy.types.Scene.import_asset_static_mesh
    del bpy.types.Scene.import_asset_skeletal_mesh
    del bpy.types.Scene.import_asset_animation

    for x in list_class_to_register[::-1]:
        unregister_class(x)