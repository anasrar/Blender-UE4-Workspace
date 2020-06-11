import bpy
from bpy.types import (Panel, Operator)

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_AnimationUnrealEnginePanel"
    bl_parent_id = "UE4WORKSPACE_PT_AnimationPanel"
    bl_label = "Unreal Engine Export Setting"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons[__package__].preferences

        layout.prop(preferences, "ANIM_TabAnimation", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.ANIM_TabAnimation], emboss=False)
        if preferences.ANIM_TabAnimation:
            box = layout.box()
            for arr in [["ANIM_AnimationLength", "Animation Length"], ["ANIM_ImportMeshesInBoneHierarchy", "Import Meshes in Bone Hierarchy"], ["ANIM_FrameImportRangeMin", "Frame Import Range"], ["ANIM_UseDefaultSampleRate", "Use Default Sample Rate"], ["ANIM_CustomSampleRate", "Custom Sample Rate"], ["ANIM_ImportCustomAttribute", "Import Custom Attribute"], ["ANIM_DeleteExistingCustomAttributeCurves", "Delete Existing Custom Attribute Curves"], ["ANIM_ImportBoneTracks", "Import Bone Tracks"], ["ANIM_SetMaterialDriveParameterOnCustomAttribute", "Set Material Curve Type"], ["ANIM_MaterialCurveSuffixes", "Material Curve Suffixes"], ["ANIM_RemoveRedundantKeys", "Remove Redundant Keys"], ["ANIM_DeleteExistingMorphTargetCurves", "Delete Existing Morph Target Curves"], ["ANIM_DoNotImportCurveWithZero", "Do not Import Curve With 0 Values"], ["ANIM_PreserveLocalTransform", "Preserve Local Transform"]]:
                if arr[0] == "ANIM_FrameImportRangeMin":
                    col = box.column()
                    row = col.row()
                    split = row.split(factor=0.6)
                    col = split.column()
                    col.alignment = "RIGHT"
                    col.label(text=arr[1])
                    split = split.split()
                    col = split.column(align=True)
                    col.enabled = (preferences.ANIM_AnimationLength == "FBXALIT_SET_RANGE")
                    col.prop(preferences, arr[0], text="Min")
                    col.prop(preferences, "ANIM_FrameImportRangeMax", text="Max")
                elif arr[0] == "ANIM_MaterialCurveSuffixes":
                    arrSuffixs = preferences.ANIM_MaterialCurveSuffixes.split("|")
                    col = box.column()
                    row = col.row()
                    split = row.split(factor=0.6)
                    col = split.column()
                    col.alignment = "RIGHT"
                    col.label(text=arr[1])
                    split = split.split()
                    row = split.row(align=True)
                    row.label(text=str(len(arrSuffixs)) + " Array" if preferences.ANIM_MaterialCurveSuffixes else "0 Array")
                    row.alignment = "RIGHT"
                    # operator location on UE4WS_Animation.py
                    row.operator("ue4workspace.animaddsuffixe",icon="PLUS", text="")
                    row.operator("ue4workspace.animclearsuffixes",icon="TRASH", text="")
                    if preferences.ANIM_MaterialCurveSuffixes:
                        for index, surffix in enumerate(arrSuffixs):
                            col = box.column()
                            row = col.row()
                            split = row.split(factor=0.6)
                            col = split.column()
                            col.alignment = "RIGHT"
                            col.label(text=str(index))
                            split = split.split()
                            row = split.row(align=True)
                            row.label(text=surffix)
                            # operator location on UE4WS_Animation.py
                            op = row.operator("ue4workspace.animeditvaluesuffixe",icon="GREASEPENCIL", text="")
                            op.idx = index
                            op.val = surffix
                            row.operator("ue4workspace.animremoveindexsuffixe",icon="TRASH", text="").idx = index
                else:
                    col = box.column()
                    row = col.row()
                    split = row.split(factor=0.6)
                    col = split.column()
                    col.alignment = "RIGHT"
                    col.label(text=arr[1])
                    split = split.split()
                    col = split.column()
                    col.prop(preferences, arr[0], text="")

        layout.prop(preferences, "ANIM_TabTransform", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.ANIM_TabTransform], emboss=False)
        if preferences.ANIM_TabTransform:
            box = layout.box()
            for arr in [["ANIM_ImportTranslation", "Import Translation"], ["ANIM_ImportRotation", "Import Translation"], ["ANIM_ImportUniformScale", "Import Uniform Scale"]]:
                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text=arr[1])
                split = split.split()
                col = split.column()
                col.prop(preferences, arr[0], text="")

        layout.prop(preferences, "ANIM_TabMisc", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.ANIM_TabMisc], emboss=False)
        if preferences.ANIM_TabMisc:
            box = layout.box()
            for arr in [["ANIM_ConvertScene", "Convert Scene"], ["ANIM_ForceFrontXAxis", "Force Front XAxis"], ["ANIM_ConvertSceneUnit", "Convert Scene Unit"], ["ANIM_OverrideFullName", "Override Full Name"]]:
                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text=arr[1])
                split = split.split()
                col = split.column()
                col.prop(preferences, arr[0], text="")