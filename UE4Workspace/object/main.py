import bpy
from bpy.utils import register_class, unregister_class
from .. utils.base import ObjectPanel

from . import custom_collision
from . import socket
from . import level_of_detail
from . import skeletal_mesh_part

class PANEL(ObjectPanel):
    bl_idname = 'UE4WORKSPACE_PT_ObjectPanel'
    bl_label = 'Object'

    def draw(self, context):
        pass

list_class_to_register = [
    custom_collision,
    socket,
    level_of_detail,
    skeletal_mesh_part
]

def register():
    register_class(PANEL)
    for x in list_class_to_register:
        x.register()

def unregister():
    unregister_class(PANEL)
    for x in list_class_to_register[::-1]:
        x.unregister()