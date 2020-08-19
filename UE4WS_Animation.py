import os
import json
import time
import re
import bpy
from bpy.types import (Panel, UIList, Operator)

# PROPS

Props = [
    {
        "type": "action",
        "name": "isExport",
        "value": bpy.props.BoolProperty(
            default=False
            ),
        "resetVariable": True
    },
    {
        "type": "object",
        "name": "ANIM_index_action",
        "value": bpy.props.IntProperty(
            default=-1
            ),
        "resetVariable": True
    }
]

# PANEL

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_AnimationPanel"
    bl_label = "Animation"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        return (context.mode == "OBJECT")

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons[__package__].preferences

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Subfolder")
        split = split.split()
        col = split.column()
        col.prop(preferences, "ANIM_Subfolder", text="")

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Overwrite File")
        split = split.split()
        col = split.column()
        col.prop(preferences, "ANIM_OverwriteFile", text="")

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Frame Rate")
        split = split.split()
        col = split.column()
        col.prop(context.scene.render, "fps", text="")

        if context.active_object is not None:
            row = layout.row()
            row.enabled = (context.active_object is not None and context.active_object.type == "ARMATURE")
            row.template_list("ANIM_UL_actionList", "", bpy.data, "actions", context.active_object, "ANIM_index_action")

            row = layout.row(align=True)
            row.scale_y = 1.5
            row.operator("ue4workspace.selectanimation", text="SELECT").type="SELECT"
            row.operator("ue4workspace.selectanimation", text="DESELECT").type="DESELECT"
            row.operator("ue4workspace.selectanimation", text="INVERT").type="INVERT"

        if preferences.exportOption in ["BOTH", "UNREAL"]:
            col = layout.column()
            row = col.row()
            split = row.split(factor=0.6)
            col = split.column()
            col.alignment = "RIGHT"
            col.label(text="Character Skeleton")
            split = split.split()
            col = split.column()
            col.prop(preferences, "ANIM_CharacterSkeleton", text="")

            row = layout.row()
            row.scale_y = 1.5
            # operator location on UE4WS_Character.py
            row.operator("ue4workspace.updateskeletonlist",icon="ARMATURE_DATA")

        row = layout.row()
        row.scale_y = 1.5
        row.operator("ue4workspace.exportanimation",icon="ARMATURE_DATA", text="Export")

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.prop(preferences, "ANIM_ExportProfile", text="")
        split = split.split()
        row = split.row(align=True)
        row.alignment = "RIGHT"
        row.operator("ue4workspace.animupdateexportprofile",icon="GREASEPENCIL", text="")
        row.operator("ue4workspace.animcreateexportprofile",icon="FILE_NEW", text="")
        row.operator("ue4workspace.animremoveexportprofile",icon="TRASH", text="")

# UIList

class ANIM_UL_actionList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if context.active_object is not None and context.active_object.type == "ARMATURE" and True:
            boneNames = [bone.name for bone in context.active_object.pose.bones]
            layout.prop(item, "name", text="", icon="ACTION", emboss=False)
            if (any(name in fcurve.data_path for fcurve in item.fcurves for name in boneNames)):
                layout.prop(item, "isExport", text="")

#  OPERATOR

class OP_ExportAnimation(Operator):
    bl_idname = "ue4workspace.exportanimation"
    bl_label = "Export Animation"
    bl_description = "Export Animation"
    bl_options = {"UNDO"}

    remote = None

    @classmethod
    def poll(self, context):
        preferences = context.preferences.addons[__package__].preferences
        # return preferences.exportOption in ["UNREAL", "BOTH"] and self.remote.remote_nodes
        if context.mode == "OBJECT" and context.active_object is not None and context.active_object.type == "ARMATURE":
            if preferences.exportOption == "UNREAL" and preferences.ANIM_CharacterSkeleton != "NONE":
                return bool(preferences.TempFolder.strip())
            elif preferences.exportOption == "BOTH" and preferences.ANIM_CharacterSkeleton != "NONE":
                return bool(preferences.ExportFBXFolder.strip())
            elif preferences.exportOption == "FBX":
                return bool(preferences.ExportFBXFolder.strip())
        return False

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        armature = context.active_object
        originalName = armature.name
        originalAction = armature.animation_data.action
        # Deselect all object
        bpy.ops.object.select_all(action="DESELECT")
        # select armature
        armature.select_set(state=True)
        # copy location
        originalLocation = armature.location.copy()
        # reset location
        armature.location = [0, 0, 0]
        # check root bone
        isHaveRootBone = armature.data.bones.get("root", False)
        if armature.get("UE4RIGGED"):
            # change name to "Armature" if armature is ue4 rigged
            armature.name = "Armature"
        else:
            # change name to "Armature" if have root bone or "root" if doesn't have root bone
            if isHaveRootBone:
                armature.name = "Armature"
            else:
                armature.name = "root"

        # pop "UE4RIGVERSION"
        # its because blender do not support array in custom property to export
        rigVersion = armature.pop("UE4RIGVERSION", None)

        # get bone name from armature
        boneNames = [bone.name for bone in armature.pose.bones]
        # filter action
        actions = [action for action in bpy.data.actions if action.isExport and any(name in fcurve.data_path for fcurve in action.fcurves for name in boneNames)]

        subFolder = re.sub("[\\/:<>\'\"|?*&]", "", preferences.ANIM_Subfolder).strip()
        directory = os.path.join((preferences.TempFolder, preferences.ExportFBXFolder)[preferences.exportOption in ["FBX","BOTH"]], subFolder)

        arrAnimationObject = []

        # Check Subfolder if exist, if not will make new folder
        if not os.path.isdir(directory) and subFolder:
            os.mkdir(directory)

        for action in actions:
            # Remove invalid character for filename
            filename = re.sub("[\\/:<>\'\"|?*&]", "", originalName + "_" + action.name).strip()
            # Check duplicate from arrAnimationObject
            checkDuplicate = len([obj for obj in arrAnimationObject if obj["name"].startswith(filename)])
            # Add number if have duplicate name
            filename += ("", "_" + str(checkDuplicate) )[bool(checkDuplicate)]

            # Check if file alredy exist and overwrite
            if not os.path.isfile(os.path.join(directory, filename + ".fbx")) or preferences.ANIM_OverwriteFile:
                armature.animation_data.action = action

                # Export animation option
                bpy.ops.export_scene.fbx(
                    filepath= os.path.join(directory, filename + ".fbx"),
                    check_existing=False,
                    filter_glob="*.fbx",
                    use_selection=True,
                    use_active_collection=False,
                    global_scale=preferences.ANIM_FBXGlobalScale,
                    apply_unit_scale=preferences.ANIM_FBXApplyUnitScale,
                    apply_scale_options=preferences.ANIM_FBXApplyScaleOptions,
                    bake_space_transform=preferences.ANIM_FBXBakeSpaceTransform,
                    object_types={"ARMATURE"},
                    use_custom_props=True,
                    add_leaf_bones=preferences.ANIM_FBXAddLeafBones,
                    primary_bone_axis=preferences.ANIM_FBXPrimaryBoneAxis,
                    secondary_bone_axis=preferences.ANIM_FBXSecondaryBoneAxis,
                    use_armature_deform_only=preferences.ANIM_FBXOnlyDeformBones,
                    armature_nodetype=preferences.ANIM_FBXArmatureFBXNodeType,
                    bake_anim=True,
                    bake_anim_use_all_bones=preferences.ANIM_FBXKeyAllBones,
                    bake_anim_use_nla_strips=False,
                    bake_anim_use_all_actions=False,
                    bake_anim_force_startend_keying=preferences.ANIM_FBXForceStartEndKeying,
                    bake_anim_step=preferences.ANIM_FBXSamplingRate,
                    bake_anim_simplify_factor=preferences.ANIM_FBXSimplify,
                    path_mode="AUTO",
                    embed_textures=False,
                    batch_mode="OFF",
                    axis_forward=preferences.ANIM_FBXAxisUp,
                    axis_up=preferences.ANIM_FBXAxisForward
                )

                arrAnimationObject.append({
                    "name": filename,
                    "skeleton": preferences.ANIM_CharacterSkeleton
                })

        # restore location
        armature.location = originalLocation

        # restore "UE4RIGVERSION" if exist
        if rigVersion is not None:
            armature["UE4RIGVERSION"] = rigVersion

        if armature.get("UE4RIGGED"):
            # change name to original name if armature is ue4 rigged
            armature.name = originalName
        else:
            armature.name = originalName

        armature.animation_data.action = originalAction

        if preferences.exportOption in ["UNREAL", "BOTH"] and self.remote.remote_nodes:
            # Unreal engine import option
            unrealsetting = {
                "folder": directory,
                "files": arrAnimationObject,
                "subfolder": subFolder,
                "overwrite_file": preferences.ANIM_OverwriteFile,
                "temporary": preferences.exportOption == "UNREAL",

                "animation_length": preferences.ANIM_AnimationLength,
                "import_meshes_in_bone_hierarchy": preferences.ANIM_ImportMeshesInBoneHierarchy,
                "frame_import_range": [preferences.ANIM_FrameImportRangeMin, preferences.ANIM_FrameImportRangeMax],
                "use_default_sample_rate": preferences.ANIM_UseDefaultSampleRate,
                "custom_sample_rate": preferences.ANIM_CustomSampleRate,
                "import_custom_attribute": preferences.ANIM_ImportCustomAttribute,
                "delete_existing_custom_attribute_curves": preferences.ANIM_DeleteExistingCustomAttributeCurves,
                "import_bone_tracks": preferences.ANIM_ImportBoneTracks,
                "set_material_drive_parameter_on_custom_attribute": preferences.ANIM_SetMaterialDriveParameterOnCustomAttribute,
                "material_curve_suffixes": preferences.ANIM_MaterialCurveSuffixes.split("|") if preferences.ANIM_MaterialCurveSuffixes else [],
                "remove_redundant_keys": preferences.ANIM_RemoveRedundantKeys,
                "delete_existing_morph_target_curves": preferences.ANIM_DeleteExistingMorphTargetCurves,
                "do_not_import_curve_with_zero": preferences.ANIM_DoNotImportCurveWithZero,
                "preserve_local_transform": preferences.ANIM_PreserveLocalTransform,

                "import_translation": list(preferences.ANIM_ImportTranslation),
                "import_rotation": list(preferences.ANIM_ImportRotation),
                "import_uniform_scale": preferences.ANIM_ImportUniformScale,

                "convert_scene": preferences.ANIM_ConvertScene,
                "force_front_x_axis": preferences.ANIM_ForceFrontXAxis,
                "convert_scene_unit": preferences.ANIM_ConvertSceneUnit,
                "override_full_name": preferences.ANIM_OverrideFullName,
            }

            # Save unreal engine import option into a file json
            file = open(os.path.join(os.path.dirname(__file__), "Data", "unrealenginesetting.json"), "w+")
            file.write(json.dumps(unrealsetting))
            file.close()

            for node_id in [user["node_id"] for user in self.remote.remote_nodes]:
            # tell unreal engine tor run python script
                self.remote.open_command_connection(node_id)
                # self.remote.run_command(os.path.join(os.path.dirname(os.path.realpath(__file__)), "PyScript", "Animation.py"), exec_mode="ExecuteFile")
                # Fix Python PATH Script Issue #9
                self.remote.run_command("execfile(\"" + os.path.join(os.path.dirname(os.path.realpath(__file__)), "PyScript", "Animation.py").replace(os.sep, "/") +"\")", exec_mode="ExecuteStatement")
                self.remote.close_command_connection()

        try:
            bpy.ops.ue4workspace.popup("INVOKE_DEFAULT", msg="Exprot Animation Complete")
        except Exception: 
            pass

        return {"FINISHED"}

class OP_SelectAnimation(Operator):
    bl_idname = "ue4workspace.selectanimation"
    bl_label = "Select Animation To Export"
    bl_description = "Select Animation To Export"
    bl_options = {"UNDO"}

    type: bpy.props.StringProperty()

    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT" and context.active_object is not None and context.active_object.type == "ARMATURE"

    def execute(self, context):
        if context.active_object is not None and context.active_object.type == "ARMATURE" and True:
            for action in bpy.data.actions:
                boneNames = [bone.name for bone in context.active_object.pose.bones]
                if (any(name in fcurve.data_path for fcurve in action.fcurves for name in boneNames)):
                    if self.type == "SELECT":
                        action.isExport = True
                    elif self.type == "DESELECT":
                        action.isExport = False
                    elif self.type == "INVERT":
                        action.isExport = not action.isExport

        return {"FINISHED"}

class OP_ANIM_AddSuffixe(Operator):
    bl_idname = "ue4workspace.animaddsuffixe"
    bl_label = "Add Suffixes"
    bl_description = "Add Suffixes on Animation Export Setting"
    bl_options = {"UNDO"}

    val: bpy.props.StringProperty()

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        arrSuffixs = preferences.ANIM_MaterialCurveSuffixes.split("|") if preferences.ANIM_MaterialCurveSuffixes else []
        arrSuffixs.append(self.val.replace("|", ""))
        preferences.ANIM_MaterialCurveSuffixes = "|".join(arrSuffixs)

        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 250)

    def draw(self, context):
        col = self.layout.column()
        row = col.row()
        split = row.split(factor=0.5)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Value :")
        split = split.split()
        col = split.column()
        col.prop(self, "val", text="")

class OP_ANIM_ClearSuffixes(Operator):
    bl_idname = "ue4workspace.animclearsuffixes"
    bl_label = "Clear Suffixes"
    bl_description = "Clear Suffixes on Animation Export Setting"
    bl_options = {"UNDO"}

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences

        preferences.ANIM_MaterialCurveSuffixes = ""

        return {"FINISHED"}

class OP_ANIM_RemoveIndexSuffixe(Operator):
    bl_idname = "ue4workspace.animremoveindexsuffixe"
    bl_label = "Remove Index Suffixes"
    bl_description = "Remove Suffixes Base on Index Animation Export Setting"
    bl_options = {"UNDO"}

    idx: bpy.props.IntProperty()

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        arrSuffixs = preferences.ANIM_MaterialCurveSuffixes.split("|")
        arrSuffixs.pop(self.idx)
        preferences.ANIM_MaterialCurveSuffixes = "|".join(arrSuffixs)

        return {"FINISHED"}

class OP_ANIM_EditValueSuffixe(Operator):
    bl_idname = "ue4workspace.animeditvaluesuffixe"
    bl_label = "Edit Value Suffixes"
    bl_description = "Edit Value Suffixes on Animation Export Setting"
    bl_options = {"UNDO"}

    val: bpy.props.StringProperty()
    idx: bpy.props.IntProperty()

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        arrSuffixs = preferences.ANIM_MaterialCurveSuffixes.split("|")
        arrSuffixs[self.idx] = self.val.replace("|", "")
        preferences.ANIM_MaterialCurveSuffixes = "|".join(arrSuffixs)

        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 250)

    def draw(self, context):
        col = self.layout.column()
        row = col.row()
        split = row.split(factor=0.5)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Value :")
        split = split.split()
        col = split.column()
        col.prop(self, "val", text="")

class OP_ANIMUpdateExportProfile(Operator):
    bl_idname = "ue4workspace.animupdateexportprofile"
    bl_label = "Animatiion Update Export Profile"
    bl_description = "Update Current Export Profile"

    @classmethod
    def poll(self, context):
        preferences = context.preferences.addons[__package__].preferences
        return not preferences.ANIM_IsProfileLock

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        jsonSetting = open(os.path.join(os.path.dirname(__file__), "Data", "exportProfile.json"), "r").read()
        jsonSetting = json.loads(jsonSetting)

        for key in ["ANIM_FBXGlobalScale", "ANIM_FBXApplyScaleOptions","ANIM_FBXAxisForward","ANIM_FBXAxisUp", "ANIM_FBXApplyUnitScale", "ANIM_FBXBakeSpaceTransform", "ANIM_FBXPrimaryBoneAxis", "ANIM_FBXSecondaryBoneAxis", "ANIM_FBXArmatureFBXNodeType", "ANIM_FBXOnlyDeformBones", "ANIM_FBXAddLeafBones", "ANIM_FBXKeyAllBones", "ANIM_FBXForceStartEndKeying", "ANIM_FBXSamplingRate", "ANIM_FBXSimplify"]:
            jsonSetting["animation"][preferences.ANIM_ExportProfile]["FBX"][key] = getattr(preferences, key)

        for key in [
            "ANIM_AnimationLength",
            "ANIM_ImportMeshesInBoneHierarchy",
            "ANIM_FrameImportRangeMin",
            "ANIM_FrameImportRangeMax",
            "ANIM_UseDefaultSampleRate",
            "ANIM_CustomSampleRate",
            "ANIM_ImportCustomAttribute",
            "ANIM_DeleteExistingCustomAttributeCurves",
            "ANIM_ImportBoneTracks",
            "ANIM_SetMaterialDriveParameterOnCustomAttribute",
            "ANIM_MaterialCurveSuffixes",
            "ANIM_RemoveRedundantKeys",
            "ANIM_DeleteExistingMorphTargetCurves",
            "ANIM_DoNotImportCurveWithZero",
            "ANIM_PreserveLocalTransform",
            "ANIM_ImportTranslation",
            "ANIM_ImportRotation",
            "ANIM_ImportUniformScale",
            "ANIM_ConvertScene",
            "ANIM_ForceFrontXAxis",
            "ANIM_ConvertSceneUnit",
            "ANIM_OverrideFullName"
        ]:
            jsonSetting["animation"][preferences.ANIM_ExportProfile]["UNREALENGINE"][key] = list(getattr(preferences, key)) if (key in ["ANIM_ImportTranslation", "ANIM_ImportRotation"]) else getattr(preferences, key)

        # Save profile export into a file json
        file = open(os.path.join(os.path.dirname(__file__), "Data", "exportProfile.json"), "w+")
        file.write(json.dumps(jsonSetting, indent=4))
        file.close()

        try:
            bpy.ops.ue4workspace.popup("INVOKE_DEFAULT", msg="Update Profile Success")
        except Exception: 
            pass
        return {"FINISHED"}

class OP_ANIMCreateExportProfile(Operator):
    bl_idname = "ue4workspace.animcreateexportprofile"
    bl_label = "Animation Create Export Profile"
    bl_description = "Create Export Profile Base On Current Setting"

    name: bpy.props.StringProperty(
        name = "Name Profile",
        description = "Name Profile",
        default = ""
    )

    description: bpy.props.StringProperty(
        name = "Description",
        description = "Description Profile",
        default = ""
    )

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        if(self.name):
            setting = {
                "name": self.name,
                "description": self.description,
                "lock": False,
                "FBX": {},
                "UNREALENGINE": {}
            }
            for key in ["ANIM_FBXGlobalScale", "ANIM_FBXApplyScaleOptions","ANIM_FBXAxisForward","ANIM_FBXAxisUp", "ANIM_FBXApplyUnitScale", "ANIM_FBXBakeSpaceTransform", "ANIM_FBXPrimaryBoneAxis", "ANIM_FBXSecondaryBoneAxis", "ANIM_FBXArmatureFBXNodeType", "ANIM_FBXOnlyDeformBones", "ANIM_FBXAddLeafBones", "ANIM_FBXKeyAllBones", "ANIM_FBXForceStartEndKeying", "ANIM_FBXSamplingRate", "ANIM_FBXSimplify"]:
                setting["FBX"][key] = getattr(preferences, key)

            for key in [
                "ANIM_AnimationLength",
                "ANIM_ImportMeshesInBoneHierarchy",
                "ANIM_FrameImportRangeMin",
                "ANIM_FrameImportRangeMax",
                "ANIM_UseDefaultSampleRate",
                "ANIM_CustomSampleRate",
                "ANIM_ImportCustomAttribute",
                "ANIM_DeleteExistingCustomAttributeCurves",
                "ANIM_ImportBoneTracks",
                "ANIM_SetMaterialDriveParameterOnCustomAttribute",
                "ANIM_MaterialCurveSuffixes",
                "ANIM_RemoveRedundantKeys",
                "ANIM_DeleteExistingMorphTargetCurves",
                "ANIM_DoNotImportCurveWithZero",
                "ANIM_PreserveLocalTransform",
                "ANIM_ImportTranslation",
                "ANIM_ImportRotation",
                "ANIM_ImportUniformScale",
                "ANIM_ConvertScene",
                "ANIM_ForceFrontXAxis",
                "ANIM_ConvertSceneUnit",
                "ANIM_OverrideFullName"
            ]:
                setting["UNREALENGINE"][key] = list(getattr(preferences, key)) if (key in ["ANIM_ImportTranslation", "ANIM_ImportRotation"]) else getattr(preferences, key)
            jsonSetting = open(os.path.join(os.path.dirname(__file__), "Data", "exportProfile.json"), "r").read()
            jsonSetting = json.loads(jsonSetting)
            timestamp = int(time.time())
            jsonSetting["animation"][timestamp] = setting
            # Save profile export into a file json
            file = open(os.path.join(os.path.dirname(__file__), "Data", "exportProfile.json"), "w+")
            file.write(json.dumps(jsonSetting, indent=4))
            file.close()

            preferences.ANIM_ExportProfile = str(timestamp)

            self.report({"INFO"}, "Create Profile Success")
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 250)

class OP_ANIMRemoveExportProfile(Operator):
    bl_idname = "ue4workspace.animremoveexportprofile"
    bl_label = "Animation Remove Export Profile"
    bl_description = "Remove Current Export Profile"

    @classmethod
    def poll(self, context):
        preferences = context.preferences.addons[__package__].preferences
        return not preferences.ANIM_IsProfileLock

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        jsonSetting = open(os.path.join(os.path.dirname(__file__), "Data", "exportProfile.json"), "r").read()
        jsonSetting = json.loads(jsonSetting)
        del jsonSetting["animation"][preferences.ANIM_ExportProfile]
        # Save profile export into a file json
        file = open(os.path.join(os.path.dirname(__file__), "Data", "exportProfile.json"), "w+")
        file.write(json.dumps(jsonSetting, indent=4))
        file.close()
        preferences.ANIM_ExportProfile = "UNREAL_ENGINE"
        try:
            bpy.ops.ue4workspace.popup("INVOKE_DEFAULT", msg="Remove Profile Success")
        except Exception: 
            pass
        return {"FINISHED"}

# operator export

Ops = [
    OP_ExportAnimation,
    OP_SelectAnimation,
    OP_ANIM_AddSuffixe,
    OP_ANIM_ClearSuffixes,
    OP_ANIM_RemoveIndexSuffixe,
    OP_ANIM_EditValueSuffixe,
    OP_ANIMUpdateExportProfile,
    OP_ANIMCreateExportProfile,
    OP_ANIMRemoveExportProfile
]