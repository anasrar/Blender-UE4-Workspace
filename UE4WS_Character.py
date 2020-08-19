import os
import json
import time
import re
import bpy
from mathutils import Matrix
from bpy.types import (Panel, Operator)
from bpy.props import (EnumProperty, StringProperty)
from . UE4WS_CharacterBoneManipulation import (BoneManipulation)

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_CharacterPanel"
    bl_label = "Character"
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
        col.label(text="Skeleton Preset")
        split = split.split()
        col = split.column()
        col.prop(preferences, "CHAR_SkeletonPreset", text="")

        row = layout.row()
        row.scale_y = 1.5
        row.operator("ue4workspace.importunrealenginerig",icon="ARMATURE_DATA", text="Import Skeleton")

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Subfolder")
        split = split.split()
        col = split.column()
        col.prop(preferences, "CHAR_Subfolder", text="")

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Overwrite File")
        split = split.split()
        col = split.column()
        col.prop(preferences, "CHAR_OverwriteFile", text="")

        # UE4 Python still not support add socket using python for skeletal mesh
        # col = layout.column()
        # row = col.row()
        # split = row.split(factor=0.6)
        # col = split.column()
        # col.alignment = "RIGHT"
        # col.label(text="Socket")
        # split = split.split()
        # col = split.column()
        # col.prop(preferences, "CHAR_Socket", text="")

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Export Character Option")
        split = split.split()
        col = split.column()
        col.prop(preferences, "CHAR_ExportCharacterOption", text="")

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Character Option")
        split = split.split()
        col = split.column()
        col.prop(preferences, "CHAR_CharacterOption", text="")

        if preferences.exportOption in ["BOTH", "UNREAL"]:
            col = layout.column()
            row = col.row()
            split = row.split(factor=0.6)
            col = split.column()
            col.alignment = "RIGHT"
            col.label(text="Character Skeleton")
            split = split.split()
            col = split.column()
            col.prop(preferences, "CHAR_CharacterSkeleton", text="")

            row = layout.row()
            row.scale_y = 1.5
            row.operator("ue4workspace.updateskeletonlist",icon="ARMATURE_DATA")

        row = layout.row()
        row.scale_y = 1.5
        row.operator("ue4workspace.exportcharacter",icon="MESH_CUBE", text="Export")

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.prop(preferences, "CHAR_ExportProfile", text="")
        split = split.split()
        row = split.row(align=True)
        row.alignment = "RIGHT"
        row.operator("ue4workspace.charupdateexportprofile",icon="GREASEPENCIL", text="")
        row.operator("ue4workspace.charcreateexportprofile",icon="FILE_NEW", text="")
        row.operator("ue4workspace.charremoveexportprofile",icon="TRASH", text="")

#  OPERATOR

class OP_CHARUpdateExportProfile(Operator):
    bl_idname = "ue4workspace.charupdateexportprofile"
    bl_label = "Character Update Export Profile"
    bl_description = "Update Current Export Profile"

    @classmethod
    def poll(self, context):
        preferences = context.preferences.addons[__package__].preferences
        return not preferences.CHAR_IsProfileLock

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        jsonSetting = open(os.path.join(os.path.dirname(__file__), "Data", "exportProfile.json"), "r").read()
        jsonSetting = json.loads(jsonSetting)

        for key in ["CHAR_FBXGlobalScale", "CHAR_FBXApplyScaleOptions","CHAR_FBXAxisForward","CHAR_FBXAxisUp", "CHAR_FBXApplyUnitScale", "CHAR_FBXBakeSpaceTransform", "CHAR_FBXMeshSmoothType", "CHAR_FBXUseSubsurf", "CHAR_FBXUseMeshModifiers", "CHAR_FBXUseMeshEdges", "CHAR_FBXUseTSpace", "CHAR_FBXPrimaryBoneAxis", "CHAR_FBXSecondaryBoneAxis", "CHAR_FBXArmatureFBXNodeType", "CHAR_FBXOnlyDeformBones", "CHAR_FBXAddLeafBones"]:
            jsonSetting["character"][preferences.CHAR_ExportProfile]["FBX"][key] = getattr(preferences, key)

        for key in [
                "CHAR_ImportContentType",
                "CHAR_VertexColorImportOption",
                "CHAR_VertexOverrideColor",
                "CHAR_UpdateSkeletonReferencePose",
                "CHAR_UseT0AsRefPose",
                "CHAR_PreserveSmoothingGroups",
                "CHAR_ImportMeshesInBoneHierarchy",
                "CHAR_ImportMorphTargets",
                "CHAR_ImportMeshLODs",
                "CHAR_NormalImportMethod",
                "CHAR_NormalGenerationMethod",
                "CHAR_ComputeWeightedNormals",
                "CHAR_ThresholdPosition",
                "CHAR_ThresholdTangentNormal",
                "CHAR_ThresholdUV",
                "CHAR_PhysicsAsset",
                "CHAR_ImportTranslation",
                "CHAR_ImportRotation",
                "CHAR_ImportUniformScale",
                "CHAR_ConvertScene",
                "CHAR_ForceFrontXAxis",
                "CHAR_ConvertSceneUnit",
                "CHAR_OverrideFullName",
                "CHAR_MaterialSearchLocation",
                "CHAR_ImportMaterial",
                "CHAR_ImportTexture",
                "CHAR_InvertNormalMaps",
                "CHAR_ReorderMaterialToFBXOrder"
        ]:
            jsonSetting["character"][preferences.CHAR_ExportProfile]["UNREALENGINE"][key] = list(getattr(preferences, key)) if (key in ["CHAR_VertexOverrideColor", "CHAR_ImportTranslation", "CHAR_ImportRotation"]) else getattr(preferences, key)

        # Save profile export into a file json
        file = open(os.path.join(os.path.dirname(__file__), "Data", "exportProfile.json"), "w+")
        file.write(json.dumps(jsonSetting, indent=4))
        file.close()

        try:
            bpy.ops.ue4workspace.popup("INVOKE_DEFAULT", msg="Update Profile Success")
        except Exception: 
            pass
        return {"FINISHED"}

class OP_CHARCreateExportProfile(Operator):
    bl_idname = "ue4workspace.charcreateexportprofile"
    bl_label = "Character Create Export Profile"
    bl_description = "Create Export Profile Base On Current Setting"

    name: StringProperty(
        name = "Name Profile",
        description = "Name Profile",
        default = ""
    )

    description: StringProperty(
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
            for key in ["CHAR_FBXGlobalScale", "CHAR_FBXApplyScaleOptions","CHAR_FBXAxisForward","CHAR_FBXAxisUp", "CHAR_FBXApplyUnitScale", "CHAR_FBXBakeSpaceTransform", "CHAR_FBXMeshSmoothType", "CHAR_FBXUseSubsurf", "CHAR_FBXUseMeshModifiers", "CHAR_FBXUseMeshEdges", "CHAR_FBXUseTSpace", "CHAR_FBXPrimaryBoneAxis", "CHAR_FBXSecondaryBoneAxis", "CHAR_FBXArmatureFBXNodeType", "CHAR_FBXOnlyDeformBones", "CHAR_FBXAddLeafBones"]:
                setting["FBX"][key] = getattr(preferences, key)

            for key in [
                "CHAR_ImportContentType",
                "CHAR_VertexColorImportOption",
                "CHAR_VertexOverrideColor",
                "CHAR_UpdateSkeletonReferencePose",
                "CHAR_UseT0AsRefPose",
                "CHAR_PreserveSmoothingGroups",
                "CHAR_ImportMeshesInBoneHierarchy",
                "CHAR_ImportMorphTargets",
                "CHAR_ImportMeshLODs",
                "CHAR_NormalImportMethod",
                "CHAR_NormalGenerationMethod",
                "CHAR_ComputeWeightedNormals",
                "CHAR_ThresholdPosition",
                "CHAR_ThresholdTangentNormal",
                "CHAR_ThresholdUV",
                "CHAR_PhysicsAsset",
                "CHAR_ImportTranslation",
                "CHAR_ImportRotation",
                "CHAR_ImportUniformScale",
                "CHAR_ConvertScene",
                "CHAR_ForceFrontXAxis",
                "CHAR_ConvertSceneUnit",
                "CHAR_OverrideFullName",
                "CHAR_MaterialSearchLocation",
                "CHAR_ImportMaterial",
                "CHAR_ImportTexture",
                "CHAR_InvertNormalMaps",
                "CHAR_ReorderMaterialToFBXOrder"
            ]:
                setting["UNREALENGINE"][key] = list(getattr(preferences, key)) if (key in ["CHAR_VertexOverrideColor", "CHAR_ImportTranslation", "CHAR_ImportRotation"]) else getattr(preferences, key)
            jsonSetting = open(os.path.join(os.path.dirname(__file__), "Data", "exportProfile.json"), "r").read()
            jsonSetting = json.loads(jsonSetting)
            timestamp = int(time.time())
            jsonSetting["character"][timestamp] = setting
            # Save profile export into a file json
            file = open(os.path.join(os.path.dirname(__file__), "Data", "exportProfile.json"), "w+")
            file.write(json.dumps(jsonSetting, indent=4))
            file.close()

            preferences.CHAR_ExportProfile = str(timestamp)

            self.report({"INFO"}, "Create Profile Success")
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 250)

class OP_CHARRemoveExportProfile(Operator):
    bl_idname = "ue4workspace.charremoveexportprofile"
    bl_label = "Character Remove Export Profile"
    bl_description = "Remove Current Export Profile"

    @classmethod
    def poll(self, context):
        preferences = context.preferences.addons[__package__].preferences
        return not preferences.CHAR_IsProfileLock

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        jsonSetting = open(os.path.join(os.path.dirname(__file__), "Data", "exportProfile.json"), "r").read()
        jsonSetting = json.loads(jsonSetting)
        del jsonSetting["character"][preferences.CHAR_ExportProfile]
        # Save profile export into a file json
        file = open(os.path.join(os.path.dirname(__file__), "Data", "exportProfile.json"), "w+")
        file.write(json.dumps(jsonSetting, indent=4))
        file.close()
        preferences.CHAR_ExportProfile = "UNREAL_ENGINE"
        try:
            bpy.ops.ue4workspace.popup("INVOKE_DEFAULT", msg="Remove Profile Success")
        except Exception: 
            pass
        return {"FINISHED"}

class OP_IMPORTARMATURE(Operator):
    bl_idname = "ue4workspace.importunrealenginerig"
    bl_label = "Import Skeleton Preset"
    bl_description = "Import Skeleton Preset"
    bl_options = {"UNDO", "REGISTER"}

    isImportCharacterPlacement: bpy.props.BoolProperty(
        name="Import Character Placement",
        default=True
        )

    addonVersion = None

    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        jsonSetting = open(os.path.join(os.path.dirname(__file__), "Data", "skeletonPreset.json"), "r").read()
        jsonSetting = json.loads(jsonSetting)

        skeleton = jsonSetting["skeleton"].get(preferences.CHAR_SkeletonPreset, False)
        if skeleton:
            if skeleton.get("characterPlacement", False) and self.isImportCharacterPlacement:
                path = os.path.dirname(os.path.realpath(__file__))
                directory = os.path.join(path, "Data","BLEND.blend", "Object")
                bpy.ops.wm.append(filename=skeleton["characterPlacement"], directory=directory, active_collection=True, autoselect=False)

            oldMode = context.mode
            armature = bpy.data.armatures.new(preferences.CHAR_SkeletonPreset)
            armature_object = bpy.data.objects.new(preferences.CHAR_SkeletonPreset, armature)
            armature_object.show_in_front = True
            for key, val in skeleton["prop"].items():
                armature_object[key] = val
            armature_object.data.layers[31] = True
            armature_object["UE4RIGVERSION"] = self.addonVersion
            context.scene.collection.objects.link(armature_object)

            context.view_layer.objects.active = armature_object
            bpy.ops.object.select_all(action="DESELECT")
            bpy.ops.object.mode_set(mode="EDIT")

            parentList = {}
            editBones = armature_object.data.edit_bones
            boneLists = skeleton["bones"]
            for (boneName, value) in boneLists.items():
                newBone = editBones.new(boneName)
                parentList[boneName] = newBone
                newBone.head = value["head"]
                newBone.tail = value["tail"]
                newBone.roll = value["roll"]
                newBone.parent = parentList[value["parent"]] if value["parent"] is not None else None
                newBone.use_connect = value["connect"]
                newBone.use_inherit_rotation = value.get("use_inherit_rotation", True)
                newBone.use_deform = value.get("use_deform", True)

                for key, propValue in value["prop"].items():
                    if key == "boneOrient":
                        newBone[key] = "|".join(str(x) for x in propValue)
                    else:
                        newBone[key] = propValue

            bpy.ops.armature.select_all(action="DESELECT")
            bpy.ops.object.mode_set(mode=oldMode)

        # try:
        #     bpy.ops.ue4workspace.popup("INVOKE_DEFAULT", msg="Import Skeleton Success")
        # except Exception: 
        #     pass

        return {"FINISHED"}

class OP_UpdateSkeletonList(Operator):
    bl_idname = "ue4workspace.updateskeletonlist"
    bl_label = "Update Skeleton List"
    bl_description = "Update Skeleton List From Unreal Engine"

    remote = None

    @classmethod
    def poll(self, context):
        preferences = context.preferences.addons[__package__].preferences

        return preferences.exportOption in ["UNREAL", "BOTH"] and self.remote.remote_nodes

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences

        # clear all skeleton list
        preferences.skeleton.clear()
        skeletonList = []

        for node_id in [user["node_id"] for user in self.remote.remote_nodes]:
            self.remote.open_command_connection(node_id)
            # output = self.remote.run_command(os.path.join(os.path.dirname(os.path.realpath(__file__)), "PyScript", "GetAllSkeleton.py"), exec_mode="ExecuteFile")
            # Fix Python PATH Script Issue #9
            output = self.remote.run_command("execfile(\"" + os.path.join(os.path.dirname(os.path.realpath(__file__)), "PyScript", "GetAllSkeleton.py").replace(os.sep, "/") +"\")", exec_mode="ExecuteStatement")
            self.remote.close_command_connection()
            skeletonList += json.loads(output["output"][0]["output"])

        # add skeleton
        for enum in skeletonList:
            preferences.skeleton.append((enum[0], enum[1], enum[0]))

        try:
            bpy.ops.ue4workspace.popup("INVOKE_DEFAULT", msg="Update List Skeleton Done")
        except Exception: 
            pass

        return {"FINISHED"}

class OP_CharacterGenerateRig(Operator):
    bl_idname = "ue4workspace.generaterig"
    bl_label = "Generate Rig"
    bl_description = "Generate Rig"
    bl_options = {"UNDO"}

    @classmethod
    def poll(self, context):
        return context.active_object is not None and context.active_object.type == "ARMATURE" and context.active_object.get("UE4RIG") and context.mode == "OBJECT"

    def execute(self, context):
        armature = context.active_object
        bpy.ops.object.select_all(action="DESELECT")
        armature.select_set(True)
        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":"TRANSLATION"}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":"GLOBAL", "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type":"GLOBAL", "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":"SMOOTH", "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":"CLOSEST", "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
        rig = context.active_object
        rig.name = "RIGGED_" + armature.name
        bone = BoneManipulation(context)
        bone.rotateBone()
        bone.generateRig()
        # move socket
        socketObjects = [obj for obj in armature.children if obj.type == "EMPTY" and obj.get("isSocket")]
        for socketObj in socketObjects:
            parentType = socketObj.parent_type
            parentBone = socketObj.parent_bone
            socketObj.parent = rig
            socketObj.parent_type = parentType
            if parentType == "BONE":
                socketObj.parent_bone = parentBone
                bone = rig.pose.bones.get(parentBone)
                if bone:
                    socketObj.matrix_parent_inverse = (rig.matrix_world @ Matrix.Translation(bone.tail - bone.head) @ bone.matrix).inverted()
            else:
                socketObj.matrix_parent_inverse = rig.matrix_world.inverted()

        try:
            bpy.ops.ue4workspace.popup("INVOKE_DEFAULT", msg="Generate Rig Complete")
        except Exception:
            pass
        return {"FINISHED"}

class OP_CharacterRotateBone(Operator):
    bl_idname = "ue4workspace.rotatebone"
    bl_label = "UE4Workspace Operator"
    bl_description = "Character Rotate Bone"
    bl_options = {"UNDO"}

    remote = None

    @classmethod
    def poll(self, context):
        return context.active_object is not None and context.active_object.type == "ARMATURE" and context.active_object.get("UE4RIG")

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences

        bone = BoneManipulation(context)
        bone.rotateBone()
        context.active_object["UE4RIGHASTEMPBONE"] = 1
        try:
            bpy.ops.ue4workspace.popup("INVOKE_DEFAULT", msg="Calculate Bone Done")
        except Exception:
            pass

        return {"FINISHED"}

class OP_CharacterRemoveTemporaryBone(Operator):
    bl_idname = "ue4workspace.characterremovetemporarybone"
    bl_label = "UE4Workspace Operator"
    bl_description = "Characte Remove Temporary Bone"
    bl_options = {"UNDO"}

    remote = None
    
    @classmethod
    def poll(self, context):
        return context.active_object is not None and context.active_object.type == "ARMATURE" and context.active_object.get("UE4RIG") and context.active_object.get("UE4RIGHASTEMPBONE", False)

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences

        bone = BoneManipulation(context)
        bone.removeTemporaryBone()
        context.active_object.pop("UE4RIGHASTEMPBONE")
        try:
            bpy.ops.ue4workspace.popup("INVOKE_DEFAULT", msg="Remove Temporary Bone Done")
        except Exception:
            pass

        return {"FINISHED"}

class OP_CharacterAddTwistBone(Operator):
    bl_idname = "ue4workspace.addtwistbone"
    bl_label = "Add Twist Bone"
    bl_description = "Add Twist Bone"
    bl_options = {"UNDO", "REGISTER"}

    numberBone: bpy.props.IntProperty(
        name="Number Bone",
        min=1,
        default=1
        )

    @classmethod
    def poll(self, context):
        return context.active_object is not None and context.active_object.type == "ARMATURE" and context.active_object.get("UE4RIG") and context.mode == "EDIT_ARMATURE" and context.active_bone is not None and (context.active_bone.get("UE4RIGTYPE") in ["LEG_HUMAN", "ARM_HUMAN"] or context.active_bone.parent.get("UE4RIGTYPE") in ["LEG_HUMAN", "ARM_HUMAN"])

    def execute(self, context):
        editBones = context.active_object.data.edit_bones
        activeBone = context.active_bone
        bpy.ops.armature.select_all(action="DESELECT")
        for bone in [child for child in activeBone.children if "_twist_" in child.name]:
            editBones.remove(bone)
        if activeBone.parent is not None and activeBone.use_connect:
            activeBone.parent.select_tail = True
        else:
            activeBone.select_head = True
        activeBone.select = True
        activeBone.select_tail = True
        bpy.ops.armature.duplicate_move(ARMATURE_OT_duplicate={"do_flip_names":False}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":"GLOBAL", "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type":"GLOBAL", "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":"SMOOTH", "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":"CLOSEST", "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
        if self.numberBone == 1:
            selectedBones = context.selected_bones
            bpy.ops.armature.select_all(action="DESELECT")
            editBones.active = activeBone
            for bone in selectedBones:
                parent = editBones.get(bone.name.split(".")[0])
                bone.parent = parent
                bone.length = activeBone.length / 2
                arrBoneName = bone.name.split(".")[0].split("_")
                bone.name = arrBoneName[0] + "_twist_01_" + arrBoneName[-1]
                bone.select = True
                bone.select_head = True
                bone.select_tail = True
                for key in parent.keys():
                    if key == "UE4RIGTYPE":
                        if bone.get(key, False):
                            del bone[key]
                    else:
                        bone[key] = parent[key]
                if not activeBone.get("UE4RIGTYPE") == "ARM_HUMAN":
                    bpy.ops.transform.translate(value=(0, parent.length/2, 0), orient_type="NORMAL", orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type="GLOBAL", mirror=True, use_proportional_edit=False, proportional_edit_falloff="SMOOTH", proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
                bpy.ops.armature.select_all(action="DESELECT")
        else:
            isReverse = activeBone.parent.get("UE4RIGTYPE") in ["LEG_HUMAN", "ARM_HUMAN"]
            bpy.ops.armature.subdivide(number_cuts=(self.numberBone-1, self.numberBone)[isReverse])
            selectedBones = context.selected_bones
            bpy.ops.armature.select_all(action="DESELECT")
            arrBoneSide = {
                "l": [bone for bone in selectedBones if bone.name.split(".")[1] == "001" and bone.name.split(".")[0].split("_")[-1] == "l"],
                "r": [bone for bone in selectedBones if bone.name.split(".")[1] == "001" and bone.name.split(".")[0].split("_")[-1] == "r"]
            }
            for side in arrBoneSide:
                for bone in arrBoneSide[side]:
                    arrBoneName = bone.name.split(".")[0].split("_")
                    parent = editBones.get(arrBoneName[0] + "_" + side)
                    bone.use_connect = False
                    bone.name = (arrBoneName[0] + "_twist_01_" + side, arrBoneName[0] + "_twist_temp_" + side)[isReverse]
                    bone.parent = parent
                    for key in parent.keys():
                        if key == "UE4RIGTYPE":
                            if bone.get(key, False):
                                del bone[key]
                        else:
                            bone[key] = parent[key]
                    for index, bn in enumerate((bone.children_recursive, bone.children_recursive[::-1])[isReverse], start=2):
                        if isReverse:
                            index -= 1
                        bn.use_connect = False
                        bn.name = arrBoneName[0] + "_twist_" + ("", "0")[index < 10] + str(index) + "_" + side
                        bn.parent = parent
                        for key in activeBone.keys():
                            if key == "UE4RIGTYPE":
                                if bn.get(key, False):
                                    del bn[key]
                            else:
                                bn[key] = activeBone[key]
                    editBones.active = activeBone
                    bpy.ops.armature.select_all(action="DESELECT")
                    if isReverse:
                        editBones.remove(bone)

        return {"FINISHED"}

class OP_CharacterRemoveTwistBone(Operator):
    bl_idname = "ue4workspace.removetwistbone"
    bl_label = "Remove Twist Bone"
    bl_description = "Remove Twist Bone"
    bl_options = {"UNDO"}

    @classmethod
    def poll(self, context):
        return context.active_object is not None and context.active_object.type == "ARMATURE" and context.active_object.get("UE4RIG") and context.mode == "EDIT_ARMATURE" and context.active_bone is not None and (context.active_bone.get("UE4RIGTYPE") in ["LEG_HUMAN", "ARM_HUMAN"] or context.active_bone.parent.get("UE4RIGTYPE") in ["LEG_HUMAN", "ARM_HUMAN"]) and len([child for child in context.active_bone.children if child.name.split("_")[1] == "twist"]) != 0

    def execute(self, context):
        editBones = context.active_object.data.edit_bones
        activeBone = context.active_bone
        bpy.ops.armature.select_all(action="DESELECT")
        for bone in [child for child in activeBone.children if child.name.split("_")[1] == "twist"]:
            editBones.remove(bone)
        try:
            bpy.ops.ue4workspace.popup("INVOKE_DEFAULT", msg="Remove Twist Complete")
        except Exception:
            pass
        return {"FINISHED"}

class OP_ExportCharacter(Operator):
    bl_idname = "ue4workspace.exportcharacter"
    bl_label = "UE4Workspace Operator"
    bl_description = "Export Character"

    remote = None

    @classmethod
    def description(self, context, properties):
        preferences = context.preferences.addons[__package__].preferences
        description = "Export Character"

        # Check folder for validation
        if preferences.exportOption in ["FBX", "BOTH"]:
            return ("FBX folder not valid", description)[bool(preferences.ExportFBXFolder.strip())]
        return ("Temporary folder not valid", description)[bool(preferences.TempFolder.strip())]

    @classmethod
    def poll(self, context):
        preferences = context.preferences.addons[__package__].preferences

        # Check folder for validation
        if preferences.exportOption in ["FBX", "BOTH"]:
            return bool(preferences.ExportFBXFolder.strip())
        return bool(preferences.TempFolder.strip())

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        oldActiveObject = context.active_object
        selectedObjects = context.selected_objects
        objects = (selectedObjects, context.scene.objects)[preferences.CHAR_ExportCharacterOption == "ALL"]
        # Filter object for armture
        objects = [obj for obj in objects if obj.type == "ARMATURE"]

        # Deselect all object
        bpy.ops.object.select_all(action="DESELECT")

        subFolder = re.sub("[\\/:<>\'\"|?*&]", "", preferences.CHAR_Subfolder).strip()
        directory = os.path.join((preferences.TempFolder, preferences.ExportFBXFolder)[preferences.exportOption in ["FBX","BOTH"]], subFolder)

        arrCharacterObject = []

        # Check Subfolder if exist, if not will make new folder
        if not os.path.isdir(directory) and subFolder:
            os.mkdir(directory)

        # Socket Collection
        socketCollection = bpy.data.collections.get("UE4Socket", False)
        socketHideProp = {
            "render": None,
            "select": None,
            "viewport": None
        }
        # Unhide socket collection
        if (socketCollection and preferences.CHAR_Socket):
            for key in socketHideProp:
                socketHideProp[key] = getattr(socketCollection, "hide_" + key)
                setattr(socketCollection, "hide_" + key, False)

        for obj in objects:
            if preferences.CHAR_CharacterOption == "COMBINE":
                # Remove invalid character for filename
                filename = re.sub("[\\/:<>\'\"|?*&]", "", obj.name).strip()
                # Check duplicate from arrCharacterObject
                checkDuplicate = len([obj for obj in arrCharacterObject if obj["name"].startswith(filename)])
                # Add number if have duplicate name
                filename += ("", "_" + str(checkDuplicate) )[bool(checkDuplicate)]

                # Check if file alredy exist and overwrite
                if not os.path.isfile(os.path.join(directory, filename + ".fbx")) or preferences.CHAR_OverwriteFile:
                    # set armature as active object
                    context.view_layer.objects.active = obj
                    # original name
                    originalName = obj.name
                    # copy location
                    originalLocation = obj.location.copy()
                    # reset location
                    obj.location = [0, 0, 0]
                    # check root bone
                    isHaveRootBone = obj.data.bones.get("root", False)
                    if obj.get("UE4RIG"):
                        bone = BoneManipulation(context)
                        bone.rotateBone()
                        bone.beforeExport()
                    elif obj.get("UE4RIGGED"):
                        # change name to "Armature"
                        obj.name = "Armature"
                    else:
                        # change name to "Armature" if have root bone or "root" if doesn't have root bone
                        if isHaveRootBone:
                            obj.name = "Armature"
                        else:
                            obj.name = "root"

                    # pop "UE4RIGVERSION"
                    # its because blender do not support array in custom property to export
                    rigVersion = obj.pop("UE4RIGVERSION", None)

                    # Socket filter from children objects
                    socketObjects = [obj for obj in obj.children if obj.type == "EMPTY" and obj.get("isSocket")]
                    # Socket array for information [disable select, hide_viewport]
                    socketArrInfo = []

                    if preferences.CHAR_Socket and socketObjects:
                        for index, socketObj in enumerate(socketObjects, start=1):
                            socketArrInfo.append([socketObj.hide_select, socketObj.hide_viewport])
                            # Select object
                            socketObj.hide_select = False
                            socketObj.hide_viewport = False
                            socketObj.select_set(state=True)
                            # Scale
                            for index, val in enumerate(socketObj.scale):
                                socketObj.scale[index] = val / 100
                            # Rotate
                            socketObj.rotation_euler[0] = abs(socketObj.rotation_euler[0]) if (socketObj.rotation_euler[0] < 0) else -abs(socketObj.rotation_euler[0])
                            socketObj.rotation_euler[1] = abs(socketObj.rotation_euler[1]) if (socketObj.rotation_euler[1] < 0) else -abs(socketObj.rotation_euler[1])
                            socketObj.rotation_euler[2] -= 3.14159
                            # Rename object
                            socketObj.name = "SOCKET_" + socketObj.name

                    # attach constraint
                    constraint = obj.constraints.get("AttachTo")
                    constraintMute = False
                    if constraint:
                        constraintMute = constraint.mute
                        constraint.mute = True

                    obj.select_set(state=True)
                    # select children mesh
                    for mesh in [mesh for mesh in obj.children if mesh.type == "MESH"]:
                        mesh.select_set(state=True)

                    # Export character option
                    bpy.ops.export_scene.fbx(
                        filepath= os.path.join(directory, filename + ".fbx"),
                        check_existing=False,
                        filter_glob="*.fbx",
                        use_selection=True,
                        use_active_collection=False,
                        global_scale=preferences.CHAR_FBXGlobalScale,
                        apply_unit_scale=preferences.CHAR_FBXApplyUnitScale,
                        apply_scale_options=preferences.CHAR_FBXApplyScaleOptions,
                        bake_space_transform=preferences.CHAR_FBXBakeSpaceTransform,
                        object_types={"MESH", "ARMATURE"},
                        use_mesh_modifiers=preferences.CHAR_FBXUseMeshModifiers,
                        mesh_smooth_type=preferences.CHAR_FBXMeshSmoothType,
                        use_subsurf=preferences.CHAR_FBXUseSubsurf,
                        use_mesh_edges=preferences.CHAR_FBXUseMeshEdges,
                        use_tspace=preferences.CHAR_FBXUseTSpace,
                        use_custom_props=False,
                        add_leaf_bones=preferences.CHAR_FBXAddLeafBones,
                        primary_bone_axis=preferences.CHAR_FBXPrimaryBoneAxis,
                        secondary_bone_axis=preferences.CHAR_FBXSecondaryBoneAxis,
                        use_armature_deform_only=preferences.CHAR_FBXOnlyDeformBones,
                        armature_nodetype=preferences.CHAR_FBXArmatureFBXNodeType,
                        bake_anim=False,
                        path_mode="AUTO",
                        embed_textures=False,
                        batch_mode="OFF",
                        axis_forward=preferences.CHAR_FBXAxisUp,
                        axis_up=preferences.CHAR_FBXAxisForward
                    )

                    arrCharacterObject.append({
                        "name": filename,
                        "skeleton": preferences.CHAR_CharacterSkeleton
                    })

                    obj.select_set(state=False)
                    # deselect children mesh
                    for mesh in [mesh for mesh in obj.children if mesh.type == "MESH"]:
                        mesh.select_set(state=False)

                    # restore location
                    obj.location = originalLocation

                    if obj.get("UE4RIG"):
                        bone.afterExport()
                        if not obj.get("UE4RIGHASTEMPBONE"):
                            bone.removeTemporaryBone()
                    elif obj.get("UE4RIGGED"):
                        # change name to original name
                        obj.name = originalName
                    else:
                        obj.name = originalName

                    # restore "UE4RIGVERSION" if exist
                    if rigVersion is not None:
                        obj["UE4RIGVERSION"] = rigVersion

                    # restore socket
                    if preferences.CHAR_Socket and socketObjects:
                        for index, socketObj in enumerate(socketObjects, start=0):
                            # deselect object
                            socketObj.select_set(state=False)
                            socketObj.hide_select = socketArrInfo[index][0]
                            socketObj.hide_viewport = socketArrInfo[index][1]
                            # Scale
                            for index, val in enumerate(socketObj.scale):
                                socketObj.scale[index] = val * 100
                            # Rotate
                            socketObj.rotation_euler[0] = abs(socketObj.rotation_euler[0]) if (socketObj.rotation_euler[0] < 0) else -abs(socketObj.rotation_euler[0])
                            socketObj.rotation_euler[1] = abs(socketObj.rotation_euler[1]) if (socketObj.rotation_euler[1] < 0) else -abs(socketObj.rotation_euler[1])
                            socketObj.rotation_euler[2] += 3.14159
                            # Rename object
                            socketObj.name = socketObj.name[7:]

                    # restore attach constraint
                    if constraint:
                        constraint.mute = constraintMute
            else:
                context.view_layer.objects.active = obj
                armatureName = obj.name
                # copy location
                originalLocation = obj.location.copy()
                # reset location
                obj.location = [0, 0, 0]
                # check root bone
                isHaveRootBone = obj.data.bones.get("root", False)
                if obj.get("UE4RIG"):
                    bone = BoneManipulation(context)
                    bone.rotateBone()
                    bone.beforeExport()
                elif obj.get("UE4RIGGED"):
                    # change name to "Armature"
                    obj.name = "Armature"
                else:
                    # change name to "Armature" if have root bone or "root" if doesn't have root bone
                    if isHaveRootBone:
                        obj.name = "Armature"
                    else:
                        obj.name = "root"

                # pop "UE4RIGVERSION"
                # its because blender do not support array in custom property to export
                rigVersion = obj.pop("UE4RIGVERSION", None)

                # Socket filter from children objects
                socketObjects = [obj for obj in obj.children if obj.type == "EMPTY" and obj.get("isSocket")]
                # Socket array for information [disable select, hide_viewport]
                socketArrInfo = []

                if preferences.CHAR_Socket and socketObjects:
                    for index, socketObj in enumerate(socketObjects, start=1):
                        socketArrInfo.append([socketObj.hide_select, socketObj.hide_viewport])
                        # Select object
                        socketObj.hide_select = False
                        socketObj.hide_viewport = False
                        socketObj.select_set(state=True)
                        # Scale
                        for index, val in enumerate(socketObj.scale):
                            socketObj.scale[index] = val / 100
                        # Rotate
                        socketObj.rotation_euler[0] = abs(socketObj.rotation_euler[0]) if (socketObj.rotation_euler[0] < 0) else -abs(socketObj.rotation_euler[0])
                        socketObj.rotation_euler[1] = abs(socketObj.rotation_euler[1]) if (socketObj.rotation_euler[1] < 0) else -abs(socketObj.rotation_euler[1])
                        socketObj.rotation_euler[2] -= 3.14159
                        # Rename object
                        socketObj.name = "SOCKET_" + socketObj.name

                # attach constraint
                constraint = obj.constraints.get("AttachTo")
                constraintMute = False
                if constraint:
                    constraintMute = constraint.mute
                    constraint.mute = True

                for mesh in [mesh for mesh in obj.children if mesh.type == "MESH"]:
                    # Remove invalid character for filename
                    filename = re.sub("[\\/:<>\'\"|?*&]", "", armatureName + "_" + mesh.name).strip()
                    # Check duplicate from arrCharacterObject
                    checkDuplicate = len([obj for obj in arrCharacterObject if obj["name"].startswith(filename)])
                    # Add number if have duplicate name
                    filename += ("", "_" + str(checkDuplicate) )[bool(checkDuplicate)]

                    # Check if file alredy exist and overwrite
                    if not os.path.isfile(os.path.join(directory, filename + ".fbx")) or preferences.CHAR_OverwriteFile:
                        obj.select_set(state=True)
                        # select children mesh
                        mesh.select_set(state=True)

                        # Export character option
                        bpy.ops.export_scene.fbx(
                            filepath= os.path.join(directory, filename + ".fbx"),
                            check_existing=False,
                            filter_glob="*.fbx",
                            use_selection=True,
                            use_active_collection=False,
                            global_scale=preferences.CHAR_FBXGlobalScale,
                            apply_unit_scale=preferences.CHAR_FBXApplyUnitScale,
                            apply_scale_options=preferences.CHAR_FBXApplyScaleOptions,
                            bake_space_transform=preferences.CHAR_FBXBakeSpaceTransform,
                            object_types={"MESH", "ARMATURE"},
                            use_mesh_modifiers=preferences.CHAR_FBXUseMeshModifiers,
                            mesh_smooth_type=preferences.CHAR_FBXMeshSmoothType,
                            use_subsurf=preferences.CHAR_FBXUseSubsurf,
                            use_mesh_edges=preferences.CHAR_FBXUseMeshEdges,
                            use_tspace=preferences.CHAR_FBXUseTSpace,
                            use_custom_props=False,
                            add_leaf_bones=preferences.CHAR_FBXAddLeafBones,
                            primary_bone_axis=preferences.CHAR_FBXPrimaryBoneAxis,
                            secondary_bone_axis=preferences.CHAR_FBXSecondaryBoneAxis,
                            use_armature_deform_only=preferences.CHAR_FBXOnlyDeformBones,
                            armature_nodetype=preferences.CHAR_FBXArmatureFBXNodeType,
                            bake_anim=False,
                            path_mode="AUTO",
                            embed_textures=False,
                            batch_mode="OFF",
                            axis_forward=preferences.CHAR_FBXAxisUp,
                            axis_up=preferences.CHAR_FBXAxisForward
                        )

                        arrCharacterObject.append({
                            "name": filename,
                            "skeleton": preferences.CHAR_CharacterSkeleton
                        })

                        obj.select_set(state=False)
                        # deselect children mesh
                        mesh.select_set(state=False)

                # restore location
                obj.location = originalLocation

                if obj.get("UE4RIG"):
                    bone.afterExport()
                    if not obj.get("UE4RIGHASTEMPBONE"):
                        bone.removeTemporaryBone()
                elif obj.get("UE4RIGGED"):
                    # change name to original name
                    obj.name = armatureName
                else:
                    obj.name = armatureName

                # restore "UE4RIGVERSION" if exist
                if rigVersion is not None:
                    obj["UE4RIGVERSION"] = rigVersion

                # restore socket
                if preferences.CHAR_Socket and socketObjects:
                    for index, socketObj in enumerate(socketObjects, start=0):
                        # deselect object
                        socketObj.select_set(state=False)
                        socketObj.hide_select = socketArrInfo[index][0]
                        socketObj.hide_viewport = socketArrInfo[index][1]
                        # Scale
                        for index, val in enumerate(socketObj.scale):
                            socketObj.scale[index] = val * 100
                        # Rotate
                        socketObj.rotation_euler[0] = abs(socketObj.rotation_euler[0]) if (socketObj.rotation_euler[0] < 0) else -abs(socketObj.rotation_euler[0])
                        socketObj.rotation_euler[1] = abs(socketObj.rotation_euler[1]) if (socketObj.rotation_euler[1] < 0) else -abs(socketObj.rotation_euler[1])
                        socketObj.rotation_euler[2] += 3.14159
                        # Rename object
                        socketObj.name = socketObj.name[7:]

                # restore attach constraint
                if constraint:
                    constraint.mute = constraintMute

        # Restore hide attribute of socket collection
        if (socketCollection and preferences.CHAR_Socket):
            for key, val in socketHideProp.items():
                setattr(socketCollection, "hide_" + key, val)

        # Select all object after export
        for obj in selectedObjects:
            obj.select_set(state=True)
        context.view_layer.objects.active = oldActiveObject

        if preferences.exportOption in ["UNREAL", "BOTH"] and self.remote.remote_nodes:
            # Unreal engine import option
            unrealsetting = {
                "folder": directory,
                "files": arrCharacterObject,
                "subfolder": subFolder,
                "overwrite_file": preferences.CHAR_OverwriteFile,
                "temporary": preferences.exportOption == "UNREAL",

                "import_content_type": preferences.CHAR_ImportContentType,
                "vertex_color_import_option": preferences.CHAR_VertexColorImportOption,
                "vertex_override_color": list(preferences.CHAR_VertexOverrideColor),
                "update_skeleton_reference_pose": preferences.CHAR_UpdateSkeletonReferencePose,
                "use_t0_as_ref_pose": preferences.CHAR_UseT0AsRefPose,
                "preserve_smoothing_groups": preferences.CHAR_PreserveSmoothingGroups,
                "import_meshes_in_bone_hierarchy": preferences.CHAR_ImportMeshesInBoneHierarchy,
                "import_morph_targets": preferences.CHAR_ImportMorphTargets,
                "import_mesh_lo_ds": preferences.CHAR_ImportMeshLODs,
                "normal_import_method": preferences.CHAR_NormalImportMethod,
                "normal_generation_method": preferences.CHAR_NormalGenerationMethod,
                "compute_weighted_normals": preferences.CHAR_ComputeWeightedNormals,
                "threshold_position": preferences.CHAR_ThresholdPosition,
                "threshold_tangent_normal": preferences.CHAR_ThresholdTangentNormal,
                "threshold_uv": preferences.CHAR_ThresholdUV,
                "physics_asset": preferences.CHAR_PhysicsAsset,

                "import_translation": list(preferences.CHAR_ImportTranslation),
                "import_rotation": list(preferences.CHAR_ImportRotation),
                "import_uniform_scale": preferences.CHAR_ImportUniformScale,

                "convert_scene": preferences.CHAR_ConvertScene,
                "force_front_x_axis": preferences.CHAR_ForceFrontXAxis,
                "convert_scene_unit": preferences.CHAR_ConvertSceneUnit,
                "override_full_name": preferences.CHAR_OverrideFullName,

                "material_search_location": preferences.CHAR_MaterialSearchLocation,
                "import_material": preferences.CHAR_ImportMaterial,
                "import_texture": preferences.CHAR_ImportTexture,
                "invert_normal_maps": preferences.CHAR_InvertNormalMaps,
                "reorder_material_to_fbx_order": preferences.CHAR_ReorderMaterialToFBXOrder
            }

            # Save unreal engine import option into a file json
            file = open(os.path.join(os.path.dirname(__file__), "Data", "unrealenginesetting.json"), "w+")
            file.write(json.dumps(unrealsetting))
            file.close()

            for node_id in [user["node_id"] for user in self.remote.remote_nodes]:
            # tell unreal engine tor run python script
                self.remote.open_command_connection(node_id)
                # self.remote.run_command(os.path.join(os.path.dirname(os.path.realpath(__file__)), "PyScript", "Character.py"), exec_mode="ExecuteFile")
                # Fix Python PATH Script Issue #9
                self.remote.run_command("execfile(\"" + os.path.join(os.path.dirname(os.path.realpath(__file__)), "PyScript", "Character.py").replace(os.sep, "/") +"\")", exec_mode="ExecuteStatement")
                self.remote.close_command_connection()

        try:
            bpy.ops.ue4workspace.popup("INVOKE_DEFAULT", msg="Export Character Done")
        except Exception:
            pass

        return {"FINISHED"}

# operator export

Ops = [
    OP_IMPORTARMATURE,
    OP_UpdateSkeletonList,
    OP_CharacterRotateBone,
    OP_CharacterGenerateRig,
    OP_CharacterRemoveTemporaryBone,
    OP_CharacterAddTwistBone,
    OP_CharacterRemoveTwistBone,
    OP_CHARUpdateExportProfile,
    OP_CHARCreateExportProfile,
    OP_CHARRemoveExportProfile,
    OP_ExportCharacter
]