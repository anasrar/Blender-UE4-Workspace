import bpy
from bpy.types import (Panel, Operator)

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_StaticMeshUnrealEnginePanel"
    bl_parent_id = "UE4WORKSPACE_PT_StaticMeshPanel"
    bl_label = "Unreal Engine Export Setting"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons[__package__].preferences

        layout.prop(preferences, "SM_TabMesh", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.SM_TabMesh], emboss=False)
        if preferences.SM_TabMesh:
            box = layout.box()
            for arr in [["SM_AutoGenerateCollision", "Auto Generate Collision"], ["SM_VertexColorImportOption", "Vertex Color Import Option"], ["SM_VertexOverrideColor", "Vertex Override Color"], ["SM_RemoveDegenerates", "Remove Degenerate"], ["SM_BuildAdjacencyBuffer", "Build Adjacency Buffer"], ["SM_BuildReversedIndexBuffer", "Build Reversed Index Buffer"], ["SM_GenerateLightmapsUVs", "Generate Lightmaps UVs"], ["SM_OneConvexHullPerUCX", "One Convex Hull Per UCX"], ["SM_CombineMeshes", "Combine Meshes"], ["SM_TransformVertexToAbsolute", "Transform Vertex to Absolute"], ["SM_BakePivotInVertex", "Bake Pivot in Vertex"], ["SM_ImportMeshLODs", "Import Mesh LODs"], ["SM_NormalImportMethod", "Normal Import Method"], ["SM_NormalGenerationMethod", "Normal Generation Method"], ["SM_ComputeWeightedNormals", "Compute Weighted Normals"]]:
                if not arr[0] in ["SM_ImportMeshLODs"]:
                    col = box.column()
                    row = col.row()
                    split = row.split(factor=0.6)
                    col = split.column()
                    col.alignment = "RIGHT"
                    col.label(text=arr[1])
                    split = split.split()
                    col = split.column()
                    col.prop(preferences, arr[0], text="")

        layout.prop(preferences, "SM_TabTransform", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.SM_TabTransform], emboss=False)
        if preferences.SM_TabTransform:
            box = layout.box()
            for arr in [["SM_ImportTranslation", "Import Translation"], ["SM_ImportRotation", "Import Translation"], ["SM_ImportUniformScale", "Import Uniform Scale"]]:
                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text=arr[1])
                split = split.split()
                col = split.column()
                col.prop(preferences, arr[0], text="")

        layout.prop(preferences, "SM_TabMisc", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.SM_TabMisc], emboss=False)
        if preferences.SM_TabMisc:
            box = layout.box()
            for arr in [["SM_ConvertScene", "Convert Scene"], ["SM_ForceFrontXAxis", "Force Front XAxis"], ["SM_ConvertSceneUnit", "Convert Scene Unit"], ["SM_OverrideFullName", "Override Full Name"]]:
                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text=arr[1])
                split = split.split()
                col = split.column()
                col.prop(preferences, arr[0], text="")

        if preferences.SM_ImportMeshLODs:
            layout.prop(preferences, "SM_TabLODSetting", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.SM_TabLODSetting], emboss=False)
            if preferences.SM_TabLODSetting:
                box = layout.box()

                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text="Auto Compute LOD Screen Size")
                split = split.split()
                col = split.column()
                col.prop(preferences, "SM_AutoComputeLODScreenSize", text="")

                if not preferences.SM_AutoComputeLODScreenSize:
                    for numLOD in range(8):
                        col = box.column()
                        row = col.row()
                        split = row.split(factor=0.6)
                        col = split.column()
                        col.alignment = "RIGHT"
                        col.label(text="LOD {0} Screen Size".format(numLOD))
                        split = split.split()
                        col = split.column()
                        col.prop(preferences, "SM_LODDistance{0}".format(numLOD), text="")

                for arr in [["SM_MinimumLODNumber", "Minimum LOD"], ["SM_NumberOfLODs", "Number of LODs"]]:
                    col = box.column()
                    row = col.row()
                    split = row.split(factor=0.6)
                    col = split.column()
                    col.alignment = "RIGHT"
                    col.label(text=arr[1])
                    split = split.split()
                    col = split.column()
                    col.prop(preferences, arr[0], text="")

        layout.prop(preferences, "SM_TabMaterial", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.SM_TabMaterial], emboss=False)
        if preferences.SM_TabMaterial:
            box = layout.box()
            for arr in [["SM_MaterialSearchLocation", "Search Location"], ["SM_ImportMaterial", "Import Material"], ["SM_ImportTexture", "Import Texture"], ["SM_InvertNormalMaps", "Invert Normal Maps"], ["SM_ReorderMaterialToFBXOrder", "Reorder Material To FBX Order"]]:
                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text=arr[1])
                split = split.split()
                col = split.column()
                col.prop(preferences, arr[0], text="")