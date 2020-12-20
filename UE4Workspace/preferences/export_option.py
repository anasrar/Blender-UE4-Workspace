import bpy
from bpy.types import PropertyGroup

class EXPORT_option(PropertyGroup):

    type: bpy.props.EnumProperty(
        name='Export Type',
        description='Select the way you want export',
        items=[
            ('FILE', 'To File', 'Export as a file'),
            ('UNREAL', 'To Unreal Engine', 'Export directly to Unreal Engine project'),
            ('BOTH', 'To File and Unreal Engine', 'Export as a file and directly export to Unreal Engine project')
            ],
        default='BOTH'
    )

    export_folder: bpy.props.StringProperty(
        name='Export Folder',
        description='Folder to export, must have write permissions',
        default='',
        maxlen=1024,
        subtype='DIR_PATH'
    )

    temp_folder: bpy.props.StringProperty(
        name='Temporary Folder',
        description='Temporary folder for export, must have write permissions',
        default='',
        maxlen=1024,
        subtype='DIR_PATH'
    )

    project_list: bpy.props.BoolProperty(
        name='Project List',
        description='Project List Tab',
        default=False
    )