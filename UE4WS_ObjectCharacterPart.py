import bpy
from mathutils import Matrix
from bpy.props import (EnumProperty, BoolProperty, FloatVectorProperty, StringProperty, PointerProperty)
from bpy.types import (Panel, Operator)

# PROPS

Props = [
    {
        "type": "mesh",
        "name": "isExportCharacterPart",
        "value": BoolProperty(
            name="Export Character Part",
            description="If true, it will export the mesh",
            default=True
        ),
        "resetVariable": False
    }
]

# PANEL

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_ObjectCharacterPartPanel"
    bl_parent_id = "UE4WORKSPACE_PT_ObjectPanel"
    bl_label = "Character Part"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        return context.active_object is not None and context.active_object.type in ["ARMATURE"]

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object

        if list(activeObject.children):
            characterPartObjects = [obj for obj in activeObject.children if obj.type == "MESH"]
            layout.label(text="Export Part")
            box = layout.box()
            for obj in characterPartObjects:
                row = box.row()
                split = row.split(factor=0.7)
                row = split.row()
                row.prop(obj.data, "isExportCharacterPart", text="")
                row.prop(obj, "name", text="")
                split = split.split()
                row = split.row()
                row.alignment = "RIGHT"
                row.operator("ue4workspace.togglevisibilityobject",icon=("HIDE_OFF", "HIDE_ON")[obj.hide_get()], text="", emboss=False).objName = obj.name
                row.operator("ue4workspace.removeobject",icon="TRASH", text="", emboss=False).objName = obj.name
        else:
            col = layout.column(align=True)
            col.label(text="This armature does not")
            col.label(text="have any mesh to export.")

# OPERATOR

class OP_SomeOperatorHere(Operator):
    bl_idname = "ue4workspace.someoperatorhere"
    bl_label = "Some Name Operator Here"
    bl_description = "Some Description Operator Here"
    bl_options = {"UNDO"}

    @classmethod
    def poll(self, context):
        return True

    def execute(self, context):
        return {"FINISHED"}

# operator export

Ops = [
]