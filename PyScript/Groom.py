import os
import inspect
import json

## NOT TESTED YET, BECAUSE GROOM STILL NOT STABLE IN UNREAL ENGINE AND I"M NOT YET UPGRADE TO 25 (LOL)

from unreal import (
    EditorAssetLibrary,
    GroomImportOptions,
    AssetImportTask,
    AssetToolsHelpers,

    Vector,
    GroomInterpolationQuality,
    GroomInterpolationWeight
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
    sourceFile = os.path.join(jsonSetting["folder"], file["name"] + ".abc").replace(os.sep, "/")

    if os.path.exists(sourceFile):
        importOptions = GroomImportOptions()

        # Conversion

        importOptions.conversion_settings.set_editor_property("rotation", Vector(*jsonSetting["rotation"]))
        importOptions.conversion_settings.set_editor_property("scale", Vector(*jsonSetting["scale"]))

        # Build settings

        importOptions.build_settings.set_editor_property("override_guides", jsonSetting["override_guides"])
        importOptions.build_settings.set_editor_property("hair_to_guide_density", jsonSetting["hair_to_guide_density"])
        importOptions.build_settings.set_editor_property("interpolation_quality", getattr(GroomInterpolationQuality, jsonSetting["interpolation_quality"]))
        importOptions.build_settings.set_editor_property("interpolation_distance", getattr(GroomInterpolationWeight, jsonSetting["interpolation_distance"]))
        importOptions.build_settings.set_editor_property("randomize_guide", jsonSetting["randomize_guide"])
        importOptions.build_settings.set_editor_property("use_unique_guide", jsonSetting["use_unique_guide"])

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