import bpy
from bpy.props import (EnumProperty, StringProperty)
from bpy.types import (Panel, Operator)

# PROPS

Props = [
    # {
    #     "type": "scene",
    #     "name": "ExportOption",
    #     "value": EnumProperty(
    #         name="Export Type",
    #         description="Select the way you want export",
    #         items=[("FBX", "To FBX", "Export as FBX file"), ("UNREAL", "To Unreal", "Export directly to Unreal Engine Project")],
    #         default="FBX"
    #         )
    # },
    # {
    #     "type": "scene",
    #     "name": "ExportFBXFolder",
    #     "value": StringProperty(
    #         name="Export Folder",
    #         description="Folder To Export Character, Must Have Write Permissions",
    #         default="",
    #         maxlen=1024,
    #         subtype="DIR_PATH"
    #         )
    # }
]

# PANEL

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_ObjectPanel"
    bl_label = "Object"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    remote = None

    @classmethod
    def poll(self, context):
        return context.active_object is not None and context.active_object.type in ["MESH"]

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons[__package__].preferences

        if context.active_object is not None and context.active_object.type == "MESH":

            layout.prop(preferences, "SM_OBJTabCustomCollision", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.SM_OBJTabCustomCollision], emboss=False)
            if preferences.SM_OBJTabCustomCollision:
                row = layout.row()
                row.scale_y = 1.5
                row.operator("wm.url_open",icon="INFO", text="FBX Static Mesh Pipeline").url="https://docs.unrealengine.com/en-US/Engine/Content/Importing/FBX/StaticMeshes/#collision"
                # Add Collision Button
                row = layout.row()
                row.scale_y = 1.5
                row.operator("ue4workspace.makecollision",icon="OUTLINER_OB_MESH", text="Make Collision")

                collisionObjects = [obj for obj in context.scene.objects if obj.type == "MESH" and obj.name.startswith("UCX_" + context.active_object.name)]

                if collisionObjects:
                    box = layout.box()
                    for obj in collisionObjects:
                        col = box.column()
                        row = col.row()
                        split = row.split(factor=0.6)
                        col = split.column()
                        col.label(text=obj.name)
                        split = split.split()
                        row = split.row()
                        row.alignment = "RIGHT"
                        row.operator("ue4workspace.togglevisibilityobject",icon=("HIDE_OFF", "HIDE_ON")[obj.hide_get()], text="", emboss=False).objName = obj.name
                        row.operator("ue4workspace.removeobject",icon="TRASH", text="", emboss=False).objName = obj.name

            layout.prop(preferences, "SM_OBJTabLOD", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.SM_OBJTabLOD], emboss=False)
            if preferences.SM_OBJTabLOD:
                pass

# OPERATOR

class OP_ToggleVisibilityObject(Operator):
    bl_idname = "ue4workspace.togglevisibilityobject"
    bl_label = "UE4Workspace Operator"
    bl_description = "Toggle Visibility Object"
    bl_options = {"UNDO"}

    objName: StringProperty(name="Object name")

    def execute(self, context):
        obj = context.scene.objects[self.objName]
        obj.hide_set(not obj.hide_get())
        return {"FINISHED"}

class OP_RemoveObject(Operator):
    bl_idname = "ue4workspace.removeobject"
    bl_label = "UE4Workspace Operator"
    bl_description = "Remove Object"
    bl_options = {"UNDO"}

    objName: StringProperty(name="Object name")

    def execute(self, context):
        obj = context.scene.objects[self.objName]
        bpy.data.objects.remove(obj, do_unlink=True)
        return {"FINISHED"}

class OP_MakeCollision(Operator):
    bl_idname = "ue4workspace.makecollision"
    bl_label = "UE4Workspace Operator"
    bl_description = "Make Custom Collison Mesh\nSelect a Mesh > Edit Mode > Select Edge"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.active_object is not None and context.active_object.mode == "EDIT" and context.active_object.type == "MESH" and (not context.active_object.name.startswith("UCX_"))

    def execute(self, context):
        parentObj = context.active_object

        collName = "UCX_" + context.active_object.name + "_"
        index = len([obj for obj in context.scene.objects if obj.name.startswith(collName)])
        collName += ("", "0")[index < 9] + str(index + 1)

        mode = context.active_object.mode
        bpy.ops.object.mode_set(mode="OBJECT")
        selected_verts = [verts for verts in context.active_object.data.vertices if verts.select]
        selected_verts = [verts.co for verts in selected_verts]

        mesh = bpy.data.meshes.new(collName)
        obj = bpy.data.objects.new(collName,mesh)
        context.collection.objects.link(obj)
        mesh.from_pydata(selected_verts, [], [])

        bpy.ops.object.mode_set(mode="OBJECT")
        obj.location = parentObj.location
        bpy.ops.object.select_all(action="DESELECT")
        obj.show_wire = True

        context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.convex_hull()
        bpy.ops.mesh.delete(type="ONLY_FACE")

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        context.view_layer.objects.active = parentObj
        parentObj.select_set(state=True)
        bpy.ops.object.mode_set(mode=mode)

        return {"FINISHED"}

# operator export

Ops = [
    OP_ToggleVisibilityObject,
    OP_RemoveObject,
    OP_MakeCollision
]