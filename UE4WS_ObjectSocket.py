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

# operator export

Ops = [
    OP_AttachObject,
    OP_CreateSocket
]