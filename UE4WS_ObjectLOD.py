import math
import bpy
from bpy.props import (EnumProperty, FloatProperty, FloatVectorProperty, IntProperty, StringProperty, PointerProperty, BoolProperty, CollectionProperty)
from bpy.types import (Panel, Operator, PropertyGroup)
from mathutils import Vector

# PROPERTY GROUP

class LOD_Struct(PropertyGroup):
    screenSize: FloatProperty(
        name="LOD Screen Size",
        description="Set a screen size value for LOD",
        default=0.0
    )
    obj: PointerProperty(
        name="LOD Object",
        description="Mesh to LOD",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == "MESH" and not "ARMATURE" in [mod.type for mod in obj.modifiers] and obj != bpy.context.active_object and obj.data.objectAsLOD
    )

# group export

Groups = [
    LOD_Struct
]

# PROPS

Props = [
    {
        "type": "mesh",
        "name": "objectAsLOD",
        "value": BoolProperty(
            name="Expot as LOD",
            description="If checked, will not export as static mesh instead will be a part of LOD",
            default=False
        ),
        "resetVariable": False
    },
    {
        "type": "mesh",
        "name": "AutoComputeLODScreenSize",
        "value": BoolProperty(
            name="Auto Compute LOD ScreenSize",
            description="If checked, the editor will automatically compute screen size values for the static mesh’s LODs. If unchecked, the user can enter custom screen size values for each LOD",
            default=True
            ),
        "resetVariable": False
    },
    {
        "type": "mesh",
        "name": "LOD0ScreenSize",
        "value": FloatProperty(
            name="LOD 0 Screen Size",
            description="Set a screen size value for LOD 0",
            default=1.0
            ),
        "resetVariable": False
    },
    {
        "type": "mesh",
        "name": "LODs",
        "value": CollectionProperty(type=LOD_Struct),
        "resetVariable": False
    }
]

# PANEL

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_ObjectLODPanel"
    bl_parent_id = "UE4WORKSPACE_PT_ObjectPanel"
    bl_label = "Level of Detail"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        return context.active_object is not None and context.active_object.type in ["MESH"] and not "ARMATURE" in [mod.type for mod in context.active_object.modifiers]

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object

        split = layout.row().split(factor=0.6)
        row = split.row()
        row.alignment = "RIGHT"
        row.label(text="Object as LOD")
        split = split.split()
        row = split.row()
        row.prop(activeObject.data, "objectAsLOD", text="")

        if not activeObject.data.objectAsLOD:
            # row = layout.row()
            # row.scale_y = 1.5
            # row.operator("ue4workspace.previewlodmode", icon="FULLSCREEN_ENTER", text="LOD Preview Mode")

            row = layout.row()
            row.scale_y = 1.5
            row.operator("ue4workspace.addlodslot", icon="PRESET_NEW", text="Add LOD Slot")

            split = layout.row().split(factor=0.6)
            row = split.row()
            row.alignment = "RIGHT"
            row.label(text="Auto LOD Screen Size")
            split = split.split()
            row = split.row()
            row.prop(activeObject.data, "AutoComputeLODScreenSize", text="")

            split = layout.row().split(factor=0.6)
            col = split.column()
            row = col.row(align=True)
            row.alignment = "RIGHT"
            row.label(text="LOD 0")
            # row.label(text="", icon="RESTRICT_VIEW_OFF")
            if not activeObject.data.AutoComputeLODScreenSize:
                row = col.row(align=True)
                row.alignment = "RIGHT"
                row.label(text="Screen Size")
            split = split.split()
            col = split.column()
            row = col.row(align=True)
            row.label(text=activeObject.name, icon="MESH_CUBE")
            if not activeObject.data.AutoComputeLODScreenSize:
                row = col.row(align=True)
                row.prop(activeObject.data, "LOD0ScreenSize", text="")

            for index, lod in enumerate(activeObject.data.LODs, start=1):
                split = layout.row().split(factor=0.6)
                col = split.column()
                row = col.row(align=True)
                row.operator("ue4workspace.removelodslot", icon="X", text="").index = index - 1
                sub = row.row()
                sub.alignment = "RIGHT"
                sub.scale_x = 2.0
                sub.label(text="LOD " + str(index))
                # row.prop(activeObject, "hide_viewport", icon="RESTRICT_VIEW_OFF", text="", emboss=False)
                if not activeObject.data.AutoComputeLODScreenSize:
                    row = col.row(align=True)
                    row.alignment = "RIGHT"
                    row.label(text="Screen Size")
                split = split.split()
                col = split.column()
                row = col.row(align=True)
                row.prop(lod, "obj", text="", icon="MESH_CUBE")
                if not activeObject.data.AutoComputeLODScreenSize:
                    row = col.row(align=True)
                    row.prop(lod, "screenSize", text="")

# OPERATOR

# I was try to make preview lod mode but for now I dont now how uneal engine calculate "current screen size"

class OP_PreviewLODMode(Operator):
    bl_idname = "ue4workspace.previewlodmode"
    bl_label = "Preview LOD Mode"
    bl_description = "Preview LOD Mode"
    bl_options = {"UNDO"}

    _initial_matrix = None # matrix for restore location and rotation
    _forwardVector = None
    _moveSpeed = 1
    _cameraFOV = 39.6 # default FOV blender
    _radiusObject = None
    _worldLocationObject = None

    @classmethod
    def poll(self, context):
        activeObject = context.active_object
        return context.mode == "OBJECT" and activeObject is not None and activeObject.type in ["MESH"] and len([lod for lod in activeObject.data.LODs if lod.obj])

    def modal(self, context, event):
        v3d = context.space_data
        rv3d = v3d.region_3d

        rv3d_loc, rv3d_rot, rv3d_sca = rv3d.view_matrix.decompose()

        distanceToObject = (self._worldLocationObject - rv3d_loc).length

        headerText = "Preview LOD Mode | Speed {} | Screen Size {}".format(self._moveSpeed, distanceToObject)

        if event.type in ["WHEELUPMOUSE", "WHEELDOWNMOUSE"]:
            # zoom in / out
            rv3d.view_location = rv3d.view_location + (self._forwardVector * self._moveSpeed) if event.type == "WHEELUPMOUSE" else rv3d.view_location - (self._forwardVector * self._moveSpeed)
            context.area.header_text_set(headerText)
        # increase or decrease speed
        if event.type in ["UP_ARROW", "DOWN_ARROW"]:
            self._moveSpeed += 1 if event.type == "UP_ARROW" else -1
            context.area.header_text_set(headerText)
        # exit mode
        elif event.type in {"RIGHTMOUSE", "ESC"}:
            # restore location and rotation
            rv3d.view_matrix = self._initial_matrix
            context.area.header_text_set(None)
            return {"CANCELLED"}
        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        if context.space_data.type == "VIEW_3D":
            v3d = context.space_data
            rv3d = v3d.region_3d
            if rv3d.view_perspective in ["CAMERA", "ORTHO"]:
                rv3d.view_perspective = "PERSP"
            # copy current matrix
            self._initial_matrix = rv3d.view_matrix.copy()

            # Focus to object
            bpy.ops.object.select_all(action="DESELECT")
            context.active_object.select_set(True)
            bpy.ops.view3d.view_selected(use_all_regions=False)
            context.active_object.select_set(False)
            # get radius object
            self._radiusObject = (max(context.active_object.dimensions)/2)/100
            obj_loc, obj_rot, obj_sca = context.active_object.matrix_world.decompose()
            self._worldLocationObject = obj_loc

            # get forward vector
            self._forwardVector = rv3d.view_rotation.copy() @ Vector((0,0,-1))

            context.window_manager.modal_handler_add(self)
            return {"RUNNING_MODAL"}
        else:
            self.report({"WARNING"}, "Active space must be a View3d")
            return {"CANCELLED"}

class OP_AddLODSlot(Operator):
    bl_idname = "ue4workspace.addlodslot"
    bl_label = "Add LOD Slot"
    bl_description = "Add LOD Slot"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        activeObject = context.active_object
        return activeObject is not None and activeObject.type in ["MESH"] and not "ARMATURE" in [mod.type for mod in activeObject.modifiers] and 7 > len(activeObject.data.LODs)

    def execute(self, context):
        activeObject = context.active_object
        activeObject.data.LODs.add()
        return {"FINISHED"}

class OP_RemoveLODSlot(Operator):
    bl_idname = "ue4workspace.removelodslot"
    bl_label = "Remove LOD Slot"
    bl_description = "Remove LOD Slot"
    bl_options = {"UNDO"}

    index: IntProperty(default=-1)

    @classmethod
    def poll(cls, context):
        activeObject = context.active_object
        return activeObject is not None and activeObject.type in ["MESH"] and not "ARMATURE" in [mod.type for mod in activeObject.modifiers]

    def execute(self, context):
        activeObject = context.active_object
        if self.index > -1:
            lod = activeObject.data.LODs[self.index]
            activeObject.data.LODs.remove(self.index)
        return {"FINISHED"}

# operator export

Ops = [
    # OP_PreviewLODMode,
    OP_AddLODSlot,
    OP_RemoveLODSlot
]