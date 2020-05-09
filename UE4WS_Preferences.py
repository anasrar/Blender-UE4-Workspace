import bpy
from bpy.types import (AddonPreferences)
from bpy.props import (StringProperty, BoolProperty, BoolVectorProperty, IntProperty, IntVectorProperty, FloatProperty, FloatVectorProperty, EnumProperty, PointerProperty, CollectionProperty)

class Preferences(AddonPreferences):
    bl_idname = __package__

    remote = None

    skeleton = []

    multicastGroupEndPoint: StringProperty(
        name="Multicast Group Endpoint",
        default="239.0.0.1:6766"
    )

    multicastBindAddress: StringProperty(
        name="Multicast Bind Address",
        default="0.0.0.0"
    )

    multicastTTL: IntProperty(
        name="Multicast Time-To-Live",
        default=0
    )

    devMode: BoolProperty(
        name="Development Mode",
        description="Enable some feature that in development",
        default=False
    )

    exportOption: EnumProperty(
        name="Export Type",
        description="Select the way you want export",
        items=[
            ("FBX", "To FBX", "Export as FBX file"),
            ("UNREAL", "To Unreal Engine", "Export directly to Unreal Engine project"),
            ("BOTH", "To FBX and Unreal Engine", "Export as FBX file and directly export to Unreal Engine Project")
            ],
        default="BOTH"
    )

    ExportFBXFolder: StringProperty(
        name="Export Folder",
        description="Folder to export, must have write permissions",
        default="",
        maxlen=1024,
        subtype="DIR_PATH"
    )

    TempFolder: StringProperty(
        name="Temporary Folder",
        description="Temporary folder for export, must have write permissions",
        default="",
        maxlen=1024,
        subtype="DIR_PATH"
    )

    SM_TabListProject: BoolProperty(
        name="List Project",
        description="List Project Tab",
        default=False
    )


    # Object

    SM_OBJTabCustomCollision: BoolProperty(
        name="Custom Collision",
        description="Custom Collision Tab",
        default=False
    )

    SM_OBJTabLOD: BoolProperty(
        name="Level of Detail",
        description="Level of Detail Tab",
        default=False
    )


    # Static mesh export setting

    SM_Subfolder: StringProperty(
        name="Subfolder",
        description="Subfolder for static mesh export folder, leave it blank if you want to export to root project folder",
        default=""
    )

    SM_CustomCollision: BoolProperty(
        name="Custom Collision",
        description="Export mesh with custom collision (if exist)",
        default=True
    )

    SM_LOD: BoolProperty(
        name="Level of Detail",
        description="Export mesh with level of detail (if exist)",
        default=False
    )

    SM_OverwriteFile: BoolProperty(
        name="Overwrite File",
        description="Overwrite file if filename exist, if false will not export",
        default=True
    )

    SM_ExportMeshOption: EnumProperty(
        name="Export Mesh Option",
        description="Export Mesh Option",
        items=[
            ("SELECT", "Select", "Export selected mesh on scene"),
            ("ALL", "All", "Export All Mesh On Scene")
        ],
        default="SELECT"
    )

    SM_MeshOrigin: EnumProperty(
        name="Mesh Origin",
        description="Mesh Origin",
        items=[
            ("OBJECT", "Object", "Use object origin"),
            ("SCENE", "Scene", "Use scene origin")
        ],
        default="OBJECT"
    )

    ## FBX Option

    ## Transform

    SM_FBXTabTransform: BoolProperty(
        name="Transform",
        description="Transform Tab",
        default=False
    )

    SM_FBXGlobalScale: FloatProperty(
        name="Scale",
        description="Scale all data (Some importers do not support scaled armatures!)",
        default=1.0,
        min=0.001,
        max=1000
    )

    SM_FBXApplyScaleOptions: EnumProperty(
        name="Apply Scalings",
        description="How to apply custom and units scalings in generated FBX file (Blender uses FBX scale to detect units on import, but many other applications do not handle the same way)",
        items=[
            ("FBX_SCALE_NONE", "All Local", "Apply custom scaling and units scaling to each object transformation, FBX scale remains at 1.0"),
            ("FBX_SCALE_UNITS", "FBX Units Scale", "Apply custom scaling to each object transformation, and units scaling to FBX scale"),
            ("FBX_SCALE_CUSTOM", "FBX Custom Scale", "Apply custom scaling to FBX scale, and units scaling to each object transformation"),
            ("FBX_SCALE_ALL", "FBX All", "Apply custom scaling and units scaling to FBX scale")
        ],
        default="FBX_SCALE_NONE"
    )

    SM_FBXAxisForward: EnumProperty(
        name="Forward",
        description="Forward",
        items=[
            ("X", "X Forward", "X Forward"),
            ("Y", "Y Forward", "Y Forward"),
            ("Z", "Z Forward", "Z Forward"),
            ("-X", "-X Forward", "-X Forward"),
            ("-Y", "-Y Forward", "-Y Forward"),
            ("-Z", "-Z Forward", "-Z Forward")
        ],
        default="-Z"
    )

    SM_FBXAxisUp: EnumProperty(
        name="Up",
        description="Up",
        items=[
            ("X", "X Up", "X Up"),
            ("Y", "Y Up", "Y Up"),
            ("Z", "Z Up", "Z Up"),
            ("-X", "-X Up", "-X Up"),
            ("-Y", "-Y Up", "-Y Up"),
            ("-Z", "-Z Up", "-Z Up")
        ],
        default="Y"
    )

    SM_FBXApplyUnitScale: BoolProperty(
        name="Apply Unit",
        description="Take into account current Blender units settings (if unset, raw Blender Units values are used as-is)",
        default=True
    )

    SM_FBXBakeSpaceTransform: BoolProperty(
        name="!EXPERIMENTAL! Apply Transform",
        description="Bake space transform into object data, avoids getting unwanted rotations to objects when target space is not aligned with Blender’s space (WARNING! experimental option, use at own risks, known broken with armatures/animations)",
        default=False
    )

    ## Geometry

    SM_FBXTabGeometry: BoolProperty(
        name="Geometry",
        description="Geometry Tab",
        default=False
    )

    SM_FBXMeshSmoothType: EnumProperty(
        name="Smoothing",
        description="Export smoothing information (prefer ‘Normals Only’ option if your target importer understand split normals)",
        items=[
            ("OFF", "Normals Only", "Export only normals instead of writing edge or face smoothing data"),
            ("FACE", "Face", "Write face smoothing"),
            ("EDGE", "Edge", "Write edge smoothing")
        ],
        default="OFF"
    ) 

    SM_FBXUseSubsurf: BoolProperty(
        name="Export Subdivision Surface",
        description="Export the last Catmull-Rom subidivion modifier as FBX subdivision (Does not apply the modifier even if ‘Apply Modifiers’ is enabled)",
        default=False
    )

    SM_FBXUseMeshModifiers: BoolProperty(
        name="Apply Modifiers",
        description="Apply modifiers to mesh objects (except Armature ones) - WARNING: prevents exporting shape keys",
        default=True
    )

    SM_FBXUseMeshEdges: BoolProperty(
        name="Loose Edges",
        description="Export loose edges (as two-vertices polygons)",
        default=False
    )

    SM_FBXUseTSpace: BoolProperty(
        name="Tangent Space",
        description="Add binormal and tangent vectors, together with normal they form the tangent space (will only work correctly with tris/quads only meshes!)",
        default=False
    )

    ## Unreal Engine Option

    ## Mesh

    SM_TabMesh: BoolProperty(
        name="Mesh",
        description="Mesh Tab",
        default=False
    )

    SM_AutoGenerateCollision: BoolProperty(
        name="Auto Generate Collision",
        description="If checked, collision will automatically be generated (ignored if custom collision is imported or used)",
        default=True
    )

    """
    Static Mesh LODGroup: Enums ; None
    """

    SM_VertexColorImportOption: EnumProperty(
        name="Vertex Color Import Option",
        description="Specify how vertex colors should be imported",
        items=[
            ("IGNORE", "Ignore", "Ignore vertex colors from the FBX file, and keep the existing mesh vertex colors"),
            ("OVERRIDE", "Override", "Override all vertex colors with the specified color"),
            ("REPLACE", "Replace", "Import the static mesh using the vertex colors from the FBX file")
        ],
        default="IGNORE"
    )

    SM_RemoveDegenerates: BoolProperty(
        name="Remove Degenerates",
        description="Disabling this option will keep degenerate triangles found. In general you should leave this option on",
        default=True
    )

    SM_BuildAdjacencyBuffer: BoolProperty(
        name="Build Adjacency Buffer",
        description="Required for PNT tessellation but can be slow. Recommend disabling for larger meshes",
        default=True
    )

    SM_BuildReversedIndexBuffer: BoolProperty(
        name="Build Reversed Index Buffer",
        description="Build Reversed Index Buffer",
        default=True
    )

    SM_GenerateLightmapsUVs: BoolProperty(
        name="Generate Lightmaps UVs",
        description="Generate Lightmap UVs",
        default=True
    )

    SM_OneConvexHullPerUCX: BoolProperty(
        name="One Convex Hull Per UCX",
        description="If checked, one convex hull per UCX_ prefixed collision mesh will be generated instead of decomposing into multiple hulls",
        default=True
    )

    SM_CombineMeshes: BoolProperty(
        name="Combine Meshes",
        description="If enabled, combines all meshes into a single mesh",
        default=False
    )

    SM_TransformVertexToAbsolute: BoolProperty(
        name="Transform Vertex to Absolute",
        description="If this option is true the node absolute transform (transform, offset and pivot) will be apply to the mesh vertices",
        default=True
    )

    SM_BakePivotInVertex: BoolProperty(
        name="Bake Pivot in Vertex",
        description="Experimental - If this option is true the inverse node rotation pivot will be apply to the mesh vertices. The pivot from the DCC will then be the origin of the mesh. Note: “TransformVertexToAbsolute” must be false",
        default=False
    )

    SM_ImportMeshLODs: BoolProperty(
        name="Import Mesh LODs",
        description="If enabled, creates LOD models for Unreal meshes from LODs in the import file; If not enabled, only the base mesh from the LOD group is imported",
        default=False
    )

    SM_NormalImportMethod: EnumProperty(
        name="Normal Import Method",
        description="Enabling this option will read the tangents(tangent,binormal,normal) from FBX file instead of generating them automatically",
        items=[
            ("COMPUTE_NORMALS", "Compute Normals", ""),
            ("IMPORT_NORMALS", "Import Normals", ""),
            ("IMPORT_NORMALS_AND_TANGENTS", "Import Normals and Tangents", "")
        ],
        default="IMPORT_NORMALS"
    )

    SM_NormalGenerationMethod: EnumProperty(
        name="Normal Generation Method",
        description="Use the MikkTSpace tangent space generator for generating normals and tangents on the mesh",
        items=[
            ("BUILT_IN", "Built In", "Use the legacy built in method to generate normals (faster in some cases)"),
            ("MIKK_T_SPACE", "Mikk T Space", "Use MikkTSpace to generate normals and tangents")
            ],
        default="MIKK_T_SPACE"
    )

    SM_ComputeWeightedNormals: BoolProperty(
        name="Compute Weighted Normals",
        description="Enabling this option will use weighted normals algorithm (area and angle) when computing normals or tangents",
        default=True
    )

    ## Transform

    SM_TabTransform: BoolProperty(
        name="Transform",
        description="Transform Tab",
        default=False
    )

    SM_ImportTranslation: FloatVectorProperty(
        name="Import Translation",
        description="Import Translation",
        subtype="XYZ",
        default=(0.0, 0.0, 0.0)
    )

    SM_ImportRotation: FloatVectorProperty(
        name="Import Rotation",
        description="Import Rotation",
        subtype="XYZ",
        default=(0.0, 0.0, 0.0)
    )

    SM_ImportUniformScale: FloatProperty(
        name="Import Uniform Scale",
        description="Import Uniform Scale",
        default=1.0
    )

    ## Misc.

    SM_TabMisc: BoolProperty(
        name="Misc.",
        description="Miscellaneous Tab",
        default=False
    )


    SM_ConvertScene: BoolProperty(
        name="Convert Scene",
        description="Convert the scene from FBX coordinate system to UE4 coordinate system",
        default=True
    )

    SM_ForceFrontXAxis: BoolProperty(
        name="Force Front XAxis",
        description="Convert the scene from FBX coordinate system to UE4 coordinate system with front X axis instead of -Y",
        default=False
    )

    SM_ConvertSceneUnit: BoolProperty(
        name="Convert Scene Unit",
        description="Convert the scene from FBX unit to UE4 unit (centimeter)",
        default=False
    )

    SM_OverrideFullName: BoolProperty(
        name="Override Full Name",
        description="Use the string in “Name” field as full name of mesh. The option only works when the scene contains one mesh",
        default=True
    )

    ## LODSetting

    SM_TabLODSetting: BoolProperty(
        name="LODSetting",
        description="LODSetting Tab",
        default=False
    )

    SM_AutoComputeLODScreenSize: BoolProperty(
        name="Auto Compute LOD Screen Size",
        description="If checked, the editor will automatically compute screen size values for the static mesh’s LODs. If unchecked, the user can enter custom screen size values for each LOD",
        default=True
    )

    SM_LODDistance0: FloatProperty(
        name="LOD 0 Screen Size",
        description="Set a screen size value for LOD 0",
        default=0.0
    )

    SM_LODDistance1: FloatProperty(
        name="LOD 1 Screen Size",
        description="Set a screen size value for LOD 1",
        default=0.0
    )

    SM_LODDistance2: FloatProperty(
        name="LOD 2 Screen Size",
        description="Set a screen size value for LOD 2",
        default=0.0
    )

    SM_LODDistance3: FloatProperty(
        name="LOD 3 Screen Size",
        description="Set a screen size value for LOD 3",
        default=0.0
    )

    SM_LODDistance4: FloatProperty(
        name="LOD 4 Screen Size",
        description="Set a screen size value for LOD 4",
        default=0.0
    )

    SM_LODDistance5: FloatProperty(
        name="LOD 5 Screen Size",
        description="Set a screen size value for LOD 5",
        default=0.0
    )

    SM_LODDistance6: FloatProperty(
        name="LOD 6 Screen Size",
        description="Set a screen size value for LOD 6",
        default=0.0
    )

    SM_LODDistance7: FloatProperty(
        name="LOD 7 Screen Size",
        description="Set a screen size value for LOD 7",
        default=0.0
    )

    SM_MinimumLODNumber: IntProperty(
        name="Minimum LOD",
        description="Set the minimum LOD used for rendering. Setting the value to 0 will use the default value of LOD0",
        default=0
    ) 

    SM_NumberOfLODs: IntProperty(
        name="Number of LODs",
        description="Set the number of LODs for the editor to import. Setting the value to 0 imports the number of LODs found in the file (up to the maximum)",
        default=0
    ) 

    ## Material

    SM_TabMaterial: BoolProperty(
        name="Material",
        description="Material Tab",
        default=False
    )

    SM_MaterialSearchLocation: EnumProperty(
        name="Search Location",
        description="Specify where we should search for matching materials when importing",
        items=[
            ("LOCAL", "Local", "Search for matching material in local import folder only"),
            ("UNDER_PARENT", "Under Parent", "Search for matching material recursively from parent folder"),
            ("UNDER_ROOT", "Under Root", "Search for matching material recursively from root folder"),
            ("ALL_ASSETS", "All Assets", "Search for matching material in all assets folders")
            ],
        default="LOCAL"
    )

    SM_ImportMaterial: BoolProperty(
        name="Import Material",
        description="Whether to automatically create Unreal materials for materials found in the FBX scene",
        default=False
    )

    SM_ImportTexture: BoolProperty(
        name="Import Texture",
        description="The option works only when option “Import Material” is OFF. If “Import Material” is ON, textures are always imported",
        default=True
    )

    SM_InvertNormalMaps: BoolProperty(
        name="Invert Normal Maps",
        description="If importing textures is enabled, this option will cause normal map Y (Green) values to be inverted",
        default=False
    )

    SM_ReorderMaterialToFBXOrder: BoolProperty(
        name="Reorder Material To FBX Order",
        description="If checked, The material list will be reorder to the same order has the FBX file",
        default=True
    )

    # Character 

    CHAR_Subfolder: StringProperty(
        name="Subfolder",
        description="Subfolder for skeleton mesh export folder, leave it blank if you want to export to root project folder",
        default=""
    )

    CHAR_OverwriteFile: BoolProperty(
        name="Overwrite File",
        description="Overwrite file if filename exist, if false will not export",
        default=True
    )

    CHAR_ExportCharacterOption: EnumProperty(
        name="Export Character Option",
        description="Export Character Option",
        items=[
            ("SELECT", "Select", "Export selected character on scene"),
            ("ALL", "All", "Export All Character On Scene")
        ],
        default="SELECT"
    )

    CHAR_CharacterOption: EnumProperty(
        name="Character Option",
        description="Character Option",
        items=[
            ("COMBINE", "Combine", "Combine character mesh into one fbx file"),
            ("PART", "Part", "Separate character mesh into multiple fbx file")
        ],
        default="COMBINE"
    )

    def update_skeleton(self, context):
        return [("NEW", "New", "Create new skeleton")] + self.skeleton

    CHAR_CharacterSkeleton: EnumProperty(
        name="Character Skeleton",
        description="Character Skeleton",
        items=update_skeleton,
        default=None
    )

    ## FBX Option

    ## Transform

    CHAR_FBXTabTransform: BoolProperty(
        name="Transform",
        description="Transform Tab",
        default=False
    )

    CHAR_FBXGlobalScale: FloatProperty(
        name="Scale",
        description="Scale all data (Some importers do not support scaled armatures!)",
        default=1.0,
        min=0.001,
        max=1000
    )

    CHAR_FBXApplyScaleOptions: EnumProperty(
        name="Apply Scalings",
        description="How to apply custom and units scalings in generated FBX file (Blender uses FBX scale to detect units on import, but many other applications do not handle the same way)",
        items=[
            ("FBX_SCALE_NONE", "All Local", "Apply custom scaling and units scaling to each object transformation, FBX scale remains at 1.0"),
            ("FBX_SCALE_UNITS", "FBX Units Scale", "Apply custom scaling to each object transformation, and units scaling to FBX scale"),
            ("FBX_SCALE_CUSTOM", "FBX Custom Scale", "Apply custom scaling to FBX scale, and units scaling to each object transformation"),
            ("FBX_SCALE_ALL", "FBX All", "Apply custom scaling and units scaling to FBX scale")
        ],
        default="FBX_SCALE_NONE"
    )

    CHAR_FBXAxisForward: EnumProperty(
        name="Forward",
        description="Forward",
        items=[
            ("X", "X Forward", "X Forward"),
            ("Y", "Y Forward", "Y Forward"),
            ("Z", "Z Forward", "Z Forward"),
            ("-X", "-X Forward", "-X Forward"),
            ("-Y", "-Y Forward", "-Y Forward"),
            ("-Z", "-Z Forward", "-Z Forward")
        ],
        default="-Z"
    )

    CHAR_FBXAxisUp: EnumProperty(
        name="Up",
        description="Up",
        items=[
            ("X", "X Up", "X Up"),
            ("Y", "Y Up", "Y Up"),
            ("Z", "Z Up", "Z Up"),
            ("-X", "-X Up", "-X Up"),
            ("-Y", "-Y Up", "-Y Up"),
            ("-Z", "-Z Up", "-Z Up")
        ],
        default="Y"
    )

    CHAR_FBXApplyUnitScale: BoolProperty(
        name="Apply Unit",
        description="Take into account current Blender units settings (if unset, raw Blender Units values are used as-is)",
        default=True
    )

    CHAR_FBXBakeSpaceTransform: BoolProperty(
        name="!EXPERIMENTAL! Apply Transform",
        description="Bake space transform into object data, avoids getting unwanted rotations to objects when target space is not aligned with Blender’s space (WARNING! experimental option, use at own risks, known broken with armatures/animations)",
        default=False
    )

    ## Geometry

    CHAR_FBXTabGeometry: BoolProperty(
        name="Geometry",
        description="Geometry Tab",
        default=False
    )

    CHAR_FBXMeshSmoothType: EnumProperty(
        name="Smoothing",
        description="Export smoothing information (prefer ‘Normals Only’ option if your target importer understand split normals)",
        items=[
            ("OFF", "Normals Only", "Export only normals instead of writing edge or face smoothing data"),
            ("FACE", "Face", "Write face smoothing"),
            ("EDGE", "Edge", "Write edge smoothing")
        ],
        default="OFF"
    ) 

    CHAR_FBXUseSubsurf: BoolProperty(
        name="Export Subdivision Surface",
        description="Export the last Catmull-Rom subidivion modifier as FBX subdivision (Does not apply the modifier even if ‘Apply Modifiers’ is enabled)",
        default=False
    )

    CHAR_FBXUseMeshModifiers: BoolProperty(
        name="Apply Modifiers",
        description="Apply modifiers to mesh objects (except Armature ones) - WARNING: prevents exporting shape keys",
        default=True
    )

    CHAR_FBXUseMeshEdges: BoolProperty(
        name="Loose Edges",
        description="Export loose edges (as two-vertices polygons)",
        default=False
    )

    CHAR_FBXUseTSpace: BoolProperty(
        name="Tangent Space",
        description="Add binormal and tangent vectors, together with normal they form the tangent space (will only work correctly with tris/quads only meshes!)",
        default=False
    )

    ## Armature

    CHAR_FBXTabArmature: BoolProperty(
        name="Armature",
        description="Armature Tab",
        default=False
    )

    CHAR_FBXPrimaryBoneAxis: EnumProperty(
        name="Primary Bone Axis",
        description="Primary Bone Axis",
        items=[
            ("X", "X Axis", "X Axis"),
            ("Y", "Y Axis", "Y Axis"),
            ("Z", "Z Axis", "Z Axis"),
            ("-X", "-X Axis", "-X Axis"),
            ("-Y", "-Y Axis", "-Y Axis"),
            ("-Z", "-Z Axis", "-Z Axis")
        ],
        default="Y"
    )

    CHAR_FBXSecondaryBoneAxis: EnumProperty(
        name="Secondary Bone Axis",
        description="Secondary Bone Axis",
        items=[
            ("X", "X Axis", "X Axis"),
            ("Y", "Y Axis", "Y Axis"),
            ("Z", "Z Axis", "Z Axis"),
            ("-X", "-X Axis", "-X Axis"),
            ("-Y", "-Y Axis", "-Y Axis"),
            ("-Z", "-Z Axis", "-Z Axis")
        ],
        default="X"
    )

    CHAR_FBXArmatureFBXNodeType: EnumProperty(
        name="Armature FBXNode Type",
        description="FBX type of node (object) used to represent Blender’s armatures (use Null one unless you experience issues with other app, other choices may no import back perfectly in Blender…)",
        items=[
            ("NULL", "Null", "‘Null’ FBX node, similar to Blender’s Empty (default)"),
            ("ROOT", "Root", "‘Root’ FBX node, supposed to be the root of chains of bones"),
            ("LIMBNODE", "LimbNode", "‘LimbNode’ FBX node, regular joint between two bones")
        ],
        default="NULL"
    )

    CHAR_FBXOnlyDeformBones: BoolProperty(
        name="Only Deform Bones",
        description="Only write deforming bones (and non-deforming ones when they have deforming children)",
        default=False
    )

    CHAR_FBXAddLeafBones: BoolProperty(
        name="Add Leaf Bones",
        description="Only write deforming bones (and non-deforming ones when they have deforming children)",
        default=True
    )

    ## Unreal Engine Option

    ## Mesh

    CHAR_TabMesh: BoolProperty(
        name="Mesh",
        description="Mesh Tab",
        default=False
    )

    CHAR_ImportContentType: EnumProperty(
        name="Import Content Type",
        description="Filter the content we want to import from the incoming FBX skeletal mesh",
        items=[
            ("FBXICT_ALL", "Geometry and Skinning Weights", "Import all fbx content* – geometry, skinning and weights"),
            ("FBXICT_GEOMETRY", "Geometry", "Import the skeletal mesh geometry only (will create a default skeleton, or map the geometry to the existing one). Morph and LOD can be imported with it"),
            ("FBXICT_SKINNING_WEIGHTS", "Skinning Weights", "Import the skeletal mesh skinning and weights only (no geometry will be imported). Morph and LOD will not be imported with this settings")
        ],
        default="FBXICT_ALL"
    )

    CHAR_VertexColorImportOption: EnumProperty(
        name="Vertex Color Import Option",
        description="Specify how vertex colors should be imported",
        items=[
            ("REPLACE", "Replace", "Import the static mesh using the vertex colors from the FBX file"),
            ("IGNORE", "Ignore", "Ignore vertex colors from the FBX file, and keep the existing mesh vertex colors"),
            ("OVERRIDE", "Override", "Override all vertex colors with the specified color")
        ],
        default="REPLACE"
    )

    CHAR_VertexOverrideColor: FloatVectorProperty(
        name="Vertex Override Color",
        description="Specify override color in the case that VertexColorImportOption is set to Override",
        subtype="COLOR_GAMMA",
        size=4,
        default=(0.0,0.0,0.0,0.0),
        min=0.0,
        max=1.0
    )

    CHAR_UpdateSkeletonReferencePose: BoolProperty(
        name="Update Skeleton Reference Pose",
        description="If enabled, update the Skeleton (of the mesh being imported)’s reference pose",
        default=False
    ) 

    CHAR_UseT0AsRefPose: BoolProperty(
        name="Use T0 As Ref Pose",
        description="Enable this option to use frame 0 as reference pose",
        default=False
    )

    CHAR_PreserveSmoothingGroups: BoolProperty(
        name="Preserve Smoothing Groups",
        description="If checked, triangles with non-matching smoothing groups will be physically split",
        default=True
    )

    CHAR_ImportMeshesInBoneHierarchy: BoolProperty(
        name="Import Meshes In Bone Hierarchy",
        description="If checked, meshes nested in bone hierarchies will be imported instead of being converted to bones",
        default=True
    )

    CHAR_ImportMorphTargets: BoolProperty(
        name="Import Morph Targets",
        description="If enabled, creates Unreal morph objects for the imported meshes",
        default=False
    )

    CHAR_ImportMeshLODs: BoolProperty(
        name="Import Mesh LODs",
        description="If enabled, creates LOD models for Unreal meshes from LODs in the import file; If not enabled, only the base mesh from the LOD group is imported",
        default=False
    )

    CHAR_NormalImportMethod: EnumProperty(
        name="Normal Import Method",
        description="Enabling this option will read the tangents(tangent,binormal,normal) from FBX file instead of generating them automatically",
        items=[
            ("COMPUTE_NORMALS", "Compute Normals", ""),
            ("IMPORT_NORMALS", "Import Normals", ""),
            ("IMPORT_NORMALS_AND_TANGENTS", "Import Normals and Tangents", "")
        ],
        default="IMPORT_NORMALS"
    )

    CHAR_NormalGenerationMethod: EnumProperty(
        name="Normal Generation Method",
        description="Use the MikkTSpace tangent space generator for generating normals and tangents on the mesh",
        items=[
            ("BUILT_IN", "Built In", "Use the legacy built in method to generate normals (faster in some cases)"),
            ("MIKK_T_SPACE", "Mikk T Space", "Use MikkTSpace to generate normals and tangents")
            ],
        default="MIKK_T_SPACE"
    )

    CHAR_ComputeWeightedNormals: BoolProperty(
        name="Compute Weighted Normals",
        description="Enabling this option will use weighted normals algorithm (area and angle) when computing normals or tangents",
        default=True
    )

    CHAR_ThresholdPosition: FloatProperty(
        name="Threshold Position",
        description="Threshold to compare vertex position equality",
        default=0.00002
    )

    CHAR_ThresholdTangentNormal: FloatProperty(
        name="Threshold Tangent Normal",
        description="Threshold to compare normal, tangent or bi-normal equality",
        default=0.00002
    )

    CHAR_ThresholdUV: FloatProperty(
        name="Threshold UV",
        description="Threshold to compare UV equality",
        default=0.000977
    )

    CHAR_PhysicsAsset: EnumProperty(
        name="Physics Asset",
        description="Physics Asset",
        items=[
            ("CREATE", "Create", "create new PhysicsAsset")
        ],
        default="CREATE"
    )

    ## Transform

    CHAR_TabTransform: BoolProperty(
        name="Transform",
        description="Transform Tab",
        default=False
    )

    CHAR_ImportTranslation: FloatVectorProperty(
        name="Import Translation",
        description="Import Translation",
        subtype="XYZ",
        default=(0.0, 0.0, 0.0)
    )

    CHAR_ImportRotation: FloatVectorProperty(
        name="Import Rotation",
        description="Import Rotation",
        subtype="XYZ",
        default=(0.0, 0.0, 0.0)
    )

    CHAR_ImportUniformScale: FloatProperty(
        name="Import Uniform Scale",
        description="Import Uniform Scale",
        default=1.0
    )

    ## Misc.

    CHAR_TabMisc: BoolProperty(
        name="Misc.",
        description="Miscellaneous Tab",
        default=False
    )

    CHAR_ConvertScene: BoolProperty(
        name="Convert Scene",
        description="Convert the scene from FBX coordinate system to UE4 coordinate system",
        default=True
    )

    CHAR_ForceFrontXAxis: BoolProperty(
        name="Force Front XAxis",
        description="Convert the scene from FBX coordinate system to UE4 coordinate system with front X axis instead of -Y",
        default=False
    )

    CHAR_ConvertSceneUnit: BoolProperty(
        name="Convert Scene Unit",
        description="Convert the scene from FBX unit to UE4 unit (centimeter)",
        default=False
    )

    CHAR_OverrideFullName: BoolProperty(
        name="Override Full Name",
        description="Use the string in “Name” field as full name of mesh. The option only works when the scene contains one mesh",
        default=True
    )

    ## Material

    CHAR_TabMaterial: BoolProperty(
        name="Material",
        description="Material Tab",
        default=False
    )

    CHAR_MaterialSearchLocation: EnumProperty(
        name="Search Location",
        description="Specify where we should search for matching materials when importing",
        items=[
            ("LOCAL", "Local", "Search for matching material in local import folder only"),
            ("UNDER_PARENT", "Under Parent", "Search for matching material recursively from parent folder"),
            ("UNDER_ROOT", "Under Root", "Search for matching material recursively from root folder"),
            ("ALL_ASSETS", "All Assets", "Search for matching material in all assets folders")
            ],
        default="LOCAL"
    )

    CHAR_ImportMaterial: BoolProperty(
        name="Import Material",
        description="Whether to automatically create Unreal materials for materials found in the FBX scene",
        default=False
    )

    CHAR_ImportTexture: BoolProperty(
        name="Import Texture",
        description="The option works only when option “Import Material” is OFF. If “Import Material” is ON, textures are always imported",
        default=True
    )

    CHAR_InvertNormalMaps: BoolProperty(
        name="Invert Normal Maps",
        description="If importing textures is enabled, this option will cause normal map Y (Green) values to be inverted",
        default=False
    )

    CHAR_ReorderMaterialToFBXOrder: BoolProperty(
        name="Reorder Material To FBX Order",
        description="If checked, The material list will be reorder to the same order has the FBX file",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        row = box.row()
        row.prop(self, "devMode")
        row = box.row()
        row.prop(self, "multicastGroupEndPoint")
        row.prop(self, "multicastBindAddress")
        row.prop(self, "multicastTTL")
