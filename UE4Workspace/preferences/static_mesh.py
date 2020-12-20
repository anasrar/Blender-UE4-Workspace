import bpy
from bpy.types import PropertyGroup

class STATIC_MESH_FBX_export(PropertyGroup):

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

    def to_dict(self):
        return {prop: getattr(self, prop, None) for prop in ['global_scale', 'apply_unit_scale', 'axis_forward', 'axis_up', 'apply_unit_scale', 'bake_space_transform', 'mesh_smooth_type', 'use_subsurf', 'use_mesh_modifiers', 'use_mesh_edges', 'use_tspace']}

class STATIC_MESH_unreal_engine_export(PropertyGroup):

    tab_mesh: bpy.props.BoolProperty(
        name='Mesh',
        description='Mesh Tab',
        default=False
    )

    auto_generate_collision: bpy.props.BoolProperty(
        name='Auto Generate Collision',
        description='If checked, collision will automatically be generated (ignored if custom collision is imported or used)',
        default=True
    )

    vertex_color_import_option: bpy.props.EnumProperty(
        name='Vertex Color Import Option',
        description='Specify how vertex colors should be imported',
        items=[
            ('IGNORE', 'Ignore', 'Ignore vertex colors from the FBX file, and keep the existing mesh vertex colors'),
            ('OVERRIDE', 'Override', 'Override all vertex colors with the specified color'),
            ('REPLACE', 'Replace', 'Import the static mesh using the vertex colors from the FBX file')
        ],
        default='IGNORE'
    )

    vertex_override_color: bpy.props.FloatVectorProperty(
        name='Vertex Override Color',
        description='Specify override color in the case that VertexColorImportOption is set to Override',
        subtype='COLOR_GAMMA',
        size=4,
        default=(1.0,1.0,1.0,1.0),
        min=0.0,
        max=1.0
    )

    remove_degenerates: bpy.props.BoolProperty(
        name='Remove Degenerates',
        description='Disabling this option will keep degenerate triangles found. In general you should leave this option on',
        default=True
    )

    build_adjacency_buffer: bpy.props.BoolProperty(
        name='Build Adjacency Buffer',
        description='Required for PNT tessellation but can be slow. Recommend disabling for larger meshes',
        default=True
    )

    build_reversed_index_buffer: bpy.props.BoolProperty(
        name='Build Reversed Index Buffer',
        description='Build Reversed Index Buffer',
        default=True
    )

    generate_lightmap_u_vs: bpy.props.BoolProperty(
        name='Generate Lightmaps UVs',
        description='Generate Lightmap UVs',
        default=True
    )

    one_convex_hull_per_ucx: bpy.props.BoolProperty(
        name='One Convex Hull Per UCX',
        description='If checked, one convex hull per UCX_ prefixed collision mesh will be generated instead of decomposing into multiple hulls',
        default=True
    )

    combine_meshes: bpy.props.BoolProperty(
        name='Combine Meshes',
        description='If enabled, combines all meshes into a single mesh',
        default=False
    )

    transform_vertex_to_absolute: bpy.props.BoolProperty(
        name='Transform Vertex to Absolute',
        description='If this option is true the node absolute transform (transform, offset and pivot) will be apply to the mesh vertices',
        default=True
    )

    bake_pivot_in_vertex: bpy.props.BoolProperty(
        name='Bake Pivot in Vertex',
        description='Experimental - If this option is true the inverse node rotation pivot will be apply to the mesh vertices. The pivot from the DCC will then be the origin of the mesh. Note: “TransformVertexToAbsolute” must be false',
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

    tab_lod: bpy.props.BoolProperty(
        name='LOD',
        description='LOD Tab',
        default=False
    )

    auto_compute_lod_distances: bpy.props.BoolProperty(
        name='Auto Compute LOD Screen Size',
        description='If checked, the editor will automatically compute screen size values for the static mesh’s LODs. If unchecked, the user can enter custom screen size values for each LOD',
        default=True
    )

    lod_distance0: bpy.props.FloatProperty(
        name='LOD 0 Screen Size',
        description='Set a screen size value for LOD 0',
        default=0.0
    )

    lod_distance1: bpy.props.FloatProperty(
        name='LOD 1 Screen Size',
        description='Set a screen size value for LOD 1',
        default=0.0
    )

    lod_distance2: bpy.props.FloatProperty(
        name='LOD 2 Screen Size',
        description='Set a screen size value for LOD 2',
        default=0.0
    )

    lod_distance3: bpy.props.FloatProperty(
        name='LOD 3 Screen Size',
        description='Set a screen size value for LOD 3',
        default=0.0
    )

    lod_distance4: bpy.props.FloatProperty(
        name='LOD 4 Screen Size',
        description='Set a screen size value for LOD 4',
        default=0.0
    )

    lod_distance5: bpy.props.FloatProperty(
        name='LOD 5 Screen Size',
        description='Set a screen size value for LOD 5',
        default=0.0
    )

    lod_distance6: bpy.props.FloatProperty(
        name='LOD 6 Screen Size',
        description='Set a screen size value for LOD 6',
        default=0.0
    )

    lod_distance7: bpy.props.FloatProperty(
        name='LOD 7 Screen Size',
        description='Set a screen size value for LOD 7',
        default=0.0
    )

    minimum_lod_number: bpy.props.IntProperty(
        name='Minimum LOD',
        description='Set the minimum LOD used for rendering. Setting the value to 0 will use the default value of LOD0',
        default=0
    ) 

    lod_number: bpy.props.IntProperty(
        name='Number of LODs',
        description='Set the number of LODs for the editor to import. Setting the value to 0 imports the number of LODs found in the file (up to the maximum)',
        default=0
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
                'auto_generate_collision',
                'vertex_color_import_option',
                'vertex_override_color',
                'remove_degenerates',
                'build_adjacency_buffer',
                'build_reversed_index_buffer',
                'generate_lightmap_u_vs',
                'one_convex_hull_per_ucx',
                'combine_meshes',
                'transform_vertex_to_absolute',
                'bake_pivot_in_vertex',
                'import_mesh_lo_ds',
                'normal_import_method',
                'normal_generation_method',
                'compute_weighted_normals',

                'import_translation',
                'import_rotation',
                'import_uniform_scale',

                'convert_scene',
                'force_front_x_axis',
                'convert_scene_unit',
                'override_full_name',

                'auto_compute_lod_distances',
                'lod_distance0',
                'lod_distance1',
                'lod_distance2',
                'lod_distance3',
                'lod_distance4',
                'lod_distance5',
                'lod_distance6',
                'lod_distance7',
                'minimum_lod_number',
                'lod_number',

                'material_search_location',
                'import_materials',
                'import_textures',
                'invert_normal_maps',
                'reorder_material_to_fbx_order'
            ]}

class STATIC_MESH_export(PropertyGroup):

    subfolder: bpy.props.StringProperty(
        name='Subfolder',
        description='Subfolder for static mesh export folder, leave it blank if you want to export to root project folder',
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

    custom_collision: bpy.props.BoolProperty(
        name='Custom Collision',
        description='Export mesh with custom collision (if exist)',
        default=True
    )

    socket: bpy.props.BoolProperty(
        name='Socket',
        description='Export mesh with socket (if exist)',
        default=True
    )

    lod: bpy.props.BoolProperty(
        name='Level of Detail',
        description='Export mesh with level of detail (if exist)',
        default=True
    )

    option: bpy.props.EnumProperty(
        name='Export Static Mesh Option',
        description='Export Mesh Option',
        items=[
            ('SELECT', 'Select', 'Export selected mesh on scene'),
            ('ALL', 'All', 'Export All Mesh On Scene')
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

    fbx: bpy.props.PointerProperty(
        type=STATIC_MESH_FBX_export
    )

    unreal_engine: bpy.props.PointerProperty(
        type=STATIC_MESH_unreal_engine_export
    )