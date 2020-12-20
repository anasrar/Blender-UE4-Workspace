import bpy
from bpy.utils import register_class, unregister_class
from bpy.types import Operator
from . utils import BuildStringMap

class OP_CopyTransformToUnrealEngineMap(Operator):
    bl_idname = 'ue4workspace.copy_transform_to_unreal_engine_map'
    bl_label = 'Copy Transform To Unreal Engine Map'
    bl_description = 'Copy Transform Selected Object To Unreal Engine Map\nOnly Support Static Mesh'

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        selected_objects = context.selected_objects
        selected_objects = [obj for obj in selected_objects if obj.type == 'MESH' and not obj.data.is_custom_collision]

        context.window_manager.clipboard = BuildStringMap.generate_string(selected_objects)

        self.report({'INFO'}, 'copy transform success')

        return {'FINISHED'}

def draw_menu(self, context):
    layout = self.layout

    if context.mode == 'OBJECT':
        layout.separator()
        layout.operator('ue4workspace.copy_transform_to_unreal_engine_map')

list_class_to_register = [
    OP_CopyTransformToUnrealEngineMap
]

def register():
    bpy.types.VIEW3D_MT_object_context_menu.append(draw_menu)

    for x in list_class_to_register:
        register_class(x)

def unregister():
    bpy.types.VIEW3D_MT_object_context_menu.remove(draw_menu)

    for x in list_class_to_register[::-1]:
        unregister_class(x)