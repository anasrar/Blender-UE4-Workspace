import bpy
from bpy.props import (EnumProperty, StringProperty)
from bpy.types import (Panel, Operator)

class RemoteExecutionConfig(object):
    '''
    Configuration data for establishing a remote connection with a UE4 instance running Python.
    '''
    def __init__(self, DEFAULT_MULTICAST_TTL=0, DEFAULT_MULTICAST_GROUP_ENDPOINT=("239.0.0.1", 6766), DEFAULT_MULTICAST_BIND_ADDRESS="0.0.0.0", DEFAULT_COMMAND_ENDPOINT=("127.0.0.1", 6776)):
        self.multicast_ttl = DEFAULT_MULTICAST_TTL
        self.multicast_group_endpoint = DEFAULT_MULTICAST_GROUP_ENDPOINT
        self.multicast_bind_address = DEFAULT_MULTICAST_BIND_ADDRESS
        self.command_endpoint = DEFAULT_COMMAND_ENDPOINT

# PANEL

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_ExportOptionPanel"
    bl_label = "Export Option"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    remote = None

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons[__package__].preferences

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Export Type")
        split = split.split()
        col = split.column()
        col.prop(preferences, "exportOption", text="")

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text=("Temporary Folder", "Export Folder")[preferences.exportOption in ["BOTH", "FBX"]])
        split = split.split()
        col = split.column()
        col.prop(preferences, ("TempFolder", "ExportFBXFolder")[preferences.exportOption in ["BOTH", "FBX"]], text="")

        if preferences.exportOption in ["BOTH", "UNREAL"]:
            row = layout.row(align=True)
            row.scale_y = 1.5
            row.operator("ue4workspace.connecttounrealengine",icon="PLUGIN", text=("Disconnect Unreal Engine", "Connect Unreal Engine")[self.remote._broadcast_connection is None])
            row = layout.row(align=True)
            row.scale_y = 1.5
            row.operator("ue4workspace.checkconnection",icon="FILE_REFRESH", text="Refresh Project")

            if self.remote.remote_nodes:
                layout.prop(preferences, "SM_TabListProject", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.SM_TabListProject], emboss=False)
                if preferences.SM_TabListProject:
                    for X in self.remote.remote_nodes:
                        boxes = layout.box()
                        boxes.label(text=X.get("project_name", "Project"), icon="FILE_FOLDER")

# OPERATOR

class OP_ConnectToUnrealEngine(Operator):
    bl_idname = "ue4workspace.connecttounrealengine"
    bl_label = "UE4Workspace Operator"
    bl_description = "Connect / Disconnect Unreal Engine"

    remote = None

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences

        if self.remote._broadcast_connection is None:
            config = RemoteExecutionConfig(DEFAULT_MULTICAST_TTL=preferences.multicastTTL, DEFAULT_MULTICAST_GROUP_ENDPOINT=(preferences.multicastGroupEndPoint.split(":")[0], int(preferences.multicastGroupEndPoint.split(":")[1])), DEFAULT_MULTICAST_BIND_ADDRESS=preferences.multicastBindAddress, DEFAULT_COMMAND_ENDPOINT=("127.0.0.1", 6776))
            self.remote.start(config=config)
        else:
            self.remote.stop()
        return {"FINISHED"}

class OP_CheckConnection(Operator):
    bl_idname = "ue4workspace.checkconnection"
    bl_label = "UE4Workspace Operator"
    bl_description = "Refresh Project List"

    remote = None

    def execute(self, context):
        print(self.remote.remote_nodes)
        return {"FINISHED"}

# operator export

Ops = [
    OP_ConnectToUnrealEngine,
    OP_CheckConnection
]