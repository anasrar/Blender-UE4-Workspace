import os
import json
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

        if preferences.devMode:
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

#  OPERATOR

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
        # Filter object for mesh, object name not start with UCX_, and mesh does not have ARMATURE modifiers
        objects = [obj for obj in objects if obj.type == "MESH" and not obj.name.startswith("UCX_") and not "ARMATURE" in [mod.type for mod in obj.modifiers]]

        # Deselect all object
        bpy.ops.object.select_all(action="DESELECT")

        subFolder = re.sub("[\\/:<>\'\"|?*&]", "", preferences.SM_Subfolder).strip()
        directory = os.path.join((preferences.TempFolder, preferences.ExportFBXFolder)[preferences.exportOption in ["FBX","BOTH"]], subFolder)

        arrMeshObject = []

        # Check Subfolder if exist, if not will make new folder
        if not os.path.isdir(directory) and subFolder:
            os.mkdir(directory)

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
                collObjects = [obj for obj in context.scene.objects if obj.name.startswith(collName)]
                # Collision array for information [name, location, disable select]
                collArrInfo = []

                if preferences.SM_CustomCollision and collObjects:
                    for index, collObj in enumerate(collObjects, start=1):
                        collArrInfo.append([collObj.name, collObj.location.copy(), collObj.hide_select])
                        # Select object
                        collObj.hide_select = False
                        collObj.select_set(state=True)
                        # Rename object
                        collObj.name = collName + ("", "0")[index <= 9] + str(index)
                        if collObj.parent is None or collObj.parent is not obj:
                            if preferences.SM_MeshOrigin == "OBJECT":
                                # Reset location
                                collObj.location = (0, 0, 0)

                

                # Copy original location for mesh origin by object
                originalLocation = obj.location.copy()
                if preferences.SM_MeshOrigin == "OBJECT":
                    # Reset location
                    obj.location = (0, 0, 0)

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
                    use_custom_props=False,
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
                    "lod": False
                })

                if preferences.SM_MeshOrigin == "OBJECT":
                    # Set location object back to original
                    obj.location = originalLocation
                # Deselect current object
                obj.select_set(state=False)

                if preferences.SM_CustomCollision and collObjects:
                    for index, collObj in enumerate(collObjects, start=0):
                        # deselect object
                        collObj.select_set(state=False)
                        collObj.hide_select = collArrInfo[index][2]
                        # Rename object
                        collObj.name = collArrInfo[index][0]
                        collObj.location = collArrInfo[index][1]

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
                self.remote.run_command(os.path.join(os.path.dirname(os.path.realpath(__file__)), "PyScript", "StaticMesh.py"), exec_mode="ExecuteFile")
                self.remote.close_command_connection()

        try:
            bpy.ops.ue4workspace.popup("INVOKE_DEFAULT", msg="Export Static Mesh Done")
        except Exception: 
            pass

        return {"FINISHED"}

# operator export

Ops = [
    OP_ExportStaticMesh
]