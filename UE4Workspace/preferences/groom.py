import bpy
from bpy.types import PropertyGroup

class GROOM_export(PropertyGroup):

    subfolder: bpy.props.StringProperty(
        name='Subfolder',
        description='Subfolder for groom export folder, leave it blank if you want to export to root project folder',
        default=''
    )

    overwrite_file: bpy.props.BoolProperty(
        name='Overwrite File',
        description='Overwrite file if filename exist, if false will not export',
        default=True
    )

    apply_rotation: bpy.props.BoolProperty(
        name='Apply Rotation',
        description='Apply local rotation object',
        default=True
    )

    use_custom_props: bpy.props.BoolProperty(
        name='Custom Properties',
        description='Export custom properties',
        default=True
    )

    option: bpy.props.EnumProperty(
        name='Export Groom Option',
        description='Export Groom Option',
        items=[
            ('SELECT', 'Select', 'Export selected mesh with hair on scene'),
            ('ALL', 'All', 'Export all mesh with hair on scene')
        ],
        default='SELECT'
    )

    origin: bpy.props.EnumProperty(
        name='Mesh Origin',
        description='Mesh Origin',
        items=[
            ('OBJECT', 'Object', 'Use object origin'),
            ('SCENE', 'Scene', 'Use scene origin')
        ],
        default='OBJECT'
    )