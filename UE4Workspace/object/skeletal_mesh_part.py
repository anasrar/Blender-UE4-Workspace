import bpy
from bpy.utils import register_class, unregister_class
from .. utils.base import ObjectSubPanel

class PANEL(ObjectSubPanel):
    bl_idname = 'UE4WORKSPACE_PT_ObjectSkeletalMeshPartPanel'
    bl_label = 'Skeletal Mesh Part'

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type in ['ARMATURE']

    def draw(self, context):
        layout =  self.layout
        preferences = context.preferences.addons['UE4Workspace'].preferences
        active_object = context.active_object

        meshes = [obj for obj in active_object.children if obj.type == 'MESH']

        if bool(meshes):
            layout.box().label(text='Export Part')
            for obj in meshes:
                row = layout.box().row()
                split = row.split(factor=0.7)
                row = split.row()
                row.prop(obj.data, 'is_export_skeletal_mesh_part', text='')
                row.prop(obj, 'name', text='')
                split = split.split()
                row = split.row()
                row.alignment = 'RIGHT'
                row.operator('ue4workspace.toggle_visibility_object', icon=('HIDE_ON' if obj.hide_get() else 'HIDE_OFF'), text='', emboss=False).object_name = obj.name
                row.operator('ue4workspace.remove_object', icon='TRASH', text='', emboss=False).object_name = obj.name
        else:
            col = layout.box().column(align=True)
            col.label(text='This armature does not')
            col.label(text='have any mesh to export.')

list_class_to_register = [
    PANEL
]

def register():
    bpy.types.Mesh.is_export_skeletal_mesh_part = bpy.props.BoolProperty(
        name='Export Skeletal Mesh Part',
        description='If true, it will export the mesh',
        default=True
    )

    for x in list_class_to_register:
        register_class(x)

def unregister():
    del bpy.types.Mesh.is_export_skeletal_mesh_part

    for x in list_class_to_register[::-1]:
        unregister_class(x)