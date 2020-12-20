import bpy
from bpy.utils import register_class, unregister_class
from bpy.types import Panel, Operator
from .. utils.connect import remote

class OP_ConnectToUnrealEngine(Operator):
    bl_idname = 'ue4workspace.connect_to_unreal_engine'
    bl_label = 'Connect / Disconnect Unreal Engine'

    def execute(self, context):
        preferences = context.preferences.addons['UE4Workspace'].preferences
        connect_unreal_engine = preferences.connect_unreal_engine

        if remote.is_connect:
            remote.disconnect()
        else:
            remote.connect(DEFAULT_MULTICAST_TTL=connect_unreal_engine.multicast_ttl, DEFAULT_MULTICAST_GROUP_ENDPOINT=(connect_unreal_engine.multicast_group_end_point.split(':')[0], int(connect_unreal_engine.multicast_group_end_point.split(':')[1])), DEFAULT_MULTICAST_BIND_ADDRESS=connect_unreal_engine.multicast_bind_address, DEFAULT_COMMAND_ENDPOINT=('127.0.0.1', 6776))

        return {'FINISHED'}

class OP_RefreshProjectList(Operator):
    bl_idname = 'ue4workspace.refresh_project_list'
    bl_label = 'Refresh Project'

    def execute(self, context):
        print(remote.remote_nodes)
        return {'FINISHED'}

class PANEL(Panel):
    bl_idname = 'UE4WORKSPACE_PT_ExportOptionPanel'
    bl_label = 'Export Option'
    bl_category = 'UE4Workspace'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons['UE4Workspace'].preferences

        row = layout.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = 'RIGHT'
        col.label(text='Export Type')
        col = split.column()
        col.prop(preferences.export, 'type', text='')

        row = layout.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = 'RIGHT'
        col.label(text=('Export Folder' if preferences.export.type in ['BOTH', 'FILE'] else 'Temporary Folder'))
        col = split.column()
        col.prop(preferences.export, ('export_folder' if preferences.export.type in ['BOTH', 'FILE'] else 'temp_folder'), text='')

        if preferences.export.type in ['BOTH', 'UNREAL']:
            col = layout.column()
            col.scale_y = 1.5
            col.operator('ue4workspace.connect_to_unreal_engine', icon='PLUGIN', text=('Disconnect Unreal Engine' if remote.is_connect else 'Connect Unreal Engine'))
            col.operator('ue4workspace.refresh_project_list', icon='FILE_REFRESH')

            if remote.remote_nodes:
                layout.prop(preferences.export, 'project_list', icon=('TRIA_DOWN' if preferences.export.project_list else 'TRIA_RIGHT'), emboss=False)
                if preferences.export.project_list:
                    for X in remote.remote_nodes:
                        box = layout.box()

                        col = box.column()
                        row = col.row()
                        split = row.split(factor=0.4)
                        col = split.column()
                        col.label(text='Project', icon='TEXT')
                        col.label(text='Engine', icon='TOOL_SETTINGS')
                        col = split.column()
                        col.label(text=X.get('project_name', 'Project'))
                        col.label(text=X.get('engine_version', 'XX.XX.XX').split('-')[0])

list_class_to_register = [
    OP_ConnectToUnrealEngine,
    OP_RefreshProjectList,
    PANEL
]

def register():
    for x in list_class_to_register:
        register_class(x)

def unregister():
    for x in list_class_to_register[::-1]:
        unregister_class(x)