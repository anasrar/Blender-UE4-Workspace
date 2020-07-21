import bpy
from bpy.props import (EnumProperty, StringProperty, IntProperty, BoolProperty, PointerProperty)
from bpy.types import (Panel, Operator)

# maping bone
mannequinBoneMaps = [{
    # enum["LOCATION", "ROTATION", "SCALE"]
    "copy": ["LOCATION"],
    "target": "root",
    "source": "",
    # axis format (target: enum("X", "Y", "Z"), source: enum("X", "Y", "Z", "-X", "-Y", "-Z"))
    "axis": [("X", "X"), ("Y", "Y"), ("Z", "Z")],
    "expression": "({var} * 100) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "TWEAK_pelvis",
    "source": "pelvis",
    "axis": [("X", "-Z"), ("Y", "X"), ("Z", "-Y")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "TWEAK_spine_01",
    "source": "spine_01",
    "axis": [("X", "-Z"), ("Y", "X"), ("Z", "-Y")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "TWEAK_spine_02",
    "source": "spine_02",
    "axis": [("X", "-Z"), ("Y", "X"), ("Z", "-Y")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "TWEAK_spine_03",
    "source": "spine_03",
    "axis": [("X", "-Z"), ("Y", "X"), ("Z", "-Y")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "TWEAK_neck_01",
    "source": "neck_01",
    "axis": [("X", "-Z"), ("Y", "X"), ("Z", "-Y")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "TWEAK_head",
    "source": "head",
    "axis": [("X", "-Z"), ("Y", "X"), ("Z", "-Y")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "FK_thigh_l",
    "source": "thigh_l",
    "axis": [("X", "-Y"), ("Y", "-X"), ("Z", "-Z")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "FK_calf_l",
    "source": "calf_l",
    "axis": [("X", "-Y"), ("Y", "-X"), ("Z", "-Z")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "TWEAK_foot_l",
    "source": "foot_l",
    "axis": [("X", "Z"), ("Y", "-Y"), ("Z", "X")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "CONTROL_ball_l",
    "source": "ball_l",
    "axis": [("X", "Z"), ("Y", "X"), ("Z", "Y")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "FK_thigh_r",
    "source": "thigh_r",
    "axis": [("X", "-Y"), ("Y", "X"), ("Z", "Z")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "FK_calf_r",
    "source": "calf_r",
    "axis": [("X", "-Y"), ("Y", "X"), ("Z", "Z")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "TWEAK_foot_r",
    "source": "foot_r",
    "axis": [("X", "Z"), ("Y", "Y"), ("Z", "-X")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "CONTROL_ball_r",
    "source": "ball_r",
    "axis": [("X", "Z"), ("Y", "-X"), ("Z", "-Y")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "TWEAK_clavicle_l",
    "source": "clavicle_l",
    "axis": [("X", "Y"), ("Y", "X"), ("Z", "-Z")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "FK_upperarm_l",
    "source": "upperarm_l",
    "axis": [("X", "Y"), ("Y", "X"), ("Z", "-Z")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "FK_lowerarm_l",
    "source": "lowerarm_l",
    "axis": [("X", "Y"), ("Y", "X"), ("Z", "-Z")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["ROTATION"],
    "target": "TWEAK_hand_l",
    "source": "hand_l",
    "axis": [("X", "-Z"), ("Y", "X"), ("Z", "-Y")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "TWEAK_clavicle_r",
    "source": "clavicle_r",
    "axis": [("X", "Y"), ("Y", "-X"), ("Z", "Z")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "FK_upperarm_r",
    "source": "upperarm_r",
    "axis": [("X", "Y"), ("Y", "-X"), ("Z", "Z")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "FK_lowerarm_r",
    "source": "lowerarm_r",
    "axis": [("X", "Y"), ("Y", "-X"), ("Z", "Z")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["ROTATION"],
    "target": "TWEAK_hand_r",
    "source": "hand_r",
    "axis": [("X", "-Z"), ("Y", "-X"), ("Z", "Y")],
    "expression": "({var}) + {offset}"
}]

mixamoBoneMaps = [{
    # enum["LOCATION", "ROTATION", "SCALE"]
    "copy": ["LOCATION"],
    "target": "root",
    "source": "mixamorig:Hips",
    # axis format (target: enum("X", "Y", "Z"), source: enum("X", "Y", "Z", "-X", "-Y", "-Z"))
    "axis": [("X", "X"), ("Y", "-Z")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION"],
    "target": "TWEAK_pelvis",
    "source": "mixamorig:Hips",
    "axis": [("Y", "Y")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["ROTATION"],
    "target": "TWEAK_pelvis",
    "source": "mixamorig:Hips",
    "axis": [("X", "X"), ("Y", "Y"), ("Z", "Z")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["ROTATION"],
    "target": "TWEAK_spine_01",
    "source": "mixamorig:Spine",
    "axis": [("X", "X"), ("Y", "Y"), ("Z", "Z")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["ROTATION"],
    "target": "TWEAK_spine_02",
    "source": "mixamorig:Spine1",
    "axis": [("X", "X"), ("Y", "Y"), ("Z", "Z")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["ROTATION"],
    "target": "TWEAK_spine_03",
    "source": "mixamorig:Spine2",
    "axis": [("X", "X"), ("Y", "Y"), ("Z", "Z")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["ROTATION"],
    "target": "TWEAK_neck_01",
    "source": "mixamorig:Neck",
    "axis": [("X", "X"), ("Y", "Y"), ("Z", "Z")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["ROTATION"],
    "target": "TWEAK_head",
    "source": "mixamorig:Head",
    "axis": [("X", "X"), ("Y", "Y"), ("Z", "Z")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "FK_thigh_l",
    "source": "mixamorig:LeftUpLeg",
    "axis": [("X", "Z"), ("Y", "-Y"), ("Z", "X")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "FK_calf_l",
    "source": "mixamorig:LeftLeg",
    "axis": [("X", "Z"), ("Y", "-Y"), ("Z", "X")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "TWEAK_foot_l",
    "source": "mixamorig:LeftFoot",
    "axis": [("X", "-X"), ("Y", "Z"), ("Z", "Y")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "CONTROL_ball_l",
    "source": "mixamorig:LeftToeBase",
    "axis": [("X", "-X"), ("Y", "Z"), ("Z", "Y")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "FK_thigh_r",
    "source": "mixamorig:RightUpLeg",
    "axis": [("X", "-Z"), ("Y", "-Y"), ("Z", "-X")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "FK_calf_r",
    "source": "mixamorig:RightLeg",
    "axis": [("X", "-Z"), ("Y", "-Y"), ("Z", "-X")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "TWEAK_foot_r",
    "source": "mixamorig:RightFoot",
    "axis": [("X", "-X"), ("Y", "Z"), ("Z", "Y")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "CONTROL_ball_r",
    "source": "mixamorig:RightToeBase",
    "axis": [("X", "-X"), ("Y", "Z"), ("Z", "Y")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "TWEAK_clavicle_l",
    "source": "mixamorig:LeftShoulder",
    "axis": [("X", "-Z"), ("Y", "X"), ("Z", "-Y")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "FK_upperarm_l",
    "source": "mixamorig:LeftArm",
    "axis": [("X", "-Z"), ("Y", "X"), ("Z", "-Y")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "FK_lowerarm_l",
    "source": "mixamorig:LeftForeArm",
    "axis": [("X", "-Z"), ("Y", "X"), ("Z", "-Y")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "TWEAK_hand_l",
    "source": "mixamorig:LeftHand",
    "axis": [("X", "Z"), ("Y", "X"), ("Z", "Y")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "TWEAK_clavicle_r",
    "source": "mixamorig:RightShoulder",
    "axis": [("X", "Z"), ("Y", "-X"), ("Z", "-Y")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "FK_upperarm_r",
    "source": "mixamorig:RightArm",
    "axis": [("X", "Z"), ("Y", "-X"), ("Z", "-Y")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "FK_lowerarm_r",
    "source": "mixamorig:RightForeArm",
    "axis": [("X", "Z"), ("Y", "-X"), ("Z", "-Y")],
    "expression": "({var}) + {offset}"
},{
    "copy": ["LOCATION", "ROTATION"],
    "target": "TWEAK_hand_r",
    "source": "mixamorig:RightHand",
    "axis": [("X", "-Z"), ("Y", "-X"), ("Z", "Y")],
    "expression": "({var}) + {offset}"
}]

copyMaps = {
    "LOCATION": "location",
    "ROTATION": "rotation_euler",
    "SCALE": "scale"
}
transformTypeMaps = {
    "LOCATION": "LOC_",
    "ROTATION": "ROT_",
    "SCALE": "SCALE_"
}
axisMaps = {
    "X": 0,
    "Y": 1,
    "Z": 2
}

# PROPS

Props = [
    {
        "type": "scene",
        "name": "HasBindMannequin",
        "value": BoolProperty(
            default=False
            ),
        "resetVariable": False
    },
    {
        "type": "scene",
        "name": "RetargetMannequinSource",
        "value": PointerProperty(
            name="Source",
            description="Armature Source (Must Be Mannequin Armature)",
            type=bpy.types.Object,
            poll=lambda self, obj: obj.type == "ARMATURE" and not obj.get("UE4RIGGED", False)
            ),
        "resetVariable": False
    },
    {
        "type": "scene",
        "name": "RetargetMannequinTarget",
        "value": PointerProperty(
            name="Target",
            description="Armature Source (Must Be UE4Workspace Rig Armature)",
            type=bpy.types.Object,
            poll=lambda self, obj: obj.type == "ARMATURE" and obj.get("UE4RIGGED", False) and obj.get("UE4RIGTYPE") == "HUMANOID"
        ),
        "resetVariable": False
    },
    {
        "type": "scene",
        "name": "HasBindMixamo",
        "value": BoolProperty(
            default=False
            ),
        "resetVariable": False
    },
    {
        "type": "scene",
        "name": "RetargetMixamoSource",
        "value": PointerProperty(
            name="Source",
            description="Armature Source (Must Be Mixamo Armature)",
            type=bpy.types.Object,
            poll=lambda self, obj: obj.type == "ARMATURE" and not obj.get("UE4RIGGED", False)
            ),
        "resetVariable": False
    },
    {
        "type": "scene",
        "name": "RetargetMixamoTarget",
        "value": PointerProperty(
            name="Target",
            description="Armature Source (Must Be UE4Workspace Rig Armature)",
            type=bpy.types.Object,
            poll=lambda self, obj: obj.type == "ARMATURE" and obj.get("UE4RIGGED", False) and obj.get("UE4RIGTYPE") == "HUMANOID"
        ),
        "resetVariable": False
    }
]

# PANEL

class PANEL_RetargetMannequin(Panel):
    bl_idname = "UE4WORKSPACE_PT_RetargetMannequinPanel"
    bl_label = "Retarget Mannequin"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        preferences = context.preferences.addons[__package__].preferences
        return preferences.experimentalFeatures and context.mode == "OBJECT"

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.enabled = not context.scene.HasBindMannequin
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Source")
        split = split.split()
        col = split.column()
        col.prop(context.scene, "RetargetMannequinSource", text="", icon="OUTLINER_OB_ARMATURE")

        col = layout.column()
        col.enabled = not context.scene.HasBindMannequin
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Target")
        split = split.split()
        col = split.column()
        col.prop(context.scene, "RetargetMannequinTarget", text="", icon="OUTLINER_OB_ARMATURE")

        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("ue4workspace.bindarmaturemannequin",icon="MOD_MIRROR", text=("BIND", "UNBIND")[context.scene.HasBindMannequin])

        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("ue4workspace.bakeactionmannequin",icon="RENDER_ANIMATION", text="BAKE ACTION")

class PANEL_RetargetMixamo(Panel):
    bl_idname = "UE4WORKSPACE_PT_RetargetMixamoPanel"
    bl_label = "Retarget Mixamo"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        preferences = context.preferences.addons[__package__].preferences
        return preferences.experimentalFeatures and context.mode == "OBJECT"

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.enabled = not context.scene.HasBindMixamo
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Source")
        split = split.split()
        col = split.column()
        col.prop(context.scene, "RetargetMixamoSource", text="", icon="OUTLINER_OB_ARMATURE")

        col = layout.column()
        col.enabled = not context.scene.HasBindMixamo
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Target")
        split = split.split()
        col = split.column()
        col.prop(context.scene, "RetargetMixamoTarget", text="", icon="OUTLINER_OB_ARMATURE")

        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("ue4workspace.bindarmaturemixamo",icon="MOD_MIRROR", text=("BIND", "UNBIND")[context.scene.HasBindMixamo])

        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("ue4workspace.bakeactionmixamo",icon="RENDER_ANIMATION", text="BAKE ACTION")

#  OPERATOR

class OP_BindArmatureMannequin(Operator):
    bl_idname = "ue4workspace.bindarmaturemannequin"
    bl_label = "Bind/Unbind Armature Mannequin"
    bl_description = "Bind/Unbind Armature"
    bl_options = {"UNDO"}

    @classmethod
    def poll(self, context):
        return (context.scene.RetargetMannequinSource is not None and context.scene.RetargetMannequinTarget is not None)

    def execute(self, context):
        targetObj = context.scene.RetargetMannequinTarget
        sourceObj = context.scene.RetargetMannequinSource
        boneMaps = mannequinBoneMaps
        bpy.ops.object.select_all(action="DESELECT")
        context.view_layer.objects.active = targetObj
        bpy.ops.object.mode_set(mode="POSE")
        poseBones = targetObj.pose.bones

        # unbind
        if context.scene.HasBindMannequin:
            # add remove parent constraint on control bone and pole bone
            for controlBone, poleBone, fkBone  in [("CONTROL_hand_l", "IKPOLE_upperarm_l", "FK_lowerarm_l"), ("CONTROL_hand_r", "IKPOLE_upperarm_r", "FK_lowerarm_r"), ("CONTROL_foot_l", "IKPOLE_thigh_l", "FK_calf_l"), ("CONTROL_foot_r", "IKPOLE_thigh_r", "FK_calf_r")]:
                for boneName in [controlBone, poleBone]:
                    bone = poseBones.get(boneName)
                    constraint = bone.constraints.get("RETARGET_PARENT")
                    bone.constraints.remove(constraint)

            # remove driver
            for boneMap in boneMaps:
                poseBone = poseBones.get(boneMap["target"])
                # change rotation mode to QUATERNION
                poseBone.rotation_mode = "QUATERNION"
                for copyType in boneMap["copy"]:
                    poseBone.driver_remove(copyMaps.get(copyType))

            # clear transform
            bpy.ops.pose.select_all(action="SELECT")
            bpy.ops.pose.rot_clear()
            bpy.ops.pose.loc_clear()
            bpy.ops.pose.scale_clear()
            bpy.ops.pose.select_all(action="DESELECT")

        # bind
        else:
            # snap FK bone to TWEAK bone
            for boneName in ["FK_thigh_l", "FK_thigh_r", "FK_calf_l", "FK_calf_r", "FK_upperarm_l", "FK_upperarm_r", "FK_lowerarm_l", "FK_lowerarm_r"]:
                bone = poseBones.get(boneName)
                tweakBone = poseBones.get(boneName.replace("FK_", "TWEAK_"))
                bpy.ops.pose.visual_transform_apply()
                bone.matrix = tweakBone.matrix

            # switch to fk
            # for ikControl in ["CR_IK_foot_l", "CR_IK_foot_r", "CR_IK_hand_l", "CR_IK_hand_r"]:
            #     targetObj[ikControl] = 0.0

            # add parent constraint on control bone and pole to fk bone
            for controlBone, poleBone, fkBone  in [("CONTROL_hand_l", "IKPOLE_upperarm_l", "FK_lowerarm_l"), ("CONTROL_hand_r", "IKPOLE_upperarm_r", "FK_lowerarm_r"), ("CONTROL_foot_l", "IKPOLE_thigh_l", "FK_calf_l"), ("CONTROL_foot_r", "IKPOLE_thigh_r", "FK_calf_r")]:
                for boneName in [controlBone, poleBone]:
                    bone = poseBones.get(boneName)
                    constraint = bone.constraints.new("CHILD_OF")
                    constraint.name = "RETARGET_PARENT"
                    constraint.show_expanded = False
                    constraint.target = targetObj
                    constraint.subtarget = fkBone
                    # set inverse
                    context_copy = bpy.context.copy()
                    context_copy["constraint"] = constraint
                    targetObj.data.bones.active = bone.bone
                    bpy.ops.constraint.childof_set_inverse(context_copy, constraint=constraint.name, owner="BONE")

            # maping
            for boneMap in boneMaps:
                poseBone = poseBones.get(boneMap["target"])
                # change rotation mode to XYZ
                poseBone.rotation_mode = "XYZ"
                for copyType in boneMap["copy"]:
                    for target, source in boneMap["axis"]:
                        isInverse = source.startswith("-")
                        source = source.replace("-", "")
                        offset = getattr(poseBone, copyMaps.get(copyType))[axisMaps.get(target)]

                        driver = poseBone.driver_add(copyMaps.get(copyType), axisMaps.get(target)).driver
                        driver.type = "SCRIPTED"

                        var = driver.variables.new()
                        var.type = "TRANSFORMS"
                        varTarget = var.targets[0]
                        varTarget.id = sourceObj
                        varTarget.bone_target = boneMap["source"]
                        varTarget.transform_type = transformTypeMaps.get(copyType) + source
                        varTarget.rotation_mode = "AUTO"
                        varTarget.transform_space = "LOCAL_SPACE"

                        varName = "-" + var.name if isInverse else var.name
                        driver.expression = boneMap["expression"].format(var=varName, offset=offset)

        bpy.ops.object.mode_set(mode="OBJECT")
        context.scene.HasBindMannequin = not context.scene.HasBindMannequin
        return {"FINISHED"}

class OP_BakeActionMannequin(Operator):
    bl_idname = "ue4workspace.bakeactionmannequin"
    bl_label = "Bake Action Mannequin"
    bl_description = "Bake Action Mannequin"
    bl_options = {"UNDO"}

    actionName: StringProperty(default="BakeAction")
    startFrame: IntProperty(default=1)
    endFrame: IntProperty(default=250)
    frameStep: IntProperty(default=1)

    @classmethod
    def poll(self, context):
        return context.scene.HasBindMannequin

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
        targetObj = context.scene.RetargetMannequinTarget
        sourceObj = context.scene.RetargetMannequinSource
        boneMaps = mannequinBoneMaps
        controlBones = ["CONTROL_hand_l", "IKPOLE_upperarm_l", "CONTROL_hand_r", "IKPOLE_upperarm_r", "CONTROL_foot_l", "IKPOLE_thigh_l", "CONTROL_foot_r", "IKPOLE_thigh_r"]
        bpy.ops.object.select_all(action="DESELECT")
        targetObj.select_set(True)
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
        # control bone matrix to keyframe, because using child of constraint does not get local transform
        # format (boneName: str, matrix: Matrix, frame: int)
        controlBoneMatrixs = []
        # bake animation manually because bake action operator in python is very buggy and give me more control
        frame = self.startFrame
        while frame <= self.endFrame:
            context.scene.frame_set(frame)
            # bake bone base on bone map list
            for boneMap in boneMaps:
                poseBone = poseBones.get(boneMap["target"])
                for copyType in boneMap["copy"]:
                    # insert keyframe base on copy target
                    poseBone.keyframe_insert(copyMaps.get(copyType))
                    if copyType == "ROTATION":
                        # insert keyframe to quaternion rotation
                        # convert euler to rotation so you can use two mode rotation
                        poseBone.rotation_quaternion = poseBone.rotation_euler.to_quaternion()
                        poseBone.keyframe_insert("rotation_quaternion")

            # get matrix control bone
            for boneName in controlBones:
                poseBone = poseBones.get(boneName)
                boneMatrix = poseBone.matrix.copy()
                controlBoneMatrixs.append((boneName, boneMatrix, frame))

            frame += self.frameStep

        # mute child_of constraint
        for boneName in controlBones:
            poseBone = poseBones.get(boneName)
            constraint = poseBone.constraints.get("RETARGET_PARENT")
            constraint.mute = True

        # insert control bone keyframe matrix
        for boneName, matrix, frame in controlBoneMatrixs:
            poseBone = poseBones.get(boneName)
            poseBone.matrix = matrix
            poseBone.keyframe_insert("location", frame=frame)
            poseBone.keyframe_insert("rotation_quaternion", frame=frame)
            poseBone.keyframe_insert("rotation_euler", frame=frame)

        # unmute child_of constraint
        for boneName in controlBones:
            poseBone = poseBones.get(boneName)
            constraint = poseBone.constraints.get("RETARGET_PARENT")
            constraint.mute = False

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

        bpy.ops.object.mode_set(mode="OBJECT")
        return {"FINISHED"}

class OP_BindArmatureMixamo(Operator):
    bl_idname = "ue4workspace.bindarmaturemixamo"
    bl_label = "Bind/Unbind Armature Mannequin"
    bl_description = "Bind/Unbind Armature"
    bl_options = {"UNDO"}

    @classmethod
    def poll(self, context):
        return (context.scene.RetargetMixamoSource is not None and context.scene.RetargetMixamoTarget is not None)

    def execute(self, context):
        targetObj = context.scene.RetargetMixamoTarget
        sourceObj = context.scene.RetargetMixamoSource
        boneMaps = mixamoBoneMaps
        bpy.ops.object.select_all(action="DESELECT")
        context.view_layer.objects.active = targetObj
        bpy.ops.object.mode_set(mode="POSE")
        poseBones = targetObj.pose.bones

        # unbind
        if context.scene.HasBindMixamo:
            # add remove parent constraint on control bone and pole bone
            for controlBone, poleBone, fkBone  in [("CONTROL_hand_l", "IKPOLE_upperarm_l", "FK_lowerarm_l"), ("CONTROL_hand_r", "IKPOLE_upperarm_r", "FK_lowerarm_r"), ("CONTROL_foot_l", "IKPOLE_thigh_l", "FK_calf_l"), ("CONTROL_foot_r", "IKPOLE_thigh_r", "FK_calf_r")]:
                for boneName in [controlBone, poleBone]:
                    bone = poseBones.get(boneName)
                    constraint = bone.constraints.get("RETARGET_PARENT")
                    bone.constraints.remove(constraint)

            # remove driver
            for boneMap in boneMaps:
                poseBone = poseBones.get(boneMap["target"])
                # change rotation mode to QUATERNION
                poseBone.rotation_mode = "QUATERNION"
                for copyType in boneMap["copy"]:
                    poseBone.driver_remove(copyMaps.get(copyType))

            # clear transform
            bpy.ops.pose.select_all(action="SELECT")
            bpy.ops.pose.rot_clear()
            bpy.ops.pose.loc_clear()
            bpy.ops.pose.scale_clear()
            bpy.ops.pose.select_all(action="DESELECT")

        # bind
        else:
            # snap FK bone to TWEAK bone
            for boneName in ["FK_thigh_l", "FK_thigh_r", "FK_calf_l", "FK_calf_r", "FK_upperarm_l", "FK_upperarm_r", "FK_lowerarm_l", "FK_lowerarm_r"]:
                bone = poseBones.get(boneName)
                tweakBone = poseBones.get(boneName.replace("FK_", "TWEAK_"))
                bpy.ops.pose.visual_transform_apply()
                bone.matrix = tweakBone.matrix

            # switch to fk
            # for ikControl in ["CR_IK_foot_l", "CR_IK_foot_r", "CR_IK_hand_l", "CR_IK_hand_r"]:
            #     targetObj[ikControl] = 0.0

            # add parent constraint on control bone and pole to fk bone
            for controlBone, poleBone, fkBone  in [("CONTROL_hand_l", "IKPOLE_upperarm_l", "FK_lowerarm_l"), ("CONTROL_hand_r", "IKPOLE_upperarm_r", "FK_lowerarm_r"), ("CONTROL_foot_l", "IKPOLE_thigh_l", "FK_calf_l"), ("CONTROL_foot_r", "IKPOLE_thigh_r", "FK_calf_r")]:
                for boneName in [controlBone, poleBone]:
                    bone = poseBones.get(boneName)
                    constraint = bone.constraints.new("CHILD_OF")
                    constraint.name = "RETARGET_PARENT"
                    constraint.show_expanded = False
                    constraint.target = targetObj
                    constraint.subtarget = fkBone
                    # set inverse
                    context_copy = bpy.context.copy()
                    context_copy["constraint"] = constraint
                    targetObj.data.bones.active = bone.bone
                    bpy.ops.constraint.childof_set_inverse(context_copy, constraint=constraint.name, owner="BONE")

            # maping
            for boneMap in boneMaps:
                poseBone = poseBones.get(boneMap["target"])
                # change rotation mode to XYZ
                poseBone.rotation_mode = "XYZ"
                for copyType in boneMap["copy"]:
                    for target, source in boneMap["axis"]:
                        isInverse = source.startswith("-")
                        source = source.replace("-", "")
                        offset = getattr(poseBone, copyMaps.get(copyType))[axisMaps.get(target)]

                        driver = poseBone.driver_add(copyMaps.get(copyType), axisMaps.get(target)).driver
                        driver.type = "SCRIPTED"

                        var = driver.variables.new()
                        var.type = "TRANSFORMS"
                        varTarget = var.targets[0]
                        varTarget.id = sourceObj
                        varTarget.bone_target = boneMap["source"]
                        varTarget.transform_type = transformTypeMaps.get(copyType) + source
                        varTarget.rotation_mode = "AUTO"
                        varTarget.transform_space = "LOCAL_SPACE"

                        varName = "-" + var.name if isInverse else var.name
                        driver.expression = boneMap["expression"].format(var=varName, offset=offset)

        bpy.ops.object.mode_set(mode="OBJECT")
        context.scene.HasBindMixamo = not context.scene.HasBindMixamo
        return {"FINISHED"}

class OP_BakeActionMixamo(Operator):
    bl_idname = "ue4workspace.bakeactionmixamo"
    bl_label = "Bake Action Mixamo"
    bl_description = "Bake Action Mixamo"
    bl_options = {"UNDO"}

    actionName: StringProperty(default="BakeAction")
    startFrame: IntProperty(default=1)
    endFrame: IntProperty(default=250)
    frameStep: IntProperty(default=1)

    @classmethod
    def poll(self, context):
        return context.scene.HasBindMixamo

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
        targetObj = context.scene.RetargetMixamoTarget
        sourceObj = context.scene.RetargetMixamoSource
        boneMaps = mixamoBoneMaps
        controlBones = ["CONTROL_hand_l", "IKPOLE_upperarm_l", "CONTROL_hand_r", "IKPOLE_upperarm_r", "CONTROL_foot_l", "IKPOLE_thigh_l", "CONTROL_foot_r", "IKPOLE_thigh_r"]
        bpy.ops.object.select_all(action="DESELECT")
        targetObj.select_set(True)
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
        # control bone matrix to keyframe, because using child of constraint does not get local transform
        # format (boneName: str, matrix: Matrix, frame: int)
        controlBoneMatrixs = []
        # bake animation manually because bake action operator in python is very buggy and give me more control
        frame = self.startFrame
        while frame <= self.endFrame:
            context.scene.frame_set(frame)
            # bake bone base on bone map list
            for boneMap in boneMaps:
                poseBone = poseBones.get(boneMap["target"])
                for copyType in boneMap["copy"]:
                    # insert keyframe base on copy target
                    poseBone.keyframe_insert(copyMaps.get(copyType))
                    if copyType == "ROTATION":
                        # insert keyframe to quaternion rotation
                        # convert euler to rotation so you can use two mode rotation
                        poseBone.rotation_quaternion = poseBone.rotation_euler.to_quaternion()
                        poseBone.keyframe_insert("rotation_quaternion")

            # get matrix control bone
            for boneName in controlBones:
                poseBone = poseBones.get(boneName)
                boneMatrix = poseBone.matrix.copy()
                controlBoneMatrixs.append((boneName, boneMatrix, frame))

            frame += self.frameStep

        # mute child_of constraint
        for boneName in controlBones:
            poseBone = poseBones.get(boneName)
            constraint = poseBone.constraints.get("RETARGET_PARENT")
            constraint.mute = True

        # insert control bone keyframe matrix
        for boneName, matrix, frame in controlBoneMatrixs:
            poseBone = poseBones.get(boneName)
            poseBone.matrix = matrix
            poseBone.keyframe_insert("location", frame=frame)
            poseBone.keyframe_insert("rotation_quaternion", frame=frame)
            poseBone.keyframe_insert("rotation_euler", frame=frame)

        # unmute child_of constraint
        for boneName in controlBones:
            poseBone = poseBones.get(boneName)
            constraint = poseBone.constraints.get("RETARGET_PARENT")
            constraint.mute = False

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

        bpy.ops.object.mode_set(mode="OBJECT")
        return {"FINISHED"}

# operator export

Ops = [
    OP_BindArmatureMannequin,
    OP_BakeActionMannequin,
    OP_BindArmatureMixamo,
    OP_BakeActionMixamo
]