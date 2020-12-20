import math
import bpy
from bpy.utils import register_class, unregister_class
from bpy.types import Operator
from mathutils import Matrix
from .. utils.base import ObjectSubPanel, create_matrix_scale_from_vector

class OP_AttachObject(Operator):
    bl_idname = 'ue4workspace.attach_object'
    bl_label = 'Attach Object'
    bl_description = 'Attach or Detach Object'
    bl_options = {'UNDO', 'REGISTER'}

    snap: bpy.props.BoolProperty(
        name='Snap',
        default=True
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.attach_to is not None and context.active_object.attach_to.parent is not context.active_object

    def execute(self, context):
        active_object = context.active_object
        is_attach_to_object = active_object.is_attach_to_object
        active_object.is_attach_to_object = not is_attach_to_object

        if not is_attach_to_object:
            # attach
            constraint = active_object.constraints.new(type='CHILD_OF')
            constraint.name = 'attach_to'
            constraint.target = active_object.attach_to
            if self.snap:
                socket_world_location, socket_world_rotation, socket_world_scale = active_object.attach_to.matrix_world.decompose()
                active_object.matrix_world = Matrix.Translation(socket_world_location) @ socket_world_rotation.to_matrix().to_4x4() @ create_matrix_scale_from_vector(active_object.matrix_world.to_scale())
        else:
            # detach
            constraint = active_object.constraints.get('attach_to')
            if constraint:
                active_object.constraints.remove(constraint)

        self.report({'INFO'}, 'Detach Object Success' if is_attach_to_object else 'Attach Object Success')

        return {'FINISHED'}

class OP_CreateSocket(Operator):
    bl_idname = 'ue4workspace.create_socket'
    bl_label = 'Create Socket'
    bl_description = 'Create socket for attach object'
    bl_options = {'UNDO', 'REGISTER'}

    socket_name: bpy.props.StringProperty(
        name='Name',
        default='name_socket'
        )

    size: bpy.props.FloatProperty(
        name='Size',
        min=0.01,
        default=1
        )

    rotation: bpy.props.FloatVectorProperty(
        name='Rotation',
        subtype='XYZ',
        unit='ROTATION',
        default=[0, 0, 0]
        )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type in ['ARMATURE', 'MESH']

    def execute(self, context):
        is_armature = context.active_object.type == 'ARMATURE' and context.mode in ['POSE', 'EDIT_ARMATURE']
        bone = None
        if is_armature:
            case_bone = {
                'EDIT_ARMATURE': context.active_bone,
                'POSE': context.active_pose_bone
            }
            bone = case_bone.get(context.mode)

        # create collection (UE4Socket) if not exist
        collection = bpy.data.collections.get('UE4Socket', False)
        if (not collection):
            collection = bpy.data.collections.new('UE4Socket')
            context.scene.collection.children.link(collection)

        socket = bpy.data.objects.new(name=self.socket_name, object_data=None)
        socket.is_socket = True
        socket.rotation_euler = self.rotation
        socket.location = context.scene.cursor.location
        socket.show_name = True
        socket.empty_display_type = 'ARROWS'
        socket.empty_display_size = self.size
        collection.objects.link(socket)
        socket.parent = context.active_object
        if is_armature and bone:
            socket.parent_type = 'BONE'
            socket.parent_bone = bone.name
            # clear Local Transform
            socket.matrix_parent_inverse = (context.active_object.matrix_world @ Matrix.Translation(bone.tail - bone.head) @ bone.matrix).inverted()
        else:
            socket.parent_type = 'OBJECT'
            # clear Local Transform
            socket.matrix_parent_inverse = context.active_object.matrix_world.inverted()

        return {'FINISHED'}

class OP_CopySocket(Operator):
    bl_idname = 'ue4workspace.copy_socket'
    bl_label = 'Copy Socket'
    bl_description = 'Copy socket for unreal engine skeleton'
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(self, context):
        return context.mode == 'OBJECT' and context.active_object is not None and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        active_object = context.active_object

        bone_parent = bpy.data.objects.new(name='dummy_socket_bone_parent', object_data=None)
        socket_point = bpy.data.objects.new(name='dummy_socket_point', object_data=None)

        socket_point.parent = bone_parent

        context.scene.collection.objects.link(bone_parent)
        context.scene.collection.objects.link(socket_point)

        socket_bone_objects = [obj for obj in active_object.children if obj.type == 'EMPTY' and obj.is_socket and obj.parent_type == 'BONE' and obj.parent_bone]

        string_clipboard = 'SocketCopyPasteBuffer\n\nNumSockets={}\n\n'.format(len(socket_bone_objects))

        for index, socket_obj in enumerate(socket_bone_objects):

            pose_bone_target = active_object.pose.bones.get(socket_obj.parent_bone)

            if pose_bone_target is not None:

                bone_parent.matrix_world = active_object.matrix_world @ pose_bone_target.matrix
                socket_point.matrix_world = socket_obj.matrix_world.copy()

                socket_point_location, socket_point_rotation_quaternion, socket_point_scale = socket_point.matrix_local.decompose()
                socket_point_rotation_euler = socket_point_rotation_quaternion.to_euler('XYZ')

                string_clipboard += 'IsOnSkeleton=1\nBegin Object Class=/Script/Engine.SkeletalMeshSocket Name=\"SkeletalMeshSocket_{index}\"\nSocketName=\"{socket_name}\"\nBoneName=\"{bone_name}\"\nRelativeLocation=(X={location[x]},Y={location[y]},Z={location[z]})\nRelativeRotation=(Pitch={rotation[y]},Yaw={rotation[z]},Roll={rotation[x]})\nRelativeScale=(X={scale[x]},Y={scale[y]},Z={scale[z]})\nEnd Object\n\n'.format(
                    index = index,
                    socket_name = socket_obj.name,
                    bone_name = socket_obj.parent_bone,
                    location = {
                        "x": socket_point_location.x,
                        "y": socket_point_location.y * -1,
                        "z": socket_point_location.z
                    },
                    rotation = {
                        "x": math.degrees(socket_point_rotation_euler.x),
                        "y": math.degrees(socket_point_rotation_euler.y * -1),
                        "z": math.degrees(socket_point_rotation_euler.z * -1)
                    },
                    scale = {
                        "x": float(socket_point_scale.x / 100),
                        "y": float(socket_point_scale.y / 100),
                        "z": float(socket_point_scale.z / 100)
                    }
                )

        bpy.data.objects.remove(socket_point, do_unlink=True)
        bpy.data.objects.remove(bone_parent, do_unlink=True)

        context.window_manager.clipboard = string_clipboard

        self.report({'INFO'}, 'Copy socket success')

        return {"FINISHED"}

class PANEL(ObjectSubPanel):
    bl_idname = 'UE4WORKSPACE_PT_ObjectSocketPanel'
    bl_label = 'Socket'

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type in ['ARMATURE', 'MESH']

    def draw(self, context):
        layout =  self.layout
        preferences = context.preferences.addons['UE4Workspace'].preferences
        active_object = context.active_object

        col = layout.box().column()
        split = col.split(factor=0.6)
        col = split.column()
        col.alignment = 'RIGHT'
        col.label(text='Attach to')
        col = split.column()
        row = col.row()
        row.enabled = not active_object.is_attach_to_object
        row.prop(active_object, 'attach_to', text='', icon='EMPTY_ARROWS')
        row = col.row()
        row.scale_y = 1.5
        row.operator('ue4workspace.attach_object',icon='CON_PIVOT', text=('Detach' if active_object.is_attach_to_object else 'Attach'))

        row = layout.box().row()
        row.scale_y = 1.5
        row.operator('ue4workspace.create_socket',icon='EMPTY_ARROWS')

        socket_objects = [obj for obj in context.scene.objects if obj.type == 'EMPTY' and obj.is_socket and obj.parent is active_object]

        if socket_objects and active_object.type == 'ARMATURE':
            row = layout.box().row()
            row.scale_y = 1.5
            row.operator('ue4workspace.copy_socket',icon='DECORATE_ANIMATE', text='Copy Socket')

        if socket_objects:
            for obj in socket_objects:
                box = layout.box()

                col = box.column()
                split = col.split(factor=0.6)
                col = split.column()
                col.prop(obj, 'name', text='')
                row = split.row()
                row.alignment = 'RIGHT'
                row.operator('ue4workspace.toggle_visibility_object', icon=('HIDE_ON' if obj.hide_get() else 'HIDE_OFF'), text='', emboss=False).object_name = obj.name
                row.operator('ue4workspace.remove_object', icon='TRASH', text='', emboss=False).object_name = obj.name

                col = box.column()
                split = col.split(factor=0.6)
                col = split.column()
                col.alignment = 'RIGHT'
                col.label(text='Size')
                col = split.column()
                col.prop(obj, 'empty_display_size', text='')

                col = box.column()
                split = col.split(factor=0.6)
                col = split.column()
                col.alignment = 'RIGHT'
                col.label(text='Show Name')
                col = split.column()
                col.prop(obj, 'show_name', text='')

                # socket parent bone for character
                if obj.parent_type == 'BONE':
                    col = box.column()
                    split = col.split(factor=0.6)
                    col = split.column()
                    col.alignment = 'RIGHT'
                    col.label(text='Bone')
                    col = split.column()
                    col.prop_search(obj, 'parent_bone', active_object.data, 'bones', text='')

list_class_to_register = [
    OP_AttachObject,
    OP_CreateSocket,
    OP_CopySocket,
    PANEL
]

def register():
    bpy.types.Object.is_socket = bpy.props.BoolProperty(
        name='Is socket ?',
        description='socket ?',
        default=False
    )

    bpy.types.Object.is_attach_to_object = bpy.props.BoolProperty(
        default=False
    )

    bpy.types.Object.attach_to = bpy.props.PointerProperty(
        name='Attach to',
        description='Attach object to socket',
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'EMPTY' and obj.is_socket and obj.parent is not bpy.context.active_object
    )

    for x in list_class_to_register:
        register_class(x)

def unregister():
    del bpy.types.Object.is_socket
    del bpy.types.Mesh.is_attach_to_object
    del bpy.types.Object.attach_to

    for x in list_class_to_register[::-1]:
        unregister_class(x)