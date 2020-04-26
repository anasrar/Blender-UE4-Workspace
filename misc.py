import bpy
from bpy.props import (StringProperty)
from bpy.types import (Operator)

class PopUpWindow(Operator):
    bl_idname = "ue4workspace.popup"
    bl_label = "Message"

    msg: StringProperty(
        name = "message",
        description = "message",
        default = ""
    )

    def execute(self, context):
        self.report({"INFO"}, self.msg)
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 250)

    def draw(self, context):
        self.layout.label(text=self.msg)
