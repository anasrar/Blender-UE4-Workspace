import math
import bpy
from mathutils import Matrix
from bpy.props import (EnumProperty, BoolProperty, FloatVectorProperty, StringProperty, PointerProperty)
from bpy.types import (Panel, Operator)

# PROPS

Props = [
    {
        "type": "object",
        "name": "attachTo",
        "value": PointerProperty(
            name="Attach to",
            description="Attach object to socket",
            type=bpy.types.Object,
            poll=lambda self, obj: obj.type == "EMPTY" and obj.get("isSocket") and obj.parent is not bpy.context.active_object
            ),
        "resetVariable": False
    },
    {
        "type": "object",
        "name": "isAttachToObject",
        "value": BoolProperty(default=False),
        "resetVariable": False
    },
    {
        "type": "object",
        "name": "attachLocationOriginal",
        "value": FloatVectorProperty(size=3),
        "resetVariable": False
    },
    {
        "type": "object",
        "name": "attachRotationOriginal",
        "value": FloatVectorProperty(size=3),
        "resetVariable": False
    }
]

# PANEL

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_ObjectSocketPanel"
    bl_parent_id = "UE4WORKSPACE_PT_ObjectPanel"
    bl_label = "Socket"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        return context.active_object is not None and context.active_object.type in ["ARMATURE", "MESH"]

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object

        col = layout.box().column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Attach to")
        split = split.split()
        col = split.column()
        row = col.row()
        row.enabled = not activeObject.isAttachToObject
        row.prop(activeObject, "attachTo", text="", icon="EMPTY_ARROWS")
        row = col.row()
        row.scale_y = 1.5
        row.operator("ue4workspace.attachobject",icon="CON_PIVOT", text=("Attach", "Detach")[activeObject.isAttachToObject])

        box = layout.box()
        row = box.row()
        row.scale_y = 1.5
        row.operator("ue4workspace.createsocket",icon="EMPTY_ARROWS", text="Add Socket")

        socketObjects = [obj for obj in context.scene.objects if obj.type == "EMPTY" and obj.get("isSocket") and obj.parent is activeObject]

        if socketObjects and activeObject.type == "ARMATURE":
            row = box.row()
            row.scale_y = 1.5
            row.operator("ue4workspace.copysocket",icon="DECORATE_ANIMATE", text="Copy Socket")

        if socketObjects:
            for obj in socketObjects:
                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.prop(obj, "name", text="")
                split = split.split()
                row = split.row()
                row.alignment = "RIGHT"
                row.operator("ue4workspace.togglevisibilityobject",icon=("HIDE_OFF", "HIDE_ON")[obj.hide_get()], text="", emboss=False).objName = obj.name
                row.operator("ue4workspace.removeobject",icon="TRASH", text="", emboss=False).objName = obj.name

                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text="Size")
                split = split.split()
                col = split.column()
                col.prop(obj, "empty_display_size", text="")

                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text="Show Name")
                split = split.split()
                col = split.column()
                col.prop(obj, "show_name", text="")

                # Socket parent bone for character
                if obj.parent_type == "BONE":
                    col = box.column()
                    row = col.row()
                    split = row.split(factor=0.6)
                    col = split.column()
                    col.alignment = "RIGHT"
                    col.label(text="Bone")
                    split = split.split()
                    col = split.column()
                    col.prop_search(obj, "parent_bone", activeObject.data, "bones", text="")

# OPERATOR

class OP_AttachObject(Operator):
    bl_idname = "ue4workspace.attachobject"
    bl_label = "Attach Object"
    bl_description = "Attach or Detach Object"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.attachTo is not None and context.active_object.attachTo.parent is not context.active_object

    def execute(self, context):
        obj = context.active_object
        isAttach = not obj.isAttachToObject

        if isAttach:
            # Attach
            constraint = obj.constraints.new(type="CHILD_OF")
            constraint.name = "AttachTo"
            constraint.target = obj.attachTo

            obj.attachLocationOriginal = obj.location
            obj.attachRotationOriginal = obj.rotation_euler
            obj.isAttachToObject = True
            obj.location = [0, 0, 0]
            obj.rotation_euler = [0, 0, 0]

        else:
            # Detach
            constraint = obj.constraints.get("AttachTo")
            if constraint:
                obj.constraints.remove(constraint)
            obj.isAttachToObject = False
            obj.location = obj.attachLocationOriginal
            obj.rotation_euler = obj.attachRotationOriginal

        try:
            bpy.ops.ue4workspace.popup("INVOKE_DEFAULT", msg=("Detach Object Success", "Attach Object Success")[isAttach])
        except Exception: 
            pass

        return {"FINISHED"}

class OP_CreateSocket(Operator):
    bl_idname = "ue4workspace.createsocket"
    bl_label = "Create Socket"
    bl_description = "Create socket for attach object"
    bl_options = {"UNDO", "REGISTER"}

    SocketName: bpy.props.StringProperty(
        name="Name",
        default="socketName"
        )

    Size: bpy.props.FloatProperty(
        name="Size",
        min=0.01,
        default=1
        )

    Rotation: bpy.props.FloatVectorProperty(
        name="Rotation",
        subtype="XYZ",
        unit="ROTATION",
        default=[0, 0, 0]
        )

    # @classmethod
    # def poll(cls, context):
    #     return True

    def execute(self, context):
        parentObj = context.active_object
        isBone = parentObj.type == "ARMATURE" and context.mode in ["POSE", "EDIT_ARMATURE"]
        bone = None
        if isBone:
            caseBone = {
                "EDIT_ARMATURE": context.active_bone,
                "POSE": context.active_pose_bone
            }
            bone = caseBone.get(context.mode)

        # create collection (UE4Socket) if not exist
        collection = bpy.data.collections.get("UE4Socket", False)
        if (not collection):
            collection = bpy.data.collections.new("UE4Socket")
            context.scene.collection.children.link(collection)

        socket = bpy.data.objects.new(name=self.SocketName, object_data=None)
        socket["isSocket"]  = True
        socket.rotation_euler = self.Rotation
        socket.location = context.scene.cursor.location
        socket.show_name = True

        socket.empty_display_type = "ARROWS"
        socket.empty_display_size = self.Size
        collection.objects.link(socket)
        socket.parent = parentObj
        if isBone and bone:
            socket.parent_type = "BONE"
            socket.parent_bone = bone.name
            # Clear Local Transform
            socket.matrix_parent_inverse = (parentObj.matrix_world @ Matrix.Translation(bone.tail - bone.head) @ bone.matrix).inverted()
        else:
            socket.parent_type = "OBJECT"
            # Clear Local Transform
            socket.matrix_parent_inverse = parentObj.matrix_world.inverted()

        return {"FINISHED"}

class OP_CopySocket(Operator):
    bl_idname = "ue4workspace.copysocket"
    bl_label = "Copy Socket"
    bl_description = "Copy socket for unreal engine skeleton"
    bl_options = {"UNDO", "REGISTER"}

    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT" and context.active_object is not None and context.active_object.type == "ARMATURE"

    def execute(self, context):
        activeObject = context.active_object

        # create new empty
        boneParent = bpy.data.objects.new(name="dummySocketBoneParent", object_data=None)
        socketPoint = bpy.data.objects.new(name="dummySocketPoint", object_data=None)

        context.scene.collection.objects.link(boneParent)
        context.scene.collection.objects.link(socketPoint)

        socketPoint.parent = boneParent

        # set constraint
        boneParentConstraint = boneParent.constraints.new("COPY_TRANSFORMS")
        socketPointConstraint = socketPoint.constraints.new("COPY_TRANSFORMS")

        boneParentConstraint.target = activeObject

        bpy.ops.object.select_all(action="DESELECT")

        # select bone parent and socket point
        boneParent.select_set(state=True)
        socketPoint.select_set(state=True)

        # get all socket parent with bone
        socketBoneObjects = [obj for obj in context.scene.objects if obj.type == "EMPTY" and obj.get("isSocket") and obj.parent is activeObject and obj.parent_type == "BONE" and obj.parent_bone]

        # string to copy on clipboard
        stringClipboard = "SocketCopyPasteBuffer\n\nNumSockets={}\n\n".format(len(socketBoneObjects))

        for index, socketObj in enumerate(socketBoneObjects):
            # set target
            boneParentConstraint.subtarget = socketObj.parent_bone
            socketPointConstraint.target = socketObj
            # get relative transform using apply visual transfrom
            bpy.ops.object.visual_transform_apply()
            stringClipboard += "IsOnSkeleton=1\nBegin Object Class=/Script/Engine.SkeletalMeshSocket Name=\"SkeletalMeshSocket_{index}\"\nSocketName=\"{socketName}\"\nBoneName=\"{boneName}\"\nRelativeLocation=(X={location[x]},Y={location[y]},Z={location[z]})\nRelativeRotation=(Pitch={rotation[y]},Yaw={rotation[z]},Roll={rotation[x]})\nRelativeScale=(X={scale[x]},Y={scale[y]},Z={scale[z]})\nEnd Object\n\n".format(
                index = index,
                socketName = socketObj.name,
                boneName = socketObj.parent_bone,
                location = {
                    "x": socketPoint.location.x,
                    "y": socketPoint.location.y * -1,
                    "z": socketPoint.location.z
                },
                rotation = {
                    "x": math.degrees(socketPoint.rotation_euler.x),
                    "y": math.degrees(socketPoint.rotation_euler.y * -1),
                    "z": math.degrees(socketPoint.rotation_euler.z * -1)
                },
                scale = {
                    "x": float(socketPoint.scale.x / 100),
                    "y": float(socketPoint.scale.y / 100),
                    "z": float(socketPoint.scale.z / 100)
                }
            )

        # remove constarint
        boneParent.constraints.remove(boneParentConstraint)
        socketPoint.constraints.remove(socketPointConstraint)

        # remove object
        bpy.data.objects.remove(boneParent, do_unlink=True)
        bpy.data.objects.remove(socketPoint, do_unlink=True)

        # copy string to clipboard
        context.window_manager.clipboard = stringClipboard

        try:
            bpy.ops.ue4workspace.popup("INVOKE_DEFAULT", msg="Copy Socket Success")
        except Exception: 
            pass

        return {"FINISHED"}

# operator export

Ops = [
    OP_AttachObject,
    OP_CreateSocket,
    OP_CopySocket
]