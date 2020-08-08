import bpy
from bpy.types import (Panel, Operator)

# PANEL

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_ExportOptionImportAssetsFBXOptionPanel"
    bl_parent_id = "UE4WORKSPACE_PT_ExportOptionImportAssetsPanel"
    bl_label = "FBX Import Setting"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons[__package__].preferences

        layout.prop(preferences, "IMPORTASSETS_TabFBXInclude", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.IMPORTASSETS_TabFBXInclude], emboss=False)
        if preferences.IMPORTASSETS_TabFBXInclude:
            box = layout.box()
            for arr in [["IMPORTASSETS_FBXCustomNormals", "Custom Normals"], ["IMPORTASSETS_FBXSubdivisionData", "Subdivision Data"], ["IMPORTASSETS_FBXCustomProperties", "Custom Properties"], ["IMPORTASSETS_FBXImportEnums", "Import Enums As Strings"], ["IMPORTASSETS_FBXImageSearch", "Image Search"]]:
                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text=arr[1])
                split = split.split()
                col = split.column()
                col.prop(preferences, arr[0], text="")

        layout.prop(preferences, "IMPORTASSETS_TabFBXOrientation", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.IMPORTASSETS_TabFBXOrientation], emboss=False)
        if preferences.IMPORTASSETS_TabFBXOrientation:
            box = layout.box()
            for arr in [["IMPORTASSETS_FBXManualOrientation", "Manual Orientation"], ["IMPORTASSETS_FBXAxisForward", "Forward"], ["IMPORTASSETS_FBXAxisUp", "Up"]]:
                if arr[0] == "IMPORTASSETS_FBXManualOrientation":
                    col = box.column()
                    row = col.row()
                    split = row.split(factor=0.6)
                    col = split.column()
                    col.alignment = "RIGHT"
                    col.label(text=arr[1])
                    split = split.split()
                    col = split.column()
                    col.prop(preferences, arr[0], text="")
                else:
                    col = box.column()
                    col.enabled = preferences.IMPORTASSETS_FBXManualOrientation
                    row = col.row()
                    split = row.split(factor=0.6)
                    col = split.column()
                    col.alignment = "RIGHT"
                    col.label(text=arr[1])
                    split = split.split()
                    col = split.column()
                    col.prop(preferences, arr[0], text="")

        layout.prop(preferences, "IMPORTASSETS_TabFBXAnimation", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.IMPORTASSETS_TabFBXAnimation], emboss=False)
        if preferences.IMPORTASSETS_TabFBXAnimation:
            box = layout.box()
            for arr in [["IMPORTASSETS_FBXImportAnimation", "Import Animation"], ["IMPORTASSETS_FBXAnimationOffset", "Animation Offset"]]:
                if arr[0] == "IMPORTASSETS_FBXImportAnimation":
                    col = box.column()
                    row = col.row()
                    split = row.split(factor=0.6)
                    col = split.column()
                    col.alignment = "RIGHT"
                    col.label(text=arr[1])
                    split = split.split()
                    col = split.column()
                    col.prop(preferences, arr[0], text="")
                else:
                    col = box.column()
                    col.enabled = preferences.IMPORTASSETS_FBXImportAnimation
                    row = col.row()
                    split = row.split(factor=0.6)
                    col = split.column()
                    col.alignment = "RIGHT"
                    col.label(text=arr[1])
                    split = split.split()
                    col = split.column()
                    col.prop(preferences, arr[0], text="")

        layout.prop(preferences, "IMPORTASSETS_TabFBXArmature", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.IMPORTASSETS_TabFBXArmature], emboss=False)
        if preferences.IMPORTASSETS_TabFBXArmature:
            box = layout.box()
            for arr in [["IMPORTASSETS_FBXIgnoreLeafBones", "Ignore Leaf Bones"], ["IMPORTASSETS_FBXForceConnectChildren", "Force Connect Children"], ["IMPORTASSETS_FBXAutomaticBoneOrientation", "Automatic Bone Orientation"], ["IMPORTASSETS_FBXPrimaryBoneAxis", "Primary Bone Axis"], ["IMPORTASSETS_FBXSecondaryBoneAxis", "Secondary Bone Axis"]]:
                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text=arr[1])
                split = split.split()
                col = split.column()
                col.prop(preferences, arr[0], text="")