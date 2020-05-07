import bpy
from bpy.types import (Panel, Operator)

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_CharacterFBXOption"
    bl_parent_id = "UE4WORKSPACE_PT_CharacterPanel"
    bl_label = "FBX Export Setting"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons[__package__].preferences

        layout.prop(preferences, "CHAR_FBXTabTransform", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.CHAR_FBXTabTransform], emboss=False)
        if preferences.CHAR_FBXTabTransform:
            box = layout.box()
            for arr in [["CHAR_FBXGlobalScale", "Scale"], ["CHAR_FBXApplyScaleOptions", "Apply Scalings"], ["CHAR_FBXAxisForward", "Forward"], ["CHAR_FBXAxisUp", "Up"], ["CHAR_FBXApplyUnitScale", "Apply Unit"], ["CHAR_FBXBakeSpaceTransform", "!EXPERIMENTAL! Apply Transform"]]:
                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text=arr[1])
                split = split.split()
                col = split.column()
                col.prop(preferences, arr[0], text="")

        layout.prop(preferences, "CHAR_FBXTabGeometry", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.CHAR_FBXTabGeometry], emboss=False)
        if preferences.CHAR_FBXTabGeometry:
            box = layout.box()
            for arr in [["CHAR_FBXMeshSmoothType", "Smoothing"], ["CHAR_FBXUseSubsurf", "Export Subdivision Surface"], ["CHAR_FBXUseMeshModifiers", "Apply Modifiers"], ["CHAR_FBXUseMeshEdges", "Loose Edges"], ["CHAR_FBXUseTSpace", "Tangent Space"]]:
                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text=arr[1])
                split = split.split()
                col = split.column()
                col.prop(preferences, arr[0], text="")

        layout.prop(preferences, "CHAR_FBXTabArmature", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.CHAR_FBXTabArmature], emboss=False)
        if preferences.CHAR_FBXTabArmature:
            box = layout.box()
            for arr in [["CHAR_FBXPrimaryBoneAxis", "Primary Bone Axis"], ["CHAR_FBXSecondaryBoneAxis", "Secondary Bone Axis"], ["CHAR_FBXArmatureFBXNodeType", "Armature FBXNode Type"], ["CHAR_FBXOnlyDeformBones", "Only Deform Bones"], ["CHAR_FBXAddLeafBones", "Add Leaf Bones"]]:
                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text=arr[1])
                split = split.split()
                col = split.column()
                col.prop(preferences, arr[0], text="")