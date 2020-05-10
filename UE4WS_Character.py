import os
import json
import re
import bpy
from bpy.types import (Panel, Operator)
from . UE4WS_CharacterBoneManipulation import (BoneManipulation)

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_CharacterPanel"
    bl_label = "Character"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

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
            row.operator("ue4workspace.updatelistskeleton",icon="ARMATURE_DATA", text="Update List Skeleton")

        row = layout.row()
        row.scale_y = 1.5
        row.operator("ue4workspace.exportcharacter",icon="MESH_CUBE", text="Export")

#  OPERATOR

class OP_UpdateListSkeleton(Operator):
    bl_idname = "ue4workspace.updatelistskeleton"
    bl_label = "UE4Workspace Operator"
    bl_description = "Update List Skeleton"

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
            output = self.remote.run_command(os.path.join(os.path.dirname(os.path.realpath(__file__)), "PyScript", "GetAllSkeleton.py"), exec_mode="ExecuteFile")
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

class OP_CharacteRemoveTemporaryBone(Operator):
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

class OP_ExportCharacter(Operator):
    bl_idname = "ue4workspace.exportcharacter"
    bl_label = "UE4Workspace Operator"
    bl_description = "Export Character"

    remote = None

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        oldActiveObject = context.active_object
        selectedObjects = context.selected_objects
        objects = (selectedObjects, context.scene.objects)[preferences.CHAR_ExportCharacterOption == "ALL"]
        # Filter object for aramture
        objects = [obj for obj in objects if obj.type == "ARMATURE"]

        # Deselect all object
        bpy.ops.object.select_all(action="DESELECT")

        subFolder = re.sub("[\\/:<>\'\"|?*&]", "", preferences.CHAR_Subfolder).strip()
        directory = os.path.join((preferences.TempFolder, preferences.ExportFBXFolder)[preferences.exportOption in ["FBX","BOTH"]], subFolder)

        arrCharacterObject = []

        # Check Subfolder if exist, if not will make new folder
        if not os.path.isdir(directory) and subFolder:
            os.mkdir(directory)

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
                    if obj.get("UE4RIG"):
                        bone = BoneManipulation(context)
                        bone.rotateBone()
                        bone.beforeExport()

                    obj.select_set(state=True)
                    # select childern mesh
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
                    # deselect childern mesh
                    for mesh in [mesh for mesh in obj.children if mesh.type == "MESH"]:
                        mesh.select_set(state=False)

                    if obj.get("UE4RIG"):
                        bone.afterExport()
                        if not obj.get("UE4RIGHASTEMPBONE"):
                            bone.removeTemporaryBone()
            else:
                context.view_layer.objects.active = obj
                if obj.get("UE4RIG"):
                    # save armature name because will rename to root on bone.beforeExport()
                    armatureName = obj.name
                    bone = BoneManipulation(context)
                    bone.rotateBone()
                    bone.beforeExport()

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
                        # select childern mesh
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
                        # deselect childern mesh
                        mesh.select_set(state=False)

                if obj.get("UE4RIG"):
                    bone.afterExport()
                    if not obj.get("UE4RIGHASTEMPBONE"):
                        bone.removeTemporaryBone()

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
                self.remote.run_command(os.path.join(os.path.dirname(os.path.realpath(__file__)), "PyScript", "Character.py"), exec_mode="ExecuteFile")
                self.remote.close_command_connection()

        try:
            bpy.ops.ue4workspace.popup("INVOKE_DEFAULT", msg="Export Character Done")
        except Exception:
            pass

        return {"FINISHED"}

# operator export

Ops = [
    OP_UpdateListSkeleton,
    OP_CharacterRotateBone,
    OP_CharacteRemoveTemporaryBone,
    OP_ExportCharacter
]