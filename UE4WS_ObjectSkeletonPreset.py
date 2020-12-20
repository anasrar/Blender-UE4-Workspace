import os
import bpy
from mathutils import (Matrix, Quaternion, Vector)
from bpy.props import (EnumProperty, BoolProperty, IntProperty, StringProperty, PointerProperty)
from bpy.types import (Panel, Operator)

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_ObjectSkeletonPresetPanel"
    bl_parent_id = "UE4WORKSPACE_PT_ObjectPanel"
    bl_label = "Skeleton Preset"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        return context.active_object is not None and context.active_object.type == "ARMATURE" and context.active_object.data.UE4RIG

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object
        activePoseBone = context.active_pose_bone

        layout.label(text="RIG")
        row = layout.row()
        row.scale_y = 1.5
        # operator location on UE4WS_Character.py
        row.operator("ue4workspace.generaterig",icon="CON_ARMATURE", text="Generate Rig")
        row = layout.row()
        row.scale_y = 1.5
        # operator location on UE4WS_Character.py
        row.operator("ue4workspace.rotatebone",icon="BONE_DATA", text=("Create Preview Orient Bone", "Update Preview Orient Bone")[activeObject.get("UE4RIGHASTEMPBONE", False)])

        row = layout.row()
        row.scale_y = 1.5
        # operator location on UE4WS_Character.py
        row.operator("ue4workspace.characterremovetemporarybone",icon="BONE_DATA", text="Remove Preview Orient Bone")

        layout.label(text="TWIST BONE")
        # add twist bone
        row = layout.row(align=True)
        row.scale_y = 1.5
        # operator location on UE4WS_Character.py
        row.operator("ue4workspace.addtwistbone", text="Add Twist")
        # operator location on UE4WS_Character.py
        row.operator("ue4workspace.removetwistbone", text="Remove Twist")

        layout.label(text="POSE")
        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("ue4workspace.posetoapose", text="Pose to A-Pose")
        row.operator("ue4workspace.applypose", text="Apply Pose")

        layout.label(text="COMPONENT TO ADD")
        col = layout.column(align=True)
        col.scale_y = 1.5
        row = col.row(align=True)
        row.operator("ue4workspace.bonecomponentcopy", text="COPY_BONE")
        row = col.row(align=True)
        row.operator("ue4workspace.bonecomponenteyelid", text="EYELID_UPPER").eyelidPosition = ("U")
        row.operator("ue4workspace.bonecomponenteyelid", text="EYELID_LOWER").eyelidPosition = ("L")
        row = col.row(align=True)
        row.operator("ue4workspace.bonecomponenteye", text="EYE")
        row = col.row(align=True)
        row.operator("ue4workspace.bonecomponentlandmark", text="LANDMARK")
        row.operator("ue4workspace.bonecomponentjaw", text="JAW")
        row = col.row(align=True)
        row.operator("ue4workspace.bonecomponentfaceattach", text="FACE_ATTACH")
        row = col.row(align=True)
        row.operator("ue4workspace.bonecomponenthead", text="HEAD")
        row = col.row(align=True)
        row.operator("ue4workspace.bonecomponentneck", text="NECK")
        row = col.row(align=True)
        row.operator("ue4workspace.bonecomponentarmhuman", text="ARM_HUMAN")
        row.operator("ue4workspace.bonecomponentfinger", text="FINGER")
        row = col.row(align=True)
        row.operator("ue4workspace.bonecomponentspine", text="SPINE")
        row = col.row(align=True)
        row.operator("ue4workspace.bonecomponentpelvis", text="PELVIS")
        row = col.row(align=True)
        row.operator("ue4workspace.bonecomponentleghuman", text="LEG_HUMAN")
        row = col.row(align=True)
        row.operator("ue4workspace.rotatebone", text="TAIL")
        row.operator("ue4workspace.bonecomponentchain", text="CHAIN")
        row = col.row(align=True)
        row.operator("ue4workspace.rotatebone", text="PROP")

# bone rotation (Quaternion)
APoseBoneRotation = {
    "pelvis": (0.6774330139160156, 0.7355844974517822, 0.0, -8.834048514927417e-08),
    "spine_01": (0.7314896583557129, 0.6818525791168213, -2.4284102137348993e-15, -7.973857663046147e-08),
    "spine_02": (0.7575458288192749, 0.6527820229530334, -2.3448836595314423e-15, -7.835525650534692e-08),
    "spine_03": (0.7561419606208801, 0.654407799243927, 2.349237832396803e-15, -8.093304160183834e-08),
    "neck_01": (0.6307977437973022, 0.7759473919868469, -1.1264193110161955e-14, -9.32003061393516e-08),
    "head": (0.7071068286895752, 0.7071068286895752, -1.821307353251731e-14, 0.0),
    "clavicle_l": (0.04727831482887268, -0.5242606401443481, -0.8473084568977356, 0.07059772312641144),
    "upperarm_l": (0.33164140582084656, -0.6278275847434998, -0.6528890132904053, 0.2637849748134613),
    "lowerarm_l": (0.12208843976259232, -0.7716752290725708, -0.5201354026794434, 0.3450668156147003),
    "hand_l": (0.48904913663864136, -0.25943198800086975, 0.19929619133472443, -0.8085833191871643),
    "thumb_01_l": (0.07611946761608124, -0.30184561014175415, -0.2840867340564728, 0.9068570733070374),
    "thumb_02_l": (0.11387968808412552, -0.2798141539096832, -0.42500805854797363, 0.8532899618148804),
    "thumb_03_l": (0.15496234595775604, -0.28445395827293396, -0.3283044695854187, 0.8872929215431213),
    "index_01_l": (0.39686378836631775, -0.262618750333786, 0.43310123682022095, -0.7654761672019958),
    "index_02_l": (0.3635122776031494, -0.2863125801086426, 0.5191501379013062, -0.7185868620872498),
    "index_03_l": (0.37079939246177673, -0.24763469398021698, 0.4614221453666687, -0.7669904828071594),
    "middle_01_l": (0.4633159637451172, -0.30906328558921814, 0.38876861333847046, -0.7339463829994202),
    "middle_02_l": (0.4404599666595459, -0.39435091614723206, 0.44046053290367126, -0.6756308078765869),
    "middle_03_l": (0.5031590461730957, -0.2988421320915222, 0.3704220652580261, -0.7213265895843506),
    "ring_01_l": (0.5472036004066467, -0.414227157831192, 0.3159283995628357, -0.6551132798194885),
    "ring_02_l": (0.49488329887390137, -0.4463731348514557, 0.4152567386627197, -0.619195818901062),
    "ring_03_l": (0.5284509062767029, -0.40227004885673523, 0.3283996880054474, -0.6716189384460449),
    "pinky_01_l": (0.6147031188011169, -0.39491501450538635, 0.2866409718990326, -0.6196928024291992),
    "pinky_02_l": (0.573142945766449, -0.43456700444221497, 0.3651326298713684, -0.5910473465919495),
    "pinky_03_l": (0.5492244362831116, -0.45223113894462585, 0.35505184531211853, -0.6064468026161194),
    "clavicle_r": (0.0472794808447361, -0.5242604613304138, 0.8473084568977356, -0.07059790194034576),
    "upperarm_r": (0.33164137601852417, -0.6278276443481445, 0.6528889536857605, -0.2637850344181061),
    "lowerarm_r": (0.12208835035562515, -0.7716752290725708, 0.5201353430747986, -0.3450668752193451),
    "hand_r": (0.4890492558479309, -0.25943201780319214, -0.19929620623588562, 0.8085833191871643),
    "thumb_01_r": (0.0761200487613678, -0.3018467426300049, 0.2840867340564728, -0.9068567156791687),
    "thumb_02_r": (0.11388018727302551, -0.27981463074684143, 0.4250081479549408, -0.8532896637916565),
    "thumb_03_r": (0.15496280789375305, -0.2844545245170593, 0.3283045291900635, -0.887292742729187),
    "index_01_r": (0.3968636989593506, -0.262618750333786, -0.43310144543647766, 0.7654762268066406),
    "index_02_r": (0.36351215839385986, -0.28631269931793213, -0.5191503167152405, 0.7185867428779602),
    "index_03_r": (0.37079930305480957, -0.24763473868370056, -0.46142229437828064, 0.7669904232025146),
    "middle_01_r": (0.46331602334976196, -0.30906325578689575, -0.38876861333847046, 0.7339462637901306),
    "middle_02_r": (0.4404599964618683, -0.39435088634490967, -0.4404605031013489, 0.6756307482719421),
    "middle_03_r": (0.5031589865684509, -0.29884207248687744, -0.3704220652580261, 0.7213265299797058),
    "ring_01_r": (0.5472036004066467, -0.41422712802886963, -0.31592845916748047, 0.6551132798194885),
    "ring_02_r": (0.4948832392692566, -0.4463730752468109, -0.4152568280696869, 0.6191956996917725),
    "ring_03_r": (0.5284509658813477, -0.40227004885673523, -0.32839974761009216, 0.6716188788414001),
    "pinky_01_r": (0.6147030591964722, -0.39491504430770874, -0.286641001701355, 0.6196928024291992),
    "pinky_02_r": (0.573142945766449, -0.43456703424453735, -0.3651326894760132, 0.5910472869873047),
    "pinky_03_r": (0.5492244362831116, -0.45223113894462585, -0.3550519049167633, 0.6064467430114746),
    "thigh_l": (0.5693971514701843, -0.49655330181121826, 0.43672093749046326, -0.48836109042167664),
    "calf_l": (0.566271185874939, -0.4513953626155853, 0.5072813630104065, -0.4671669602394104),
    "foot_l": (0.020697886124253273, 0.004743354860693216, 0.283678263425827, -0.9586843252182007),
    "ball_l": (-0.008751435205340385, 0.999891459941864, 0.011833819560706615, 0.0007140806410461664),
    "thigh_r": (0.5693917274475098, -0.4965547025203705, -0.43672415614128113, 0.48836320638656616),
    "calf_r": (0.5662640333175659, -0.4513973593711853, -0.507286548614502, 0.4671678841114044),
    "foot_r": (0.020876646041870117, 0.0044718775898218155, -0.2835838496685028, 0.9587096571922302),
    "ball_r": (-0.008750335313379765, 0.9998914003372192, -0.011838369071483612, -0.0007135455380193889)
}

class OP_PoseToAPose(Operator):
    bl_idname = "ue4workspace.posetoapose"
    bl_label = "Pose to A-Pose"
    bl_description = "Set Pose to A-Pose (Unreal Engine Mannequin)"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        activeObject = context.active_object
        return context.mode == "POSE" and activeObject is not None and activeObject.data.UE4RIG

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object

        poseBones = activeObject.pose.bones
        for boneName, rotation in APoseBoneRotation.items():
            poseBone = poseBones.get(boneName)
            if poseBone:
                oriMat = poseBone.matrix.copy()
                newMat = Quaternion(rotation).to_matrix().to_4x4()
                newMat.translation = oriMat.to_translation()
                poseBone.matrix = newMat
                bpy.ops.pose.visual_transform_apply()

        return {"FINISHED"}

class OP_ApplyPose(Operator):
    bl_idname = "ue4workspace.applypose"
    bl_label = "Apply Pose"
    bl_description = "Apply pose for as rest pose"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        activeObject = context.active_object
        return context.mode == "POSE" and activeObject is not None and activeObject.data.UE4RIG

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object

        bpy.ops.object.mode_set(mode="OBJECT")

        for childObj in [obj for obj in activeObject.children if obj.type == "MESH" and bool([mod.type for mod in obj.modifiers if mod.type == "ARMATURE" and mod.object == activeObject])]:
            context.view_layer.objects.active = childObj
            for modifier in [mod for mod in childObj.modifiers if mod.type == "ARMATURE" and mod.object == activeObject]:
                newModifier = childObj.modifiers.new("DUP_" + modifier.name, "ARMATURE")
                newModifier.show_expanded = modifier.show_expanded
                newModifier.show_in_editmode = modifier.show_in_editmode
                newModifier.show_on_cage = modifier.show_on_cage
                newModifier.show_render = modifier.show_render
                newModifier.show_viewport = modifier.show_viewport
                newModifier.use_apply_on_spline = modifier.use_apply_on_spline
                newModifier.invert_vertex_group = modifier.invert_vertex_group
                newModifier.object = activeObject
                newModifier.use_bone_envelopes = modifier.use_bone_envelopes
                newModifier.use_deform_preserve_volume = modifier.use_deform_preserve_volume
                newModifier.use_multi_modifier = modifier.use_multi_modifier
                newModifier.use_vertex_groups = modifier.use_vertex_groups
                newModifier.vertex_group = modifier.vertex_group
                bpy.ops.object.modifier_apply(modifier=modifier.name)
                newModifier.name = newModifier.name.replace("DUP_", "")

        context.view_layer.objects.active = activeObject
        bpy.ops.object.mode_set(mode="POSE")
        bpy.ops.pose.armature_apply(selected=False)

        return {"FINISHED"}

# base bone component

class OP_MixBoneComponent(Operator):
    bl_options = {"UNDO", "REGISTER"}

    @classmethod
    def poll(cls, context):
        activeObject = context.active_object
        activeBone = context.active_bone
        return context.mode == "EDIT_ARMATURE" and activeObject is not None and activeObject.data.UE4RIG

    def buildName(self, listString = []):
        string = []
        listString = [a for a in listString if a != ""]
        for name in listString:
            string.append(name)
        return "_".join(string)

class OP_MixFaceAttachComponent(OP_MixBoneComponent):
    @classmethod
    def poll(cls, context):
        activeObject = context.active_object
        activeBone = context.active_bone
        return context.mode == "EDIT_ARMATURE" and activeObject is not None and activeObject.data.UE4RIG and activeBone is not None and activeBone.get("UE4RIGTYPE") == "FACE_ATTACH"

class OP_MixEyeComponent(OP_MixFaceAttachComponent):
    @classmethod
    def poll(cls, context):
        activeObject = context.active_object
        activeBone = context.active_bone
        return context.mode == "EDIT_ARMATURE" and activeObject is not None and activeObject.data.UE4RIG and activeBone is not None and activeBone.get("UE4RIGTYPE") == "EYE"

class OP_BoneComponent_Copy(OP_MixBoneComponent):
    bl_idname = "ue4workspace.bonecomponentcopy"
    bl_label = "Add COPY_BONE"
    bl_description = "Add Copy Bone Component"

    boneName: StringProperty(
        name="Bone Name",
        default="bone"
    )

    prefixName: StringProperty(
        name="Prefix Name",
        default=""
    )

    suffixName: StringProperty(
        name="Suffix Name",
        default=""
    )

    sideBone: EnumProperty(
        name="Side Name",
        items=[
            ("NONE", "None", ""),
            ("l", "Left", ""),
            ("r", "Right", "")
        ],
        default=("NONE")
    )

    sideMirror: BoolProperty(
        name="Mirror Side",
        default=False
    )

    parentToBone: BoolProperty(
        name="Parent To Active Bone",
        default=False
    )

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object
        editBones = activeObject.data.edit_bones
        activeBone = context.active_bone

        boneData = {
            "NONE": (
                # roll
                0,
                # rotationRadian
                -1.5708,
                # orientAxis
                0,
                # orientRoll
                -1.5708
            ),
            "l": (
                # roll
                1.5708,
                # rotationRadian
                -1.5708,
                # orientAxis
                2,
                # orientRoll
                3.14159
                ),
            "r": (
                # roll
                -1.5708,
                # rotationRadian
                -1.5708,
                # orientAxis
                2,
                # orientRoll
                0.0
                )
        }

        newBone = editBones.new(self.buildName([self.prefixName, self.boneName, self.suffixName, (self.sideBone if self.sideBone != "NONE" else "")]))

        roll, rotRad, orientAxis, orientRoll = boneData[self.sideBone]

        newBone.head = context.scene.cursor.location
        newBone.tail = context.scene.cursor.location + Vector((0.0, 0.0, 0.15))
        newBone.roll = roll

        newBone["UE4RIGTYPE"] = "COPY_BONE"
        newBone["rotateBone"] = 1
        newBone["rotationRadian"] = rotRad
        newBone["orientAxis"] = orientAxis
        newBone["orientRoll"] = orientRoll

        newBone["customShape"] = 1
        newBone["customShapeType"] = 0
        newBone["customShapeParam"] = [10.0, 10.0, 0.0, 15.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        if self.parentToBone and activeBone:
            newBone.parent = activeBone

        editBones.active = newBone

        if self.sideMirror and self.sideBone != "NONE":
            newBoneSide = editBones.new(self.buildName([self.prefixName, self.boneName, self.suffixName, ("r" if self.sideBone == "l" else "l")]))

            roll, rotRad, orientAxis, orientRoll = boneData[("r" if self.sideBone == "l" else "l")]

            newBoneSide.head = newBone.head
            newBoneSide.head.x = -newBone.head.x
            newBoneSide.tail = newBone.tail
            newBoneSide.tail.x = -newBone.tail.x
            newBoneSide.roll = roll

            newBoneSide["UE4RIGTYPE"] = "COPY_BONE"
            newBoneSide["rotateBone"] = 1
            newBoneSide["rotationRadian"] = rotRad
            newBoneSide["orientAxis"] = orientAxis
            newBoneSide["orientRoll"] = orientRoll

            newBoneSide["customShape"] = 1
            newBoneSide["customShapeType"] = 0
            newBoneSide["customShapeParam"] = [10.0, 10.0, 0.0, 15.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

            if self.parentToBone and activeBone:
                parentSide = editBones.get(activeBone.name[:-1] + ("r" if self.sideBone == "l" else "l"))
                newBoneSide.parent = parentSide if parentSide else activeBone

        return {"FINISHED"}

class OP_BoneComponent_Pelvis(OP_MixBoneComponent):
    bl_idname = "ue4workspace.bonecomponentpelvis"
    bl_label = "Add PELVIS"
    bl_description = "Add Pelvis Bone Component"

    boneName: StringProperty(
        name="Bone Name",
        default="pelvis"
    )

    prefixName: StringProperty(
        name="Prefix Name",
        default=""
    )

    suffixName: StringProperty(
        name="Suffix Name",
        default=""
    )

    sideBone: EnumProperty(
        name="Side Name",
        items=[
            ("NONE", "None", ""),
            ("l", "Left", ""),
            ("r", "Right", "")
        ],
        default=("NONE")
    )

    sideMirror: BoolProperty(
        name="Mirror Side",
        default=False
    )

    parentToBone: BoolProperty(
        name="Parent To Active Bone",
        default=False
    )

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object
        editBones = activeObject.data.edit_bones
        activeBone = context.active_bone

        newBone = editBones.new(self.buildName([self.prefixName, self.boneName, self.suffixName, (self.sideBone if self.sideBone != "NONE" else "")]))

        newBone.head = context.scene.cursor.location
        newBone.tail = context.scene.cursor.location + Vector((0.0, 0.0, 0.2))
        newBone.roll = 0

        newBone["UE4RIGTYPE"] = "PELVIS"
        newBone["rotateBone"] = 1
        newBone["rotationRadian"] = -1.5708
        newBone["orientAxis"] = 0
        newBone["orientRoll"] = -1.5708

        newBone["customShape"] = 1
        newBone["customShapeType"] = 2
        newBone["customShapeParam"] = [16.0, 25.0, 0.0, 2.25, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        if self.parentToBone and activeBone:
            newBone.parent = activeBone

        editBones.active = newBone

        if self.sideMirror and self.sideBone != "NONE":
            newBoneSide = editBones.new(self.buildName([self.prefixName, self.boneName, self.suffixName, ("r" if self.sideBone == "l" else "l")]))

            newBoneSide.head = newBone.head
            newBoneSide.head.x = -newBone.head.x
            newBoneSide.tail = newBone.tail
            newBoneSide.tail.x = -newBone.tail.x
            newBoneSide.roll = 0

            newBoneSide["UE4RIGTYPE"] = "PELVIS"
            newBoneSide["rotateBone"] = 1
            newBoneSide["rotationRadian"] = -1.5708
            newBoneSide["orientAxis"] = 0
            newBoneSide["orientRoll"] = -1.5708

            newBoneSide["customShape"] = 1
            newBoneSide["customShapeType"] = 2
            newBoneSide["customShapeParam"] = [16.0, 25.0, 0.0, 2.25, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

            if self.parentToBone and activeBone:
                parentSide = editBones.get(activeBone.name[:-1] + ("r" if self.sideBone == "l" else "l"))
                newBoneSide.parent = parentSide if parentSide else activeBone

        return {"FINISHED"}

class OP_BoneComponent_Spine(OP_MixBoneComponent):
    bl_idname = "ue4workspace.bonecomponentspine"
    bl_label = "Add SPINE"
    bl_description = "Add Spine Bone Component"

    boneName: StringProperty(
        name="Bone Name",
        default="spine"
    )

    prefixName: StringProperty(
        name="Prefix Name",
        default=""
    )

    suffixName: StringProperty(
        name="Suffix Name",
        default=""
    )

    sideBone: EnumProperty(
        name="Side Name",
        items=[
            ("NONE", "None", ""),
            ("l", "Left", ""),
            ("r", "Right", "")
        ],
        default=("NONE")
    )

    numberBone: IntProperty(
        name="Number Bone",
        min=1,
        default=1
    )

    sideMirror: BoolProperty(
        name="Mirror Side",
        default=False
    )

    parentToBone: BoolProperty(
        name="Parent To Active Bone",
        default=False
    )

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object
        editBones = activeObject.data.edit_bones
        activeBone = context.active_bone

        listBone = []
        for index in range(1, self.numberBone+1):
            newBone = editBones.new(self.buildName([self.prefixName, self.boneName, self.suffixName, (("0" if index < 10 else "") + str(index)), (self.sideBone if self.sideBone != "NONE" else "")]))

            newBone.head = context.scene.cursor.location
            newBone.tail = context.scene.cursor.location + Vector((0.0, 0.0, 0.2 * index))
            newBone.roll = 0

            newBone["UE4RIGTYPE"] = "SPINE"
            newBone["rotateBone"] = 1
            newBone["rotationRadian"] = -1.5708
            newBone["orientAxis"] = 0
            newBone["orientRoll"] = -1.5708

            newBone["customShape"] = 1
            newBone["customShapeType"] = 2
            newBone["customShapeParam"] = [16.0, 22.5, 0.0, 2.25, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

            if listBone:
                newBone.parent = listBone[index-2]
                newBone.use_connect = True

            listBone.append(newBone)

        if self.parentToBone and activeBone:
            listBone[0].parent = activeBone

        editBones.active = listBone[0]

        if self.sideMirror and self.sideBone != "NONE":
            listBone = []
            for index in range(1, self.numberBone+1):
                newBoneSide = editBones.new(self.buildName([self.prefixName, self.boneName, self.suffixName, (("0" if index < 10 else "") + str(index)), ("r" if self.sideBone == "l" else "l")]))

                newBoneSide.head = context.scene.cursor.location
                newBoneSide.head.x = -newBoneSide.head.x
                newBoneSide.tail = context.scene.cursor.location + Vector((0.0, 0.0, 0.2 * index))
                newBoneSide.tail.x = -newBoneSide.tail.x
                newBoneSide.roll = 0

                newBoneSide["UE4RIGTYPE"] = "SPINE"
                newBoneSide["rotateBone"] = 1
                newBoneSide["rotationRadian"] = -1.5708
                newBoneSide["orientAxis"] = 0
                newBoneSide["orientRoll"] = -1.5708

                newBoneSide["customShape"] = 1
                newBoneSide["customShapeType"] = 2
                newBoneSide["customShapeParam"] = [16.0, 22.5, 0.0, 2.25, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

                if listBone:
                    newBoneSide.parent = listBone[index-2]
                    newBoneSide.use_connect = True

                listBone.append(newBoneSide)

            if self.parentToBone and activeBone:
                parentSide = editBones.get(activeBone.name[:-1] + ("r" if self.sideBone == "l" else "l"))
                listBone[0].parent = parentSide if parentSide else activeBone

        return {"FINISHED"}

class OP_BoneComponent_Neck(OP_MixBoneComponent):
    bl_idname = "ue4workspace.bonecomponentneck"
    bl_label = "Add NECK"
    bl_description = "Add Neck Bone Component"

    boneName: StringProperty(
        name="Bone Name",
        default="neck"
    )

    prefixName: StringProperty(
        name="Prefix Name",
        default=""
    )

    suffixName: StringProperty(
        name="Suffix Name",
        default=""
    )

    sideBone: EnumProperty(
        name="Side Name",
        items=[
            ("NONE", "None", ""),
            ("l", "Left", ""),
            ("r", "Right", "")
        ],
        default=("NONE")
    )

    numberBone: IntProperty(
        name="Number Bone",
        min=1,
        default=1
    )

    sideMirror: BoolProperty(
        name="Mirror Side",
        default=False
    )

    parentToBone: BoolProperty(
        name="Parent To Active Bone",
        default=False
    )

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object
        editBones = activeObject.data.edit_bones
        activeBone = context.active_bone

        listBone = []

        for index in range(1, self.numberBone+1):
            newBone = editBones.new(self.buildName([self.prefixName, self.boneName, self.suffixName, (("0" if index < 10 else "") + str(index)), (self.sideBone if self.sideBone != "NONE" else "")]))

            newBone.head = context.scene.cursor.location
            newBone.tail = context.scene.cursor.location + Vector((0.0, 0.0, 0.2 * index))
            newBone.roll = 0

            newBone["UE4RIGTYPE"] = "NECK"
            newBone["rotateBone"] = 1
            newBone["rotationRadian"] = -1.5708
            newBone["orientAxis"] = 0
            newBone["orientRoll"] = -1.5708

            newBone["customShape"] = 1
            newBone["customShapeType"] = 2
            newBone["customShapeParam"] = [16.0, 10.0, 0.0, 2.25, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

            if listBone:
                newBone.parent = listBone[index-2]
                newBone.use_connect = True

            listBone.append(newBone)

        if self.parentToBone and activeBone:
            listBone[0].parent = activeBone

        editBones.active = listBone[0]

        if self.sideMirror and self.sideBone != "NONE":
            listBone = []
            for index in range(1, self.numberBone+1):
                newBoneSide = editBones.new(self.buildName([self.prefixName, self.boneName, self.suffixName, (("0" if index < 10 else "") + str(index)), ("r" if self.sideBone == "l" else "l")]))

                newBoneSide.head = context.scene.cursor.location
                newBoneSide.head.x = -newBoneSide.head.x
                newBoneSide.tail = context.scene.cursor.location + Vector((0.0, 0.0, 0.2 * index))
                newBoneSide.tail.x = -newBoneSide.tail.x
                newBoneSide.roll = 0

                newBoneSide["UE4RIGTYPE"] = "NECK"
                newBoneSide["rotateBone"] = 1
                newBoneSide["rotationRadian"] = -1.5708
                newBoneSide["orientAxis"] = 0
                newBoneSide["orientRoll"] = -1.5708

                newBoneSide["customShape"] = 1
                newBoneSide["customShapeType"] = 2
                newBoneSide["customShapeParam"] = [16.0, 10.0, 0.0, 2.25, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

                if listBone:
                    newBoneSide.parent = listBone[index-2]
                    newBoneSide.use_connect = True

                listBone.append(newBoneSide)

            if self.parentToBone and activeBone:
                parentSide = editBones.get(activeBone.name[:-1] + ("r" if self.sideBone == "l" else "l"))
                listBone[0].parent = parentSide if parentSide else activeBone

        return {"FINISHED"}

class OP_BoneComponent_Head(OP_MixBoneComponent):
    bl_idname = "ue4workspace.bonecomponenthead"
    bl_label = "Add HEAD"
    bl_description = "Add Head Bone Component"

    boneName: StringProperty(
        name="Bone Name",
        default="head"
    )

    prefixName: StringProperty(
        name="Prefix Name",
        default=""
    )

    suffixName: StringProperty(
        name="Suffix Name",
        default=""
    )

    sideBone: EnumProperty(
        name="Side Name",
        items=[
            ("NONE", "None", ""),
            ("l", "Left", ""),
            ("r", "Right", "")
        ],
        default=("NONE")
    )

    sideMirror: BoolProperty(
        name="Mirror Side",
        default=False
    )

    parentToBone: BoolProperty(
        name="Parent To Active Bone",
        default=False
    )

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object
        editBones = activeObject.data.edit_bones
        activeBone = context.active_bone

        newBone = editBones.new(self.buildName([self.prefixName, self.boneName, self.suffixName, (self.sideBone if self.sideBone != "NONE" else "")]))

        newBone.head = context.scene.cursor.location
        newBone.tail = context.scene.cursor.location + Vector((0.0, 0.0, 0.2))
        newBone.roll = 0

        newBone["UE4RIGTYPE"] = "HEAD"
        newBone["rotateBone"] = 1
        newBone["rotationRadian"] = -1.5708
        newBone["orientAxis"] = 0
        newBone["orientRoll"] = -1.5708

        newBone["customShape"] = 1
        newBone["customShapeType"] = 0
        newBone["customShapeParam"] = [14.0, 17.0, -2.0, 17.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        if self.parentToBone and activeBone:
            newBone.parent = activeBone

        editBones.active = newBone

        if self.sideMirror and self.sideBone != "NONE":
            newBoneSide = editBones.new(self.buildName([self.prefixName, self.boneName, self.suffixName, ("r" if self.sideBone == "l" else "l")]))

            newBoneSide.head = newBone.head
            newBoneSide.head.x = -newBone.head.x
            newBoneSide.tail = newBone.tail
            newBoneSide.tail.x = -newBone.tail.x
            newBoneSide.roll = 0

            newBoneSide["UE4RIGTYPE"] = "HEAD"
            newBoneSide["rotateBone"] = 1
            newBoneSide["rotationRadian"] = -1.5708
            newBoneSide["orientAxis"] = 0
            newBoneSide["orientRoll"] = -1.5708

            newBoneSide["customShape"] = 1
            newBoneSide["customShapeType"] = 0
            newBoneSide["customShapeParam"] = [14.0, 17.0, -2.0, 17.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

            if self.parentToBone and activeBone:
                parentSide = editBones.get(activeBone.name[:-1] + ("r" if self.sideBone == "l" else "l"))
                newBoneSide.parent = parentSide if parentSide else activeBone

        return {"FINISHED"}

class OP_BoneComponent_FaceAttach(OP_MixBoneComponent):
    bl_idname = "ue4workspace.bonecomponentfaceattach"
    bl_label = "Add FACE ATTACH"
    bl_description = "Add Face Attach To Head Bone Component"

    boneName: StringProperty(
        name="Bone Name",
        default="faceAttach"
    )

    prefixName: StringProperty(
        name="Prefix Name",
        default=""
    )

    suffixName: StringProperty(
        name="Suffix Name",
        default=""
    )

    @classmethod
    def poll(cls, context):
        activeObject = context.active_object
        activeBone = context.active_bone
        return context.mode == "EDIT_ARMATURE" and activeObject is not None and activeObject.data.UE4RIG and activeBone is not None and activeBone.get("UE4RIGTYPE") == "HEAD"

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object
        editBones = activeObject.data.edit_bones
        activeBone = context.active_bone

        newBone = editBones.new(self.buildName([self.prefixName, self.boneName, self.suffixName]))

        newBone.head = activeBone.head
        newBone.tail = activeBone.head + Vector((0.0, 0.2, 0.0))
        newBone.roll = 0
        newBone.use_deform = False

        newBone["UE4RIGTYPE"] = "FACE_ATTACH"
        newBone["rotateBone"] = 1
        newBone["rotationRadian"] = 0
        newBone["orientAxis"] = 0
        newBone["orientRoll"] = -0.785398

        newBone.parent = activeBone

        return {"FINISHED"}

class OP_BoneComponent_Jaw(OP_MixFaceAttachComponent):
    bl_idname = "ue4workspace.bonecomponentjaw"
    bl_label = "Add JAW"
    bl_description = "Add Jaw Bone To faceAttach Component"

    boneName: StringProperty(
        name="Bone Name",
        default="jaw"
    )

    prefixName: StringProperty(
        name="Prefix Name",
        default=""
    )

    suffixName: StringProperty(
        name="Suffix Name",
        default=""
    )

    sideBone: EnumProperty(
        name="Side Name",
        items=[
            ("C", "Center", ""),
            ("L", "Left", ""),
            ("R", "Right", "")
        ],
        default=("C")
    )

    sideMirror: BoolProperty(
        name="Mirror Side",
        default=False
    )

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object
        editBones = activeObject.data.edit_bones
        activeBone = context.active_bone

        newBone = editBones.new(self.buildName([self.sideBone, self.prefixName, self.boneName, self.suffixName]))

        newBone.head = context.scene.cursor.location
        newBone.tail = context.scene.cursor.location + Vector((0.0, -0.125, -0.075))
        newBone.roll = 0

        newBone["UE4RIGTYPE"] = "JAW"
        newBone["rotateBone"] = 1
        newBone["rotationRadian"] = 0
        newBone["orientAxis"] = 0
        newBone["orientRoll"] = 0

        newBone["customShape"] = 1
        newBone["customShapeType"] = 0
        newBone["customShapeParam"] = [10.0, 1.0, 0.0, 10.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        newBone.parent = activeBone

        if self.sideMirror and self.sideBone != "C":
            newBoneSide = editBones.new(self.buildName([("R" if self.sideBone == "L" else "L"), self.prefixName, self.boneName, self.suffixName]))

            newBoneSide.head = context.scene.cursor.location
            newBoneSide.head.x = -newBoneSide.head.x
            newBoneSide.tail = context.scene.cursor.location + Vector((0.0, -0.125, -0.075))
            newBoneSide.tail.x = -newBoneSide.tail.x
            newBoneSide.roll = 0

            newBoneSide["UE4RIGTYPE"] = "JAW"
            newBoneSide["rotateBone"] = 1
            newBoneSide["rotationRadian"] = 0
            newBoneSide["orientAxis"] = 0
            newBoneSide["orientRoll"] = 0

            newBoneSide["customShape"] = 1
            newBoneSide["customShapeType"] = 0
            newBoneSide["customShapeParam"] = [10.0, 1.0, 0.0, 10.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

            parentSide = editBones.get(("R" if self.sideBone == "L" else "L") + activeBone.name[1:])
            newBoneSide.parent = parentSide if parentSide else activeBone

        return {"FINISHED"}

class OP_BoneComponent_Landmark(OP_MixFaceAttachComponent):
    bl_idname = "ue4workspace.bonecomponentlandmark"
    bl_label = "Add LANDMARK"
    bl_description = "Add Landmark Bone To faceAttach Component"

    boneName: StringProperty(
        name="Bone Name",
        default="landmark"
    )

    prefixName: StringProperty(
        name="Prefix Name",
        default=""
    )

    suffixName: StringProperty(
        name="Suffix Name",
        default=""
    )

    sideBone: EnumProperty(
        name="Side Name",
        items=[
            ("C", "Center", ""),
            ("L", "Left", ""),
            ("R", "Right", "")
        ],
        default=("C")
    )

    sideMirror: BoolProperty(
        name="Mirror Side",
        default=False
    )

    @classmethod
    def poll(cls, context):
        activeObject = context.active_object
        activeBone = context.active_bone
        return context.mode == "EDIT_ARMATURE" and activeObject is not None and activeObject.data.UE4RIG and activeBone is not None and activeBone.get("UE4RIGTYPE") in ["FACE_ATTACH", "JAW"]

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object
        editBones = activeObject.data.edit_bones
        activeBone = context.active_bone

        newBone = editBones.new(self.buildName([self.sideBone, self.prefixName, self.boneName, self.suffixName]))

        newBone.head = context.scene.cursor.location
        newBone.tail = context.scene.cursor.location + Vector((0.0, 0.015, 0.0))
        newBone.roll = 0

        newBone["UE4RIGTYPE"] = "LANDMARK"
        newBone["rotateBone"] = 1
        newBone["rotationRadian"] = 0
        newBone["orientAxis"] = 0
        newBone["orientRoll"] = 0

        newBone["customShape"] = 1
        newBone["customShapeType"] = 0
        newBone["customShapeParam"] = [0.5, 0.5, -0.25, 0.25, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        newBone.parent = activeBone

        if self.sideMirror and self.sideBone != "C":
            newBoneSide = editBones.new(self.buildName([("R" if self.sideBone == "L" else "L"), self.prefixName, self.boneName, self.suffixName]))

            newBoneSide.head = context.scene.cursor.location
            newBoneSide.head.x = -newBoneSide.head.x
            newBoneSide.tail = context.scene.cursor.location + Vector((0.0, 0.015, 0.0))
            newBoneSide.tail.x = -newBoneSide.tail.x
            newBoneSide.roll = 0

            newBoneSide["UE4RIGTYPE"] = "LANDMARK"
            newBoneSide["rotateBone"] = 1
            newBoneSide["rotationRadian"] = 0
            newBoneSide["orientAxis"] = 0
            newBoneSide["orientRoll"] = 0

            newBoneSide["customShape"] = 1
            newBoneSide["customShapeType"] = 0
            newBoneSide["customShapeParam"] = [0.5, 0.5, -0.25, 0.25, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

            parentSide = editBones.get(("R" if self.sideBone == "L" else "L") + activeBone.name[1:])
            newBoneSide.parent = parentSide if parentSide else activeBone

        return {"FINISHED"}

class OP_BoneComponent_Eye(OP_MixFaceAttachComponent):
    bl_idname = "ue4workspace.bonecomponenteye"
    bl_label = "Add EYE"
    bl_description = "Add Eye Bone To faceAttach Component"

    boneName: StringProperty(
        name="Bone Name",
        default="eye"
    )

    prefixName: StringProperty(
        name="Prefix Name",
        default=""
    )

    suffixName: StringProperty(
        name="Suffix Name",
        default=""
    )

    sideBone: EnumProperty(
        name="Side Name",
        items=[
            ("C", "Center", ""),
            ("L", "Left", ""),
            ("R", "Right", "")
        ],
        default=("C")
    )

    sideMirror: BoolProperty(
        name="Mirror Side",
        default=False
    )

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object
        editBones = activeObject.data.edit_bones
        activeBone = context.active_bone

        newBone = editBones.new(self.buildName([self.sideBone, self.prefixName, self.boneName, self.suffixName]))

        newBone.head = context.scene.cursor.location
        newBone.tail = context.scene.cursor.location + Vector((0.0, -0.015, 0.0))
        newBone.roll = 0

        newBone["UE4RIGTYPE"] = "EYE"
        newBone["rotateBone"] = 1
        newBone["rotationRadian"] = 0
        newBone["orientAxis"] = 0
        newBone["orientRoll"] = 0

        newBone["customShape"] = 1
        newBone["customShapeType"] = 1
        newBone["customShapeParam"] = [8.0, 4.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        newBone.parent = activeBone

        if self.sideMirror and self.sideBone != "C":
            newBoneSide = editBones.new(self.buildName([("R" if self.sideBone == "L" else "L"), self.prefixName, self.boneName, self.suffixName]))

            newBoneSide.head = context.scene.cursor.location
            newBoneSide.head.x = -newBoneSide.head.x
            newBoneSide.tail = context.scene.cursor.location + Vector((0.0, -0.015, 0.0))
            newBoneSide.tail.x = -newBoneSide.tail.x
            newBoneSide.roll = 0

            newBoneSide["UE4RIGTYPE"] = "EYE"
            newBoneSide["rotateBone"] = 1
            newBoneSide["rotationRadian"] = 0
            newBoneSide["orientAxis"] = 0
            newBoneSide["orientRoll"] = 0

            newBoneSide["customShape"] = 1
            newBoneSide["customShapeType"] = 1
            newBoneSide["customShapeParam"] = [8.0, 4.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

            parentSide = editBones.get(("R" if self.sideBone == "L" else "L") + activeBone.name[1:])
            newBoneSide.parent = parentSide if parentSide else activeBone

        return {"FINISHED"}

class OP_BoneComponent_Eyelid(OP_MixEyeComponent):
    bl_idname = "ue4workspace.bonecomponenteyelid"
    bl_label = "Add EYELID"
    bl_description = "Add Eyelid Bone To Eye Component"

    eyelidPosition: EnumProperty(
        name="Side Name",
        items=[
            ("U", "Upper", ""),
            ("L", "Lower", "")
        ],
        options={"HIDDEN"},
        default=("U")
    )

    boneName: StringProperty(
        name="Bone Name",
        default="eye_lid"
    )

    prefixName: StringProperty(
        name="Prefix Name",
        default=""
    )

    suffixName: StringProperty(
        name="Suffix Name",
        default=""
    )

    sideBone: EnumProperty(
        name="Side Name",
        items=[
            ("C", "Center", ""),
            ("L", "Left", ""),
            ("R", "Right", "")
        ],
        default=("C")
    )

    sideMirror: BoolProperty(
        name="Mirror Side",
        default=False
    )

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object
        editBones = activeObject.data.edit_bones
        activeBone = context.active_bone

        newBone = editBones.new(self.buildName([self.sideBone, self.prefixName, self.boneName, self.suffixName]))

        newBone.head = context.scene.cursor.location
        newBone.tail = context.scene.cursor.location + Vector((0.0, -0.015, 0.0))
        newBone.roll = 0

        newBone["UE4RIGTYPE"] = "EYELID_" + ("UPPER" if self.eyelidPosition == "U" else "LOWER")
        newBone["rotateBone"] = 1
        newBone["rotationRadian"] = 0
        newBone["orientAxis"] = 0
        newBone["orientRoll"] = 0

        newBone["customShape"] = 1
        newBone["customShapeType"] = 0
        newBone["customShapeParam"] = [0.5, 0.5, -0.25, 0.25, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        newBone.parent = activeBone

        if self.sideMirror and self.sideBone != "C":
            newBoneSide = editBones.new(self.buildName([("R" if self.sideBone == "L" else "L"), self.prefixName, self.boneName, self.suffixName]))

            newBoneSide.head = context.scene.cursor.location
            newBoneSide.head.x = -newBoneSide.head.x
            newBoneSide.tail = context.scene.cursor.location + Vector((0.0, -0.015, 0.0))
            newBoneSide.tail.x = -newBoneSide.tail.x
            newBoneSide.roll = 0

            newBoneSide["UE4RIGTYPE"] = "EYELID_" + ("UPPER" if self.eyelidPosition == "U" else "LOWER")
            newBoneSide["rotateBone"] = 1
            newBoneSide["rotationRadian"] = 0
            newBoneSide["orientAxis"] = 0
            newBoneSide["orientRoll"] = 0

            newBoneSide["customShape"] = 1
            newBoneSide["customShapeType"] = 0
            newBoneSide["customShapeParam"] = [0.5, 0.5, -0.25, 0.25, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

            parentSide = editBones.get(("R" if self.sideBone == "L" else "L") + activeBone.name[1:])
            newBoneSide.parent = parentSide if parentSide else activeBone

        return {"FINISHED"}

class OP_BoneComponent_Arm_Human(OP_MixBoneComponent):
    bl_idname = "ue4workspace.bonecomponentarmhuman"
    bl_label = "Add ARM_HUMAN"
    bl_description = "Add Arm Human Bone Component"

    boneUpperName: StringProperty(
        name="Upper Name",
        default="upperarm"
    )

    boneLowerName: StringProperty(
        name="Lower Name",
        default="lowerarm"
    )

    boneHandName: StringProperty(
        name="Hand Name",
        default="hand"
    )

    prefixName: StringProperty(
        name="Prefix Name",
        default=""
    )

    suffixName: StringProperty(
        name="Suffix Name",
        default=""
    )

    sideBone: EnumProperty(
        name="Side Name",
        items=[
            ("l", "Left", ""),
            ("r", "Right", "")
        ],
        default=("l")
    )

    sideMirror: BoolProperty(
        name="Mirror Side",
        default=False
    )

    parentToBone: BoolProperty(
        name="Parent To Active Bone",
        default=False
    )

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object
        editBones = activeObject.data.edit_bones
        activeBone = context.active_bone

        boneData = {
            "l": [
                # upperarm left
                (
                    # boneName
                    self.boneUpperName,
                    # head
                    Vector((0, 0, 0)),
                    # tail
                    Vector((0.3, 0.05, 0)),
                    # roll
                    3.14159,
                    # UE4RIGTYPE
                    "ARM_HUMAN",
                    # rotateBone
                    True,
                    # rotationRadian
                    -1.5707963705062866,
                    # orientAxis
                    2,
                    # orientRoll
                    3.1415927410125732,
                    # customShape
                    True,
                    # customShapeType
                    0,
                    # customShapeParam
                    [15.0, 15.0, 0.0, 15.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
                ),
                # lowerarm left
                (
                    # boneName
                    self.boneLowerName,
                    # head
                    Vector((0.3, 0.05, 0)),
                    # tail
                    Vector((0.59, 0.01, 0)),
                    # roll
                    3.14159,
                    # UE4RIGTYPE
                    "",
                    # rotateBone
                    True,
                    # rotationRadian
                    -1.5707963705062866,
                    # orientAxis
                    2,
                    # orientRoll
                    3.1415927410125732,
                    # customShape
                    True,
                    # customShapeType
                    0,
                    # customShapeParam
                    [10.0, 10.0, 0.0, 15.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
                ),
                # hand left
                (
                    # boneName
                    self.boneHandName,
                    # head
                    Vector((0.59, 0.01, 0)),
                    # tail
                    Vector((0.69, 0.01, 0)),
                    # roll
                    5.06145e-07,
                    # UE4RIGTYPE
                    "",
                    # rotateBone
                    True,
                    # rotationRadian
                    -1.5707963705062866,
                    # orientAxis
                    0,
                    # orientRoll
                    -1.5707963705062866,
                    # customShape
                    True,
                    # customShapeType
                    0,
                    # customShapeParam
                    [10.0, 7.5, 0.0, 10.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
                )
            ],
            "r": [
                # upperarm right
                (
                    # boneName
                    self.boneUpperName,
                    # head
                    Vector((-0, 0, 0)),
                    # tail
                    Vector((-0.3, 0.05, 0)),
                    # roll
                    3.14159,
                    # UE4RIGTYPE
                    "ARM_HUMAN",
                    # rotateBone
                    True,
                    # rotationRadian
                    -1.5707963705062866,
                    # orientAxis
                    2,
                    # orientRoll
                    0,
                    # customShape
                    True,
                    # customShapeType
                    0,
                    # customShapeParam
                    [15.0, 15.0, 0.0, 15.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
                ),
                # lowerarm right
                (
                    # boneName
                    self.boneLowerName,
                    # head
                    Vector((-0.3, 0.05, 0)),
                    # tail
                    Vector((-0.59, 0.01, 0)),
                    # roll
                    3.14159,
                    # UE4RIGTYPE
                    "",
                    # rotateBone
                    True,
                    # rotationRadian
                    -1.5707963705062866,
                    # orientAxis
                    2,
                    # orientRoll
                    0,
                    # customShape
                    True,
                    # customShapeType
                    0,
                    # customShapeParam
                    [10.0, 10.0, 0.0, 15.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
                ),
                # hand right
                (
                    # boneName
                    self.boneHandName,
                    # head
                    Vector((-0.59, 0.01, 0)),
                    # tail
                    Vector((-0.69, 0.01, 0)),
                    # roll
                    -5.06145e-07,
                    # UE4RIGTYPE
                    "",
                    # rotateBone
                    True,
                    # rotationRadian
                    1.5707963705062866,
                    # orientAxis
                    0,
                    # orientRoll
                    -1.5707963705062866,
                    # customShape
                    True,
                    # customShapeType
                    0,
                    # customShapeParam
                    [10.0, 7.5, 0.0, 10.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
                )
            ]
        }

        listBone = []
        for index, data in enumerate(boneData[self.sideBone]):
            boneName, head, tail, roll, ue4rigtype, rotBone, rotRad, orientAxis, orientRoll, customShape, customShapeType, customShapeParam = data

            newBone = editBones.new(self.buildName([self.prefixName, boneName, self.suffixName, self.sideBone]))

            newBone.head = context.scene.cursor.location + head
            newBone.tail = context.scene.cursor.location + tail
            newBone.roll = roll

            newBone["UE4RIGTYPE"] = ue4rigtype
            newBone["rotateBone"] = rotBone
            newBone["rotationRadian"] = rotRad
            newBone["orientAxis"] = orientAxis
            newBone["orientRoll"] = orientRoll

            newBone["customShape"] = customShape
            newBone["customShapeType"] = customShapeType
            newBone["customShapeParam"] = customShapeParam

            if listBone:
                newBone.parent = listBone[index-1]
                newBone.use_connect = True

            listBone.append(newBone)

        if self.parentToBone and activeBone:
            listBone[0].parent = activeBone

        editBones.active = listBone[0]

        if self.sideMirror:
            listBone = []
            for index, data in enumerate(boneData[("r" if self.sideBone == "l" else "l")]):
                boneName, head, tail, roll, ue4rigtype, rotBone, rotRad, orientAxis, orientRoll, customShape, customShapeType, customShapeParam = data

                newBone = editBones.new(self.buildName([self.prefixName, boneName, self.suffixName, ("r" if self.sideBone == "l" else "l")]))

                baseLocation = context.scene.cursor.location.copy()
                baseLocation.x = -baseLocation.x

                newBone.head = baseLocation + head
                newBone.tail = baseLocation + tail
                newBone.roll = roll

                newBone["UE4RIGTYPE"] = ue4rigtype
                newBone["rotateBone"] = rotBone
                newBone["rotationRadian"] = rotRad
                newBone["orientAxis"] = orientAxis
                newBone["orientRoll"] = orientRoll

                newBone["customShape"] = customShape
                newBone["customShapeType"] = customShapeType
                newBone["customShapeParam"] = customShapeParam

                if listBone:
                    newBone.parent = listBone[index-1]
                    newBone.use_connect = True

                listBone.append(newBone)

            if self.parentToBone and activeBone:
                parentSide = editBones.get(activeBone.name[:-1] + ("r" if self.sideBone == "l" else "l"))
                listBone[0].parent = parentSide if parentSide else activeBone

        return {"FINISHED"}

class OP_BoneComponent_Finger(OP_MixBoneComponent):
    bl_idname = "ue4workspace.bonecomponentfinger"
    bl_label = "Add FINGER"
    bl_description = "Add Finger Bone Component"

    boneName: StringProperty(
        name="Bone Name",
        default="finger"
    )

    prefixName: StringProperty(
        name="Prefix Name",
        default=""
    )

    suffixName: StringProperty(
        name="Suffix Name",
        default=""
    )

    sideBone: EnumProperty(
        name="Side Name",
        items=[
            ("l", "Left", ""),
            ("r", "Right", "")
        ],
        default=("l")
    )

    numberBone: IntProperty(
        name="Number Bone",
        min=2,
        default=3
    )

    sideMirror: BoolProperty(
        name="Mirror Side",
        default=False
    )

    parentToBone: BoolProperty(
        name="Parent To Active Bone",
        default=False
    )

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object
        editBones = activeObject.data.edit_bones
        activeBone = context.active_bone

        boneData = {
            "l":
                # finger left
                (
                    # roll
                    5.58505e-07,
                    # rotRad
                    -1.5708
                )
            ,
            "r":
                # finger right
                (
                    # roll
                    -5.58505e-07,
                    # rotRad
                    1.5708
                )
        }


        listBone = []
        for index in range(1, self.numberBone+1):
            roll, rotRad = boneData[self.sideBone]
            newBone = editBones.new(self.buildName([self.prefixName, self.boneName, self.suffixName, (("0" if index < 10 else "") + str(index)), self.sideBone]))

            newBone.head = context.scene.cursor.location
            newBone.tail = context.scene.cursor.location + Vector(((0.05 * index) if self.sideBone == "l" else (-0.05 * index), 0.0, 0.0))
            newBone.roll = roll

            newBone["UE4RIGTYPE"] = "FINGER" if index == 1 else ""
            newBone["rotateBone"] = 1
            newBone["rotationRadian"] = rotRad
            newBone["orientAxis"] = 0
            newBone["orientRoll"] = -1.5708

            newBone["customShape"] = 1
            newBone["customShapeType"] = 0
            newBone["customShapeParam"] = [1.8, 1.8, 0.0, 2.25, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

            if listBone:
                newBone.parent = listBone[index-2]
                newBone.use_connect = True

            listBone.append(newBone)

        if self.parentToBone and activeBone:
            listBone[0].parent = activeBone

        editBones.active = listBone[0]

        if self.sideMirror and self.sideBone != "NONE":
            listBone = []
            for index in range(1, self.numberBone+1):
                roll, rotRad = boneData[("r" if self.sideBone == "l" else "l")]
                newBoneSide = editBones.new(self.buildName([self.prefixName, self.boneName, self.suffixName, (("0" if index < 10 else "") + str(index)), ("r" if self.sideBone == "l" else "l")]))

                baseLocation = context.scene.cursor.location.copy()
                baseLocation.x = -baseLocation.x

                newBoneSide.head = baseLocation
                newBoneSide.tail = baseLocation + Vector(((-0.05 * index) if self.sideBone == "l" else (0.05 * index), 0.0, 0.0))
                newBoneSide.roll = roll

                newBoneSide["UE4RIGTYPE"] = "FINGER" if index == 1 else ""
                newBoneSide["rotateBone"] = 1
                newBoneSide["rotationRadian"] = rotRad
                newBoneSide["orientAxis"] = 0
                newBoneSide["orientRoll"] = -1.5708

                newBone["customShape"] = 1
                newBone["customShapeType"] = 0
                newBone["customShapeParam"] = [1.8, 1.8, 0.0, 2.25, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

                if listBone:
                    newBoneSide.parent = listBone[index-2]
                    newBoneSide.use_connect = True

                listBone.append(newBoneSide)

            if self.parentToBone and activeBone:
                parentSide = editBones.get(activeBone.name[:-1] + ("r" if self.sideBone == "l" else "l"))
                listBone[0].parent = parentSide if parentSide else activeBone

        return {"FINISHED"}

class OP_BoneComponent_Leg_Human(OP_MixBoneComponent):
    bl_idname = "ue4workspace.bonecomponentleghuman"
    bl_label = "Add LEG_HUMAN"
    bl_description = "Add Leg Human Bone Component"

    boneThighName: StringProperty(
        name="Thigh Name",
        default="thigh"
    )

    boneCalfName: StringProperty(
        name="Calf Name",
        default="calf"
    )

    boneFootName: StringProperty(
        name="Foot Name",
        default="foot"
    )

    boneBallName: StringProperty(
        name="Ball Name",
        default="ball"
    )

    prefixName: StringProperty(
        name="Prefix Name",
        default=""
    )

    suffixName: StringProperty(
        name="Suffix Name",
        default=""
    )

    sideBone: EnumProperty(
        name="Side Name",
        items=[
            ("l", "Left", ""),
            ("r", "Right", "")
        ],
        default=("l")
    )

    sideMirror: BoolProperty(
        name="Mirror Side",
        default=False
    )

    parentToBone: BoolProperty(
        name="Parent To Active Bone",
        default=False
    )

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object
        editBones = activeObject.data.edit_bones
        activeBone = context.active_bone

        boneData = {
            "l": [
                # thigh left
                (
                    # boneName
                    self.boneThighName,
                    # head
                    Vector((0, 0, 0)),
                    # tail
                    Vector((0, -0.05, -0.43)),
                    # roll
                    1.5708,
                    # UE4RIGTYPE
                    "LEG_HUMAN",
                    # rotateBone
                    True,
                    # rotationRadian
                    1.5707963705062866,
                    # orientAxis
                    2,
                    # orientRoll
                    3.1415927410125732,
                    # customShape
                    True,
                    # customShapeType
                    0,
                    # customShapeParam
                    [18.0, 18.0, 0.0, 22.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
                ),
                # calf left
                (
                    # boneName
                    self.boneCalfName,
                    # head
                    Vector((0, -0.05, -0.43)),
                    # tail
                    Vector((0, -0.01, -0.8)),
                    # roll
                    1.5708,
                    # UE4RIGTYPE
                    "",
                    # rotateBone
                    True,
                    # rotationRadian
                    1.5707963705062866,
                    # orientAxis
                    2,
                    # orientRoll
                    3.1415927410125732,
                    # customShape
                    True,
                    # customShapeType
                    0,
                    # customShapeParam
                    [12.0, 12.0, 0.0, 22.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
                ),
                # foot left
                (
                    # boneName
                    self.boneFootName,
                    # head
                    Vector((0, -0.01, -0.8)),
                    # tail
                    Vector((0.0, -0.17, -0.92)),
                    # roll
                    3.14159,
                    # UE4RIGTYPE
                    "",
                    # rotateBone
                    True,
                    # rotationRadian
                    3.1415927410125732,
                    # orientAxis
                    2,
                    # orientRoll
                    1.5707963705062866,
                    # customShape
                    True,
                    # customShapeType
                    0,
                    # customShapeParam
                    [10.0, 10.0, 0.0, 17.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
                ),
                # ball left
                (
                    # boneName
                    self.boneBallName,
                    # head
                    Vector((0.0, -0.17, -0.92)),
                    # tail
                    Vector((0.0, -0.22, -0.92)),
                    # roll
                    3.14159,
                    # UE4RIGTYPE
                    "",
                    # rotateBone
                    True,
                    # rotationRadian
                    -1.5707963705062866,
                    # orientAxis
                    0,
                    # orientRoll
                    -1.5707963705062866,
                    # customShape
                    True,
                    # customShapeType
                    0,
                    # customShapeParam
                    [11.0, 3.0, 0.0, 5.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
                )
            ],
            "r": [
                # thigh right
                (
                    # boneName
                    self.boneThighName,
                    # head
                    Vector((0, 0, 0)),
                    # tail
                    Vector((0, -0.05, -0.43)),
                    # roll
                    -1.5708,
                    # UE4RIGTYPE
                    "LEG_HUMAN",
                    # rotateBone
                    True,
                    # rotationRadian
                    1.5707963705062866,
                    # orientAxis
                    2,
                    # orientRoll
                    0,
                    # customShape
                    True,
                    # customShapeType
                    0,
                    # customShapeParam
                    [18.0, 18.0, 0.0, 22.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
                ),
                # calf right
                (
                    # boneName
                    self.boneCalfName,
                    # head
                    Vector((0, -0.05, -0.43)),
                    # tail
                    Vector((0, -0.01, -0.8)),
                    # roll
                    -1.5708,
                    # UE4RIGTYPE
                    "",
                    # rotateBone
                    True,
                    # rotationRadian
                    1.5707963705062866,
                    # orientAxis
                    2,
                    # orientRoll
                    0,
                    # customShape
                    True,
                    # customShapeType
                    0,
                    # customShapeParam
                    [12.0, 12.0, 0.0, 22.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
                ),
                # foot right
                (
                    # boneName
                    self.boneFootName,
                    # head
                    Vector((0, -0.01, -0.8)),
                    # tail
                    Vector((0.0, -0.17, -0.92)),
                    # roll
                    3.14159,
                    # UE4RIGTYPE
                    "",
                    # rotateBone
                    True,
                    # rotationRadian
                    0,
                    # orientAxis
                    2,
                    # orientRoll
                    -1.5707963705062866,
                    # customShape
                    True,
                    # customShapeType
                    0,
                    # customShapeParam
                    [10.0, 10.0, 0.0, 17.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
                ),
                # ball right
                (
                    # boneName
                    self.boneBallName,
                    # head
                    Vector((0.0, -0.17, -0.92)),
                    # tail
                    Vector((0.0, -0.22, -0.92)),
                    # roll
                    3.14159,
                    # UE4RIGTYPE
                    "",
                    # rotateBone
                    True,
                    # rotationRadian
                    1.5707963705062866,
                    # orientAxis
                    0,
                    # orientRoll
                    -1.5707963705062866,
                    # customShape
                    True,
                    # customShapeType
                    0,
                    # customShapeParam
                    [11.0, 3.0, 0.0, 5.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
                )
            ]
        }

        listBone = []
        for index, data in enumerate(boneData[self.sideBone]):
            boneName, head, tail, roll, ue4rigtype, rotBone, rotRad, orientAxis, orientRoll, customShape, customShapeType, customShapeParam = data

            newBone = editBones.new(self.buildName([self.prefixName, boneName, self.suffixName, self.sideBone]))

            newBone.head = context.scene.cursor.location + head
            newBone.tail = context.scene.cursor.location + tail
            newBone.roll = roll

            newBone["UE4RIGTYPE"] = ue4rigtype
            newBone["rotateBone"] = rotBone
            newBone["rotationRadian"] = rotRad
            newBone["orientAxis"] = orientAxis
            newBone["orientRoll"] = orientRoll

            newBone["customShape"] = customShape
            newBone["customShapeType"] = customShapeType
            newBone["customShapeParam"] = customShapeParam

            if listBone:
                newBone.parent = listBone[index-1]
                newBone.use_connect = True

            listBone.append(newBone)

        if self.parentToBone and activeBone:
            listBone[0].parent = activeBone

        editBones.active = listBone[0]

        if self.sideMirror:
            listBone = []
            for index, data in enumerate(boneData[("r" if self.sideBone == "l" else "l")]):
                boneName, head, tail, roll, ue4rigtype, rotBone, rotRad, orientAxis, orientRoll, customShape, customShapeType, customShapeParam = data

                newBone = editBones.new(self.buildName([self.prefixName, boneName, self.suffixName, ("r" if self.sideBone == "l" else "l")]))

                baseLocation = context.scene.cursor.location.copy()
                baseLocation.x = -baseLocation.x

                newBone.head = baseLocation + head
                newBone.tail = baseLocation + tail
                newBone.roll = roll

                newBone["UE4RIGTYPE"] = ue4rigtype
                newBone["rotateBone"] = rotBone
                newBone["rotationRadian"] = rotRad
                newBone["orientAxis"] = orientAxis
                newBone["orientRoll"] = orientRoll

                newBone["customShape"] = customShape
                newBone["customShapeType"] = customShapeType
                newBone["customShapeParam"] = customShapeParam

                if listBone:
                    newBone.parent = listBone[index-1]
                    newBone.use_connect = True

                listBone.append(newBone)

            if self.parentToBone and activeBone:
                parentSide = editBones.get(activeBone.name[:-1] + ("r" if self.sideBone == "l" else "l"))
                listBone[0].parent = parentSide if parentSide else activeBone

        return {"FINISHED"}

class OP_BoneComponent_Chain(OP_MixBoneComponent):
    bl_idname = "ue4workspace.bonecomponentchain"
    bl_label = "Add CHAIN"
    bl_description = "Add Chain Bone Component"

    boneName: StringProperty(
        name="Bone Name",
        default="chain"
    )

    prefixName: StringProperty(
        name="Prefix Name",
        default=""
    )

    suffixName: StringProperty(
        name="Suffix Name",
        default=""
    )

    sideBone: EnumProperty(
        name="Side Name",
        items=[
            ("NONE", "None", ""),
            ("l", "Left", ""),
            ("r", "Right", "")
        ],
        default=("NONE")
    )

    numberBone: IntProperty(
        name="Number Bone",
        min=2,
        default=2
    )

    sideMirror: BoolProperty(
        name="Mirror Side",
        default=False
    )

    parentToBone: BoolProperty(
        name="Parent To Active Bone",
        default=False
    )

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object
        editBones = activeObject.data.edit_bones
        activeBone = context.active_bone

        listBone = []
        for index in range(1, self.numberBone+1):
            newBone = editBones.new(self.buildName([self.prefixName, self.boneName, self.suffixName, (("0" if index < 10 else "") + str(index)), (self.sideBone if self.sideBone != "NONE" else "")]))

            newBone.head = context.scene.cursor.location
            newBone.tail = context.scene.cursor.location + Vector((0.0, 0.0, 0.2 * index))
            newBone.roll = 0

            newBone["UE4RIGTYPE"] = "COPY_BONE"
            newBone["rotateBone"] = 1
            newBone["rotationRadian"] = 0
            newBone["orientAxis"] = 0
            newBone["orientRoll"] = 0

            newBone["customShape"] = 1
            newBone["customShapeType"] = 0
            newBone["customShapeParam"] = [10.0, 10.0, 0.0, 15.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

            if listBone:
                newBone.parent = listBone[index-2]
                newBone.use_connect = True

            listBone.append(newBone)

        if self.parentToBone and activeBone:
            listBone[0].parent = activeBone

        editBones.active = listBone[0]

        if self.sideMirror and self.sideBone != "NONE":
            listBone = []
            for index in range(1, self.numberBone+1):
                newBoneSide = editBones.new(self.buildName([self.prefixName, self.boneName, self.suffixName, (("0" if index < 10 else "") + str(index)), ("r" if self.sideBone == "l" else "l")]))

                newBoneSide.head = context.scene.cursor.location
                newBoneSide.head.x = -newBoneSide.head.x
                newBoneSide.tail = context.scene.cursor.location + Vector((0.0, 0.0, 0.2 * index))
                newBoneSide.tail.x = -newBoneSide.tail.x
                newBoneSide.roll = 0

                newBoneSide["UE4RIGTYPE"] = "COPY_BONE"
                newBoneSide["rotateBone"] = 1
                newBoneSide["rotationRadian"] = 0
                newBoneSide["orientAxis"] = 0
                newBoneSide["orientRoll"] = 0

                newBoneSide["customShape"] = 1
                newBoneSide["customShapeType"] = 0
                newBoneSide["customShapeParam"] = [10.0, 10.0, 0.0, 15.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

                if listBone:
                    newBoneSide.parent = listBone[index-2]
                    newBoneSide.use_connect = True

                listBone.append(newBoneSide)

            if self.parentToBone and activeBone:
                parentSide = editBones.get(activeBone.name[:-1] + ("r" if self.sideBone == "l" else "l"))
                listBone[0].parent = parentSide if parentSide else activeBone

        return {"FINISHED"}

class OP_BoneComponent_Prop(OP_MixBoneComponent):
    bl_idname = "ue4workspace.bonecomponentprop"
    bl_label = "Add PROP"
    bl_description = "Add Property Bone Component"

    boneName: StringProperty(
        name="Bone Name",
        default="prop"
    )

    prefixName: StringProperty(
        name="Prefix Name",
        default=""
    )

    suffixName: StringProperty(
        name="Suffix Name",
        default=""
    )

    sideBone: EnumProperty(
        name="Side Name",
        items=[
            ("NONE", "None", ""),
            ("l", "Left", ""),
            ("r", "Right", "")
        ],
        default=("NONE")
    )

    sideMirror: BoolProperty(
        name="Mirror Side",
        default=False
    )

    parentToBone: BoolProperty(
        name="Parent To Active Bone",
        default=False
    )

    def execute(self, context):
        preferences = context.preferences.addons[__package__].preferences
        activeObject = context.active_object
        editBones = activeObject.data.edit_bones
        activeBone = context.active_bone

        newBone = editBones.new(self.buildName([self.prefixName, self.boneName, self.suffixName, (self.sideBone if self.sideBone != "NONE" else "")]))

        newBone.head = context.scene.cursor.location
        newBone.tail = context.scene.cursor.location + Vector((0.0, 0.15, 0.0))
        newBone.roll = 0
        newBone.use_deform = False

        newBone["UE4RIGTYPE"] = "PROP"
        newBone["rotateBone"] = 1
        newBone["rotationRadian"] = 0.0
        newBone["orientAxis"] = 0
        newBone["orientRoll"] = 0.0

        newBone["customShape"] = 1
        newBone["customShapeType"] = 0
        newBone["customShapeParam"] = [16.0, 25.0, 0.0, 2.25, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        if self.parentToBone and activeBone:
            newBone.parent = activeBone

        editBones.active = newBone

        if self.sideMirror and self.sideBone != "NONE":
            newBoneSide = editBones.new(self.buildName([self.prefixName, self.boneName, self.suffixName, ("r" if self.sideBone == "l" else "l")]))

            newBoneSide.head = newBone.head
            newBoneSide.head.x = -newBone.head.x
            newBoneSide.tail = newBone.tail
            newBoneSide.tail.x = -newBone.tail.x
            newBoneSide.roll = 0
            newBoneSide.use_deform = False

            newBoneSide["UE4RIGTYPE"] = "PROP"
            newBoneSide["rotateBone"] = 1
            newBoneSide["rotationRadian"] = 0.0
            newBoneSide["orientAxis"] = 0
            newBoneSide["orientRoll"] = 0.0

            newBoneSide["customShape"] = 1
            newBoneSide["customShapeType"] = 0
            newBoneSide["customShapeParam"] = [16.0, 25.0, 0.0, 2.25, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

            if self.parentToBone and activeBone:
                parentSide = editBones.get(activeBone.name[:-1] + ("r" if self.sideBone == "l" else "l"))
                newBoneSide.parent = parentSide if parentSide else activeBone

        return {"FINISHED"}

# operator export

Ops = [
    OP_PoseToAPose,
    OP_ApplyPose,
    OP_BoneComponent_Copy,
    OP_BoneComponent_Pelvis,
    OP_BoneComponent_Spine,
    OP_BoneComponent_Neck,
    OP_BoneComponent_Head,
    OP_BoneComponent_FaceAttach,
    OP_BoneComponent_Jaw,
    OP_BoneComponent_Landmark,
    OP_BoneComponent_Eye,
    OP_BoneComponent_Eyelid,
    OP_BoneComponent_Arm_Human,
    OP_BoneComponent_Finger,
    OP_BoneComponent_Leg_Human,
    OP_BoneComponent_Chain
]