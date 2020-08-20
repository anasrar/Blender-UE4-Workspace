import os
import json
import time
import re
import bpy
from bpy.props import (EnumProperty, StringProperty)
from bpy.types import (Panel, Operator)

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_StaticMeshPanel"
    bl_label = "Static Mesh"
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
        col.prop(preferences, "SM_Subfolder", text="")

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Custom Collision")
        split = split.split()
        col = split.column()
        col.prop(preferences, "SM_CustomCollision", text="")

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Socket")
        split = split.split()
        col = split.column()
        col.prop(preferences, "SM_Socket", text="")

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Level of Detail")
        split = split.split()
        col = split.column()
        col.prop(preferences, "SM_LOD", text="")

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Overwrite File")
        split = split.split()
        col = split.column()
        col.prop(preferences, "SM_OverwriteFile", text="")

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Export Mesh Option")
        split = split.split()
        col = split.column()
        col.prop(preferences, "SM_ExportMeshOption", text="")

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Mesh Origin")
        split = split.split()
        col = split.column()
        col.prop(preferences, "SM_MeshOrigin", text="")

        row = layout.row()
        row.scale_y = 1.5
        row.operator("ue4workspace.exportstaticmesh",icon="MESH_CUBE", text="Export")

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.prop(preferences, "SM_ExportProfile", text="")
        split = split.split()
        row = split.row(align=True)
        row.alignment = "RIGHT"
        row.operator("ue4workspace.smupdateexportprofile",icon="GREASEPENCIL", text="")
        row.operator("ue4workspace.smcreateexportprofile",icon="FILE_NEW", text="")
        row.operator("ue4workspace.smremoveexportprofile",icon="TRASH", text="")


#  OPERATOR

class OP_SMUpdateExportProfile(Operator):
    bl_idname = "ue4workspace.smupdateexportprofile"
    bl_label = "Static Mesh Update Export Profile"
    bl_description = "Update Current Export Profile"

    @classmethod
    def poll(self, context):
        preferences = context.preferences.addons[__package__].preferences
        return not preferences.SM_IsProfileLock

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        jsonSetting = open(os.path.join(os.path.dirname(__file__), "Data", "exportProfile.json"), "r").read()
        jsonSetting = json.loads(jsonSetting)

        for key in ["SM_FBXGlobalScale", "SM_FBXApplyScaleOptions","SM_FBXAxisForward","SM_FBXAxisUp", "SM_FBXApplyUnitScale", "SM_FBXBakeSpaceTransform", "SM_FBXMeshSmoothType", "SM_FBXUseSubsurf", "SM_FBXUseMeshModifiers", "SM_FBXUseMeshEdges", "SM_FBXUseTSpace"]:
            jsonSetting["staticMesh"][preferences.SM_ExportProfile]["FBX"][key] = getattr(preferences, key)

        for key in [
            "SM_AutoGenerateCollision",
            "SM_VertexColorImportOption",
            "SM_VertexOverrideColor",
            "SM_RemoveDegenerates",
            "SM_BuildAdjacencyBuffer",
            "SM_BuildReversedIndexBuffer",
            "SM_GenerateLightmapsUVs",
            "SM_OneConvexHullPerUCX",
            "SM_CombineMeshes",
            "SM_TransformVertexToAbsolute",
            "SM_BakePivotInVertex",
            "SM_ImportMeshLODs",
            "SM_NormalImportMethod",
            "SM_NormalGenerationMethod",
            "SM_ComputeWeightedNormals",
            "SM_ImportTranslation",
            "SM_ImportRotation",
            "SM_ImportUniformScale",
            "SM_ConvertScene",
            "SM_ForceFrontXAxis",
            "SM_ConvertSceneUnit",
            "SM_OverrideFullName",
            "SM_AutoComputeLODScreenSize",
            "SM_LODDistance0",
            "SM_LODDistance1",
            "SM_LODDistance2",
            "SM_LODDistance3",
            "SM_LODDistance4",
            "SM_LODDistance5",
            "SM_LODDistance6",
            "SM_LODDistance7",
            "SM_MinimumLODNumber",
            "SM_NumberOfLODs",
            "SM_MaterialSearchLocation",
            "SM_ImportMaterial",
            "SM_ImportTexture",
            "SM_InvertNormalMaps",
            "SM_ReorderMaterialToFBXOrder"
        ]:
            jsonSetting["staticMesh"][preferences.SM_ExportProfile]["UNREALENGINE"][key] = list(getattr(preferences, key)) if (key in ["SM_VertexOverrideColor", "SM_ImportTranslation", "SM_ImportRotation"]) else getattr(preferences, key)

        # Save profile export into a file json
        file = open(os.path.join(os.path.dirname(__file__), "Data", "exportProfile.json"), "w+")
        file.write(json.dumps(jsonSetting, indent=4))
        file.close()

        try:
            bpy.ops.ue4workspace.popup("INVOKE_DEFAULT", msg="Update Profile Success")
        except Exception: 
            pass
        return {"FINISHED"}

class OP_SMCreateExportProfile(Operator):
    bl_idname = "ue4workspace.smcreateexportprofile"
    bl_label = "Static Mesh Create Export Profile"
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
            for key in ["SM_FBXGlobalScale", "SM_FBXApplyScaleOptions","SM_FBXAxisForward","SM_FBXAxisUp", "SM_FBXApplyUnitScale", "SM_FBXBakeSpaceTransform", "SM_FBXMeshSmoothType", "SM_FBXUseSubsurf", "SM_FBXUseMeshModifiers", "SM_FBXUseMeshEdges", "SM_FBXUseTSpace"]:
                setting["FBX"][key] = getattr(preferences, key)

            for key in [
                "SM_AutoGenerateCollision",
                "SM_VertexColorImportOption",
                "SM_VertexOverrideColor",
                "SM_RemoveDegenerates",
                "SM_BuildAdjacencyBuffer",
                "SM_BuildReversedIndexBuffer",
                "SM_GenerateLightmapsUVs",
                "SM_OneConvexHullPerUCX",
                "SM_CombineMeshes",
                "SM_TransformVertexToAbsolute",
                "SM_BakePivotInVertex",
                "SM_ImportMeshLODs",
                "SM_NormalImportMethod",
                "SM_NormalGenerationMethod",
                "SM_ComputeWeightedNormals",
                "SM_ImportTranslation",
                "SM_ImportRotation",
                "SM_ImportUniformScale",
                "SM_ConvertScene",
                "SM_ForceFrontXAxis",
                "SM_ConvertSceneUnit",
                "SM_OverrideFullName",
                "SM_AutoComputeLODScreenSize",
                "SM_LODDistance0",
                "SM_LODDistance1",
                "SM_LODDistance2",
                "SM_LODDistance3",
                "SM_LODDistance4",
                "SM_LODDistance5",
                "SM_LODDistance6",
                "SM_LODDistance7",
                "SM_MinimumLODNumber",
                "SM_NumberOfLODs",
                "SM_MaterialSearchLocation",
                "SM_ImportMaterial",
                "SM_ImportTexture",
                "SM_InvertNormalMaps",
                "SM_ReorderMaterialToFBXOrder"
            ]:
                setting["UNREALENGINE"][key] = list(getattr(preferences, key)) if (key in ["SM_VertexOverrideColor", "SM_ImportTranslation", "SM_ImportRotation"]) else getattr(preferences, key)
            jsonSetting = open(os.path.join(os.path.dirname(__file__), "Data", "exportProfile.json"), "r").read()
            jsonSetting = json.loads(jsonSetting)
            timestamp = int(time.time())
            jsonSetting["staticMesh"][timestamp] = setting
            # Save profile export into a file json
            file = open(os.path.join(os.path.dirname(__file__), "Data", "exportProfile.json"), "w+")
            file.write(json.dumps(jsonSetting, indent=4))
            file.close()

            preferences.SM_ExportProfile = str(timestamp)

            self.report({"INFO"}, "Create Profile Success")
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 250)

class OP_SMRemoveExportProfile(Operator):
    bl_idname = "ue4workspace.smremoveexportprofile"
    bl_label = "Static Mesh Remove Export Profile"
    bl_description = "Remove Current Export Profile"

    @classmethod
    def poll(self, context):
        preferences = context.preferences.addons[__package__].preferences
        return not preferences.SM_IsProfileLock

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        jsonSetting = open(os.path.join(os.path.dirname(__file__), "Data", "exportProfile.json"), "r").read()
        jsonSetting = json.loads(jsonSetting)
        del jsonSetting["staticMesh"][preferences.SM_ExportProfile]
        # Save profile export into a file json
        file = open(os.path.join(os.path.dirname(__file__), "Data", "exportProfile.json"), "w+")
        file.write(json.dumps(jsonSetting, indent=4))
        file.close()
        preferences.SM_ExportProfile = "UNREAL_ENGINE"
        try:
            bpy.ops.ue4workspace.popup("INVOKE_DEFAULT", msg="Remove Profile Success")
        except Exception: 
            pass
        return {"FINISHED"}

class OP_ExportStaticMesh(Operator):
    bl_idname = "ue4workspace.exportstaticmesh"
    bl_label = "UE4Workspace Operator"
    bl_description = "Export Static Mesh"

    remote = None

    @classmethod
    def description(self, context, properties):
        preferences = context.preferences.addons[__package__].preferences
        description = "Export Static Mesh"

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
        selectedObjects = context.selected_objects
        objects = (selectedObjects, context.scene.objects)[preferences.SM_ExportMeshOption == "ALL"]
        # Filter object for mesh, object is not collision, object is not lod, and mesh does not have ARMATURE modifiers
        objects = [obj for obj in objects if obj.type == "MESH" and not obj.get("isCollision") and not obj.data.objectAsLOD and not "ARMATURE" in [mod.type for mod in obj.modifiers]]

        # Deselect all object
        bpy.ops.object.select_all(action="DESELECT")

        subFolder = re.sub("[\\/:<>\'\"|?*&]", "", preferences.SM_Subfolder).strip()
        directory = os.path.join((preferences.TempFolder, preferences.ExportFBXFolder)[preferences.exportOption in ["FBX","BOTH"]], subFolder)

        arrMeshObject = []

        # Check Subfolder if exist, if not will make new folder
        if not os.path.isdir(directory) and subFolder:
            os.mkdir(directory)

        # Collision Collection
        collisionCollection = bpy.data.collections.get("UE4CustomCollision", False)
        collisionHideProp = {
            "render": None,
            "select": None,
            "viewport": None
        }
        # Unhide collision collection
        if (collisionCollection and preferences.SM_CustomCollision):
            for key in collisionHideProp:
                collisionHideProp[key] = getattr(collisionCollection, "hide_" + key)
                setattr(collisionCollection, "hide_" + key, False)

        # Socket Collection
        socketCollection = bpy.data.collections.get("UE4Socket", False)
        socketHideProp = {
            "render": None,
            "select": None,
            "viewport": None
        }
        # Unhide socket collection
        if (socketCollection and preferences.SM_Socket):
            for key in socketHideProp:
                socketHideProp[key] = getattr(socketCollection, "hide_" + key)
                setattr(socketCollection, "hide_" + key, False)

        for obj in objects:
            # Remove invalid character for filename
            filename = re.sub("[\\/:<>\'\"|?*&]", "", obj.name).strip()
            # Check duplicate from arrMeshObject
            checkDuplicate = len([obj for obj in arrMeshObject if obj["name"].startswith(filename)])
            # Add number if have duplicate name
            filename += ("", "_" + str(checkDuplicate) )[bool(checkDuplicate)]

            # Check if file alredy exist and overwrite
            if not os.path.isfile(os.path.join(directory, filename + ".fbx")) or preferences.SM_OverwriteFile:

                # Collision name
                collName = "UCX_" + obj.name + "_"
                # Collision filter from scene objects
                collObjects = [obj for obj in context.scene.objects if obj.get("isCollision")]
                # Collision array for information [name, location, disable select, hide_viewport, hide]
                collArrInfo = []

                if preferences.SM_CustomCollision and collObjects:
                    for index, collObj in enumerate(collObjects, start=1):
                        collArrInfo.append([collObj.name, collObj.location.copy(), collObj.hide_select, collObj.hide_viewport, collObj.hide_get()])
                        # Select object
                        collObj.hide_set(False)
                        collObj.hide_select = False
                        collObj.hide_viewport = False
                        collObj.select_set(state=True)
                        # Rename object
                        collObj.name = collName + ("", "0")[index <= 9] + str(index)
                        if collObj.parent is None or collObj.parent is not obj:
                            if preferences.SM_MeshOrigin == "OBJECT":
                                # Reset location
                                collObj.location = (0, 0, 0)

                # Socket filter from children objects
                socketObjects = [obj for obj in obj.children if obj.type == "EMPTY" and obj.get("isSocket")]
                # Socket array for information [disable select, hide_viewport, hide]
                socketArrInfo = []

                if preferences.SM_Socket and socketObjects:
                    for index, socketObj in enumerate(socketObjects, start=1):
                        socketArrInfo.append([socketObj.hide_select, socketObj.hide_viewport, socketObj.hide_get()])
                        # Select object
                        socketObj.hide_set(False)
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

                # Copy original location for mesh origin by object
                originalLocation = obj.location.copy()
                if preferences.SM_MeshOrigin == "OBJECT":
                    # Reset location
                    obj.location = (0, 0, 0)

                # LOD
                # lod filter from object data
                lodStructObjects = [(lod.obj, lod.screenSize) for lod in obj.data.LODs if lod.obj]
                # lod array for information (obj)
                lodArrInfo = []
                objOriginalParent = obj.parent
                LOD = None
                if preferences.SM_LOD and bool(lodStructObjects):
                    LOD = bpy.data.objects.new("LOD_" + obj.name, None)
                    context.collection.objects.link(LOD)
                    LOD.empty_display_size = 2
                    LOD.empty_display_type = "ARROWS"
                    LOD["fbx_type"] = "LodGroup"
                    LOD.select_set(state=True)
                    obj.parent = LOD
                    for lodObj, screenSize in lodStructObjects:
                        lodObjCopy = lodObj.copy()
                        context.collection.objects.link(lodObjCopy)
                        lodArrInfo.append(lodObjCopy)
                        # Select object
                        lodObjCopy.hide_set(False)
                        lodObjCopy.hide_select = False
                        lodObjCopy.hide_viewport = False
                        lodObjCopy.select_set(state=True)
                        if preferences.SM_MeshOrigin == "OBJECT":
                            lodObjCopy.location = (0, 0, 0)
                        lodObjCopy.parent = LOD

                # Select current object
                obj.select_set(state=True)

                # Export mesh option
                bpy.ops.export_scene.fbx(
                    filepath= os.path.join(directory, filename + ".fbx"),
                    check_existing=False,
                    filter_glob="*.fbx",
                    use_selection=True,
                    use_active_collection=False,
                    global_scale=preferences.SM_FBXGlobalScale,
                    apply_unit_scale=preferences.SM_FBXApplyUnitScale,
                    apply_scale_options=preferences.SM_FBXApplyScaleOptions,
                    bake_space_transform=preferences.SM_FBXBakeSpaceTransform,
                    object_types={"MESH", "EMPTY"},
                    use_mesh_modifiers=preferences.SM_FBXUseMeshModifiers,
                    mesh_smooth_type=preferences.SM_FBXMeshSmoothType,
                    use_subsurf=preferences.SM_FBXUseSubsurf,
                    use_mesh_edges=preferences.SM_FBXUseMeshEdges,
                    use_tspace=preferences.SM_FBXUseTSpace,
                    use_custom_props=True,
                    bake_anim=False,
                    path_mode="AUTO",
                    embed_textures=False,
                    batch_mode="OFF",
                    axis_forward=preferences.SM_FBXAxisUp,
                    axis_up=preferences.SM_FBXAxisForward
                )

                arrMeshObject.append({
                    "name": filename,
                    # Check if have "Lightmap" UV
                    "custom_uv": "Lightmap" in [uv.name for uv in obj.data.uv_layers],
                    "custom_collision": (preferences.SM_CustomCollision and bool(collObjects)),
                    "lod": ([obj.data.LOD0ScreenSize] + [screenSize for lodObj,screenSize in lodStructObjects]) if (preferences.SM_LOD and bool(lodStructObjects)) else [],
                    "auto_compute_lod_distances": obj.data.AutoComputeLODScreenSize
                })

                # restore LOD
                if preferences.SM_LOD and bool(lodStructObjects):
                    obj.parent = objOriginalParent
                    for lodObj in lodArrInfo:
                        bpy.data.objects.remove(lodObj, do_unlink=True)
                    bpy.data.objects.remove(LOD, do_unlink=True)

                if preferences.SM_MeshOrigin == "OBJECT":
                    # Set location object back to original
                    obj.location = originalLocation
                # Deselect current object
                obj.select_set(state=False)

                # restore collision
                if preferences.SM_CustomCollision and collObjects:
                    for index, collObj in enumerate(collObjects, start=0):
                        # deselect object
                        collObj.hide_set(collArrInfo[index][4])
                        collObj.select_set(state=False)
                        collObj.hide_select = collArrInfo[index][2]
                        collObj.hide_viewport = collArrInfo[index][3]
                        # Rename object
                        collObj.name = collArrInfo[index][0]
                        if collObj.parent is None or collObj.parent is not obj:
                            if preferences.SM_MeshOrigin == "OBJECT":
                                # Reset location
                                collObj.location = collArrInfo[index][1]

                # restore socket
                if preferences.SM_Socket and socketObjects:
                    for index, socketObj in enumerate(socketObjects, start=0):
                        # deselect object
                        socketObj.hide_set(socketArrInfo[index][2])
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

        # Restore hide attribute of collision collection
        if (collisionCollection and preferences.SM_CustomCollision):
            for key, val in collisionHideProp.items():
                setattr(collisionCollection, "hide_" + key, val)

        # Restore hide attribute of socket collection
        if (socketCollection and preferences.SM_Socket):
            for key, val in socketHideProp.items():
                setattr(socketCollection, "hide_" + key, val)

        # Select all object after export
        for obj in selectedObjects:
            obj.select_set(state=True)

        if preferences.exportOption in ["UNREAL", "BOTH"] and self.remote.remote_nodes:
            # Unreal engine import option
            unrealsetting = {
                "folder": directory,
                "files": arrMeshObject,
                "subfolder": subFolder,
                "overwrite_file": preferences.SM_OverwriteFile,
                "temporary": preferences.exportOption == "UNREAL",

                "auto_generate_collision": preferences.SM_AutoGenerateCollision,
                "vertex_color_import_option": preferences.SM_VertexColorImportOption,
                "vertex_override_color": list(preferences.SM_VertexOverrideColor),
                "remove_degenerates": preferences.SM_RemoveDegenerates,
                "build_adjacency_buffer": preferences.SM_BuildAdjacencyBuffer,
                "build_reversed_index_buffer": preferences.SM_BuildReversedIndexBuffer,
                "generate_lightmaps_uvs": preferences.SM_GenerateLightmapsUVs,
                "one_convex_hull_perucx": preferences.SM_OneConvexHullPerUCX,
                "combine_meshes": preferences.SM_CombineMeshes,
                "transform_vertex_to_absolute": preferences.SM_TransformVertexToAbsolute,
                "bake_pivot_in_vertex": preferences.SM_BakePivotInVertex,
                "import_mesh_lods": preferences.SM_ImportMeshLODs,
                "normal_import_method": preferences.SM_NormalImportMethod,
                "normal_generation_method": preferences.SM_NormalGenerationMethod,
                "compute_weighted_normals": preferences.SM_ComputeWeightedNormals,

                "import_translation": list(preferences.SM_ImportTranslation),
                "import_rotation": list(preferences.SM_ImportRotation),
                "import_uniform_scale": preferences.SM_ImportUniformScale,

                "convert_scene": preferences.SM_ConvertScene,
                "force_front_x_axis": preferences.SM_ForceFrontXAxis,
                "convert_scene_unit": preferences.SM_ConvertSceneUnit,
                "override_full_name": preferences.SM_OverrideFullName,

                "auto_compute_lod_distances": preferences.SM_AutoComputeLODScreenSize,
                "lod_distance": [ getattr(preferences, "SM_LODDistance{0}".format(numLOD), 0.0) for numLOD in range(8)],
                "minimum_lod_number": preferences.SM_MinimumLODNumber,
                "lod_number": preferences.SM_NumberOfLODs,

                "material_search_location": preferences.SM_MaterialSearchLocation,
                "import_material": preferences.SM_ImportMaterial,
                "import_texture": preferences.SM_ImportTexture,
                "invert_normal_maps": preferences.SM_InvertNormalMaps,
                "reorder_material_to_fbx_order": preferences.SM_ReorderMaterialToFBXOrder
            }

            # Save unreal engine import option into a file json
            file = open(os.path.join(os.path.dirname(__file__), "Data", "unrealenginesetting.json"), "w+")
            file.write(json.dumps(unrealsetting))
            file.close()

            for node_id in [user["node_id"] for user in self.remote.remote_nodes]:
            # tell unreal engine tor run python script
                self.remote.open_command_connection(node_id)
                # self.remote.run_command(os.path.join(os.path.dirname(os.path.realpath(__file__)), "PyScript", "StaticMesh.py"), exec_mode="ExecuteFile")
                # Fix Python PATH Script Issue #9
                self.remote.run_command("execfile(\"" + os.path.join(os.path.dirname(os.path.realpath(__file__)), "PyScript", "StaticMesh.py").replace(os.sep, "/") +"\")", exec_mode="ExecuteStatement")
                self.remote.close_command_connection()

        try:
            bpy.ops.ue4workspace.popup("INVOKE_DEFAULT", msg="Export Static Mesh Done")
        except Exception: 
            pass

        return {"FINISHED"}

# operator export

Ops = [
    OP_SMUpdateExportProfile,
    OP_SMCreateExportProfile,
    OP_SMRemoveExportProfile,
    OP_ExportStaticMesh
]