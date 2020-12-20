import bpy
import math
from mathutils import (Matrix, Vector)
from bpy.props import (EnumProperty, StringProperty, PointerProperty)
from bpy.types import (Panel, Operator)

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_ObjectControlRigPanel"
    bl_parent_id = "UE4WORKSPACE_PT_ObjectPanel"
    bl_label = "Control Rig"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        return context.mode == "POSE" and context.active_object is not None and context.active_object.data.UE4RIGGED

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object
        activeBone = context.active_pose_bone

        poseBones = activeObject.pose.bones

        row = layout.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Hide FK Bone")
        col.label(text="Hide Vis Bone")
        col = split.column()
        col.prop(activeObject.data, "hideFK", text="")
        col.prop(activeObject.data, "hideVis", text="")

        if activeBone is not None:
            # ik bone
            if activeBone.bone.controlIK:
                row = layout.row(align=True)
                row.scale_y = 1.2
                row.operator("ue4workspace.snapfktoik",icon="SNAP_ON", text="Snap FK>IK")
                row.operator("ue4workspace.snapiktofk",icon="SNAP_ON", text="Snap IK>FK")
                row = layout.row()
                row.prop(activeBone.bone, "switchIK", expand=True)
                if preferences.experimentalFeatures:
                    row = layout.row()
                    row.prop(activeBone.bone, "stretchBone", slider=True)
                    layout.label(text="Stretch Volume")
                    row = layout.row()
                    row.prop(activeBone.bone, "stretchBoneMode", expand=True)

            # ik finger bone
            if activeBone.bone.controlFingerIK:
                row = layout.row()
                row.prop(activeBone.bone, "switchIK", expand=True)

            if activeBone.bone.UE4RIGTYPE == "SPINE":
                if preferences.experimentalFeatures:
                    row = layout.row()
                    row.prop(activeBone.bone, "stretchBone", slider=True)
                    layout.label(text="Stretch Volume")
                    row = layout.row()
                    row.prop(activeBone.bone, "stretchBoneMode", expand=True)

# OPERATOR

class OP_SnapFKtoIK(Operator):
    bl_idname = "ue4workspace.snapfktoik"
    bl_label = "Snap FK to IK"
    bl_description = "Snap FK to IK"
    bl_options = {"UNDO"}

    @classmethod
    def poll(self, context):
        return context.active_object is not None and context.mode == "POSE" and context.active_pose_bone

    def execute(self, context):
        activeObject = context.active_object
        activeBone = context.active_pose_bone
        poseBones = activeObject.pose.bones

        for boneName in [activeBone.bone.pointABoneIK, activeBone.bone.pointBBoneIK]:
            tweakBone = poseBones.get("STRETCH_" + boneName)
            bone = poseBones.get("FK_" + boneName)
            bpy.ops.pose.visual_transform_apply()
            bone.matrix = tweakBone.matrix
        fkControl = poseBones.get("FK_" + activeBone.name.replace("CONTROL_", ""))
        if fkControl and fkControl.name != "FK_" + activeBone.bone.pointBBoneIK:
            bpy.ops.pose.visual_transform_apply()
            fkControl.matrix = activeBone.matrix
            bpy.ops.pose.visual_transform_apply()
        return {"FINISHED"}

class OP_SnapIKtoFK(Operator):
    bl_idname = "ue4workspace.snapiktofk"
    bl_label = "Snap IK to FK"
    bl_description = "Snap IK to FK"
    bl_options = {"UNDO"}

    @classmethod
    def poll(self, context):
        return context.active_object is not None and context.mode == "POSE" and context.active_pose_bone

    # script from rigify
    def rotation_difference(self, mat1, mat2):
        """ Returns the shortest-path rotational difference between two
            matrices.
        """
        q1 = mat1.to_quaternion()
        q2 = mat2.to_quaternion()
        angle = math.acos(min(1,max(-1,q1.dot(q2)))) * 2
        if angle > math.pi:
            angle = -angle + (2*math.pi)
        return angle

    def execute(self, context):
        activeObject = context.active_object
        activeBone = context.active_pose_bone
        poseBones = activeObject.pose.bones

        boneFKA = poseBones.get("FK_" + activeBone.bone.pointABoneIK)
        boneFKB = poseBones.get("FK_" + activeBone.bone.pointBBoneIK)
        boneIKA = poseBones.get("IK_" + activeBone.bone.pointABoneIK)
        boneIKB = poseBones.get("IK_" + activeBone.bone.pointBBoneIK)
        poleBone = poseBones.get("IKPOLE_" + activeBone.bone.pointABoneIK)
        fkControl = poseBones.get("FK_" + activeBone.name.replace("CONTROL_", ""))

        matchMatrix = activeObject.convert_space(pose_bone=boneFKA, matrix=boneFKA.matrix, from_space="POSE", to_space="POSE")

        bpy.ops.pose.visual_transform_apply()

        activeBone.matrix = fkControl.matrix if fkControl is not None and fkControl.name != "FK_" + activeBone.bone.pointBBoneIK else Matrix.Translation(boneFKB.tail) @ (activeBone.matrix.to_quaternion().to_matrix().to_4x4() @ Matrix.Scale(1, 4, activeBone.matrix.to_scale()))

        bpy.ops.pose.visual_transform_apply()

        vIK = (boneIKB.matrix.to_translation() + boneIKB.vector) - boneIKA.matrix.to_translation()

        vPerpendicular = vIK.cross(Vector((1,0,0)) if abs(vIK[0]) < abs(vIK[1]) else Vector((0,1,0))).normalized() * (boneIKA.length + boneIKB.length)

        def setPole(vP):
            pLoc = boneIKA.matrix.to_translation() + (vIK/2) + vP
            poleBone.location = poleBone.id_data.convert_space(matrix=Matrix.Translation(pLoc), pose_bone=poleBone, from_space="POSE", to_space="LOCAL").to_translation()
            bpy.ops.pose.visual_transform_apply()

        setPole(vPerpendicular)

        angle = self.rotation_difference(boneIKA.matrix, matchMatrix)

        vPerpendicular1 = Matrix.Rotation(angle, 4, vIK) @ vPerpendicular
        setPole(vPerpendicular1)
        ang1 = self.rotation_difference(boneIKA.matrix, matchMatrix)

        vPerpendicular2 = Matrix.Rotation(-angle, 4, vIK) @ vPerpendicular
        setPole(vPerpendicular2)
        ang2 = self.rotation_difference(boneIKA.matrix, matchMatrix)

        if ang1 < ang2:
            setPole(vPerpendicular1)

        return {"FINISHED"}

# operator export

Ops = [
    OP_SnapFKtoIK,
    OP_SnapIKtoFK
]