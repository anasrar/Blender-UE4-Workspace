import bpy
from bpy.types import (Panel)

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_CreditPanel"
    bl_label = "Credit"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    addonVersion = None

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        col = box.column(align=True)
        # Credit Box
        row = col.row()
        row.alignment = "CENTER"
        row.label(text="Unreal Engine 4")
        row = col.row()
        row.alignment = "CENTER"
        row.label(text="Workspace")
        row = col.row()
        row.alignment = "CENTER"
        row.label(text= "Version : " + (".".join(str(x) for x in self.addonVersion)))
        # Big Button Documentation
        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("wm.url_open",icon="INFO", text="DOCUMENTATION").url="https://anasrar.github.io/Blender-UE4-Workspace/"
        # My Link
        # col = layout.column(align=True)
        # row = col.row(align=True)
        # row.scale_y = 1.2
        # row.operator("wm.url_open",icon="LINKED", text="Youtube").url="https://www.youtube.com/channel/UCSPcMosP3pxsP8a9t9AGwaQ/"
        # row.operator("wm.url_open",icon="LINKED", text="Github").url="https://github.com/anasrar"
        # row.operator("wm.url_open",icon="LINKED", text="Blog").url="https://anasrar.github.io/blog/"