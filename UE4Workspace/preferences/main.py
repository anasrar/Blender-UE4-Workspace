import bpy
from bpy.utils import register_class, unregister_class
from bpy.types import AddonPreferences, PropertyGroup

from . export_option import EXPORT_option
from . connect_unreal_engine import CONNECT_unreal_engine
from . import_asset import IMPORT_ASSET_fbx_import, IMPORT_ASSET_unreal_engine, PG_IMPORT_ASSET
from . static_mesh import STATIC_MESH_FBX_export, STATIC_MESH_unreal_engine_export, STATIC_MESH_export
from . skeletal_mesh import SKELETAL_MESH_FBX_export, SKELETAL_MESH_unreal_engine_export, SKELETAL_MESH_export
from . animation import ANIMATION_FBX_export, ANIMATION_unreal_engine_export, ANIMATION_export
from . groom import GROOM_export
from . misc import MISC_option

class Preferences(AddonPreferences):
    bl_idname = 'UE4Workspace'

    export: bpy.props.PointerProperty(
        type=EXPORT_option
    )

    connect_unreal_engine: bpy.props.PointerProperty(
        type=CONNECT_unreal_engine
    )

    import_asset: bpy.props.PointerProperty(
        type=PG_IMPORT_ASSET
    )

    static_mesh: bpy.props.PointerProperty(
        type=STATIC_MESH_export
    )

    skeletal_mesh: bpy.props.PointerProperty(
        type=SKELETAL_MESH_export
    )

    animation: bpy.props.PointerProperty(
        type=ANIMATION_export
    )

    groom: bpy.props.PointerProperty(
        type=GROOM_export
    )

    misc: bpy.props.PointerProperty(
        type=MISC_option
    )

    active_tab_addon: bpy.props.EnumProperty(
        name='Tab',
        description='Tab setting',
        items=[
            ('CONNECT', 'Connect To Unreal Engine', ''),
            ('MISC', 'Misc.', ''),
        ],
        default='CONNECT'
    )

    def draw(self, context):
        layout = self.layout

        layout.row().prop(self, 'active_tab_addon', expand=True)

        draw_preferences_tab = {
            'CONNECT': CONNECT_unreal_engine.draw_panel,
            'MISC': MISC_option.draw_panel
        }

        draw_preferences_tab[self.active_tab_addon](context, layout, self)

list_class_to_register = [
    EXPORT_option,
    CONNECT_unreal_engine,
    IMPORT_ASSET_fbx_import,
    IMPORT_ASSET_unreal_engine,
    PG_IMPORT_ASSET,
    STATIC_MESH_FBX_export,
    STATIC_MESH_unreal_engine_export,
    STATIC_MESH_export,
    SKELETAL_MESH_FBX_export,
    SKELETAL_MESH_unreal_engine_export,
    SKELETAL_MESH_export,
    ANIMATION_FBX_export,
    ANIMATION_unreal_engine_export,
    ANIMATION_export,
    GROOM_export,
    MISC_option,
    Preferences
]

def register():
    for x in list_class_to_register:
        register_class(x)

def unregister():
    for x in list_class_to_register[::-1]:
        unregister_class(x)