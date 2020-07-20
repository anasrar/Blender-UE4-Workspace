import bpy
from mathutils import Matrix
from bpy.props import (EnumProperty, StringProperty, PointerProperty)
from bpy.types import (Panel, Operator)

# PANEL

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_ObjectPanel"
    bl_label = "Object"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    remote = None

    @classmethod
    def poll(self, context):
        return True

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons[__package__].preferences

# OPERATOR

class OP_ToggleVisibilityObject(Operator):
    bl_idname = "ue4workspace.togglevisibilityobject"
    bl_label = "UE4Workspace Operator"
    bl_description = "Toggle Visibility Object"
    bl_options = {"UNDO"}

    objName: StringProperty(name="Object name")

    def execute(self, context):
        obj = context.scene.objects[self.objName]
        obj.hide_set(not obj.hide_get())
        return {"FINISHED"}

class OP_RemoveObject(Operator):
    bl_idname = "ue4workspace.removeobject"
    bl_label = "UE4Workspace Operator"
    bl_description = "Remove Object"
    bl_options = {"UNDO"}

    objName: StringProperty(name="Object name")

    def execute(self, context):
        obj = context.scene.objects[self.objName]
        bpy.data.objects.remove(obj, do_unlink=True)
        return {"FINISHED"}

# operator export

Ops = [
    OP_ToggleVisibilityObject,
    OP_RemoveObject
]