import bpy
from bpy.types import PropertyGroup
from .. utils.connect import skeletons

class ANIMATION_FBX_export(PropertyGroup):

    tab_transform: bpy.props.BoolProperty(
        name='Transform',
        description='Transform Tab',
        default=False
    )

    global_scale: bpy.props.FloatProperty(
        name='Scale',
        description='Scale all data (Some importers do not support scaled armatures!)',
        default=1.0,
        min=0.001,
        max=1000
    )

    apply_unit_scale: bpy.props.EnumProperty(
        name='Apply Scalings',
        description='How to apply custom and units scalings in generated FBX file (Blender uses FBX scale to detect units on import, but many other applications do not handle the same way)',
        items=[
            ('FBX_SCALE_NONE', 'All Local', 'Apply custom scaling and units scaling to each object transformation, FBX scale remains at 1.0'),
            ('FBX_SCALE_UNITS', 'FBX Units Scale', 'Apply custom scaling to each object transformation, and units scaling to FBX scale'),
            ('FBX_SCALE_CUSTOM', 'FBX Custom Scale', 'Apply custom scaling to FBX scale, and units scaling to each object transformation'),
            ('FBX_SCALE_ALL', 'FBX All', 'Apply custom scaling and units scaling to FBX scale')
        ],
        default='FBX_SCALE_NONE'
    )

    axis_forward: bpy.props.EnumProperty(
        name='Forward',
        description='Forward',
        items=[
            ('X', 'X Forward', 'X Forward'),
            ('Y', 'Y Forward', 'Y Forward'),
            ('Z', 'Z Forward', 'Z Forward'),
            ('-X', '-X Forward', '-X Forward'),
            ('-Y', '-Y Forward', '-Y Forward'),
            ('-Z', '-Z Forward', '-Z Forward')
        ],
        default='-Z'
    )

    axis_up: bpy.props.EnumProperty(
        name='Up',
        description='Up',
        items=[
            ('X', 'X Up', 'X Up'),
            ('Y', 'Y Up', 'Y Up'),
            ('Z', 'Z Up', 'Z Up'),
            ('-X', '-X Up', '-X Up'),
            ('-Y', '-Y Up', '-Y Up'),
            ('-Z', '-Z Up', '-Z Up')
        ],
        default='Y'
    )

    apply_unit_scale: bpy.props.BoolProperty(
        name='Apply Unit',
        description='Take into account current Blender units settings (if unset, raw Blender Units values are used as-is)',
        default=True
    )

    bake_space_transform: bpy.props.BoolProperty(
        name='!EXPERIMENTAL! Apply Transform',
        description='Bake space transform into object data, avoids getting unwanted rotations to objects when target space is not aligned with Blender’s space (WARNING! experimental option, use at own risks, known broken with armatures/animations)',
        default=False
    )

    tab_armature: bpy.props.BoolProperty(
        name='Armature',
        description='Armature Tab',
        default=False
    )

    primary_bone_axis: bpy.props.EnumProperty(
        name='Primary Bone Axis',
        description='Primary Bone Axis',
        items=[
            ('X', 'X Axis', 'X Axis'),
            ('Y', 'Y Axis', 'Y Axis'),
            ('Z', 'Z Axis', 'Z Axis'),
            ('-X', '-X Axis', '-X Axis'),
            ('-Y', '-Y Axis', '-Y Axis'),
            ('-Z', '-Z Axis', '-Z Axis')
        ],
        default='Y'
    )

    secondary_bone_axis: bpy.props.EnumProperty(
        name='Secondary Bone Axis',
        description='Secondary Bone Axis',
        items=[
            ('X', 'X Axis', 'X Axis'),
            ('Y', 'Y Axis', 'Y Axis'),
            ('Z', 'Z Axis', 'Z Axis'),
            ('-X', '-X Axis', '-X Axis'),
            ('-Y', '-Y Axis', '-Y Axis'),
            ('-Z', '-Z Axis', '-Z Axis')
        ],
        default='X'
    )

    armature_nodetype: bpy.props.EnumProperty(
        name='Armature FBXNode Type',
        description='FBX type of node (object) used to represent Blender’s armatures (use Null one unless you experience issues with other app, other choices may no import back perfectly in Blender…)',
        items=[
            ('NULL', 'Null', '‘Null’ FBX node, similar to Blender’s Empty (default)'),
            ('ROOT', 'Root', '‘Root’ FBX node, supposed to be the root of chains of bones'),
            ('LIMBNODE', 'LimbNode', '‘LimbNode’ FBX node, regular joint between two bones')
        ],
        default='NULL'
    )

    use_armature_deform_only: bpy.props.BoolProperty(
        name='Only Deform Bones',
        description='Only write deforming bones (and non-deforming ones when they have deforming children)',
        default=False
    )

    add_leaf_bones: bpy.props.BoolProperty(
        name='Add Leaf Bones',
        description='Only write deforming bones (and non-deforming ones when they have deforming children)',
        default=True
    )

    tab_bake_animation: bpy.props.BoolProperty(
        name='Bake Animation',
        description='Bake Animation Tab',
        default=False
    )

    bake_anim_use_all_bones: bpy.props.BoolProperty(
        name='Key All Bones',
        description='Force exporting at least one key of animation for all bones (needed with some target applications, like UE4)',
        default=True
    )

    bake_anim_force_startend_keying: bpy.props.BoolProperty(
        name='Force Start/End Keying',
        description='Always add a keyframe at start and end of actions for animated channels',
        default=True
    )

    bake_anim_step: bpy.props.FloatProperty(
        name='Sampling Rate',
        description='How often to evaluate animated values (in frames)',
        default=1.0,
        min=0.01,
        max=100
    )

    bake_anim_simplify_factor: bpy.props.FloatProperty(
        name='Simplify',
        description='How much to simplify baked values (0.0 to disable, the higher the more simplified)',
        default=1.0,
        min=0,
        max=100
    )

    def to_dict(self):
        return {prop: getattr(self, prop, None) for prop in ['global_scale', 'apply_unit_scale', 'axis_forward', 'axis_up', 'apply_unit_scale', 'bake_space_transform', 'primary_bone_axis', 'secondary_bone_axis', 'armature_nodetype', 'use_armature_deform_only', 'add_leaf_bones', 'bake_anim_use_all_bones', 'bake_anim_force_startend_keying', 'bake_anim_step', 'bake_anim_simplify_factor']}

class ANIMATION_unreal_engine_export(PropertyGroup):

    tab_animation: bpy.props.BoolProperty(
        name='Animation',
        description='Animation Tab',
        default=False
    )

    animation_length: bpy.props.EnumProperty(
        name='Animation Length',
        description='Which animation range to import. The one defined at Exported, at Animated time or define a range manually',
        items=[
            ('FBXALIT_EXPORTED_TIME', 'Exported Time', 'This option imports animation frames based on what is defined at the time of export'),
            ('FBXALIT_ANIMATED_KEY', 'Animated Time', 'Will import the range of frames that have animation. Can be useful if the exported range is longer than the actual animation in the FBX file'),
            ('FBXALIT_SET_RANGE', 'Set Range', 'This will enable the Start Frame and End Frame properties for you to define the frames of animation to import')
        ],
        default='FBXALIT_EXPORTED_TIME'
    )

    import_meshes_in_bone_hierarchy: bpy.props.BoolProperty(
        name='Import Meshes in Bone Hierarchy',
        description='If checked, meshes nested in bone hierarchies will be imported instead of being converted to bones',
        default=True
    )

    def update_frame_import_range(self, context):
        range_min, range_max = self.frame_import_range
        if range_min > range_max:
            self.frame_import_range[1] = range_min
        if range_max < range_min:
            self.frame_import_range[0] = range_max

    frame_import_range: bpy.props.IntVectorProperty(
        name='Frame Import Range',
        description='Frame range used when Set Range is used in Animation Length',
        default=[0, 0],
        size=2,
        update=update_frame_import_range
    )

    use_default_sample_rate: bpy.props.BoolProperty(
        name='Use Default Sample Rate',
        description='If enabled, samples all animation curves to 30 FPS',
        default=False
    )

    custom_sample_rate: bpy.props.IntProperty(
        name='Custom Sample Rate',
        description='Sample fbx animation data at the specified sample rate, 0 find automaticaly the best sample rate',
        default=0,
        min=0,
        max=60
    )

    import_custom_attribute: bpy.props.BoolProperty(
        name='Import Custom Attribute',
        description='Import if custom attribute as a curve within the animation',
        default=True
    )

    delete_existing_custom_attribute_curves: bpy.props.BoolProperty(
        name='Delete Existing Custom Attribute Curves',
        description='If true, all previous custom attribute curves will be deleted when doing a re-import',
        default=False
    )

    import_bone_tracks: bpy.props.BoolProperty(
        name='Import Bone Tracks',
        description='Import bone transform tracks. If false, this will discard any bone transform tracks. (useful for curves only animations)',
        default=True
    )

    set_material_drive_parameter_on_custom_attribute: bpy.props.BoolProperty(
        name='Set Material Curve Type',
        description='Set Material Curve Type for all custom attributes that exists',
        default=False
    )

    material_curve_suffixes: bpy.props.StringProperty(
        name='Material Curve Suffixes',
        description='Set Material Curve Type for the custom attribute with the following suffixes. This doesn’t matter if Set Material Curve Type is true',
        default='_mat'
    )

    remove_redundant_keys: bpy.props.BoolProperty(
        name='Remove Redundant Keys',
        description='When importing custom attribute as curve, remove redundant keys',
        default=True
    )

    delete_existing_morph_target_curves: bpy.props.BoolProperty(
        name='Delete Existing Morph Target Curves',
        description='If enabled, this will delete this type of asset from the FBX',
        default=False
    )

    do_not_import_curve_with_zero: bpy.props.BoolProperty(
        name='Do not Import Curve With 0 Values',
        description='When importing custom attribute or morphtarget as curve, do not import if it doens’t have any value other than zero. This is to avoid adding extra curves to evaluate',
        default=True
    )

    preserve_local_transform: bpy.props.BoolProperty(
        name='Preserve Local Transform',
        description='If enabled, this will import a curve within the animation',
        default=False
    )

    tab_transform: bpy.props.BoolProperty(
        name='Transform',
        description='Transform Tab',
        default=False
    )

    import_translation: bpy.props.FloatVectorProperty(
        name='Import Translation',
        description='Import Translation',
        subtype='XYZ',
        default=(0.0, 0.0, 0.0)
    )

    import_rotation: bpy.props.FloatVectorProperty(
        name='Import Rotation',
        description='Import Rotation',
        subtype='XYZ',
        default=(0.0, 0.0, 0.0)
    )

    import_uniform_scale: bpy.props.FloatProperty(
        name='Import Uniform Scale',
        description='Import Uniform Scale',
        default=1.0
    )

    tab_misc: bpy.props.BoolProperty(
        name='Misc.',
        description='Miscellaneous Tab',
        default=False
    )

    convert_scene: bpy.props.BoolProperty(
        name='Convert Scene',
        description='Convert the scene from FBX coordinate system to UE4 coordinate system',
        default=True
    )

    force_front_x_axis: bpy.props.BoolProperty(
        name='Force Front XAxis',
        description='Convert the scene from FBX coordinate system to UE4 coordinate system with front X axis instead of -Y',
        default=False
    )

    convert_scene_unit: bpy.props.BoolProperty(
        name='Convert Scene Unit',
        description='Convert the scene from FBX unit to UE4 unit (centimeter)',
        default=False
    )

    override_full_name: bpy.props.BoolProperty(
        name='Override Full Name',
        description='Use the string in “Name” field as full name of mesh. The option only works when the scene contains one mesh',
        default=True
    )

    def to_dict(self):
        return {prop: list(getattr(self, prop, [])) if prop in ['frame_import_range', 'import_translation', 'import_rotation'] else ((self.material_curve_suffixes.split('|') if bool(self.material_curve_suffixes) else []) if prop == 'material_curve_suffixes' else getattr(self, prop, None)) for prop in [
                'animation_length',
                'import_meshes_in_bone_hierarchy',
                'frame_import_range',
                'use_default_sample_rate',
                'custom_sample_rate',
                'import_custom_attribute',
                'delete_existing_custom_attribute_curves',
                'import_bone_tracks',
                'set_material_drive_parameter_on_custom_attribute',
                'material_curve_suffixes',
                'remove_redundant_keys',
                'delete_existing_morph_target_curves',
                'do_not_import_curve_with_zero',
                'preserve_local_transform',

                'import_translation',
                'import_rotation',
                'import_uniform_scale',

                'convert_scene',
                'force_front_x_axis',
                'convert_scene_unit',
                'override_full_name'
            ]}

class ANIMATION_export(PropertyGroup):

    subfolder: bpy.props.StringProperty(
        name='Subfolder',
        description='Subfolder for skeletal mesh export folder, leave it blank if you want to export to root project folder',
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
        default=False
    )

    root_bone: bpy.props.EnumProperty(
        name='Skeletal Mesh Root',
        description='Skeletal Mesh Root Bone',
        items=[
            ('ARMATURE', 'Armature Hierarchy', 'Use original armature hierarchy'),
            ('AUTO', 'Auto Add', 'Auto add root bone if does not exist on the armature otherwise will use armature hierarchy'),
            ('OBJECT', 'Object Name', 'Use object name as root bone')
        ],
        default='ARMATURE'
    )

    origin: bpy.props.EnumProperty(
        name='Skeletal Mesh Origin',
        description='Skeletal Mesh Origin',
        items=[
            ('OBJECT', 'Object', 'Use object origin'),
            ('SCENE', 'Scene', 'Use scene origin')
        ],
        default='OBJECT'
    )

    def get_skeleton(self, context):
        return [('NONE', 'None', 'None')] + skeletons

    skeleton: bpy.props.EnumProperty(
        name='Skeleton',
        description='Skeleton',
        items=get_skeleton,
        default=None
    )

    fbx: bpy.props.PointerProperty(
        type=ANIMATION_FBX_export
    )

    unreal_engine: bpy.props.PointerProperty(
        type=ANIMATION_unreal_engine_export
    )