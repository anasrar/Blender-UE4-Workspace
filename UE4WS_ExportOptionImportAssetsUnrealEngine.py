import bpy
from bpy.types import (Panel, Operator)

# PANEL

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_ExportOptionImportAssetsUnrealEnginePanel"
    bl_parent_id = "UE4WORKSPACE_PT_ExportOptionImportAssetsPanel"
    bl_label = "Unreal Engine Import Setting"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons[__package__].preferences

        layout.prop(preferences, "IMPORTASSETS_TabExporter", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.IMPORTASSETS_TabExporter], emboss=False)
        if preferences.IMPORTASSETS_TabExporter:
            box = layout.box()
            for arr in [["IMPORTASSETS_FBXExportCompatibility", "FBX Export Compatibility"], ["IMPORTASSETS_ASCII", "ASCII"], ["IMPORTASSETS_ForceFrontXAxis", "Force Front X Axis"]]:
                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text=arr[1])
                split = split.split()
                col = split.column()
                col.prop(preferences, arr[0], text="")

        layout.prop(preferences, "IMPORTASSETS_TabMesh", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.IMPORTASSETS_TabMesh], emboss=False)
        if preferences.IMPORTASSETS_TabMesh:
            box = layout.box()
            for arr in [["IMPORTASSETS_VertexColor", "Vertex Color"], ["IMPORTASSETS_LevelOfDetail", "Level Of Detail"]]:
                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text=arr[1])
                split = split.split()
                col = split.column()
                col.prop(preferences, arr[0], text="")

        layout.prop(preferences, "IMPORTASSETS_TabStaticMesh", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.IMPORTASSETS_TabStaticMesh], emboss=False)
        if preferences.IMPORTASSETS_TabStaticMesh:
            box = layout.box()
            for arr in [["IMPORTASSETS_Collision", "Collision"]]:
                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text=arr[1])
                split = split.split()
                col = split.column()
                col.prop(preferences, arr[0], text="")

        layout.prop(preferences, "IMPORTASSETS_TabSkeletalMesh", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.IMPORTASSETS_TabSkeletalMesh], emboss=False)
        if preferences.IMPORTASSETS_TabSkeletalMesh:
            box = layout.box()
            for arr in [["IMPORTASSETS_ExportMorphTargets", "Export Morph Targets"]]:
                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text=arr[1])
                split = split.split()
                col = split.column()
                col.prop(preferences, arr[0], text="")

        layout.prop(preferences, "IMPORTASSETS_TabAnimation", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.IMPORTASSETS_TabAnimation], emboss=False)
        if preferences.IMPORTASSETS_TabAnimation:
            box = layout.box()
            for arr in [["IMPORTASSETS_ExportPreviewMesh", "Export Preview Mesh"], ["IMPORTASSETS_MapSkeletalMotionToRoot", "Map Skeletal Motion To Root"], ["IMPORTASSETS_ExportLocalTime", "Export Local Time"]]:
                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text=arr[1])
                split = split.split()
                col = split.column()
                col.prop(preferences, arr[0], text="")