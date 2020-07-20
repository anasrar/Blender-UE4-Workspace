import bpy
from mathutils import Matrix
from bpy.props import (EnumProperty, StringProperty, PointerProperty)
from bpy.types import (Panel, Operator)

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_ObjectSkeletonPresetPanel"
    bl_parent_id = "UE4WORKSPACE_PT_ObjectPanel"
    bl_label = "Skeleton Preset"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        return context.active_object is not None and context.active_object.get("UE4RIG") and context.mode != "POSE"

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object

        row = layout.row()
        row.scale_y = 1.5
        # operator location on UE4WS_Character.py
        row.operator("ue4workspace.generaterig",icon="CON_ARMATURE", text="Generate Rig")
        row = layout.row()
        row.scale_y = 1.5
        # operator location on UE4WS_Character.py
        row.operator("ue4workspace.rotatebone",icon="BONE_DATA", text=("Create Preview Orient Bone", "Update Preview Orient Bone")[activeObject.get("UE4RIGHASTEMPBONE", False)])
        if activeObject.get("UE4RIGHASTEMPBONE", False):
            row = layout.row()
            row.scale_y = 1.5
            # operator location on UE4WS_Character.py
            row.operator("ue4workspace.characterremovetemporarybone",icon="BONE_DATA", text="Remove Preview Orient Bone")
        # add twist bone
        if context.mode == "EDIT_ARMATURE" and context.active_bone is not None and (context.active_bone.get("UE4RIGTYPE") in ["LEG_HUMAN", "ARM_HUMAN"] or context.active_bone.parent is not None and context.active_bone.parent.get("UE4RIGTYPE") in ["LEG_HUMAN", "ARM_HUMAN"]) and not "_twist_" in context.active_bone.name:
            row = layout.row()
            row.scale_y = 1.5
            # operator location on UE4WS_Character.py
            row.operator("ue4workspace.addtwistbone",icon="BONE_DATA", text="Add Twist Bone")
            if len([child for child in context.active_bone.children if child.name.split("_")[1] == "twist"]) != 0:
                row = layout.row()
                row.scale_y = 1.5
                # operator location on UE4WS_Character.py
                row.operator("ue4workspace.removetwistbone",icon="BONE_DATA", text="Remove Twist Bone")
