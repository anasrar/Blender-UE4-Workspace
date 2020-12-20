import numpy as np
import bpy
from mathutils import Matrix, Vector
import bmesh
from bpy.utils import register_class, unregister_class
from bpy.types import Operator
from .. utils.base import ObjectSubPanel

class OP_CreateCollision(Operator):
    bl_idname = 'ue4workspace.create_collision'
    bl_label = 'Create Collsion'
    bl_description = 'Create Custom Collision Mesh\nSelect a Mesh > Edit Mode > Select Edge'
    bl_options = {'UNDO', 'REGISTER'}

    collision_name: bpy.props.StringProperty(
        name='Name',
        default='collision_name'
        )

    size: bpy.props.FloatProperty(
        name='Size',
        min=1,
        default=1.015
        )

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.active_object is not None and context.active_object.type == 'MESH' and context.active_object.mode == 'EDIT' and not context.active_object.data.is_custom_collision

    def execute(self, context):
        active_object = context.active_object

        active_object.update_from_editmode()
        selected_verts = [verts.co for verts in active_object.data.vertices if verts.select]

        # create collection (UE4CustomCollision) if not exist
        collection = bpy.data.collections.get('UE4CustomCollision', False)
        if (not collection):
            collection = bpy.data.collections.new('UE4CustomCollision')
            context.scene.collection.children.link(collection)

        bm = bmesh.new()

        median_space = Vector(np.median([list(vert) for vert in selected_verts], axis=0))

        # scale
        for vert_co in selected_verts:
            bmesh.ops.create_vert(bm, co=(median_space + self.size * (vert_co - median_space)))

        # convex hull
        bmesh.ops.convex_hull(bm, input=bm.verts, use_existing_faces=True)

        data_mesh = bpy.data.meshes.new(self.collision_name)
        bm.to_mesh(data_mesh)
        bm.free()

        obj = bpy.data.objects.new(self.collision_name, data_mesh)
        obj.data.is_custom_collision = True
        obj.show_wire = True
        obj.display_type = 'SOLID'
        obj.color = (0.15, 1.000000, 0, 0.200000)
        obj.parent = active_object
        context.space_data.shading.color_type = 'OBJECT'

        # create material (MAT_UE4CustomCollision) if not exist
        mat = bpy.data.materials.get('MAT_UE4CustomCollision')
        if mat is None:
            mat = bpy.data.materials.new(name='MAT_UE4CustomCollision')
            mat.blend_method = 'BLEND'
            mat.use_nodes = True
            mat.node_tree.nodes['Principled BSDF'].inputs[0].default_value = (0.15, 1.000000, 0, 1)
            mat.node_tree.nodes['Principled BSDF'].inputs[19].default_value = 0.1
            mat.use_fake_user = True

        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

        collection.objects.link(obj)

        return {'FINISHED'}

class OP_CollisionPicker(Operator):
    bl_idname = 'ue4workspace.collision_picker'
    bl_label = 'Collision Picker'
    bl_description = 'Create mesh into a custom collision'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.scene.collision_picker
        if context.mode == 'OBJECT':
            if context.active_object is not None and obj is not None and obj.type == 'MESH' and not obj.data.is_custom_collision and context.active_object is not obj:
                return True
        return False

    def execute(self, context):
        obj = context.scene.collision_picker
        context.scene.collision_picker = None

        obj.data.is_custom_collision = True
        obj.parent = context.active_object

        # clear local transform
        obj.matrix_parent_inverse = context.active_object.matrix_world.inverted()

        obj.show_wire = True
        obj.display_type = 'SOLID'
        obj.color = (0.15, 1.000000, 0, 0.200000)
        context.space_data.shading.color_type = 'OBJECT'

        # create material (MAT_UE4CustomCollision) if not exist
        mat = bpy.data.materials.get('MAT_UE4CustomCollision')
        if mat is None:
            mat = bpy.data.materials.new(name='MAT_UE4CustomCollision')
            mat.blend_method = 'BLEND'
            mat.use_nodes = True
            mat.node_tree.nodes['Principled BSDF'].inputs[0].default_value = (0.15, 1.000000, 0, 1)
            mat.node_tree.nodes['Principled BSDF'].inputs[19].default_value = 0.1
            mat.use_fake_user = True

        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

        old_collections = obj.users_collection
        collection = bpy.data.collections.get('UE4CustomCollision', False)
        if (not collection):
            collection = bpy.data.collections.new('UE4CustomCollision')
            context.scene.collection.children.link(collection)

        collection.objects.link(obj)
        for coll in old_collections:
            coll.objects.unlink(obj)

        return {'FINISHED'}

class PANEL(ObjectSubPanel):
    bl_idname = 'UE4WORKSPACE_PT_ObjectCustomCollisionPanel'
    bl_label = 'Custom Collision'

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type in ['MESH']

    def draw(self, context):
        layout =  self.layout
        preferences = context.preferences.addons['UE4Workspace'].preferences
        active_object = context.active_object

        if context.mode == 'OBJECT' and not active_object.data.is_custom_collision:
            col = layout.box().column()
            split = col.split(factor=0.6)
            col = split.column()
            col.alignment = 'RIGHT'
            col.label(text='Collision Picker')
            col = split.column()
            col.prop(context.scene, 'collision_picker', icon='MOD_SOLIDIFY', text='')
            col = col.row()
            col.scale_y = 1.5
            col.operator('ue4workspace.collision_picker',icon='MOD_SOLIDIFY', text='Convert')

        row = layout.box().row()
        row.scale_y = 1.5
        row.operator('ue4workspace.create_collision',icon='OUTLINER_OB_MESH')

        collision_objects = [obj for obj in context.scene.objects if obj.type == 'MESH' and obj.parent == active_object and obj.data.is_custom_collision]

        if collision_objects:
            box = layout.box()
            for obj in collision_objects:
                col = box.column()
                split = col.split(factor=0.6)
                col = split.column()
                col.prop(obj, 'name', text='')
                row = split.row()
                row.alignment = 'RIGHT'
                row.operator('ue4workspace.toggle_visibility_object', icon=('HIDE_ON' if obj.hide_get() else 'HIDE_OFF'), text='', emboss=False).object_name = obj.name
                row.operator('ue4workspace.remove_object', icon='TRASH', text='', emboss=False).object_name = obj.name

list_class_to_register = [
    OP_CreateCollision,
    OP_CollisionPicker,
    PANEL
]

def register():
    bpy.types.Mesh.is_custom_collision = bpy.props.BoolProperty(
        name='Is custom collision ?',
        description='custom collision ?',
        default=False
    )

    bpy.types.Scene.collision_picker = bpy.props.PointerProperty(
        name='Collision Picker',
        description='Make mesh into a custom collision',
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'MESH' and not obj.data.is_custom_collision and not 'ARMATURE' in [mod.type for mod in obj.modifiers] and obj is not bpy.context.active_object
    )

    for x in list_class_to_register:
        register_class(x)

def unregister():
    del bpy.types.Mesh.is_custom_collision
    del bpy.types.Scene.collision_picker

    for x in list_class_to_register[::-1]:
        unregister_class(x)