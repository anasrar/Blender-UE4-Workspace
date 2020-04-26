import bpy
from bpy.types import (Panel, Operator)

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_StaticMeshFBXOption"
    bl_parent_id = "UE4WORKSPACE_PT_StaticMeshPanel"
    bl_label = "FBX Export Setting"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons[__package__].preferences

        layout.prop(preferences, "SM_FBXTabTransform", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.SM_FBXTabTransform], emboss=False)
        if preferences.SM_FBXTabTransform:
            box = layout.box()
            for arr in [["SM_FBXGlobalScale", "Scale"], ["SM_FBXApplyScaleOptions", "Apply Scalings"], ["SM_FBXAxisForward", "Forward"], ["SM_FBXAxisUp", "Up"], ["SM_FBXApplyUnitScale", "Apply Unit"], ["SM_FBXBakeSpaceTransform", "!EXPERIMENTAL! Apply Transform"]]:
                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text=arr[1])
                split = split.split()
                col = split.column()
                col.prop(preferences, arr[0], text="")

        layout.prop(preferences, "SM_FBXTabGeometry", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.SM_FBXTabGeometry], emboss=False)
        if preferences.SM_FBXTabGeometry:
            box = layout.box()
            for arr in [["SM_FBXMeshSmoothType", "Smoothing"], ["SM_FBXUseSubsurf", "Export Subdivision Surface"], ["SM_FBXUseMeshModifiers", "Apply Modifiers"], ["SM_FBXUseMeshEdges", "Loose Edges"], ["SM_FBXUseTSpace", "Tangent Space"]]:
                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text=arr[1])
                split = split.split()
                col = split.column()
                col.prop(preferences, arr[0], text="")