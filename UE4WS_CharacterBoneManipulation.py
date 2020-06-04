import bpy, math

class BoneManipulation:
    """
    Class for bone manipulation

    ...

    Attributes
    ----------
    context : bpy.context
        blender context data
    objectActive : bpy.types.Object
        object data-block defining an object in a scene
    armatureName : str
        original armature name

    Methods
    -------
    getBone(name : str)
        get data bone in edit mode
    poseBone(name : str)
        get data bone in pose mode
    addIKBone()
        add ik bone
    removeTemporaryBone()
        remove temporary bone (bone that have "_temp" in name)
    rotateBone()
        make bone orient same as unreal engine mannequin
    beforeExport()
        do something before export character
        - uncheck deform bone and change bone name
        - rename temporary bone
        - rename vertex group (children mesh)
        - scale to unreal engine mannequin
        - rename armature to root
    afterExport():
        do something after export character
        - remove IK bone
        - rename temporary bone
        - check deform bone and change bone name
        - rename vertex group (children mesh)
        - scale original
        - rename armature to original name
    """

    def __init__(self, context):
        self.context = context
        self.activeObject = context.active_object
        self.armatureName = context.active_object.name

    def getBone(self, name):
        """get data bone in edit mode

        :param name: bone name
        :type name: str
        :returns: Editmode bone in an Armature data-block
        :rtype: bpy.types.EditBone
        """

        return self.activeObject.data.edit_bones.get(name)

    def poseBone(self, name):
        """get data bone in pose mode

        :param name: bone name
        :type name: str
        :returns: Channel defining pose data for a bone in a Pose
        :rtype: bpy.types.PoseBone
        """

        return self.activeObject.pose.bones.get(name)

    def addIKBone(self):
        """add ik bone

        :returns: None
        :rtype: None
        """

        oldMode = self.activeObject.mode
        bpy.ops.object.mode_set(mode="EDIT")

        editBones = self.activeObject.data.edit_bones
        rootBones = ["foot", "hand"]
        sides = ["l", "r"]
        handGun = None

        oldMirror = self.activeObject.data.use_mirror_x
        self.activeObject.data.use_mirror_x = False

        for rootBone in rootBones:
            root = editBones.new("ik_" + rootBone +"_root")
            root.head = (0,0,0)
            root.tail = (0,1.2,0)
            root.roll = 0.0

            if rootBone == "hand" and self.getBone("hand_r") is not None:
                if self.getBone("ik_hand_gun") is None:
                    rightHand = self.getBone("hand_r")
                    gun = editBones.new("ik_hand_gun")
                    handGun = gun
                    gun.head = rightHand.head
                    gun.tail = rightHand.tail
                    gun.roll = rightHand.roll
                    gun.parent = self.getBone("ik_" + rootBone +"_root")

            for side in sides:
                bone = self.getBone(rootBone + "_" + side)
                if bone is not None:
                    if self.getBone("ik_" + rootBone + "_" + side) is None:
                        ik = editBones.new("ik_" + rootBone + "_" + side)
                        ik.head = bone.head
                        ik.tail = bone.tail
                        ik.roll = bone.roll
                        ik.parent = (self.getBone("ik_" + rootBone +"_root"), handGun)[handGun is not None]

        bpy.ops.armature.select_all(action="DESELECT")

        self.activeObject.data.use_mirror_x = oldMirror
        bpy.ops.object.mode_set(mode=oldMode)

    def removeTemporaryBone(self):
        """remove temporary bone (bone that have "_temp" in name)

        :returns: None
        :rtype: None
        """

        oldMode = self.activeObject.mode
        bpy.ops.object.mode_set(mode="EDIT")

        bpy.ops.armature.select_all(action="DESELECT")

        editBones = self.activeObject.data.edit_bones

        # remove temporary bone
        for bone in [bone for bone in editBones if bone.name.endswith("_temp")]:
            editBones.remove(bone)

        bpy.ops.object.mode_set(mode=oldMode)

    def rotateBone(self):
        """make bone orient same as unreal engine mannequin

        :returns: None
        :rtype: None
        """

        oldMode = self.activeObject.mode
        bpy.ops.object.mode_set(mode="EDIT")

        bpy.ops.armature.select_all(action="DESELECT")

        editBones = self.activeObject.data.edit_bones
        oldPivot = self.context.scene.tool_settings.transform_pivot_point
        oldMirror = self.activeObject.data.use_mirror_x

        self.activeObject.data.use_mirror_x = False
        self.context.scene.tool_settings.transform_pivot_point = "ACTIVE_ELEMENT"

        # remove temporary bone
        for bone in [bone for bone in editBones if bone.name.endswith("_temp")]:
            editBones.remove(bone)

        # for check bone name purpose
        arrFingersName = ["thumb", "index", "middle", "ring", "pinky"]
        # dict bone to add
        # bone name :
        # - copy : [head bone location, tail bone location, roll bone]
        # - props : [rotate, roll bone, orient axis]
        bonesToAdd = {}
        # Bones orient info
        #                   rotate(0 = no side bone or left side, 1 = right side)
        #                                                  roll bone(0 = no side bone or left side, 1 = right side)          
        #                                                                                             orient axis
        bonesOrient = {
            "pelvis"   : [  [-math.pi/2]               ,   [math.radians(-90)]                       ,   "X"  ],
            "spine"    : [  [-math.pi/2]               ,   [math.radians(-90)]                       ,   "X"  ],
            "neck"     : [  [-math.pi/2]               ,   [math.radians(-90)]                       ,   "X"  ],
            "head"     : [  [-math.pi/2]               ,   [math.radians(-90)]                       ,   "X"  ],
            "clavicle" : [  [-math.pi/2]               ,   [math.radians(180)  , math.radians(0)]    ,   "Z"  ],
            "upperarm" : [  [-math.pi/2]               ,   [math.radians(180)  , math.radians(0)]    ,   "Z"  ],
            "lowerarm" : [  [-math.pi/2]               ,   [math.radians(180)  , math.radians(0)]    ,   "Z"  ],
            "hand"     : [  [-math.pi/2  , math.pi/2]  ,   [math.radians(-90)]                       ,   "X"  ],
            "finger"   : [  [-math.pi/2  , math.pi/2]  ,   [math.radians(-90)]                       ,   "X"  ],
            "thigh"    : [  [math.pi/2]                ,   [math.radians(180)  , math.radians(0)]    ,   "Z"  ],
            "calf"     : [  [math.pi/2]                ,   [math.radians(180)  , math.radians(0)]    ,   "Z"  ],
            "foot"     : [  [math.pi     , 0.0]        ,   [math.radians(90)   , math.radians(-90)]  ,   "Z"  ],
            "ball"     : [  [-math.pi/2  , math.pi/2]  ,   [math.radians(-90)]                       ,   "X"  ]
        }

        # set bone info for dict bonesToAdd
        for bone in editBones:
            boneName = bone.name.split("_")

            # only bone in dict bonesOrient will rotate
            orient = bonesOrient.get((boneName[0], "finger")[boneName[0] in arrFingersName])
            if orient is not None:
                # check if has side (left = 0, right = 1), otherwise will None
                side = None
                if boneName[-1] in ["l", "r"]:
                    side = (1 , 0)[boneName[-1] == "l"]
                # arr index 0 = rotate, 1 = roll bone, and 2 = orient axis
                arrProps = []
                # set 0 = rotate and 1 = roll bone depend on side
                for i in range(2):
                    arrProps.append(orient[i][(0, side)[len(orient[i]) > 1 and side is not None]])
                # set 2 = orient axis
                arrProps.append(orient[2])

                # add to bonesToAdd
                bonesToAdd[bone.name] = {}
                bonesToAdd[bone.name]["copy"] = bone.head.copy(), bone.tail.copy(), bone.roll
                bonesToAdd[bone.name]["props"] = arrProps

        for boneName in bonesToAdd:
            bone = bonesToAdd[boneName]
            if self.getBone(boneName + "_temp") is None:
                # create new temporary bone
                newBone = editBones.new(boneName + "_temp")
                newBone.head = bone["copy"][0]
                newBone.tail = bone["copy"][1]
                newBone.roll = bone["copy"][2]

                bpy.ops.armature.select_all(action="DESELECT")
                editBones.active = newBone
                editBones.active.select = True

                bpy.ops.object.mode_set(mode="POSE")
                bpy.ops.object.mode_set(mode="EDIT")

                boneTemp = self.getBone(boneName + "_temp")

                bpy.ops.transform.rotate(value=-bone["props"][0], orient_axis=bone["props"][2], orient_type="NORMAL", mirror=False)

                boneTemp.roll += bone["props"][1]

                if boneName.startswith("foot"):
                    boneTemp.tail[2] += (boneTemp.head[2]-boneTemp.tail[2])*0.95
                    bpy.ops.armature.select_all(action="DESELECT")
                    boneTemp.select = True
                    boneTemp.select_head = True
                    boneTemp.select_tail = True
                    bpy.ops.armature.calculate_roll(type="GLOBAL_NEG_X")
                elif boneName.startswith("ball"):
                    boneTemp.tail[1] = boneTemp.head[1]
                    boneTemp.tail[0] = boneTemp.head[0]
                elif boneName in ["spine_01", "spine_02", "spine_03"]:
                    boneTemp.tail[2] = boneTemp.head[2]
                    bpy.ops.transform.rotate(value=-math.radians((-7, 8)[boneName in ["spine_02", "spine_03"]]), orient_axis="Z", orient_type="NORMAL", mirror=False)

                # set parent
                if "pelvis" != boneName:
                    parentBoneName = self.getBone(boneName).parent.name
                    boneTemp.parent = self.getBone(parentBoneName + "_temp")

        bpy.ops.armature.select_all(action="DESELECT")

        for boneName in bonesToAdd:
            bone = self.getBone(boneName + "_temp")
            if bone is not None:
                bone.select = True
                bone.select_head = True
                bone.select_tail = True

        # move orient bone to last layer
        bpy.ops.armature.bone_layers(layers=(False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True))
        bpy.ops.armature.select_all(action="DESELECT")

        self.context.scene.tool_settings.transform_pivot_point = oldPivot
        self.activeObject.data.use_mirror_x = oldMirror
        bpy.ops.object.mode_set(mode=oldMode)

    def beforeExport(self):
        """do something before export character
        - uncheck deform bone and change bone name
        - rename temporary bone
        - rename vertex group (children mesh)
        - add IK bone
        - scale to unreal engine mannequin
        - rename armature to root

        :returns: None
        :rtype: None
        """

        oldMode = self.activeObject.mode
        bpy.ops.object.mode_set(mode="EDIT")

        bpy.ops.armature.select_all(action="DESELECT")
        oldMirror = self.activeObject.data.use_mirror_x
        self.activeObject.data.use_mirror_x = False

        # uncheck deform bone and change bone name
        bonesName = ("pelvis", "spine", "neck", "head", "clavicle", "upperarm", "lowerarm", "hand", "thumb", "index", "middle", "ring", "pinky", "thigh", "calf", "foot", "ball")
        for bone in [bone for bone in self.activeObject.data.edit_bones if bone.name.startswith(bonesName) and not bone.name.endswith("_temp")]:
            bone.use_deform = False
            bone.name = bone.name + "_ORIGINAL"
        # rename temporary bone
        for bone in [bone for bone in self.activeObject.data.edit_bones if bone.name.endswith("_temp")]:
            bone.name = bone.name.replace("_temp", "")
        # rename vertex group (children mesh) because rename bone also affect vertex group name
        for mesh in [mesh for mesh in self.activeObject.children if mesh.type == "MESH"]:
            for group in [group for group in mesh.vertex_groups if group.name.endswith("_ORIGINAL")]:
                group.name = group.name.replace("_ORIGINAL", "")

        self.activeObject.data.use_mirror_x = oldMirror
        bpy.ops.object.mode_set(mode="OBJECT")
        # add IK bone
        self.addIKBone()
        # Deselect all object
        bpy.ops.object.select_all(action="DESELECT")
        # scale to unreal engine mannequin
        self.activeObject.select_set(state=True)
        self.activeObject.scale = (100, 100, 100)
        bpy.ops.object.transform_apply(location = False, scale = True, rotation = False)
        self.activeObject.scale = (0.01, 0.01, 0.01)
        self.activeObject.select_set(state=False)
        # rename armature to root
        self.activeObject.name = "root"
        bpy.ops.object.mode_set(mode=oldMode)

    def afterExport(self):
        """do something after export character
        - remove IK bone
        - rename temporary bone
        - check deform bone and change bone name
        - rename vertex group (children mesh)
        - scale original
        - rename armature to original name
        """

        oldMode = self.activeObject.mode
        bpy.ops.object.mode_set(mode="EDIT")

        editBones = self.activeObject.data.edit_bones
        oldMirror = self.activeObject.data.use_mirror_x
        self.activeObject.data.use_mirror_x = False

        # remove IK bone
        IKBonesName = ["ik_hand_l", "ik_hand_r", "ik_foot_l", "ik_foot_r", "ik_hand_gun", "ik_hand_root", "ik_foot_root"]
        for boneName in IKBonesName:
            bone = self.getBone(boneName)
            if bone is not None:
                editBones.remove(bone)
        # rename temporary bone
        bonesName = ("pelvis", "spine", "neck", "head", "clavicle", "upperarm", "lowerarm", "hand", "thumb", "index", "middle", "ring", "pinky", "thigh", "calf", "foot", "ball")
        for bone in [bone for bone in self.activeObject.data.edit_bones if bone.name.startswith(bonesName) and not bone.name.endswith("_ORIGINAL")]:
            bone.name = bone.name + "_temp"
        # check deform bone and change bone name
        for bone in [bone for bone in self.activeObject.data.edit_bones if bone.name.startswith(bonesName) and bone.name.endswith("_ORIGINAL")]:
            bone.use_deform = True
            bone.name = bone.name.replace("_ORIGINAL", "")
        # rename vertex group (children mesh) because rename bone also affect vertex group name
        for mesh in [mesh for mesh in self.activeObject.children if mesh.type == "MESH"]:
            for group in [group for group in mesh.vertex_groups if group.name.endswith("_temp")]:
                group.name = group.name.replace("_temp", "")

        self.activeObject.data.use_mirror_x = oldMirror

        bpy.ops.object.mode_set(mode="OBJECT")
        # Deselect all object
        bpy.ops.object.select_all(action="DESELECT")
        # scale original
        self.activeObject.select_set(state=True)
        bpy.ops.object.transform_apply(location = False, scale = True, rotation = False)
        self.activeObject.select_set(state=False)
        # rename armature to original name
        self.activeObject.name = self.armatureName

        bpy.ops.object.mode_set(mode=oldMode)
