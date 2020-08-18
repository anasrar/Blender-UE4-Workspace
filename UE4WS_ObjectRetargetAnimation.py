import bpy
from bpy.props import (EnumProperty, StringProperty, FloatProperty, FloatVectorProperty, IntProperty, BoolProperty, BoolVectorProperty, PointerProperty, CollectionProperty)
from bpy.types import (Panel, Operator, PropertyGroup, UIList)

# PROPERTY GROUP

class RETARGET_DataPath(PropertyGroup):
    path: StringProperty(default="path")

class RETARGET_BoneParentGroup(PropertyGroup):
    name: StringProperty(default="Bone")
    boneExist: BoolProperty(default=True)
    boneNotExist: BoolProperty(name="Warning", description="Bone Does Not Exist", default=False)
    mute: BoolProperty(default=False)
    bone: StringProperty(default="Bone2")
    parent: StringProperty(default="Bone")
    influence: FloatProperty(default=1.0, min=0.0, max=1.0)

class RETARGET_BoneMapGroup(PropertyGroup):
    name: StringProperty(default="Bone")
    obj: PointerProperty(type=bpy.types.Object)
    boneTargetName: StringProperty(default="Bone")
    boneSourceName: StringProperty(default="Bone")
    boneTargetExist: BoolProperty(default=True)
    boneSourceExist: BoolProperty(default=True)
    boneNotExist: BoolProperty(name="Warning", description="Bone Does Not Exist", default=False)
    def updateMute(self, context):
        for FCurve in self.obj.animation_data.drivers:
            if FCurve.data_path + "["+ str(FCurve.array_index) +"]" in [path.path for path in self.dataPaths]:
                FCurve.mute = self.mute
    mute: BoolProperty(default=False, update=updateMute)
    transform: BoolVectorProperty(default=(False, False, False), size=3)
    axis: BoolVectorProperty(default=(False, False, False), size=3)
    source: StringProperty(default="Bone")
    target: StringProperty(default="Bone")
    dataPaths: CollectionProperty(type=RETARGET_DataPath)
    influence: FloatProperty(default=1.0, min=0.0, max=1.0)
    locationMultiply: FloatProperty(default=1.0)
    ROT_XInfluence: FloatProperty(default=1.0, min=0.0, max=1.0)
    ROT_YInfluence: FloatProperty(default=1.0, min=0.0, max=1.0)
    ROT_ZInfluence: FloatProperty(default=1.0, min=0.0, max=1.0)
    LOC_XInfluence: FloatProperty(default=1.0, min=0.0, max=1.0)
    LOC_YInfluence: FloatProperty(default=1.0, min=0.0, max=1.0)
    LOC_ZInfluence: FloatProperty(default=1.0, min=0.0, max=1.0)
    SCALE_XInfluence: FloatProperty(default=1.0, min=0.0, max=1.0)
    SCALE_YInfluence: FloatProperty(default=1.0, min=0.0, max=1.0)
    SCALE_ZInfluence: FloatProperty(default=1.0, min=0.0, max=1.0)

# group export

Groups = [
    RETARGET_DataPath,
    RETARGET_BoneParentGroup,
    RETARGET_BoneMapGroup
]

# PROPS

Props = [
    {
        "type": "armature",
        "name": "RetargetSource",
        "value": PointerProperty(
            name="Retarget Source",
            description="Armature for retarget source",
            type=bpy.types.Object,
            poll=lambda self, obj: obj.type == "ARMATURE"
            ),
        "resetVariable": False
    },
    {
        "type": "armature",
        "name": "RetargetPreset",
        "value": EnumProperty(
            name="Retarget Preset",
            items=lambda self, context: [(str(preset.flag), preset.name, preset.description) for preset in context.preferences.addons[__package__].preferences.RETARGET_Presets],
            default=None
            ),
        "resetVariable": False
    },
    {
        "type": "armature",
        "name": "HasBind",
        "value": BoolProperty(default=False),
        "resetVariable": False
    },
    {    
        "type": "armature",
        "name": "BoneParents",
        "value": CollectionProperty(type=RETARGET_BoneParentGroup),
        "resetVariable": False
    },
    {
        "type": "armature",
        "name": "indexBoneParent",
        "value": IntProperty(
            default=-1
            ),
        "resetVariable": True
    },
    {    
        "type": "armature",
        "name": "BoneMaps",
        "value": CollectionProperty(type=RETARGET_BoneMapGroup),
        "resetVariable": False
    },
    {
        "type": "armature",
        "name": "indexBoneMap",
        "value": IntProperty(
            default=-1
            ),
        "resetVariable": True
    },
    {
        "type": "armature",
        "name": "ParentBoneTab",
        "value": BoolProperty(default=False),
        "resetVariable": True
    },
    {
        "type": "armature",
        "name": "BoneMapTab",
        "value": BoolProperty(default=False),
        "resetVariable": True
    },
    {
        "type": "armature",
        "name": "boneShapeObj",
        "value": PointerProperty(type=bpy.types.Object),
        "resetVariable": False
    }
]

# PANEL

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_RetargetAnimationPanel"
    bl_parent_id = "UE4WORKSPACE_PT_ObjectPanel"
    bl_label = "Retarget Animation"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object
        return activeObject is not None and activeObject.type == "ARMATURE" and context.mode in ["OBJECT", "POSE"]

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Retarget Preset")
        col.label(text="Target")
        col.label(text="Source")
        split = split.split()
        col = split.column()
        col.prop(activeObject.data, "RetargetPreset", text="")
        col.label(text=activeObject.name, icon="OUTLINER_OB_ARMATURE")
        col.prop(activeObject.data, "RetargetSource", text="", icon="OUTLINER_OB_ARMATURE")

        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("ue4workspace.bindarmature",icon="MOD_MIRROR", text=("BIND", "UNBIND")[activeObject.data.HasBind])

        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("ue4workspace.bakeretargetaction",icon="RENDER_ANIMATION", text="BAKE ACTION")

        if activeObject.data.HasBind:
            layout.prop(activeObject.data, "ParentBoneTab", icon=("TRIA_RIGHT", "TRIA_DOWN")[activeObject.data.ParentBoneTab], text="Parent Bone Tweak", emboss=False)
            if activeObject.data.ParentBoneTab:
                col = layout.column()
                row = col.row()
                split = row.split(factor=0.8)
                col = split.column()
                col.label(text="Name")
                split = split.split()
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text="Mute")

                layout.template_list("RETARGET_UL_BoneParentList", "", activeObject.data, "BoneParents", activeObject.data, "indexBoneParent", rows=4)

                indexBoneParent = activeObject.data.indexBoneParent
                if indexBoneParent != -1 and indexBoneParent < len(activeObject.data.BoneParents):
                    BoneParent = activeObject.data.BoneParents[indexBoneParent]
                    if BoneParent.boneExist:
                        box = layout.box()
                        box.label(text=BoneParent.name)
                        col = box.column()
                        row = col.row()
                        split = row.split(factor=0.6)
                        col = split.column()
                        col.alignment = "RIGHT"
                        col.label(text="Bone")
                        col.label(text="Parent")
                        col.label(text="Influence")
                        split = split.split()
                        col = split.column()
                        col.alignment = "LEFT"
                        row = col.row(align=True)
                        if True:
                            row.prop(BoneParent, "boneNotExist", text="", icon="ERROR", emboss=False)
                        row.label(text=BoneParent.bone)
                        col.label(text=BoneParent.parent)
                        col.prop(BoneParent, "influence", text="", slider=True)

            layout.prop(activeObject.data, "BoneMapTab", icon=("TRIA_RIGHT", "TRIA_DOWN")[activeObject.data.BoneMapTab], text="Bone Tweak", emboss=False)
            if activeObject.data.BoneMapTab:
                col = layout.column()
                row = col.row()
                split = row.split(factor=0.8)
                col = split.column()
                col.label(text="Name")
                split = split.split()
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text="Mute")

                layout.template_list("RETARGET_UL_BoneMapList", "", activeObject.data, "BoneMaps", activeObject.data, "indexBoneMap", rows=4)

                indexBoneMap = activeObject.data.indexBoneMap
                if indexBoneMap != -1 and indexBoneMap < len(activeObject.data.BoneMaps):
                    BoneMap = activeObject.data.BoneMaps[indexBoneMap]

                    box = layout.box()
                    box.label(text=BoneMap.name)
                    col = box.column()
                    row = col.row()
                    split = row.split(factor=0.6)
                    col = split.column()
                    col.alignment = "RIGHT"
                    col.label(text="Target")
                    col.label(text="Source")
                    split = split.split()
                    col = split.column()
                    row = col.row(align=True)
                    if not BoneMap.boneTargetExist:
                        row.prop(BoneMap, "boneNotExist", text="", icon="ERROR", emboss=False)
                    row.label(text=BoneMap.target)
                    row = col.row(align=True)
                    if not BoneMap.boneSourceExist:
                        row.prop(BoneMap, "boneNotExist", text="", icon="ERROR", emboss=False)
                    row.label(text=BoneMap.source if BoneMap.source else "OBJECT")

                    for index, transform in enumerate(BoneMap.transform):
                        if transform:
                            transformLabel = ["Rotation", "Location", "Scale"][index]
                            transformAttribute = ["ROT_", "LOC_", "SCALE_"][index]
                            if transformAttribute == "LOC_":
                                box.row().label(text=transformLabel + " Multipy")
                                box.row(align=True).prop(BoneMap, "locationMultiply", text="")
                            box.row().label(text="Influence " + transformLabel)
                            col = box.column(align=True)
                            for axis in [i for i, x in enumerate(list(BoneMap.axis)) if x]:
                                axis = ["X", "Y", "Z"][axis]
                                col.prop(BoneMap, transformAttribute + axis + "Influence", text=axis, slider=True)

# UIList

class RETARGET_UL_BoneParentList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        activeObject = context.active_object

        row = layout.row()
        row.label(text=item.name)
        if item.boneExist:
            row.prop(item, "mute", text="", icon=("CHECKBOX_DEHLT" if item.mute else "CHECKBOX_HLT"), emboss=False)
        else:
            row.prop(item, "boneNotExist", text="", icon="ERROR", emboss=False)

class RETARGET_UL_BoneMapList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        activeObject = context.active_object

        row = layout.row()
        row.label(text=item.name)
        if item.boneTargetExist and item.boneSourceExist:
            row.prop(item, "mute", text="", icon=("CHECKBOX_DEHLT" if item.mute else "CHECKBOX_HLT"), emboss=False)
        else:
            row.prop(item, "boneNotExist", text="", icon="ERROR", emboss=False)

#  OPERATOR

class OP_BindArmature(Operator):
    bl_idname = "ue4workspace.bindarmature"
    bl_label = "Bind/Unbind Armature"
    bl_description = "Bind/Unbind Armature"
    bl_options = {"UNDO"}

    @classmethod
    def poll(self, context):
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object
        return activeObject is not None and activeObject.type == "ARMATURE" and activeObject.data.RetargetSource is not None

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        targetObj = context.active_object
        sourceObj = targetObj.data.RetargetSource
        oldMode = context.mode
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        context.view_layer.objects.active = targetObj
        selectStateTargetObj = targetObj.select_get()
        selectStateSourceObj = sourceObj.select_get()
        targetObj.select_set(True)
        sourceObj.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        targetPoseBones = targetObj.pose.bones
        sourcePoseBones = sourceObj.pose.bones
        targetEditBones = targetObj.data.edit_bones
        sourceEditBones = sourceObj.data.edit_bones

        preset = next(iter([preset for preset in preferences.RETARGET_Presets if str(preset.flag) == targetObj.data.RetargetPreset]), None)

        # unbind
        if targetObj.data.HasBind:
            bpy.ops.object.mode_set(mode="POSE")
            # remove parent constraint in bone parent list
            for index, BoneParent in enumerate([BoneParent for BoneParent in targetObj.data.BoneParents if BoneParent.boneExist]):
                poseBone = poseBones.get(BoneParent.bone)
                constraint = poseBone.constraints.get("RETARGET_PARENT")
                # remove driver
                constraint.driver_remove("mute")
                constraint.driver_remove("influence")
                poseBone.constraints.remove(constraint)
            # clear collection
            targetObj.data.BoneParents.clear()

            # remove constraint and driver
            for boneMap in [boneMap for boneMap in targetObj.data.BoneMaps if boneMap.boneSourceExist and boneMap.boneTargetExist]:
                targetPoseBone = targetPoseBones.get(boneMap.target)
                constraint = targetPoseBone.constraints.get("RETARGET_TRANSFORM")
                constraint.driver_remove("mute")
                targetPoseBone.constraints.remove(constraint)

                sourceMimicPoseBone = targetPoseBones.get(boneMap.boneSourceName)
                for transformType in [["rotation_euler", "location", "scale"][i] for i, x in enumerate(list(boneMap.transform)) if x]:
                    sourceMimicPoseBone.driver_remove(transformType)

            bpy.ops.object.mode_set(mode="EDIT")

            # remove mimic bone
            for boneMap in [boneMap for boneMap in targetObj.data.BoneMaps if boneMap.boneSourceExist and boneMap.boneTargetExist]:
                sourceMimicBone = targetEditBones.get(boneMap.boneSourceName)
                targetMimicBone = targetEditBones.get(boneMap.boneTargetName)

                targetEditBones.remove(sourceMimicBone)
                targetEditBones.remove(targetMimicBone)

            # clear collection
            targetObj.data.BoneMaps.clear()

            # remove custom shape for hide bone
            bpy.data.objects.remove(targetObj.data.boneShapeObj, do_unlink=True)
        # bind
        else:
            mesh = bpy.data.meshes.new("HideBone")
            objCustomShape = bpy.data.objects.new(mesh.name,mesh)
            mesh.from_pydata([(0, 0, 0)], [], [])
            targetObj.data.boneShapeObj = objCustomShape

            # maping bone list
            # adding mimic bone
            for boneMap in preset.AxisMaps:
                newBoneMap = targetObj.data.BoneMaps.add()
                newBoneMap.name = boneMap.name
                newBoneMap.target = boneMap.boneTarget
                newBoneMap.source = boneMap.boneSource
                newBoneMap.obj = targetObj
                newBoneMap.axis = (boneMap.axisX, boneMap.axisY, boneMap.axisZ)
                newBoneMap.transform = boneMap.transform

                sourceBone = sourceEditBones.get(boneMap.boneSource) if boneMap.boneSource else sourceObj
                targetBone = targetEditBones.get(boneMap.boneTarget)

                newBoneMap.boneSourceExist = bool(sourceBone)
                newBoneMap.boneTargetExist = bool(targetBone)

                if newBoneMap.boneSourceExist and newBoneMap.boneTargetExist:
                    sourceMimicBone = targetEditBones.new("RETARGET_SRC_" + (boneMap.boneSource if boneMap.boneSource else "[OBJECT]"))
                    sourceMimicBone.length = 0.25
                    sourceMimicBone.use_deform = False
                    sourceMimicBone.matrix = sourceBone.matrix.copy().to_quaternion().to_matrix().to_4x4() if boneMap.boneSource else sourceObj.matrix_world.copy().to_quaternion().to_matrix().to_4x4()

                    targetMimicBone = targetEditBones.new("RETARGET_TRG_" + boneMap.boneTarget)
                    targetMimicBone.length = 0.25
                    targetMimicBone.use_deform = False
                    targetMimicBone.matrix = targetBone.matrix.copy().to_quaternion().to_matrix().to_4x4()
                    targetMimicBone.parent = sourceMimicBone

                    newBoneMap.boneSourceName = sourceMimicBone.name
                    newBoneMap.boneTargetName = targetMimicBone.name

            bpy.ops.object.mode_set(mode="POSE")

            # add parent constraint in bone parent list
            for parentBone in preset.ParentBones:
                newParentBone = targetObj.data.BoneParents.add()
                newParentBone.name = parentBone.name
                newParentBone.bone = parentBone.bone
                newParentBone.parent = parentBone.parent
                poseBone = targetPoseBones.get(parentBone.bone)
                newParentBone.boneExist = bool(poseBone)
                if newParentBone.boneExist:
                    # constraint
                    constraint = poseBone.constraints.new("CHILD_OF")
                    constraint.name = "RETARGET_PARENT"
                    constraint.show_expanded = False
                    constraint.target = targetObj
                    constraint.subtarget = parentBone.parent
                    context_copy = bpy.context.copy()
                    context_copy["constraint"] = constraint
                    targetObj.data.bones.active = poseBone.bone
                    bpy.ops.constraint.childof_set_inverse(context_copy, constraint=constraint.name, owner="BONE")
                    # driver mute
                    driver = constraint.driver_add("mute").driver
                    driver.type = "SCRIPTED"

                    var = driver.variables.new()
                    var.name = "mute"
                    var.type = "SINGLE_PROP"
                    varTarget = var.targets[0]
                    varTarget.id_type = "ARMATURE"
                    varTarget.id = targetObj.data
                    varTarget.data_path = newParentBone.path_from_id("mute")
                    driver.expression = "mute"

                    # driver influence
                    driver = constraint.driver_add("influence").driver
                    driver.type = "SCRIPTED"

                    var = driver.variables.new()
                    var.name = "influence"
                    var.type = "SINGLE_PROP"
                    varTarget = var.targets[0]
                    varTarget.id_type = "ARMATURE"
                    varTarget.id = targetObj.data
                    varTarget.data_path = newParentBone.path_from_id("influence")
                    driver.expression = "influence"

            # add driver and constraint
            for boneMap in [boneMap for boneMap in targetObj.data.BoneMaps if boneMap.boneSourceExist and boneMap.boneTargetExist]:
                sourcePoseBone = targetPoseBones.get(boneMap.boneSourceName)
                # change rotation mode to XYZ
                sourcePoseBone.rotation_mode = "XYZ"
                for transformType in [["rotation_euler", "location", "scale"][i] for i, x in enumerate(list(boneMap.transform)) if x]:
                    for axis in [i for i, x in enumerate(list(boneMap.axis)) if x]:
                        transformDriver = ({"rotation_euler": "ROT_", "location": "LOC_", "scale": "SCALE_"}[transformType]) + (["X", "Y", "Z"][axis])
                        # driver bone
                        FCurve = sourcePoseBone.driver_add(transformType, axis)
                        driver = FCurve.driver
                        driver.type = "SCRIPTED"

                        var = driver.variables.new()
                        var.name = "var"
                        varName = var.name
                        var.type = "TRANSFORMS"
                        varTarget = var.targets[0]
                        varTarget.id = sourceObj
                        varTarget.bone_target = boneMap.source
                        varTarget.transform_type = transformDriver
                        varTarget.rotation_mode = "AUTO"
                        varTarget.transform_space = "LOCAL_SPACE"

                        # influence
                        var = driver.variables.new()
                        var.name = "influence"
                        varInfluence = var.name
                        var.type = "SINGLE_PROP"
                        varTarget = var.targets[0]
                        varTarget.id_type = "ARMATURE"
                        varTarget.id = targetObj.data
                        varTarget.data_path = boneMap.path_from_id(transformDriver + "Influence")

                        # location Multiply
                        var = driver.variables.new()
                        var.name = "locationMultiply"
                        varLocationMultiply = var.name
                        var.type = "SINGLE_PROP"
                        varTarget = var.targets[0]
                        varTarget.id_type = "ARMATURE"
                        varTarget.id = targetObj.data
                        varTarget.data_path = boneMap.path_from_id("locationMultiply")

                        # scale source
                        var = driver.variables.new()
                        var.name = "scaleSource"
                        varScaleSource = var.name
                        var.type = "TRANSFORMS"
                        varTarget = var.targets[0]
                        varTarget.id = sourceObj
                        varTarget.bone_target = ""
                        varTarget.transform_type = "SCALE_" + (["X", "Y", "Z"][axis])
                        varTarget.rotation_mode = "AUTO"
                        varTarget.transform_space = "LOCAL_SPACE"

                        # scale target
                        var = driver.variables.new()
                        var.name = "scaleTarget"
                        varScaleTarget = var.name
                        var.type = "TRANSFORMS"
                        varTarget = var.targets[0]
                        varTarget.id = targetObj
                        varTarget.bone_target = ""
                        varTarget.transform_type = "SCALE_" + (["X", "Y", "Z"][axis])
                        varTarget.rotation_mode = "AUTO"
                        varTarget.transform_space = "LOCAL_SPACE"

                        driver.expression = "(({}/({}/{}))*{})*{}".format(varName, varScaleTarget, varScaleSource, varLocationMultiply, varInfluence) if transformType == "location" else "{}*{}".format(varName, varInfluence)

                        # data path collection
                        dataPath = boneMap.dataPaths.add()
                        dataPath.path = FCurve.data_path + "["+ str(FCurve.array_index) +"]"

                sourcePoseBone.custom_shape = targetObj.data.boneShapeObj
                sourcePoseBone.custom_shape_scale = 0
                sourcePoseBone.bone.hide = True

                targetMimicPoseBone = targetPoseBones.get(boneMap.boneTargetName)
                targetMimicPoseBone.custom_shape = targetObj.data.boneShapeObj
                targetMimicPoseBone.custom_shape_scale = 0
                targetMimicPoseBone.bone.hide = True

                targetPoseBone = targetPoseBones.get(boneMap.target)
                constraint = targetPoseBone.constraints.new("COPY_TRANSFORMS")
                constraint.show_expanded = False
                constraint.name = "RETARGET_TRANSFORM"
                constraint.subtarget = boneMap.boneTargetName
                constraint.target = targetObj
                constraint.owner_space = "LOCAL"
                constraint.target_space = "LOCAL_WITH_PARENT"
                constraint.mix_mode = "BEFORE"
                # driver mute
                driver = constraint.driver_add("mute").driver
                driver.type = "SCRIPTED"

                var = driver.variables.new()
                var.name = "mute"
                var.type = "SINGLE_PROP"
                varTarget = var.targets[0]
                varTarget.id_type = "ARMATURE"
                varTarget.id = targetObj.data
                varTarget.data_path = boneMap.path_from_id("mute")
                driver.expression = "mute"

        bpy.ops.object.mode_set(mode="OBJECT")
        targetObj.select_set(selectStateTargetObj)
        sourceObj.select_set(selectStateSourceObj)
        bpy.ops.object.mode_set(mode=oldMode)
        targetObj.data.HasBind = not targetObj.data.HasBind
        return {"FINISHED"}

class OP_BakeRetargetAction(Operator):
    bl_idname = "ue4workspace.bakeretargetaction"
    bl_label = "Bake Retarget To Action"
    bl_description = "Bake Retarget To Action"
    bl_options = {"UNDO"}

    actionName: StringProperty(default="BakeAction")
    startFrame: IntProperty(default=1)
    endFrame: IntProperty(default=250)
    frameStep: IntProperty(default=1)

    @classmethod
    def poll(self, context):
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object
        return activeObject is not None and activeObject.type == "ARMATURE" and activeObject.data.HasBind

    def invoke(self, context, event):
        self.startFrame = context.scene.frame_start
        self.endFrame = context.scene.frame_end
        return context.window_manager.invoke_props_dialog(self, width = 250)

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Action Name")
        split = split.split()
        col = split.column()
        col.prop(self, "actionName", text="", icon="ACTION")

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Start Frame")
        split = split.split()
        col = split.column()
        col.prop(self, "startFrame", text="")

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="End Frame")
        split = split.split()
        col = split.column()
        col.prop(self, "endFrame", text="")

        col = layout.column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Frame Step")
        split = split.split()
        col = split.column()
        col.prop(self, "frameStep", text="")

    def execute(self, context):
        targetObj = context.active_object
        sourceObj = targetObj.data.RetargetSource
        oldMode = context.mode
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        context.view_layer.objects.active = targetObj
        bpy.ops.object.mode_set(mode="POSE")
        poseBones = targetObj.pose.bones

        # create new action
        action = bpy.data.actions.new(self.actionName)
        action.use_fake_user = True
        targetObj.animation_data.action = action

        # copy pose
        bpy.ops.pose.select_all(action="SELECT")
        bpy.ops.pose.copy()
        bpy.ops.pose.select_all(action="DESELECT")

        oldCurrentFrame = context.scene.frame_current
        # pose bone matrix to keyframe, because using constraint does not get local transform
        # format (poseBone: poseBone, matrix: Matrix, frame: int, transform: tuple(rotation: bool, location: bool, scale: bool), axis: tuple(x: bool, y: bool, z: bool))
        poseBoneMatrixs = []
        # same as pose bone matrix but for parent bone
        # format (poseBone: poseBone, matrix: Matrix, frame: int)
        parentBoneMatrixs = []

        # fliter bone maps
        boneMaps = [boneMap for boneMap in targetObj.data.BoneMaps if boneMap.boneTargetExist and boneMap.boneSourceExist and not boneMap.mute]
        # fliter parent bone
        parentBones = [BoneParent for BoneParent in targetObj.data.BoneParents if BoneParent.boneExist and not BoneParent.mute]

        # bake animation manually because bake action operator in python is very buggy and give me more control
        frame = self.startFrame
        while frame <= self.endFrame:
            context.scene.frame_set(frame)
            # get matrix bone maps
            for boneMap in boneMaps:
                poseBone = poseBones.get(boneMap.target)
                poseBoneMatrixs.append((poseBone, poseBone.matrix.copy(), frame, boneMap.transform, boneMap.axis))

            # get matrix parent bone
            for BoneParent in parentBones:
                poseBone = poseBones.get(BoneParent.bone)
                parentBoneMatrixs.append((poseBone, poseBone.matrix.copy(), frame))

            frame += self.frameStep

        # mute bone constraint
        for boneMap in boneMaps:
            boneMap.mute = True

        # mute parent constraint
        for BoneParent in parentBones:
            BoneParent.mute = True

        # insert bone keyframe matrix
        for poseBone, matrix, frame, transform, axis in poseBoneMatrixs:
            poseBone.matrix = matrix
            bpy.ops.pose.visual_transform_apply()
            poseBone.keyframe_insert("location", frame=frame)
            poseBone.keyframe_insert("rotation_quaternion", frame=frame)
            poseBone.keyframe_insert("rotation_euler", frame=frame)

        # insert parent bone keyframe matrix
        for poseBone, matrix, frame in parentBoneMatrixs:
            poseBone.matrix = matrix
            bpy.ops.pose.visual_transform_apply()
            poseBone.keyframe_insert("location", frame=frame)
            poseBone.keyframe_insert("rotation_quaternion", frame=frame)
            poseBone.keyframe_insert("rotation_euler", frame=frame)

        # unmute bone constraint
        for boneMap in boneMaps:
            boneMap.mute = False

        # unmute parent constraint
        for BoneParent in parentBones:
            BoneParent.mute = False

        # change interpolation to LINEAR
        for fcurve in action.fcurves:
            for keyFramePoints in fcurve.keyframe_points:
                keyFramePoints.interpolation = "LINEAR"

        # unassign action from armature
        targetObj.animation_data.action = None

        context.scene.frame_current = oldCurrentFrame

        # reset pose
        bpy.ops.pose.select_all(action="SELECT")
        bpy.ops.pose.paste(flipped=False)
        bpy.ops.pose.select_all(action="DESELECT")

        bpy.ops.object.mode_set(mode=oldMode)
        return {"FINISHED"}

# operator export

Ops = [
    OP_BindArmature,
    OP_BakeRetargetAction
]