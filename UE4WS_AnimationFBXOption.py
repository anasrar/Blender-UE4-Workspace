import bpy
from bpy.types import (Panel, Operator)

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_AnimationFBXOption"
    bl_parent_id = "UE4WORKSPACE_PT_AnimationPanel"
    bl_label = "FBX Export Setting"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons[__package__].preferences

        layout.prop(preferences, "ANIM_FBXTabTransform", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.ANIM_FBXTabTransform], emboss=False)
        if preferences.ANIM_FBXTabTransform:
            box = layout.box()
            for arr in [["ANIM_FBXGlobalScale", "Scale"], ["ANIM_FBXApplyScaleOptions", "Apply Scalings"], ["ANIM_FBXAxisForward", "Forward"], ["ANIM_FBXAxisUp", "Up"], ["ANIM_FBXApplyUnitScale", "Apply Unit"], ["ANIM_FBXBakeSpaceTransform", "!EXPERIMENTAL! Apply Transform"]]:
                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text=arr[1])
                split = split.split()
                col = split.column()
                col.prop(preferences, arr[0], text="")

        layout.prop(preferences, "ANIM_FBXTabArmature", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.ANIM_FBXTabArmature], emboss=False)
        if preferences.ANIM_FBXTabArmature:
            box = layout.box()
            for arr in [["ANIM_FBXPrimaryBoneAxis", "Primary Bone Axis"], ["ANIM_FBXSecondaryBoneAxis", "Secondary Bone Axis"], ["ANIM_FBXArmatureFBXNodeType", "Armature FBXNode Type"], ["ANIM_FBXOnlyDeformBones", "Only Deform Bones"], ["ANIM_FBXAddLeafBones", "Add Leaf Bones"]]:
                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text=arr[1])
                split = split.split()
                col = split.column()
                col.prop(preferences, arr[0], text="")

        layout.prop(preferences, "ANIM_FBXTabBakeAnimation", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.ANIM_FBXTabBakeAnimation], emboss=False)
        if preferences.ANIM_FBXTabBakeAnimation:
            box = layout.box()
            for arr in [["ANIM_FBXKeyAllBones", "Key All Bones"], ["ANIM_FBXForceStartEndKeying", "Force Start/End Keying"], ["ANIM_FBXSamplingRate", "Sampling Rate"], ["ANIM_FBXSimplify", "Simplify"]]:
                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text=arr[1])
                split = split.split()
                col = split.column()
                col.prop(preferences, arr[0], text="")