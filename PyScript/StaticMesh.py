import os
import inspect
import json

from unreal import (
    EditorAssetLibrary,
    FbxImportUI,
    AssetImportTask,
    AssetToolsHelpers,

    Vector,
    Rotator,
    Color,
    VertexColorImportOption,
    FBXNormalImportMethod,
    FBXNormalGenerationMethod,
    MaterialSearchLocation
)

# Fix Python PATH Script Issue #9
filename = inspect.getframeinfo(inspect.currentframe()).filename
currentPath = os.path.dirname(os.path.abspath(filename))

jsonSetting = open(os.path.normpath(os.path.join(currentPath, "..", "Data", "unrealenginesetting.json")), "r").read()
jsonSetting = json.loads(jsonSetting)

targetFolder = "/" + os.path.join("Game", "Blender", jsonSetting["subfolder"]).replace(os.sep, "/")

if EditorAssetLibrary.does_directory_exist(directory_path=targetFolder):
    EditorAssetLibrary.make_directory(directory_path=targetFolder)

for file in jsonSetting["files"]:
    sourceFile = os.path.join(jsonSetting["folder"], file["name"] + ".fbx").replace(os.sep, "/")

    if os.path.exists(sourceFile):
        importOptions = FbxImportUI()

        importOptions.set_editor_property("import_mesh", True)
        importOptions.set_editor_property("import_as_skeletal", False)
        importOptions.set_editor_property('import_animations', False)

        importOptions.static_mesh_import_data.set_editor_property("auto_generate_collision", (jsonSetting["auto_generate_collision"], False)[file["custom_collision"]])
        importOptions.static_mesh_import_data.set_editor_property("vertex_color_import_option", getattr(VertexColorImportOption, jsonSetting["vertex_color_import_option"]))
        importOptions.static_mesh_import_data.set_editor_property("vertex_override_color", Color(r=(float(jsonSetting["vertex_override_color"][0]) * 255), g=float(jsonSetting["vertex_override_color"][1]) * 255, b=float(jsonSetting["vertex_override_color"][2]) * 255, a=float(jsonSetting["vertex_override_color"][3]) * 255))
        importOptions.static_mesh_import_data.set_editor_property("remove_degenerates", jsonSetting["remove_degenerates"])
        importOptions.static_mesh_import_data.set_editor_property("build_adjacency_buffer", jsonSetting["build_adjacency_buffer"])
        importOptions.static_mesh_import_data.set_editor_property("build_reversed_index_buffer", jsonSetting["build_reversed_index_buffer"])
        importOptions.static_mesh_import_data.set_editor_property("generate_lightmap_u_vs", (jsonSetting["generate_lightmaps_uvs"], False)[file["custom_uv"]])
        importOptions.static_mesh_import_data.set_editor_property("one_convex_hull_per_ucx", jsonSetting["one_convex_hull_perucx"])
        importOptions.static_mesh_import_data.set_editor_property("combine_meshes", jsonSetting["combine_meshes"])
        importOptions.static_mesh_import_data.set_editor_property("transform_vertex_to_absolute", jsonSetting["transform_vertex_to_absolute"])
        importOptions.static_mesh_import_data.set_editor_property("bake_pivot_in_vertex", jsonSetting["bake_pivot_in_vertex"])
        importOptions.static_mesh_import_data.set_editor_property("import_mesh_lo_ds", (jsonSetting["import_mesh_lods"], True)[bool(file["lod"])])
        importOptions.static_mesh_import_data.set_editor_property("normal_import_method", getattr(FBXNormalImportMethod, "FBXNIM_" + jsonSetting["normal_import_method"]))
        importOptions.static_mesh_import_data.set_editor_property("normal_generation_method", getattr(FBXNormalGenerationMethod, jsonSetting["normal_generation_method"]))
        importOptions.static_mesh_import_data.set_editor_property("compute_weighted_normals", jsonSetting["compute_weighted_normals"])

        # Transform

        importOptions.static_mesh_import_data.set_editor_property("import_translation", Vector(*jsonSetting["import_translation"]))
        importOptions.static_mesh_import_data.set_editor_property("import_rotation", Rotator(*jsonSetting["import_rotation"]))
        importOptions.static_mesh_import_data.set_editor_property("import_uniform_scale", jsonSetting["import_uniform_scale"])

        # Misc.

        importOptions.static_mesh_import_data.set_editor_property("convert_scene", jsonSetting["convert_scene"])
        importOptions.static_mesh_import_data.set_editor_property("force_front_x_axis", jsonSetting["force_front_x_axis"])
        importOptions.static_mesh_import_data.set_editor_property("convert_scene_unit", jsonSetting["convert_scene_unit"])
        importOptions.set_editor_property("override_full_name", jsonSetting["override_full_name"])

        # LODSetting

        importOptions.set_editor_property("auto_compute_lod_distances", (jsonSetting["auto_compute_lod_distances"], file["auto_compute_lod_distances"])[bool(file["lod"])])

        if bool(file["lod"]):
            screenSizes = file["lod"] + jsonSetting["lod_distance"][len(file["lod"]):]
            for index, screenSize in enumerate(screenSizes):
                importOptions.set_editor_property("lod_distance{0}".format(index), screenSize)
        else:
            for index, numLOD in enumerate(jsonSetting["lod_distance"]):
                importOptions.set_editor_property("lod_distance{0}".format(index), numLOD)

        importOptions.set_editor_property("minimum_lod_number", jsonSetting["minimum_lod_number"])
        importOptions.set_editor_property("lod_number", jsonSetting["lod_number"])

        # Material

        importOptions.texture_import_data.set_editor_property("material_search_location", getattr(MaterialSearchLocation, jsonSetting["material_search_location"]))
        importOptions.set_editor_property("import_materials", jsonSetting["import_material"])
        importOptions.set_editor_property("import_textures", jsonSetting["import_texture"])
        importOptions.texture_import_data.set_editor_property("invert_normal_maps", jsonSetting["invert_normal_maps"])
        importOptions.static_mesh_import_data.set_editor_property("reorder_material_to_fbx_order", jsonSetting["reorder_material_to_fbx_order"])

        # Task

        importTask = AssetImportTask()
        importTask.set_editor_property("automated", True)
        importTask.set_editor_property("destination_name", "")
        importTask.set_editor_property("destination_path", targetFolder)
        importTask.set_editor_property("filename", sourceFile)
        importTask.set_editor_property("replace_existing", jsonSetting["overwrite_file"])
        importTask.set_editor_property("save", False)
        importTask.set_editor_property("options", importOptions)

        AssetToolsHelpers.get_asset_tools().import_asset_tasks([importTask])

        if jsonSetting["temporary"]:
            # when you try to export temporary and with create material setting, unreal engine can not handle remove file because still using for compiling material
            # https://github.com/anasrar/Blender-UE4-Workspace/issues/6
            try:
                os.remove(sourceFile)
            except:
                print("Failed to Remove Temporary File, Location : " + sourceFile)