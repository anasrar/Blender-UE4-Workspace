import os
import json
import bpy
from bpy.types import (Panel, Operator)

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_CharacterPanel"
    bl_label = "Character"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons[__package__].preferences

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Subfolder")
        split = split.split()
        col = split.column()
        col.prop(preferences, "CHAR_Subfolder", text="")

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Overwrite File")
        split = split.split()
        col = split.column()
        col.prop(preferences, "CHAR_OverwriteFile", text="")

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Export Character Option")
        split = split.split()
        col = split.column()
        col.prop(preferences, "CHAR_ExportCharacterOption", text="")

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Character Option")
        split = split.split()
        col = split.column()
        col.prop(preferences, "CHAR_CharacterOption", text="")

        if preferences.exportOption in ["BOTH", "UNREAL"]:
            col = layout.column()
            row = col.row()
            split = row.split(factor=0.6)
            col = split.column()
            col.alignment = "RIGHT"
            col.label(text="Character Skeleton")
            split = split.split()
            col = split.column()
            col.prop(preferences, "CHAR_CharacterSkeleton", text="")

            row = layout.row()
            row.scale_y = 1.5
            row.operator("ue4workspace.updatelistskeleton",icon="ARMATURE_DATA", text="Update List Skeleton")

        row = layout.row()
        row.scale_y = 1.5
        row.operator("ue4workspace.exportstaticmesh",icon="MESH_CUBE", text="Export")

#  OPERATOR

class OP_UpdateListSkeleton(Operator):
    bl_idname = "ue4workspace.updatelistskeleton"
    bl_label = "UE4Workspace Operator"
    bl_description = "Update List Skeleton"

    remote = None

    @classmethod
    def poll(self, context):
        preferences = context.preferences.addons[__package__].preferences

        return preferences.exportOption in ["UNREAL", "BOTH"] and self.remote.remote_nodes

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences

        # clear all skeleton list
        preferences.skeleton.clear()
        skeletonList = []

        for node_id in [user["node_id"] for user in self.remote.remote_nodes]:
            self.remote.open_command_connection(node_id)
            output = self.remote.run_command(os.path.join(os.path.dirname(os.path.realpath(__file__)), "PyScript", "GetAllSkeleton.py"), exec_mode="ExecuteFile")
            self.remote.close_command_connection()
            skeletonList += json.loads(output["output"][0]["output"])

        # add skeleton
        for enum in skeletonList:
            preferences.skeleton.append((enum[0], enum[1], enum[0]))

        try:
            bpy.ops.ue4workspace.popup("INVOKE_DEFAULT", msg="Update List Skeleton Done")
        except Exception: 
            pass


        return {"FINISHED"}


# operator export

Ops = [
    OP_UpdateListSkeleton
]