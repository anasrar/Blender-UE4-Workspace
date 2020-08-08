import os
import json
import bpy
from mathutils import Matrix
from bpy.props import (EnumProperty, IntProperty, StringProperty, BoolProperty, PointerProperty, CollectionProperty)
from bpy.types import (Panel, Operator, PropertyGroup, UIList)

# PROPERTY GROUP

class IMPORTASSETS_Struct(PropertyGroup):
    name: StringProperty(default="asset")
    path: StringProperty(default="path")
    isImport: BoolProperty(default=False)

# group export

Groups = [
    IMPORTASSETS_Struct
]

# PROPS

Props = [
    {
        "type": "scene",
        "name": "ImportAssetsTab",
        "value": EnumProperty(
            name="Preferences Tab",
            items=[
                ("MESH", "Mesh", "Static Mesh Tab"),
                ("CHARACTER", "Character", "Skeletal Mesh Tab"),
                ("ANIMATION", "Animation", "Animation Tab")
                ],
            default="MESH"
        ),
        "resetVariable": True
    },
    {
        "type": "scene",
        "name": "ImportAssetsMeshCollections",
        "value": CollectionProperty(type=IMPORTASSETS_Struct),
        "resetVariable": True
    },
    {
        "type": "scene",
        "name": "indexAssetsMesh",
        "value": IntProperty(default=-1),
        "resetVariable": True
    },
    {
        "type": "scene",
        "name": "ImportAssetsCharacterCollections",
        "value": CollectionProperty(type=IMPORTASSETS_Struct),
        "resetVariable": True
    },
    {
        "type": "scene",
        "name": "indexAssetsCharacter",
        "value": IntProperty(default=-1),
        "resetVariable": True
    },
    {
        "type": "scene",
        "name": "ImportAssetsAnimationCollections",
        "value": CollectionProperty(type=IMPORTASSETS_Struct),
        "resetVariable": True
    },
    {
        "type": "scene",
        "name": "indexAssetsAnimation",
        "value": IntProperty(default=-1),
        "resetVariable": True
    }
]

# PANEL

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_ExportOptionImportAssetsPanel"
    bl_parent_id = "UE4WORKSPACE_PT_ExportOptionPanel"
    bl_label = "Import Assets"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    remote = None

    @classmethod
    def poll(self, context):
        preferences = context.preferences.addons[__package__].preferences
        return preferences.exportOption in ["BOTH", "UNREAL"]

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object

        row = layout.row()
        row.scale_y = 1.25
        row.operator("ue4workspace.updateassetslist", icon="FILE_REFRESH", text="Update Assets List")

        row = layout.row()
        row.scale_y = 1.25
        row.prop(context.scene, "ImportAssetsTab", expand=True)

        layout.template_list("IMPORTASSETS_UL_AssetsList", "", context.scene, "ImportAssets" + context.scene.ImportAssetsTab.capitalize() + "Collections", context.scene, "indexAssets" + context.scene.ImportAssetsTab.capitalize(), rows=4)

        row = layout.row(align=True)
        row.scale_y = 1.25
        row.operator("ue4workspace.selectimportasset", text="SELECT").type = "SELECT"
        row.operator("ue4workspace.selectimportasset", text="DESELECT").type = "DESELECT"
        row.operator("ue4workspace.selectimportasset", text="INVERT").type = "INVERT"

        row = layout.row()
        row.scale_y = 1.5
        row.operator("ue4workspace.importassets", icon="IMPORT", text="Import Assets")

# UIList

class IMPORTASSETS_UL_AssetsList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.name)
        row.prop(item, "isImport", text="")

# OPERATOR

class OP_UpdateAssetsList(Operator):
    bl_idname = "ue4workspace.updateassetslist"
    bl_label = "Update Assets List"
    bl_description = "Update Assets List From Unreal Engine Project"
    bl_options = {"UNDO"}

    remote = None

    @classmethod
    def poll(self, context):
        preferences = context.preferences.addons[__package__].preferences
        return preferences.exportOption in ["BOTH", "UNREAL"] and self.remote.remote_nodes

    def execute(self, context):
        collection = {
            "MESH": context.scene.ImportAssetsMeshCollections,
            "ARMATURE": context.scene.ImportAssetsCharacterCollections,
            "ACTION": context.scene.ImportAssetsAnimationCollections
        }
        # clear all assets
        for coll in list(collection.values()):
            coll.clear()
        AssetsList = []

        for node_id in [user["node_id"] for user in self.remote.remote_nodes]:
            self.remote.open_command_connection(node_id)
            # output = self.remote.run_command(os.path.join(os.path.dirname(os.path.realpath(__file__)), "PyScript", "GetAllImportableAssets.py"), exec_mode="ExecuteFile")
            # Fix Python PATH Script Issue #9
            output = self.remote.run_command("execfile(\"" + os.path.join(os.path.dirname(os.path.realpath(__file__)), "PyScript", "GetAllImportableAssets.py").replace(os.sep, "/") +"\")", exec_mode="ExecuteStatement")
            self.remote.close_command_connection()
            AssetsList += json.loads(output["output"][0]["output"])

        # add asset
        for path, name, typeAsset in [tuple(asset) for asset in AssetsList]:
            assetStruct = collection[typeAsset].add()
            assetStruct.name = name
            assetStruct.path = path

        try:
            bpy.ops.ue4workspace.popup("INVOKE_DEFAULT", msg="Update Assets List Success")
        except Exception: 
            pass

        return {"FINISHED"}

class OP_SelectImportAsset(Operator):
    bl_idname = "ue4workspace.selectimportasset"
    bl_label = "Select Asset To Import"
    bl_description = "Select Asset To Import"
    bl_options = {"UNDO"}

    type: bpy.props.StringProperty(default="")

    @classmethod
    def poll(self, context):
        return True

    def execute(self, context):
        collection = {
            "MESH": context.scene.ImportAssetsMeshCollections,
            "CHARACTER": context.scene.ImportAssetsCharacterCollections,
            "ANIMATION": context.scene.ImportAssetsAnimationCollections
        }
        if self.type:
            for assetStruct in collection[context.scene.ImportAssetsTab]:
                assetStruct.isImport = {"SELECT": True, "DESELECT": False, "INVERT": not assetStruct.isImport}[self.type]
        return {"FINISHED"}

class OP_ImportAssets(Operator):
    bl_idname = "ue4workspace.importassets"
    bl_label = "Import Assets"
    bl_description = "Import Assets From Unreal Engine Project"
    bl_options = {"UNDO"}

    remote = None

    @classmethod
    def poll(self, context):
        preferences = context.preferences.addons[__package__].preferences
        if preferences.exportOption in ["FBX", "BOTH"] and context.mode == "OBJECT":
            return bool(preferences.ExportFBXFolder.strip()) and self.remote.remote_nodes
        return bool(preferences.TempFolder.strip()) and self.remote.remote_nodes

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        collection = {
            "MESH": context.scene.ImportAssetsMeshCollections,
            "CHARACTER": context.scene.ImportAssetsCharacterCollections,
            "ANIMATION": context.scene.ImportAssetsAnimationCollections
        }[context.scene.ImportAssetsTab]

        unrealsetting = {
            "folder": preferences.ExportFBXFolder.strip() if preferences.exportOption in ["FBX", "BOTH"] else preferences.TempFolder.strip(),
            "assets": [[asset.name, asset.path] for asset in collection if asset.isImport],
            "setting": {
                "fbx_export_compatibility": preferences.IMPORTASSETS_FBXExportCompatibility,
                "ascii": preferences.IMPORTASSETS_ASCII,
                "force_front_x_axis": preferences.IMPORTASSETS_ForceFrontXAxis,
                "vertex_color": preferences.IMPORTASSETS_VertexColor,
                "level_of_detail": preferences.IMPORTASSETS_LevelOfDetail,
                "collision": preferences.IMPORTASSETS_Collision,
                "export_morph_targets": preferences.IMPORTASSETS_ExportMorphTargets,
                "export_preview_mesh": preferences.IMPORTASSETS_ExportPreviewMesh,
                "map_skeletal_motion_to_root": preferences.IMPORTASSETS_MapSkeletalMotionToRoot,
                "export_local_time": preferences.IMPORTASSETS_ExportLocalTime
            }
        }

        # Save unreal engine export option into a file json
        file = open(os.path.join(os.path.dirname(__file__), "Data", "importAssets.json"), "w+")
        file.write(json.dumps(unrealsetting))
        file.close()

        arrFBXPath = []

        for node_id in [user["node_id"] for user in self.remote.remote_nodes]:
            self.remote.open_command_connection(node_id)
            # output = self.remote.run_command(os.path.join(os.path.dirname(os.path.realpath(__file__)), "PyScript", "ImportAssets.py"), exec_mode="ExecuteFile")
            # Fix Python PATH Script Issue #9
            output = self.remote.run_command("execfile(\"" + os.path.join(os.path.dirname(os.path.realpath(__file__)), "PyScript", "ImportAssets.py").replace(os.sep, "/") +"\")", exec_mode="ExecuteStatement")
            self.remote.close_command_connection()
            arrFBXPath += json.loads(output["output"][0]["output"])

        oldMode = context.mode
        if oldMode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        for filePath, fbxType in [tuple(arr) for arr in arrFBXPath]:
            filePath += ".fbx"
            if os.path.isfile(filePath):
                bpy.ops.object.select_all(action="DESELECT")
                bpy.ops.import_scene.fbx(
                    filepath=filePath,
                    directory="",
                    filter_glob="*.fbx",
                    ui_tab="MAIN",
                    use_manual_orientation=preferences.IMPORTASSETS_FBXManualOrientation,
                    global_scale=preferences.IMPORTASSETS_FBXScale,
                    bake_space_transform=preferences.IMPORTASSETS_FBXApplyTransform,
                    use_custom_normals=preferences.IMPORTASSETS_FBXCustomNormals,
                    use_image_search=preferences.IMPORTASSETS_FBXImageSearch,
                    use_alpha_decals=False,
                    decal_offset=preferences.IMPORTASSETS_FBXDecalOffset,
                    use_anim=preferences.IMPORTASSETS_FBXImportAnimation,
                    anim_offset=preferences.IMPORTASSETS_FBXAnimationOffset,
                    use_subsurf=preferences.IMPORTASSETS_FBXSubdivisionData,
                    use_custom_props=preferences.IMPORTASSETS_FBXCustomProperties,
                    use_custom_props_enum_as_string=preferences.IMPORTASSETS_FBXImportEnums,
                    ignore_leaf_bones=preferences.IMPORTASSETS_FBXIgnoreLeafBones,
                    force_connect_children=preferences.IMPORTASSETS_FBXForceConnectChildren,
                    automatic_bone_orientation=preferences.IMPORTASSETS_FBXAutomaticBoneOrientation,
                    primary_bone_axis=preferences.IMPORTASSETS_FBXPrimaryBoneAxis,
                    secondary_bone_axis=preferences.IMPORTASSETS_FBXSecondaryBoneAxis,
                    use_prepost_rot=preferences.IMPORTASSETS_FBXUsePrePostRotation,
                    axis_forward=preferences.IMPORTASSETS_FBXAxisForward,
                    axis_up=preferences.IMPORTASSETS_FBXAxisUp
                )
                selectedObjects = context.selected_objects
                if fbxType == "MESH":
                    # set custom collision
                    if preferences.IMPORTASSETS_Collision and len(selectedObjects) > 1:
                        mainObj = selectedObjects[0]
                        context.view_layer.objects.active = mainObj
                        for collisionObj in [obj for obj in selectedObjects if obj.name.startswith("UCX_")]:
                            context.scene.SM_CollsionPicker= collisionObj
                            bpy.ops.ue4workspace.smcollisionpicker()
                elif fbxType == "ARMATURE":
                    emptyObj = next(iter([obj for obj in selectedObjects if obj.type == "EMPTY"]))
                    # scale object
                    for child in emptyObj.children:
                        child.scale = child.scale / 100.0
                        child.parent = None
                        child.location = [0, 0, 0]
                    bpy.data.objects.remove(emptyObj, do_unlink=True)
                elif fbxType == "ACTION":
                    # rename action
                    mainObj = next(iter([obj for obj in selectedObjects if obj.type == "ARMATURE"]))
                    action = mainObj.animation_data.action
                    action.name = os.path.splitext(os.path.basename(filePath))[0]
                    bpy.ops.object.delete(use_global=False)
                os.remove(filePath)

        bpy.ops.object.select_all(action="DESELECT")
        if oldMode != "OBJECT":
            bpy.ops.object.mode_set(mode=oldMode)

        try:
            bpy.ops.ue4workspace.popup("INVOKE_DEFAULT", msg="Import Assets Success")
        except Exception: 
            pass

        return {"FINISHED"}

# operator export

Ops = [
    OP_UpdateAssetsList,
    OP_SelectImportAsset,
    OP_ImportAssets
]