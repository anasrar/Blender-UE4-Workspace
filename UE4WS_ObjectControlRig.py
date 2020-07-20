import bpy
from mathutils import Matrix
from bpy.props import (EnumProperty, StringProperty, PointerProperty)
from bpy.types import (Panel, Operator)

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_ObjectControlRigPanel"
    bl_parent_id = "UE4WORKSPACE_PT_ObjectPanel"
    bl_label = "Control Rig"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        return context.active_object is not None and context.active_object.get("UE4RIGGED") and context.mode == "POSE"

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object

        poseBones = activeObject.pose.bones

        IKBones = [key for key in activeObject.keys() if key.startswith("CR_IK_")]

        if IKBones:
            row = layout.row()
            row.alignment = "RIGHT"
            row.label(text="IK influence")
            for key in IKBones:
                label = key.replace("CR_IK_", "")
                col = layout.column()
                row = col.row()
                split = row.split(factor=0.5)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text=label)
                split = split.split()
                col = split.column()
                col.prop(activeObject, "[\"" + key + "\"]", text="", slider=True)
                # row = layout.row(align=True)
                # row.scale_y = 1.2
                # row.operator("wm.url_open",icon="SNAP_ON", text="Snap FK>IK")
                # row.operator("wm.url_open",icon="SNAP_ON", text="Snap IK>FK")

        lookControlBones = [key for key in activeObject.keys() if key.startswith("CR_LOOK_")]

        if lookControlBones:
            row = layout.row()
            row.alignment = "RIGHT"
            row.label(text="Look Inherit Rotation From Head")
            for key in lookControlBones:
                label = key.replace("CR_LOOK_", "")
                col = layout.column()
                row = col.row()
                split = row.split(factor=0.5)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text=label)
                split = split.split()
                col = split.column()
                col.prop(activeObject, "[\"" + key + "\"]", text="", slider=True)
