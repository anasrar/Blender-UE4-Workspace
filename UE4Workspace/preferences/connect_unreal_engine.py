import bpy
from bpy.types import PropertyGroup

class CONNECT_unreal_engine(PropertyGroup):

    main_folder: bpy.props.StringProperty(
        name='Main Folder',
        default='Blender'
    )

    multicast_group_end_point: bpy.props.StringProperty(
        name='Multicast Group Endpoint',
        default='239.0.0.1:6766'
    )

    multicast_bind_address: bpy.props.StringProperty(
        name='Multicast Bind Address',
        default='0.0.0.0'
    )

    multicast_ttl: bpy.props.IntProperty(
        name='Multicast Time-To-Live',
        default=0
    )

    @classmethod
    def draw_panel(cls, context, layout, preferences):
        box = layout.box()

        box.label(text='Remote Execution', icon='FRAME_NEXT')

        data_properties = [
            (preferences.connect_unreal_engine, 'Main Folder', 'main_folder'),
            (preferences.connect_unreal_engine, 'Multicast Group Endpoint', 'multicast_group_end_point'),
            (preferences.connect_unreal_engine, 'Multicast Bind Address', 'multicast_bind_address'),
            (preferences.connect_unreal_engine, 'Multicast Time-To-Live', 'multicast_ttl'),
        ]

        for data, label_str, property_str in data_properties:
            row = box.row()
            split = row.split(factor=0.5)
            col = split.column()
            col.alignment = 'LEFT'
            col.label(text=label_str, icon='DECORATE')
            col = split.column()
            col.prop(data, property_str, text='')
