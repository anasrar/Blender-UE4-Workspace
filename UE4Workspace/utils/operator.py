import bpy
from bpy.utils import register_class, unregister_class
from bpy.types import Operator

class OP_ToggleVisibilityObject(Operator):
    bl_idname = 'ue4workspace.toggle_visibility_object'
    bl_label = 'Toggle Visibility Object'
    bl_description = 'Toggle Visibility Object'
    bl_options = {'UNDO'}

    object_name: bpy.props.StringProperty(name='Object name')

    def execute(self, context):
        obj = context.scene.objects[self.object_name]
        obj.hide_set(not obj.hide_get())
        return {'FINISHED'}

class OP_RemoveObject(Operator):
    bl_idname = 'ue4workspace.remove_object'
    bl_label = 'Remove Object'
    bl_description = 'Remove Object'
    bl_options = {'UNDO'}

    object_name: bpy.props.StringProperty(name='Object name')

    def execute(self, context):
        obj = context.scene.objects[self.object_name]
        bpy.data.objects.remove(obj, do_unlink=True)
        return {'FINISHED'}

list_class_to_register = [
    OP_ToggleVisibilityObject,
    OP_RemoveObject
]

def register():
    for x in list_class_to_register:
        register_class(x)

def unregister():
    for x in list_class_to_register[::-1]:
        unregister_class(x)