# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "UE4Workspace",
    "author" : "Anas RAR",
    "description" : "Addon For UE4 Workspace",
    "blender" : (2, 81, 0),
    "version" : (1, 5, 0),
    "location" : "3D View > Tools",
    "warning" : "",
    "wiki_url": "https://github.com/anasrar/Blender-UE4-Workspace", # 2.82 below
    "doc_url": "https://github.com/anasrar/Blender-UE4-Workspace", # 2.83 above
    "tracker_url": "https://github.com/anasrar/Blender-UE4-Workspace/issues",
    "support": "COMMUNITY",
    "category" : "Workspace"
}

import bpy
from bpy.app.handlers import persistent
from bpy.props import (StringProperty, BoolProperty, BoolVectorProperty, IntProperty, IntVectorProperty, FloatProperty, EnumProperty, PointerProperty, CollectionProperty)
from bpy.utils import (register_class, unregister_class)

from . UE4WS_Preferences import (
    Groups as PreferencesGroup,
    Preferences,
    Ops as PreferencesOperator
)

from . UE4WS_ExportOption import (
    PANEL as exportOptionPanel,
    Ops as exportOptionOperator
)

from . UE4WS_ExportOptionImportAssets import (
    IMPORTASSETS_UL_AssetsList,
    Groups as exportOptionImportAssetsGroup,
    Props as exportOptionImportAssetsProps,
    PANEL as exportOptionImportAssetsPanel,
    Ops as exportOptionImportAssetsOperator
)

from . UE4WS_ExportOptionImportAssetsFBXOption import (
    PANEL as exportOptionImportAssetsFBXOptionPanel
)

from . UE4WS_ExportOptionImportAssetsUnrealEngine import (
    PANEL as exportOptionImportAssetsUnrealEnginePanel
)

from . UE4WS_Object import (
    PANEL as objectPanel,
    Ops as objectOperator
)

from . UE4WS_ObjectCustomCollision import (
    Props as objectCustomCollisionProps,
    PANEL as objectCustomCollisionPanel,
    Ops as objectCustomCollisionOperator
)

from . UE4WS_ObjectCharacterPart import (
    Props as objectCharacterPartProps,
    PANEL as objectCharacterPartPanel,
    Ops as objectCharacterPartOperator
)

from . UE4WS_ObjectSocket import (
    Props as objectSocketProps,
    PANEL as objectSocketPanel,
    Ops as objectSocketOperator
)

from . UE4WS_ObjectLOD import (
    Groups as objectLODPGroup,
    Props as objectLODProps,
    PANEL as objectLODPanel,
    Ops as objectLODOperator
)

from . UE4WS_ObjectControlRig import (
    PANEL as objectControlRigPanel,
    Ops as objectControlRigOperator
)

from . UE4WS_ObjectRetargetAnimation import (
    RETARGET_UL_BoneParentList,
    RETARGET_UL_BoneMapList,
    Groups as objectRetargetAnimationGroup,
    Props as objectRetargetAnimationProps,
    PANEL as objectRetargetAnimationPanel,
    Ops as objectRetargetAnimationOperator
)

from . UE4WS_ObjectSkeletonPreset import (
    PANEL as objectSkeletonPresetPanel,
    Ops as objectSkeletonPresetOperator
)

from . UE4WS_StaticMesh import (
    PANEL as staticMeshPanel,
    Ops as staticMeshOperator
)

from . UE4WS_StaticMeshFBXOption import (
    PANEL as staticMeshFBXOptionPanel
)

from . UE4WS_StaticMeshUnrealEngine import (
    PANEL as staticMeshUnrealEnginePanel
)

from . UE4WS_Character import (
    UE4WORKSPACE_MT_skeleton_preset_submenu,
    appendType as characterAppendType,
    Props as characterProps,
    PANEL as characterPanel,
    Ops as characterOperator
)

from . UE4WS_CharacterFBXOption import (
    PANEL as CharacterFBXOptionPanel
)

from . UE4WS_CharacterUnrealEngine import (
    PANEL as CharacterUnrealEnginePanel
)

from . UE4WS_Animation import (
    ANIM_UL_actionList,
    Props as animationProps,
    PANEL as animationPanel,
    Ops as animationOperator
)

from . UE4WS_AnimationFBXOption import (
    PANEL as AnimationFBXOptionPanel
)

from . UE4WS_AnimationUnrealEngine import (
    PANEL as AnimationUnrealEnginePanel
)

from . UE4WS_Credit import (
    PANEL as creditPanel
)

from . remote_execute import (
    RemoteExecution
)

from . misc import (
    PopUpWindow
)

remote_exec = RemoteExecution()

AR_UE4WS_PropsArray = []
# extend property to array, make sure you add from here
for x in [
    exportOptionImportAssetsProps,
    objectCustomCollisionProps,
    objectCharacterPartProps,
    objectSocketProps,
    objectLODProps,
    objectRetargetAnimationProps,
    characterProps,
    animationProps
    ]:
    AR_UE4WS_PropsArray.extend(x)

AR_UE4WS_OperatorArray = []
# extend operator to array, make sure you add from here
for x in [
    PreferencesGroup,
    PreferencesOperator,
    objectOperator,
    objectCustomCollisionOperator,
    objectCharacterPartOperator,
    objectSocketOperator,
    objectLODPGroup,
    objectLODOperator,
    objectControlRigOperator,
    objectRetargetAnimationGroup,
    objectRetargetAnimationOperator,
    objectSkeletonPresetOperator,
    exportOptionOperator,
    exportOptionImportAssetsGroup,
    exportOptionImportAssetsOperator,
    staticMeshOperator,
    characterOperator,
    animationOperator
    ]:
    AR_UE4WS_OperatorArray.extend(x)

AR_UE4WS_AppendTypes = []
# extend append type to array, make sure you add from here
for x in [
    characterAppendType
    ]:
    AR_UE4WS_AppendTypes.extend(x)

AR_UE4WS_classes = (
    # addon preferences
    Preferences,
    # Export Option
    exportOptionPanel,
    IMPORTASSETS_UL_AssetsList,
    exportOptionImportAssetsPanel,
    exportOptionImportAssetsFBXOptionPanel,
    exportOptionImportAssetsUnrealEnginePanel,
    # Object
    objectPanel,
    objectCustomCollisionPanel,
    objectCharacterPartPanel,
    objectSocketPanel,
    objectLODPanel,
    objectSkeletonPresetPanel,
    objectControlRigPanel,
    RETARGET_UL_BoneParentList,
    RETARGET_UL_BoneMapList,
    objectRetargetAnimationPanel,
    ## Static Mesh
    staticMeshPanel,
    staticMeshFBXOptionPanel,
    staticMeshUnrealEnginePanel,
    ## Character
    UE4WORKSPACE_MT_skeleton_preset_submenu,
    characterPanel,
    CharacterFBXOptionPanel,
    CharacterUnrealEnginePanel,
    ## Animation
    ANIM_UL_actionList,
    animationPanel,
    AnimationFBXOptionPanel,
    AnimationUnrealEnginePanel,
    ## Credit
    creditPanel,
    ## Misc.
    PopUpWindow
)

TypeProps = {
    "scene": bpy.types.Scene,
    "object": bpy.types.Object,
    "action": bpy.types.Action,
    "armature": bpy.types.Armature,
    "bone": bpy.types.Bone,
    "mesh": bpy.types.Mesh
}

@persistent
def resetVariable(scene):
    """Reset some variable and disconnect from unreal engine after load blend file"""
    preferences = bpy.context.preferences.addons[__package__].preferences
    preferences.skeleton.clear()
    preferences.CHAR_CharacterSkeleton = "NEW"
    preferences.ANIM_CharacterSkeleton = "NONE"
    remote_exec.stop()

    for P in AR_UE4WS_PropsArray:
        if hasattr(TypeProps.get(P.get("type")), P.get("name")) and P.get("resetVariable", False):
            typeProp = P.get("type")
            if (typeProp == "scene"):
                bpy.context.scene.property_unset(P.get("name"))
            elif (typeProp == "object"):
                for obj in bpy.data.objects:
                    obj.property_unset(P.get("name"))
            elif (typeProp == "action"):
                for action in bpy.data.actions:
                    action.property_unset(P.get("name"))
            elif (typeProp == "armature"):
                for armature in bpy.data.armatures:
                    armature.property_unset(P.get("name"))
            elif (typeProp == "mesh"):
                for armature in bpy.data.meshes:
                    armature.property_unset(P.get("name"))

def register():
    # Register operator
    for X in AR_UE4WS_OperatorArray:
        if hasattr(X, "remote"):
            X.remote = remote_exec
        if hasattr(X, "addonVersion"):
            X.addonVersion = bl_info["version"]
        register_class(X)

    # Register prop
    for P in AR_UE4WS_PropsArray:
        setattr(TypeProps.get(P.get("type")), P.get("name"), P.get("value"))

    # Append Type
    for bType, func in AR_UE4WS_AppendTypes:
        dataType = getattr(bpy.types, bType)
        if dataType:
            dataType.append(func)
        else:
            print("TRY TO APPEND : bpy.types.{} Not Found".format(bType))

    # Register class
    for C in AR_UE4WS_classes:
        if hasattr(C, "remote"):
            C.remote = remote_exec
        if hasattr(C, "addonVersion"):
            C.addonVersion = bl_info["version"]
        register_class(C)

    bpy.app.handlers.load_post.append(resetVariable)

def unregister():
    # Unregister operator
    for X in reversed(AR_UE4WS_OperatorArray):
        unregister_class(X)

    # Unregister prop
    for P in reversed(AR_UE4WS_PropsArray):
        delattr(TypeProps.get(P.get("type")), P.get("name"))

    # Remove Append Type
    for bType, func in AR_UE4WS_AppendTypes:
        dataType = getattr(bpy.types, bType)
        if dataType:
            dataType.remove(func)
        else:
            print("TRY TO REMOVE : bpy.types.{} Not Found".format(bType))

    # Unregister class
    for C in reversed(AR_UE4WS_classes):
        unregister_class(C)

    bpy.app.handlers.load_post.remove(resetVariable)