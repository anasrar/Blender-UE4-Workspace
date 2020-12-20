import bpy
import bpy
from bpy.utils import register_class, unregister_class
from bpy.types import Panel

class PANEL(Panel):
    bl_idname = 'UE4WORKSPACE_PT_CreditPanel'
    bl_label = 'Credit'
    bl_category = 'UE4Workspace'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    addonVersion = None

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        col = box.column(align=True)
        # Credit Box
        row = col.row()
        row.alignment = 'CENTER'
        row.label(text='Unreal Engine 4')
        row = col.row()
        row.alignment = 'CENTER'
        row.label(text='Workspace')
        row = col.row()
        row.alignment = 'CENTER'
        row.label(text= 'Version : 2.0.0 Alpha')
        # Big Button Documentation
        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator('wm.url_open',icon='INFO', text='DOCUMENTATION').url='https://anasrar.github.io/Blender-UE4-Workspace/'

list_class_to_register = [
    PANEL
]

def register():
    for x in list_class_to_register:
        register_class(x)

def unregister():
    for x in list_class_to_register[::-1]:
        unregister_class(x)