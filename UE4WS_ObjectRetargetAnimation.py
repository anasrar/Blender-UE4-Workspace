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
    boneExist: BoolProperty(default=True)
    boneNotExist: BoolProperty(name="Warning", description="Bone Does Not Exist", default=False)
    def updateMute(self, context):
        for FCurve in self.obj.animation_data.drivers:
            if FCurve.data_path + "["+ str(FCurve.array_index) +"]" in [path.path for path in self.dataPaths]:
                FCurve.mute = self.mute
    mute: BoolProperty(default=False, update=updateMute)
    transform: BoolVectorProperty(default=(False, False, False), size=3)
    source: StringProperty(default="Bone")
    target: StringProperty(default="Bone")
    dataPaths: CollectionProperty(type=RETARGET_DataPath)
    influence: FloatProperty(default=1.0, min=0.0, max=1.0)
    rotation_eulerX: FloatProperty(default=0.0, subtype="ANGLE")
    rotation_eulerY: FloatProperty(default=0.0, subtype="ANGLE")
    rotation_eulerZ: FloatProperty(default=0.0, subtype="ANGLE")
    rotation_eulerInfluence: FloatProperty(default=1.0, min=0.0, max=1.0)
    locationX: FloatProperty(default=0.0)
    locationY: FloatProperty(default=0.0)
    locationZ: FloatProperty(default=0.0)
    locationInfluence: FloatProperty(default=1.0, min=0.0, max=1.0)
    scaleX: FloatProperty(default=0.0)
    scaleY: FloatProperty(default=0.0)
    scaleZ: FloatProperty(default=0.0)
    scaleInfluence: FloatProperty(default=1.0, min=0.0, max=1.0)

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
                split = row.split(factor=0.5)
                col = split.column()
                col.label(text="Bone")
                split = split.split()
                col = split.column()
                col.label(text="Parent")

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
                        col.label(text=BoneParent.bone)
                        col.label(text=BoneParent.parent)
                        col.prop(BoneParent, "influence", text="", slider=True)

            layout.prop(activeObject.data, "BoneMapTab", icon=("TRIA_RIGHT", "TRIA_DOWN")[activeObject.data.BoneMapTab], text="Bone Tweak", emboss=False)
            if activeObject.data.BoneMapTab:
                col = layout.column()
                row = col.row()
                split = row.split(factor=0.5)
                col = split.column()
                col.label(text="Target")
                split = split.split()
                col = split.column()
                col.label(text="Source")

                layout.template_list("RETARGET_UL_BoneMapList", "", activeObject.data, "BoneMaps", activeObject.data, "indexBoneMap", rows=4)

                indexBoneMap = activeObject.data.indexBoneMap
                if indexBoneMap != -1 and indexBoneMap < len(activeObject.data.BoneMaps):
                    BoneMap = activeObject.data.BoneMaps[indexBoneMap]
                    if BoneMap.boneExist:
                        box = layout.box()
                        box.label(text=BoneMap.name)
                        col = box.column()
                        row = col.row()
                        split = row.split(factor=0.6)
                        col = split.column()
                        col.alignment = "RIGHT"
                        col.label(text="Target")
                        col.label(text="Source")
                        # col.label(text="Mute")
                        # col.label(text="Influence")
                        split = split.split()
                        col = split.column()
                        col.alignment = "LEFT"
                        col.label(text=BoneMap.target)
                        col.label(text=BoneMap.source)
                        # col.prop(BoneMap, "mute", text="", icon=("CHECKBOX_DEHLT" if BoneMap.mute else "CHECKBOX_HLT"), emboss=False)
                        # col.prop(BoneMap, "influence", text="", slider=True)

                        # i plan to expose expression variable but i think no one will really use
                        # box.row().label(text="EXPESSION")
                        # box.row().prop(BoneMap, "target", text="")

                        for index, transform in enumerate(BoneMap.transform):
                            if transform:
                                transformLabel = ["ROTATION", "LOCATION", "SCALE"][index]
                                transformAttribute = ["rotation_euler", "location", "scale"][index]
                                box.row().label(text="OFFSET " + transformLabel)
                                col = box.column(align=True)
                                for axis in ["X", "Y", "Z"]:
                                    col.prop(BoneMap, transformAttribute + axis, text=axis)
                                col.prop(BoneMap, transformAttribute + "Influence", text="Influence", slider=True)

# UIList

class RETARGET_UL_BoneParentList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        activeObject = context.active_object

        row = layout.row()
        split = row.split(factor=0.5)
        row = split.row()
        row.label(text=item.bone)
        split = split.split()
        row = split.row()
        row.label(text=item.parent)
        if item.boneExist:
            row.prop(item, "mute", text="", icon=("CHECKBOX_DEHLT" if item.mute else "CHECKBOX_HLT"), emboss=False)
        else:
            row.prop(item, "boneNotExist", text="", icon="ERROR", emboss=False)

class RETARGET_UL_BoneMapList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        activeObject = context.active_object

        row = layout.row()
        split = row.split(factor=0.5)
        row = split.row()
        row.label(text=item.target)
        split = split.split()
        row = split.row()
        row.label(text=item.source)
        if item.boneExist:
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
        bpy.ops.object.mode_set(mode="POSE")
        poseBones = targetObj.pose.bones

        preset = next(iter([preset for preset in preferences.RETARGET_Presets if str(preset.flag) == targetObj.data.RetargetPreset]), None)

        # unbind
        if targetObj.data.HasBind:
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

            # remove driver from maping bone list
            for index, boneMap in enumerate([boneMap for boneMap in targetObj.data.BoneMaps if boneMap.boneExist]):
                poseBone = poseBones.get(boneMap.target)
                # change rotation mode to QUATERNION
                poseBone.rotation_mode = "QUATERNION"
                for index, transformType in enumerate(list(boneMap.transform)):
                    if transformType:
                        poseBone.driver_remove(["rotation_euler", "location", "scale"][index])
            # clear collection
            targetObj.data.BoneMaps.clear()

            # clear transform
            bpy.ops.pose.select_all(action="SELECT")
            bpy.ops.pose.rot_clear()
            bpy.ops.pose.loc_clear()
            bpy.ops.pose.scale_clear()
            bpy.ops.pose.select_all(action="DESELECT")

        # bind
        else:
            # add parent constraint in bone parent list
            for index, parentBone in enumerate(preset.ParentBones):
                newParentBone = targetObj.data.BoneParents.add()
                newParentBone.name = parentBone.name
                newParentBone.bone = parentBone.bone
                newParentBone.parent = parentBone.parent
                poseBone = poseBones.get(parentBone.bone)
                if poseBone:
                    # constraint
                    constraint = poseBone.constraints.new("ARMATURE")
                    constraint.name = "RETARGET_PARENT"
                    constraint.show_expanded = False
                    target = constraint.targets.new()
                    target.target = targetObj
                    target.subtarget = parentBone.parent
                    target.weight = 1.0
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
                else:
                    newParentBone.boneExist = False

            # maping bone list
            for index, boneMap in enumerate(preset.AxisMaps):
                newBoneMap = targetObj.data.BoneMaps.add()
                newBoneMap.name = boneMap.name
                newBoneMap.target = boneMap.boneTarget
                newBoneMap.source = boneMap.boneSource if boneMap.boneSource else "[Object]"
                newBoneMap.obj = targetObj
                poseBone = poseBones.get(boneMap.boneTarget)
                if poseBone:
                    # change rotation mode to XYZ
                    poseBone.rotation_mode = "XYZ"
                    newBoneMap.transform = boneMap.transform
                    for index, transformType in enumerate(list(boneMap.transform)):
                        if transformType:
                            for targetAxis, sourceAxis in [("X", boneMap.axisX), ("Y", boneMap.axisY), ("Z", boneMap.axisZ)]:
                                indexToTransformName = ["rotation_euler", "location", "scale"][index]
                                targetAxisToIndex = {"X": 0, "Y": 1, "Z": 2}[targetAxis]
                                isInverse = sourceAxis.startswith("-")
                                sourceAxis = sourceAxis.replace("-", "")
                                offsetInit = getattr(poseBone, indexToTransformName)[targetAxisToIndex]

                                # driver bone
                                FCurve = poseBone.driver_add(indexToTransformName, targetAxisToIndex)
                                driver = FCurve.driver
                                driver.type = "SCRIPTED"

                                var = driver.variables.new()
                                var.type = "TRANSFORMS"
                                varTarget = var.targets[0]
                                varTarget.id = sourceObj
                                varTarget.bone_target = boneMap.boneSource
                                varTarget.transform_type = (["ROT_", "LOC_", "SCALE_"][index]) + sourceAxis
                                varTarget.rotation_mode = "AUTO"
                                varTarget.transform_space = "LOCAL_SPACE"

                                varName = "-" + var.name if isInverse else var.name

                                # offset
                                var = driver.variables.new()
                                var.name = "offset"
                                setattr(newBoneMap, indexToTransformName + targetAxis , offsetInit)
                                offset = var.name
                                var.type = "SINGLE_PROP"
                                varTarget = var.targets[0]
                                varTarget.id_type = "ARMATURE"
                                varTarget.id = targetObj.data
                                varTarget.data_path = newBoneMap.path_from_id(indexToTransformName + targetAxis)

                                # influence Transform
                                var = driver.variables.new()
                                var.name = "influence"
                                influence = var.name
                                var.type = "SINGLE_PROP"
                                varTarget = var.targets[0]
                                varTarget.id_type = "ARMATURE"
                                varTarget.id = targetObj.data
                                varTarget.data_path = newBoneMap.path_from_id( indexToTransformName + "Influence")

                                # # influence
                                # var = driver.variables.new()
                                # var.name = "influence"
                                # influence = var.name
                                # var.type = "SINGLE_PROP"
                                # varTarget = var.targets[0]
                                # varTarget.id_type = "ARMATURE"
                                # varTarget.id = targetObj.data
                                # varTarget.data_path = newBoneMap.path_from_id("influence")

                                driver.expression = boneMap.expression.format(var=varName, offset=offset, influence=influence)

                                # data path collection
                                dataPath = newBoneMap.dataPaths.add()
                                dataPath.path = FCurve.data_path + "["+ str(FCurve.array_index) +"]"
                else:
                    newBoneMap.boneExist = False

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
        # parent bone matrix to keyframe, because using constraint does not get local transform
        # format (boneName: str, matrix: Matrix, frame: int)
        parentBoneMatrixs = []

        # bake animation manually because bake action operator in python is very buggy and give me more control
        frame = self.startFrame
        while frame <= self.endFrame:
            context.scene.frame_set(frame)
            # bake bone base on bone map list
            for boneMap in [boneMap for boneMap in targetObj.data.BoneMaps if boneMap.boneExist and not boneMap.mute]:
                poseBone = poseBones.get(boneMap.target)
                for index, transformType in enumerate(list(boneMap.transform)):
                    if transformType:
                        indexToTransformName = ["rotation_euler", "location", "scale"][index]
                        poseBone.keyframe_insert(indexToTransformName)
                        if indexToTransformName == "rotation_euler":
                            # insert keyframe to quaternion rotation
                            # convert euler to rotation so you can use two mode rotation
                            poseBone.rotation_quaternion = poseBone.rotation_euler.to_quaternion()
                            poseBone.keyframe_insert("rotation_quaternion")

            # get matrix parent bone
            for index, BoneParent in enumerate([BoneParent for BoneParent in targetObj.data.BoneParents if BoneParent.boneExist and not BoneParent.mute]):
                poseBone = poseBones.get(BoneParent.bone)
                boneMatrix = poseBone.matrix.copy()
                parentBoneMatrixs.append((BoneParent.bone, boneMatrix, frame))

            frame += self.frameStep

        # mute parent constraint
        for index, BoneParent in enumerate([BoneParent for BoneParent in targetObj.data.BoneParents if BoneParent.boneExist]):
            BoneParent.mute = not BoneParent.mute

        # insert parent bone keyframe matrix
        for boneName, matrix, frame in parentBoneMatrixs:
            poseBone = poseBones.get(boneName)
            poseBone.matrix = matrix
            poseBone.keyframe_insert("location", frame=frame)
            poseBone.keyframe_insert("rotation_quaternion", frame=frame)
            poseBone.keyframe_insert("rotation_euler", frame=frame)

        # unmute parent constraint
        for index, BoneParent in enumerate([BoneParent for BoneParent in targetObj.data.BoneParents if BoneParent.boneExist]):
            BoneParent.mute = not BoneParent.mute

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