import os
import inspect
import json

from unreal import (
    EditorAssetLibrary,
    FbxImportUI,
    AssetImportTask,
    AssetToolsHelpers,
    load_asset,

    Vector,
    Rotator,
    Color,
    FBXImportContentType,
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
        importOptions.set_editor_property("import_as_skeletal", True)
        importOptions.set_editor_property('import_animations', False)

        importOptions.set_editor_property("skeleton", (load_asset(file["skeleton"]), None)[file["skeleton"] == "NEW"])

        importOptions.skeletal_mesh_import_data.set_editor_property("import_content_type", getattr(FBXImportContentType, jsonSetting["import_content_type"]))
        importOptions.skeletal_mesh_import_data.set_editor_property("vertex_color_import_option", getattr(VertexColorImportOption, jsonSetting["vertex_color_import_option"]))

        jsonSetting["vertex_override_color"] = [value * 255 for value in jsonSetting["vertex_override_color"]]
        importOptions.skeletal_mesh_import_data.set_editor_property("vertex_override_color", Color(r=jsonSetting["vertex_override_color"][0], g=jsonSetting["vertex_override_color"][1], b=jsonSetting["vertex_override_color"][2], a=jsonSetting["vertex_override_color"][3]))
        importOptions.skeletal_mesh_import_data.set_editor_property("update_skeleton_reference_pose", jsonSetting["update_skeleton_reference_pose"])
        importOptions.skeletal_mesh_import_data.set_editor_property("use_t0_as_ref_pose", jsonSetting["use_t0_as_ref_pose"])
        importOptions.skeletal_mesh_import_data.set_editor_property("preserve_smoothing_groups", jsonSetting["preserve_smoothing_groups"])
        importOptions.skeletal_mesh_import_data.set_editor_property("import_meshes_in_bone_hierarchy", jsonSetting["import_meshes_in_bone_hierarchy"])
        importOptions.skeletal_mesh_import_data.set_editor_property("import_morph_targets", jsonSetting["import_morph_targets"])
        importOptions.skeletal_mesh_import_data.set_editor_property("import_mesh_lo_ds", jsonSetting["import_mesh_lo_ds"])
        importOptions.skeletal_mesh_import_data.set_editor_property("normal_import_method", getattr(FBXNormalImportMethod, "FBXNIM_" + jsonSetting["normal_import_method"]))
        importOptions.skeletal_mesh_import_data.set_editor_property("normal_generation_method", getattr(FBXNormalGenerationMethod, jsonSetting["normal_generation_method"]))
        importOptions.skeletal_mesh_import_data.set_editor_property("compute_weighted_normals", jsonSetting["compute_weighted_normals"])
        importOptions.skeletal_mesh_import_data.set_editor_property("threshold_position", jsonSetting["threshold_position"])
        importOptions.skeletal_mesh_import_data.set_editor_property("threshold_tangent_normal", jsonSetting["threshold_tangent_normal"])
        importOptions.skeletal_mesh_import_data.set_editor_property("threshold_uv", jsonSetting["threshold_uv"])
        importOptions.set_editor_property("create_physics_asset", jsonSetting["physics_asset"] == "CREATE")
        if jsonSetting["physics_asset"] != "CREATE":
            importOptions.set_editor_property("physics_asset", jsonSetting["physics_asset"])

        # Transform

        importOptions.skeletal_mesh_import_data.set_editor_property("import_translation", Vector(*jsonSetting["import_translation"]))
        importOptions.skeletal_mesh_import_data.set_editor_property("import_rotation", Rotator(*jsonSetting["import_rotation"]))
        importOptions.skeletal_mesh_import_data.set_editor_property("import_uniform_scale", jsonSetting["import_uniform_scale"])

        # Misc.

        importOptions.skeletal_mesh_import_data.set_editor_property("convert_scene", jsonSetting["convert_scene"])
        importOptions.skeletal_mesh_import_data.set_editor_property("force_front_x_axis", jsonSetting["force_front_x_axis"])
        importOptions.skeletal_mesh_import_data.set_editor_property("convert_scene_unit", jsonSetting["convert_scene_unit"])
        importOptions.set_editor_property("override_full_name", jsonSetting["override_full_name"])

        # Material

        importOptions.texture_import_data.set_editor_property("material_search_location", getattr(MaterialSearchLocation, jsonSetting["material_search_location"]))
        importOptions.set_editor_property("import_materials", jsonSetting["import_material"])
        importOptions.set_editor_property("import_textures", jsonSetting["import_texture"])
        importOptions.texture_import_data.set_editor_property("invert_normal_maps", jsonSetting["invert_normal_maps"])
        importOptions.skeletal_mesh_import_data.set_editor_property("reorder_material_to_fbx_order", jsonSetting["reorder_material_to_fbx_order"])

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