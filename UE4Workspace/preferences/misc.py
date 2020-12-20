import bpy
from bpy.types import PropertyGroup

class MISC_option(PropertyGroup):

    experimental_features: bpy.props.BoolProperty(
        name='Experimental Features',
        description='Show some experimental features',
        default=False
    )

    @classmethod
    def draw_panel(cls, context, layout, preferences):
        box = layout.box()

        box.label(text='Misc.', icon='FRAME_NEXT')

        data_properties = [
            (preferences.misc, 'Experimental Features', 'experimental_features'),
        ]

        for data, label_str, property_str in data_properties:
            row = box.row()
            split = row.split(factor=0.5)
            col = split.column()
            col.alignment = 'LEFT'
            col.label(text=label_str, icon='DECORATE')
            col = split.column()
            col.prop(data, property_str, text='')
