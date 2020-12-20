import math
import bpy
from mathutils import Vector
from bpy.utils import register_class, unregister_class
from bpy.types import Operator, PropertyGroup
from .. utils.base import ObjectSubPanel

class OP_GenerateLODs(Operator):
    bl_idname = 'ue4workspace.generate_lods'
    bl_label = 'Generate LODs'
    bl_options = {'UNDO', 'REGISTER'}

    total: bpy.props.IntProperty(
        name='Total',
        default=3,
        min=1,
        max=7
    )

    angel: bpy.props.FloatProperty(
        name='Angel',
        default=0.0,
        min=0.0,
        max=math.pi*2,
        subtype='ANGLE',
        unit='ROTATION'
    )

    margin: bpy.props.FloatProperty(
        name='Margin',
        default=1.0,
        min=0.0,
        subtype='DISTANCE',
        unit='LENGTH'
    )

    ratio: bpy.props.FloatProperty(
        name='Ratio',
        default=1.0,
        min=0.0,
        max=10.0
    )

    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        return active_object is not None and active_object.type in ['MESH'] and not 'ARMATURE' in [mod.type for mod in active_object.modifiers] and not active_object.data.mesh_as_lod

    def execute(self, context):
        active_object = context.active_object
        active_object_world_location = active_object.matrix_world.to_translation()

        vector_angle = Vector((math.cos(self.angel), math.sin(self.angel), 0))
        vector_margin = vector_angle * self.margin

        active_object.data.lods.clear()
        for index in range(self.total):
            index += 1
            lod_obj = bpy.data.objects.new(active_object.name, active_object.data.copy())
            lod_obj.matrix_world = active_object.matrix_world.copy()

            for collection in active_object.users_collection:
                collection.objects.link(lod_obj)
            lod_obj.matrix_world.translation = active_object_world_location + ((active_object.dimensions * vector_angle) * index) + (vector_margin * index)

            lod_obj.data.mesh_as_lod = True
            lod_obj.parent = active_object
            lod_obj.matrix_parent_inverse = active_object.matrix_world.inverted()

            decimate = lod_obj.modifiers.new('LOD', 'DECIMATE')
            decimate.decimate_type = 'COLLAPSE'
            decimate.ratio = ((0.1 * self.ratio) / self.total) * (self.total - (index - 1))
            decimate.use_collapse_triangulate = True
            decimate.use_symmetry = True

            lod_data = active_object.data.lods.add()
            lod_data.obj = lod_obj
        return {'FINISHED'}

class OP_AddLODSlot(Operator):
    bl_idname = 'ue4workspace.add_lod_slot'
    bl_label = 'Add LOD Slot'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        return active_object is not None and active_object.type in ['MESH'] and not 'ARMATURE' in [mod.type for mod in active_object.modifiers] and 7 > len(active_object.data.lods)

    def execute(self, context):
        active_object = context.active_object
        active_object.data.lods.add()
        return {'FINISHED'}

class OP_RemoveLODSlot(Operator):
    bl_idname = 'ue4workspace.remove_lod_slot'
    bl_label = 'Remove LOD Slot'
    bl_options = {'UNDO'}

    index: bpy.props.IntProperty(default=-1)

    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        return active_object is not None and active_object.type in ['MESH'] and not 'ARMATURE' in [mod.type for mod in active_object.modifiers]

    def execute(self, context):
        active_object = context.active_object
        if self.index > -1:
            active_object.data.lods.remove(self.index)
        return {'FINISHED'}

class PG_LOD(PropertyGroup):

    screen_size: bpy.props.FloatProperty(
        name='LOD Screen Size',
        description='Set a screen size value for LOD',
        default=0.0
    )

    obj: bpy.props.PointerProperty(
        name='LOD Object',
        description='Mesh to LOD',
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'MESH' and not 'ARMATURE' in [mod.type for mod in obj.modifiers] and obj != bpy.context.active_object and obj.data.mesh_as_lod
    )

class PANEL(ObjectSubPanel):
    bl_idname = 'UE4WORKSPACE_PT_ObjectLODPanel'
    bl_label = 'Level of Detail'

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type in ['MESH'] and not 'ARMATURE' in [mod.type for mod in context.active_object.modifiers]

    def draw(self, context):
        layout =  self.layout
        preferences = context.preferences.addons['UE4Workspace'].preferences
        active_object = context.active_object

        box = layout.box()

        split = box.column().split(factor=0.6)
        col = split.column()
        col.alignment = 'RIGHT'
        col.label(text='Mesh as LOD')
        col = split.column()
        col.prop(active_object.data, 'mesh_as_lod', text='')

        if not active_object.data.mesh_as_lod:
            row = layout.box().row()
            row.scale_y = 1.5
            row.operator('ue4workspace.generate_lods', icon='MOD_DECIM')

            split = box.column().split(factor=0.6)
            col = split.column()
            col.alignment = 'RIGHT'
            col.label(text='Auto LOD Screen Size')
            col = split.column()
            col.prop(active_object.data, 'auto_compute_lod_screen_size', text='')

            row = layout.box().row()
            row.scale_y = 1.5
            row.operator('ue4workspace.add_lod_slot', icon='PRESET_NEW')

            box = layout.box()

            split = box.split(factor=0.6)
            col = split.column()
            col.alignment = 'RIGHT'
            col.label(text='LOD 0')
            col = split.column()
            col.label(text=active_object.name, icon='MESH_CUBE')

            if not active_object.data.auto_compute_lod_screen_size:
                split = box.split(factor=0.6)
                col = split.column()
                col.alignment = 'RIGHT'
                col.label(text='Screen Size')
                col = split.column()
                col.prop(active_object.data, 'lod_0_screen_size', text='')

            for index, lod in enumerate(active_object.data.lods, start=1):
                box = layout.box()

                split = box.split(factor=0.6)
                col = split.column()
                row = col.row(align=True)
                row.operator('ue4workspace.remove_lod_slot', icon='X', text='').index = index - 1
                sub = row.row()
                sub.alignment = 'RIGHT'
                sub.scale_x = 2.0
                sub.label(text='LOD ' + str(index))
                col = split.column()
                col.prop(lod, 'obj', text='', icon='MESH_CUBE')

                if not active_object.data.auto_compute_lod_screen_size:
                    split = box.split(factor=0.6)
                    col = split.column()
                    col.alignment = 'RIGHT'
                    col.label(text='Screen Size')
                    col = split.column()
                    col.prop(lod, 'screen_size', text='')

                if lod.obj:
                    decimate = lod.obj.modifiers.get('LOD', False)
                    if decimate:
                        split = box.split(factor=0.6)
                        col = split.column()
                        col.alignment = 'RIGHT'
                        col.label(text='Ratio')
                        col = split.column()
                        col.prop(decimate, 'ratio', text='', slider=True)

list_class_to_register = [
    PG_LOD,
    OP_GenerateLODs,
    OP_AddLODSlot,
    OP_RemoveLODSlot,
    PANEL
]

def register():

    bpy.types.Mesh.mesh_as_lod = bpy.props.BoolProperty(
        name='Mesh as LOD',
        description='If checked, will not export as static mesh instead will be a part of LOD',
        default=False
    )

    bpy.types.Mesh.auto_compute_lod_screen_size = bpy.props.BoolProperty(
        name='Auto Compute LOD ScreenSize',
        description='If checked, the editor will automatically compute screen size values for the static mesh’s LODs. If unchecked, the user can enter custom screen size values for each LOD',
        default=True
    )

    bpy.types.Mesh.lod_0_screen_size = bpy.props.FloatProperty(
        name='LOD 0 Screen Size',
        description='Set a screen size value for LOD 0',
        default=1.0
    )

    for x in list_class_to_register:
        register_class(x)

    bpy.types.Mesh.lods = bpy.props.CollectionProperty(type=PG_LOD)

def unregister():
    del bpy.types.Mesh.mesh_as_lod
    del bpy.types.Mesh.auto_compute_lod_screen_size

    for x in list_class_to_register[::-1]:
        unregister_class(x)

    del bpy.types.Mesh.lods