import os
import inspect
import json

from unreal import (
    AssetRegistryHelpers,
    FbxExportOption,
    FbxExportCompatibility,
    AssetExportTask,
    Exporter,

    AnimSequenceExporterFBX,
    SkeletalMeshExporterFBX,
    StaticMeshExporterFBX
)

asset_registry = AssetRegistryHelpers.get_asset_registry()

# Fix Python PATH Script Issue #9
filename = inspect.getframeinfo(inspect.currentframe()).filename
currentPath = os.path.dirname(os.path.abspath(filename))

jsonSetting = open(os.path.normpath(os.path.join(currentPath, "..", "Data", "importAssets.json")), "r").read()
jsonSetting = json.loads(jsonSetting)

setting = jsonSetting["setting"]

arrBlenderToImport = []

for assetsName, pathAsset in [(asset[0], asset[1]) for asset in jsonSetting["assets"]]:
    asset = asset_registry.get_asset_by_object_path(pathAsset)
    assetObject = asset.get_asset()
    targetFile = os.path.join(jsonSetting["folder"], assetsName).replace(os.sep, "/")

    exportOptions = FbxExportOption()
    exportOptions.set_editor_property("fbx_export_compatibility", getattr(FbxExportCompatibility, setting["fbx_export_compatibility"]))
    exportOptions.set_editor_property("ascii", setting["ascii"])
    exportOptions.set_editor_property("force_front_x_axis", setting["force_front_x_axis"])
    exportOptions.set_editor_property("vertex_color", setting["vertex_color"])
    exportOptions.set_editor_property("level_of_detail", setting["level_of_detail"])
    exportOptions.set_editor_property("collision", setting["collision"])
    exportOptions.set_editor_property("export_morph_targets", setting["export_morph_targets"])
    exportOptions.set_editor_property("export_preview_mesh", setting["export_preview_mesh"])
    exportOptions.set_editor_property("map_skeletal_motion_to_root", setting["map_skeletal_motion_to_root"])
    exportOptions.set_editor_property("export_local_time", setting["export_local_time"])

    # Task

    exportTask = AssetExportTask()
    exportTask.set_editor_property("automated", True)
    exportTask.set_editor_property("object", assetObject)
    exportTask.set_editor_property("filename", targetFile)
    exportTask.set_editor_property("exporter", {"StaticMesh": StaticMeshExporterFBX(), "SkeletalMesh": SkeletalMeshExporterFBX(), "AnimSequence": AnimSequenceExporterFBX()}[str(asset.asset_class)])
    exportTask.set_editor_property("options", exportOptions)
    exportTask.set_editor_property("prompt", False)
    exportTask.set_editor_property("replace_identical", True)

    isExportSuccess = Exporter.run_asset_export_task(exportTask)
    if isExportSuccess:
        arrBlenderToImport += [[targetFile, {"StaticMesh": "MESH", "SkeletalMesh": "ARMATURE", "AnimSequence": "ACTION"}[str(asset.asset_class)]]]

print(json.dumps(arrBlenderToImport))