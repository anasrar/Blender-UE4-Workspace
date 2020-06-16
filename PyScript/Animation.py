import os
import json

from unreal import (
    EditorAssetLibrary,
    FbxImportUI,
    AssetImportTask,
    AssetToolsHelpers,
    load_asset,

    Vector,
    Rotator,
    FBXAnimationLengthImportType,
    Int32Interval
)

jsonSetting = open(os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "Data", "unrealenginesetting.json")), "r").read()
jsonSetting = json.loads(jsonSetting)

targetFolder = "/" + os.path.join("Game", "Blender", jsonSetting["subfolder"]).replace(os.sep, "/")

if EditorAssetLibrary.does_directory_exist(directory_path=targetFolder):
    EditorAssetLibrary.make_directory(directory_path=targetFolder)

for file in jsonSetting["files"]:
    sourceFile = os.path.join(jsonSetting["folder"], file["name"] + ".fbx").replace(os.sep, "/")

    if os.path.exists(sourceFile) and file["skeleton"] != "NONE":
        importOptions = FbxImportUI()

        importOptions.set_editor_property("import_mesh", False)
        importOptions.set_editor_property("import_as_skeletal", False)
        importOptions.set_editor_property('import_animations', True)

        importOptions.set_editor_property("skeleton", load_asset(file["skeleton"]))

        importOptions.anim_sequence_import_data.set_editor_property("animation_length", getattr(FBXAnimationLengthImportType, jsonSetting["animation_length"]))
        importOptions.anim_sequence_import_data.set_editor_property("import_meshes_in_bone_hierarchy", jsonSetting["import_meshes_in_bone_hierarchy"])
        frameImportRange = Int32Interval()
        frameImportRange.set_editor_property("min", jsonSetting["frame_import_range"][0])
        frameImportRange.set_editor_property("max", jsonSetting["frame_import_range"][1])
        importOptions.anim_sequence_import_data.set_editor_property("frame_import_range", frameImportRange)
        importOptions.anim_sequence_import_data.set_editor_property("use_default_sample_rate", jsonSetting["use_default_sample_rate"])
        importOptions.anim_sequence_import_data.set_editor_property("custom_sample_rate", jsonSetting["custom_sample_rate"])
        importOptions.anim_sequence_import_data.set_editor_property("import_custom_attribute", jsonSetting["import_custom_attribute"])
        importOptions.anim_sequence_import_data.set_editor_property("delete_existing_custom_attribute_curves", jsonSetting["delete_existing_custom_attribute_curves"])
        importOptions.anim_sequence_import_data.set_editor_property("import_bone_tracks", jsonSetting["import_bone_tracks"])
        importOptions.anim_sequence_import_data.set_editor_property("set_material_drive_parameter_on_custom_attribute", jsonSetting["set_material_drive_parameter_on_custom_attribute"])
        importOptions.anim_sequence_import_data.set_editor_property("material_curve_suffixes", jsonSetting["material_curve_suffixes"])
        importOptions.anim_sequence_import_data.set_editor_property("remove_redundant_keys", jsonSetting["remove_redundant_keys"])
        importOptions.anim_sequence_import_data.set_editor_property("delete_existing_morph_target_curves", jsonSetting["delete_existing_morph_target_curves"])
        importOptions.anim_sequence_import_data.set_editor_property("do_not_import_curve_with_zero", jsonSetting["do_not_import_curve_with_zero"])
        importOptions.anim_sequence_import_data.set_editor_property("preserve_local_transform", jsonSetting["preserve_local_transform"])

        # Transform

        importOptions.anim_sequence_import_data.set_editor_property("import_translation", Vector(*jsonSetting["import_translation"]))
        importOptions.anim_sequence_import_data.set_editor_property("import_rotation", Rotator(*jsonSetting["import_rotation"]))
        importOptions.anim_sequence_import_data.set_editor_property("import_uniform_scale", jsonSetting["import_uniform_scale"])

        # Misc.

        importOptions.anim_sequence_import_data.set_editor_property("convert_scene", jsonSetting["convert_scene"])
        importOptions.anim_sequence_import_data.set_editor_property("force_front_x_axis", jsonSetting["force_front_x_axis"])
        importOptions.anim_sequence_import_data.set_editor_property("convert_scene_unit", jsonSetting["convert_scene_unit"])
        importOptions.set_editor_property("override_full_name", jsonSetting["override_full_name"])

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