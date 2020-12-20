import bpy
from bpy.types import PropertyGroup

class IMPORT_ASSET_fbx_import(PropertyGroup):

    tab_include: bpy.props.BoolProperty(
        name='Include',
        description='Include Tab',
        default=False
    )

    tab_transform: bpy.props.BoolProperty(
        name='Transform',
        description='Transform Tab',
        default=False
    )

    tab_orientation: bpy.props.BoolProperty(
        name='Orientation',
        description='Orientation Tab',
        default=False
    )

    tab_animation: bpy.props.BoolProperty(
        name='Animation',
        description='Animation Tab',
        default=False
    )

    tab_armature: bpy.props.BoolProperty(
        name='Armature',
        description='Armature Tab',
        default=False
    )

    use_manual_orientation: bpy.props.BoolProperty(
        name='Manual Orientation',
        description='Specify orientation and scale, instead of using embedded data in FBX file',
        default=False
    )

    global_scale: bpy.props.FloatProperty(
        name='Scale',
        description='Scale',
        default=1.0,
        min=0.001,
        max=1000.0
    )

    bake_space_transform: bpy.props.BoolProperty(
        name='Apply Transform',
        description='Bake space transform into object data, avoids getting unwanted rotations to objects when target space is not aligned with Blender’s space (WARNING! experimental option, use at own risks, known broken with armatures/animations)',
        default=False
    )

    use_custom_normals: bpy.props.BoolProperty(
        name='Custom Normals',
        description='if available (otherwise Blender will recompute them)',
        default=True
    )

    use_image_search: bpy.props.BoolProperty(
        name='Image Search',
        description='Search subdirs for any associated images (WARNING: bpy.props.may be slow)',
        default=True
    )

    use_alpha_decals: bpy.props.BoolProperty(
        name='Alpha Decals',
        description='Treat materials with alpha as decals (no shadow casting)',
        default=True
    )

    decal_offset: bpy.props.FloatProperty(
        name='Decal Offset',
        description='Displace geometry of alpha meshes',
        default=0.0,
        min=0.0,
        max=1.0
    )

    use_anim: bpy.props.BoolProperty(
        name='Animation',
        description='Import FBX animation',
        default=True
    )

    anim_offset: bpy.props.FloatProperty(
        name='Animation Offset',
        description='Offset to apply to animation during import, in frames',
        default=1.0
    )

    use_subsurf: bpy.props.BoolProperty(
        name='Subdivision Data',
        description='Import FBX subdivision information as subdivision surface modifiers',
        default=False
    )

    use_custom_props: bpy.props.BoolProperty(
        name='Custom Properties',
        description='Import user properties as custom properties',
        default=True
    )

    use_custom_props_enum_as_string: bpy.props.BoolProperty(
        name='Import Enums As Strings',
        description='Store enumeration values as strings',
        default=True
    )

    ignore_leaf_bones: bpy.props.BoolProperty(
        name='Ignore Leaf Bones',
        description='Ignore the last bone at the end of each chain (used to mark the length of the previous bone)',
        default=False
    )

    force_connect_children: bpy.props.BoolProperty(
        name='Force Connect Children',
        description='Force connection of children bones to their parent, even if their computed head/tail positions do not match (can be useful with pure-joints-type armatures)',
        default=False
    )

    automatic_bone_orientation: bpy.props.BoolProperty(
        name='Automatic Bone Orientation',
        description='Try to align the major bone axis with the bone children',
        default=False
    )

    primary_bone_axis: bpy.props.EnumProperty(
        name='Primary Bone Axis',
        description='',
        items=[
            ('X', 'X Axis', ''),
            ('Y', 'Y Axis', ''),
            ('Z', 'Z Axis', ''),
            ('-X', '-X Axis', ''),
            ('-Y', '-Y Axis', ''),
            ('-Z', '-Z Axis', '')
            ],
        default='Y'
    )

    secondary_bone_axis: bpy.props.EnumProperty(
        name='Secondary Bone Axis',
        description='',
        items=[
            ('X', 'X Axis', ''),
            ('Y', 'Y Axis', ''),
            ('Z', 'Z Axis', ''),
            ('-X', '-X Axis', ''),
            ('-Y', '-Y Axis', ''),
            ('-Z', '-Z Axis', '')
            ],
        default='X'
    )

    use_prepost_rot: bpy.props.BoolProperty(
        name='Use Pre/Post Rotation',
        description='Use pre/post rotation from FBX transform (you may have to disable that in some cases)',
        default=True
    )

    axis_forward: bpy.props.EnumProperty(
        name='Axis Forward',
        description='Forward',
        items=[
            ('X', 'X Forward', ''),
            ('Y', 'Y Forward', ''),
            ('Z', 'Z Forward', ''),
            ('-X', '-X Forward', ''),
            ('-Y', '-Y Forward', ''),
            ('-Z', '-Z Forward', '')
            ],
        default='-Z'
    )

    axis_up: bpy.props.EnumProperty(
        name='Axis Up',
        description='Up',
        items=[
            ('X', 'X Up', ''),
            ('Y', 'Y Up', ''),
            ('Z', 'Z Up', ''),
            ('-X', '-X Up', ''),
            ('-Y', '-Y Up', ''),
            ('-Z', '-Z Up', '')
            ],
        default='Y'
    )

    def to_dict(self):
        return {prop: getattr(self, prop, None) for prop in [
            'use_manual_orientation',
            'global_scale',
            'bake_space_transform',
            'use_custom_normals',
            'use_image_search',
            'use_alpha_decals',
            'decal_offset',
            'use_anim',
            'anim_offset',
            'use_subsurf',
            'use_custom_props',
            'use_custom_props_enum_as_string',
            'ignore_leaf_bones',
            'force_connect_children',
            'automatic_bone_orientation',
            'primary_bone_axis',
            'secondary_bone_axis',
            'use_prepost_rot',
            'axis_forward',
            'axis_up'
        ]}

class IMPORT_ASSET_unreal_engine(PropertyGroup):

    tab_exporter: bpy.props.BoolProperty(
        name='Exporter',
        description='Exporter Tab',
        default=False
    )

    fbx_export_compatibility: bpy.props.EnumProperty(
        name='FBX Export Compatibility',
        description='This will set the fbx sdk compatibility when exporting to fbx file. The default value is 2013',
        items=[
            ('FBX_2011', '2011', 'FBX 2011'),
            ('FBX_2012', '2012', 'FBX 2012'),
            ('FBX_2013', '2013', 'FBX 2013'),
            ('FBX_2014', '2014', 'FBX 2014'),
            ('FBX_2016', '2016', 'FBX 2016'),
            ('FBX_2018', '2018', 'FBX 2018')
            ],
        default='FBX_2013'
    )

    ascii: bpy.props.BoolProperty(
        name='ASCII',
        description='If enabled, save as ascii instead of binary',
        default=False
    )

    force_front_x_axis: bpy.props.BoolProperty(
        name='Force Front X Axis',
        description='If enabled, export with X axis as the front axis instead of default -Y',
        default=False
    )

    tab_mesh: bpy.props.BoolProperty(
        name='Mesh',
        description='Mesh Tab',
        default=False
    )

    vertex_color: bpy.props.BoolProperty(
        name='Vertex Color',
        description='If enabled, export vertex color',
        default=True
    )

    level_of_detail: bpy.props.BoolProperty(
        name='Level Of Detail',
        description='If enabled, export the level of detail',
        default=True
    )

    tab_static_mesh: bpy.props.BoolProperty(
        name='Static Mesh',
        description='Static Mesh Tab',
        default=False
    )

    collision: bpy.props.BoolProperty(
        name='Collision',
        description='If enabled, export collision',
        default=True
    )

    tab_skeletal_mesh: bpy.props.BoolProperty(
        name='Skeletal Mesh',
        description='Skeletal Mesh Tab',
        default=False
    )

    export_morph_targets: bpy.props.BoolProperty(
        name='Export Morph Targets',
        description='If enabled, export the morph targets',
        default=True
    )

    tab_animation: bpy.props.BoolProperty(
        name='Animation',
        description='Animation Tab',
        default=False
    )

    export_preview_mesh: bpy.props.BoolProperty(
        name='Export Preview Mesh',
        description='If enable, the preview mesh link to the exported animations will be also exported',
        default=False
    )

    map_skeletal_motion_to_root: bpy.props.BoolProperty(
        name='Map Skeletal Motion To Root',
        description='If enable, Map skeletal actor motion to the root bone of the skeleton',
        default=False
    )

    export_local_time: bpy.props.BoolProperty(
        name='Export Local Time',
        description='If enabled, export sequencer animation in its local time, relative to its master sequence',
        default=True
    )

    def to_dict(self):
        return {prop: getattr(self, prop, None) for prop in [
            'fbx_export_compatibility',
            'ascii',
            'force_front_x_axis',
            'vertex_color',
            'level_of_detail',
            'collision',
            'export_morph_targets',
            'export_preview_mesh',
            'map_skeletal_motion_to_root',
            'export_local_time',
        ]}

class PG_IMPORT_ASSET(PropertyGroup):

    fbx: bpy.props.PointerProperty(
        type=IMPORT_ASSET_fbx_import
    )

    unreal_engine: bpy.props.PointerProperty(
        type=IMPORT_ASSET_unreal_engine
    )