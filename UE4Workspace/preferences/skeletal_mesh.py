import bpy
from bpy.types import PropertyGroup
from .. utils.connect import skeletons

class SKELETAL_MESH_FBX_export(PropertyGroup):

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

    tab_geometry: bpy.props.BoolProperty(
        name='Geometry',
        description='Geometry Tab',
        default=False
    )

    mesh_smooth_type: bpy.props.EnumProperty(
        name='Smoothing',
        description='Export smoothing information (prefer ‘Normals Only’ option if your target importer understand split normals)',
        items=[
            ('OFF', 'Normals Only', 'Export only normals instead of writing edge or face smoothing data'),
            ('FACE', 'Face', 'Write face smoothing'),
            ('EDGE', 'Edge', 'Write edge smoothing')
        ],
        default='OFF'
    )

    use_subsurf: bpy.props.BoolProperty(
        name='Export Subdivision Surface',
        description='Export the last Catmull-Rom subidivion modifier as FBX subdivision (Does not apply the modifier even if ‘Apply Modifiers’ is enabled)',
        default=False
    )

    use_mesh_modifiers: bpy.props.BoolProperty(
        name='Apply Modifiers',
        description='Apply modifiers to mesh objects (except Armature ones) - WARNING: prevents exporting shape keys',
        default=True
    )

    use_mesh_edges: bpy.props.BoolProperty(
        name='Loose Edges',
        description='Export loose edges (as two-vertices polygons)',
        default=False
    )

    use_tspace: bpy.props.BoolProperty(
        name='Tangent Space',
        description='Add binormal and tangent vectors, together with normal they form the tangent space (will only work correctly with tris/quads only meshes!)',
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

    def to_dict(self):
        return {prop: getattr(self, prop, None) for prop in ['global_scale', 'apply_unit_scale', 'axis_forward', 'axis_up', 'apply_unit_scale', 'bake_space_transform', 'mesh_smooth_type', 'use_subsurf', 'use_mesh_modifiers', 'use_mesh_edges', 'use_tspace', 'primary_bone_axis', 'secondary_bone_axis', 'armature_nodetype', 'use_armature_deform_only', 'add_leaf_bones']}

class SKELETAL_MESH_unreal_engine_export(PropertyGroup):

    tab_mesh: bpy.props.BoolProperty(
        name='Mesh',
        description='Mesh Tab',
        default=False
    )

    import_content_type: bpy.props.EnumProperty(
        name='Import Content Type',
        description='Filter the content we want to import from the incoming FBX skeletal mesh',
        items=[
            ('FBXICT_ALL', 'Geometry and Skinning Weights', 'Import all fbx content* – geometry, skinning and weights'),
            ('FBXICT_GEOMETRY', 'Geometry', 'Import the skeletal mesh geometry only (will create a default skeleton, or map the geometry to the existing one). Morph and LOD can be imported with it'),
            ('FBXICT_SKINNING_WEIGHTS', 'Skinning Weights', 'Import the skeletal mesh skinning and weights only (no geometry will be imported). Morph and LOD will not be imported with this settings')
        ],
        default='FBXICT_ALL'
    )

    vertex_color_import_option: bpy.props.EnumProperty(
        name='Vertex Color Import Option',
        description='Specify how vertex colors should be imported',
        items=[
            ('REPLACE', 'Replace', 'Import the static mesh using the vertex colors from the FBX file'),
            ('IGNORE', 'Ignore', 'Ignore vertex colors from the FBX file, and keep the existing mesh vertex colors'),
            ('OVERRIDE', 'Override', 'Override all vertex colors with the specified color')
        ],
        default='REPLACE'
    )

    vertex_override_color: bpy.props.FloatVectorProperty(
        name='Vertex Override Color',
        description='Specify override color in the case that VertexColorImportOption is set to Override',
        subtype='COLOR_GAMMA',
        size=4,
        default=(0.0,0.0,0.0,0.0),
        min=0.0,
        max=1.0
    )

    update_skeleton_reference_pose: bpy.props.BoolProperty(
        name='Update Skeleton Reference Pose',
        description='If enabled, update the Skeleton (of the mesh being imported)’s reference pose',
        default=False
    ) 

    use_t0_as_ref_pose: bpy.props.BoolProperty(
        name='Use T0 As Ref Pose',
        description='Enable this option to use frame 0 as reference pose',
        default=False
    )

    preserve_smoothing_groups: bpy.props.BoolProperty(
        name='Preserve Smoothing Groups',
        description='If checked, triangles with non-matching smoothing groups will be physically split',
        default=True
    )

    import_meshes_in_bone_hierarchy: bpy.props.BoolProperty(
        name='Import Meshes In Bone Hierarchy',
        description='If checked, meshes nested in bone hierarchies will be imported instead of being converted to bones',
        default=True
    )

    import_morph_targets: bpy.props.BoolProperty(
        name='Import Morph Targets',
        description='If enabled, creates Unreal morph objects for the imported meshes',
        default=False
    )

    import_mesh_lo_ds: bpy.props.BoolProperty(
        name='Import Mesh LODs',
        description='If enabled, creates LOD models for Unreal meshes from LODs in the import file; If not enabled, only the base mesh from the LOD group is imported',
        default=False
    )

    normal_import_method: bpy.props.EnumProperty(
        name='Normal Import Method',
        description='Enabling this option will read the tangents(tangent,binormal,normal) from FBX file instead of generating them automatically',
        items=[
            ('COMPUTE_NORMALS', 'Compute Normals', ''),
            ('IMPORT_NORMALS', 'Import Normals', ''),
            ('IMPORT_NORMALS_AND_TANGENTS', 'Import Normals and Tangents', '')
        ],
        default='IMPORT_NORMALS'
    )

    normal_generation_method: bpy.props.EnumProperty(
        name='Normal Generation Method',
        description='Use the MikkTSpace tangent space generator for generating normals and tangents on the mesh',
        items=[
            ('BUILT_IN', 'Built In', 'Use the legacy built in method to generate normals (faster in some cases)'),
            ('MIKK_T_SPACE', 'Mikk T Space', 'Use MikkTSpace to generate normals and tangents')
            ],
        default='MIKK_T_SPACE'
    )

    compute_weighted_normals: bpy.props.BoolProperty(
        name='Compute Weighted Normals',
        description='Enabling this option will use weighted normals algorithm (area and angle) when computing normals or tangents',
        default=True
    )

    threshold_position: bpy.props.FloatProperty(
        name='Threshold Position',
        description='Threshold to compare vertex position equality',
        default=0.00002
    )

    threshold_tangent_normal: bpy.props.FloatProperty(
        name='Threshold Tangent Normal',
        description='Threshold to compare normal, tangent or bi-normal equality',
        default=0.00002
    )

    threshold_uv: bpy.props.FloatProperty(
        name='Threshold UV',
        description='Threshold to compare UV equality',
        default=0.000977
    )

    create_physics_asset: bpy.props.EnumProperty(
        name='Physics Asset',
        description='Physics Asset',
        items=[
            ('CREATE', 'Create New', 'create new PhysicsAsset')
        ],
        default='CREATE'
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

    tab_material: bpy.props.BoolProperty(
        name='Material',
        description='Material Tab',
        default=False
    )

    material_search_location: bpy.props.EnumProperty(
        name='Search Location',
        description='Specify where we should search for matching materials when importing',
        items=[
            ('LOCAL', 'Local', 'Search for matching material in local import folder only'),
            ('UNDER_PARENT', 'Under Parent', 'Search for matching material recursively from parent folder'),
            ('UNDER_ROOT', 'Under Root', 'Search for matching material recursively from root folder'),
            ('ALL_ASSETS', 'All Assets', 'Search for matching material in all assets folders')
            ],
        default='LOCAL'
    )

    import_materials: bpy.props.BoolProperty(
        name='Import Material',
        description='Whether to automatically create Unreal materials for materials found in the FBX scene',
        default=False
    )

    import_textures: bpy.props.BoolProperty(
        name='Import Texture',
        description='The option works only when option “Import Material” is OFF. If “Import Material” is ON, textures are always imported',
        default=True
    )

    invert_normal_maps: bpy.props.BoolProperty(
        name='Invert Normal Maps',
        description='If importing textures is enabled, this option will cause normal map Y (Green) values to be inverted',
        default=False
    )

    reorder_material_to_fbx_order: bpy.props.BoolProperty(
        name='Reorder Material To FBX Order',
        description='If checked, The material list will be reorder to the same order has the FBX file',
        default=True
    )

    def to_dict(self):
        return {prop: list(getattr(self, prop, [])) if prop in ['vertex_override_color', 'import_translation', 'import_rotation'] else getattr(self, prop, None) for prop in [
                'import_content_type',
                'vertex_color_import_option',
                'vertex_override_color',
                'update_skeleton_reference_pose',
                'use_t0_as_ref_pose',
                'preserve_smoothing_groups',
                'import_meshes_in_bone_hierarchy',
                'import_morph_targets',
                'import_mesh_lo_ds',
                'normal_import_method',
                'normal_generation_method',
                'compute_weighted_normals',
                'threshold_position',
                'threshold_tangent_normal',
                'threshold_uv',
                'create_physics_asset',

                'import_translation',
                'import_rotation',
                'import_uniform_scale',

                'convert_scene',
                'force_front_x_axis',
                'convert_scene_unit',
                'override_full_name',

                'material_search_location',
                'import_materials',
                'import_textures',
                'invert_normal_maps',
                'reorder_material_to_fbx_order'
            ]}

class SKELETAL_MESH_export(PropertyGroup):

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

    use_custom_props: bpy.props.BoolProperty(
        name='Custom Properties',
        description='Export custom properties',
        default=False
    )

    apply_rotation: bpy.props.BoolProperty(
        name='Apply Rotation',
        description='Apply local rotation object',
        default=True
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

    option: bpy.props.EnumProperty(
        name='Export Skeletal Mesh Option',
        description='Export Mesh Option',
        items=[
            ('SELECT', 'Select', 'Export selected skeletal mesh on scene'),
            ('ALL', 'All', 'Export All Skeletal Mesh On Scene')
        ],
        default='SELECT'
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

    mesh: bpy.props.EnumProperty(
        name='Mesh Option',
        description='Mesh Option',
        items=[
            ('COMBINE', 'Combine', 'Combine mesh into one fbx file'),
            ('PART', 'Part', 'Separate mesh into multiple fbx file')
        ],
        default='COMBINE'
    )

    def get_skeleton(self, context):
        return [('CREATE', 'Create New', 'Create new skeleton')] + skeletons

    skeleton: bpy.props.EnumProperty(
        name='Skeleton',
        description='Skeleton',
        items=get_skeleton,
        default=None
    )

    fbx: bpy.props.PointerProperty(
        type=SKELETAL_MESH_FBX_export
    )

    unreal_engine: bpy.props.PointerProperty(
        type=SKELETAL_MESH_unreal_engine_export
    )