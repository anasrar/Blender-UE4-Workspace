import bpy
from bpy.types import (Panel, Operator)

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_CharacterUnrealEnginePanel"
    bl_parent_id = "UE4WORKSPACE_PT_CharacterPanel"
    bl_label = "Unreal Engine Export Setting"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons[__package__].preferences

        layout.prop(preferences, "CHAR_TabMesh", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.CHAR_TabMesh], emboss=False)
        if preferences.CHAR_TabMesh:
            box = layout.box()
            for arr in [["CHAR_ImportContentType", "Import Content Type"], ["CHAR_VertexColorImportOption", "Vertex Color Import Option"], ["CHAR_VertexOverrideColor", "Vertex Override Color"], ["CHAR_UpdateSkeletonReferencePose", "Update Skeleton Reference Pose"], ["CHAR_UseT0AsRefPose", "Use T0 As Ref Pose"], ["CHAR_PreserveSmoothingGroups", "Preserve Smoothing Groups"], ["CHAR_ImportMeshesInBoneHierarchy", "Import Meshes In Bone Hierarchy"], ["CHAR_ImportMorphTargets", "Import Morph Targets"], ["CHAR_ImportMeshLODs", "Import Mesh LODs"], ["CHAR_NormalImportMethod", "Normal Import Method"], ["CHAR_NormalGenerationMethod", "Normal Generation Method"], ["CHAR_ComputeWeightedNormals", "Compute Weighted Normals"], ["CHAR_ThresholdPosition", "Threshold Position"], ["CHAR_ThresholdTangentNormal", "Threshold Tangent Normal"], ["CHAR_ThresholdUV", "Threshold UV"], ["CHAR_PhysicsAsset", "Physics Asset"]]:
                if not arr[0] in ["CHAR_ImportMeshLODs"]:
                    col = box.column()
                    row = col.row()
                    split = row.split(factor=0.6)
                    col = split.column()
                    col.alignment = "RIGHT"
                    col.label(text=arr[1])
                    split = split.split()
                    col = split.column()
                    col.prop(preferences, arr[0], text="")

        layout.prop(preferences, "CHAR_TabTransform", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.CHAR_TabTransform], emboss=False)
        if preferences.CHAR_TabTransform:
            box = layout.box()
            for arr in [["CHAR_ImportTranslation", "Import Translation"], ["CHAR_ImportRotation", "Import Translation"], ["CHAR_ImportUniformScale", "Import Uniform Scale"]]:
                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text=arr[1])
                split = split.split()
                col = split.column()
                col.prop(preferences, arr[0], text="")

        layout.prop(preferences, "CHAR_TabMisc", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.CHAR_TabMisc], emboss=False)
        if preferences.CHAR_TabMisc:
            box = layout.box()
            for arr in [["CHAR_ConvertScene", "Convert Scene"], ["CHAR_ForceFrontXAxis", "Force Front XAxis"], ["CHAR_ConvertSceneUnit", "Convert Scene Unit"], ["CHAR_OverrideFullName", "Override Full Name"]]:
                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text=arr[1])
                split = split.split()
                col = split.column()
                col.prop(preferences, arr[0], text="")

        layout.prop(preferences, "CHAR_TabMaterial", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.CHAR_TabMaterial], emboss=False)
        if preferences.CHAR_TabMaterial:
            box = layout.box()
            for arr in [["CHAR_MaterialSearchLocation", "Search Location"], ["CHAR_ImportMaterial", "Import Material"], ["CHAR_ImportTexture", "Import Texture"], ["CHAR_InvertNormalMaps", "Invert Normal Maps"], ["CHAR_ReorderMaterialToFBXOrder", "Reorder Material To FBX Order"]]:
                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text=arr[1])
                split = split.split()
                col = split.column()
                col.prop(preferences, arr[0], text="")