import bpy, math
from mathutils import (Matrix, Vector)
from . import boneShape
import inspect

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
        remove temporary bone (bone that have "TWEAK_" in name)
    rotateBone()
        make bone orient same as unreal engine mannequin
    beforeExport()
        do something before export character
        - unparent socket
        - uncheck deform bone and change bone name
        - rename temporary bone
        - rename vertex group (children mesh)
        - add IK bone
        - scale to unreal engine mannequin
        - restore socket
        - rename armature to root
    afterExport():
        do something after export character
        - unparent socket
        - remove IK bone
        - rename temporary bone
        - check deform bone and change bone name
        - rename vertex group (children mesh)
        - scale original
        - restore socket
        - rename armature to original name
    spineRecursiveBone(children : bpy.types.PoseBone, collection : bpy.types.Collection, vertices : list tuple, edges : list tuple, group : bpy.types.BoneGroup):
        recursive function to make custom shape to spine
    neckRecursiveBone(children : bpy.types.PoseBone, collection : bpy.types.Collection, vertices : list tuple, edges : list tuple, group : bpy.types.BoneGroup):
        recursive function to make custom shape to neck
    generateRig():
        generate rig
        - uncheck deform bone and change bone name
        - rename temporary bone and make copy bone
        - rename vertex group (children mesh)
        - add IK bone if humanoid
        - create bone control and custom shape
        - scale to unreal engine mannequin
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

    # https://blender.stackexchange.com/questions/19754/how-to-set-calculate-pole-angle-of-ik-constraint-so-the-chain-does-not-move
    def signed_angle(self, vector_u, vector_v, normal):
        # Normal specifies orientation
        angle = vector_u.angle(vector_v)
        if vector_u.cross(vector_v).angle(normal) < 1:
            angle = -angle
        return angle

    def get_pole_angle(self, base_bone, ik_bone, pole_location):
        pole_normal = (ik_bone.tail - base_bone.head).cross(pole_location - base_bone.head)
        projected_pole_axis = pole_normal.cross(base_bone.tail - base_bone.head)
        return self.signed_angle(base_bone.x_axis, projected_pole_axis, base_bone.tail - base_bone.head)

    def moveBoneLayer(self, boneList, layerList):
        """move bone layer in edit mode

        :param name: boneList
        :type name: list[(editBones)]
        :param name: layerList
        :type name: list[(int)]
        :returns: None
        :rtype: None
        """

        for bone in boneList:
            bone.select = True
            bone.select_head = True
            bone.select_tail = True
        bpy.ops.armature.bone_layers(layers=tuple([(i in layerList) for i in range(32)]))
        bpy.ops.armature.select_all(action="DESELECT")

    def generateCustomBoneShape(self, poseBone, collection, boneShape, boneGroup, scaleBone = False):
        """generate custom bone

        :param name: poseBone
        :type name: poseBone
        :param name: collection
        :type name: collection
        :param name: boneShape
        :type name: [[vertices], [edges], [face]]
        :param name: boneGroup
        :type name: boneGroup
        :param name: scaleBone
        :type name: boolean
        :returns: None
        :rtype: None
        """
        mesh = bpy.data.meshes.new("UE4WSBS_" + poseBone.name)
        objShape = bpy.data.objects.new("UE4WSBS_" + poseBone.name,mesh)
        collection.objects.link(objShape)
        mesh.from_pydata(*boneShape)

        poseBone.custom_shape = objShape
        poseBone.use_custom_shape_bone_size = scaleBone
        poseBone.bone_group = boneGroup

    def addFloorConstraint(self, poseBone, floorBoneName, offset):
        """create floor constraint to poseBone

        :param name: poseBone
        :type name: poseBone
        :param name: floorBoneName
        :type name: string
        :param name: offset
        :type name: int
        :returns: None
        :rtype: None
        """

        floorConstarint = poseBone.constraints.new("FLOOR")
        floorConstarint.name = "FLOOR"
        floorConstarint.show_expanded = False
        floorConstarint.target = self.activeObject
        floorConstarint.subtarget = floorBoneName
        floorConstarint.offset = offset
        floorConstarint.use_rotation = True
        floorConstarint.target_space = "POSE"
        floorConstarint.owner_space = "POSE"

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
            self.moveBoneLayer([root], [31])

            if rootBone == "hand" and self.getBone("hand_r") is not None:
                if self.getBone("ik_hand_gun") is None:
                    rightHand = self.getBone("hand_r")
                    gun = editBones.new("ik_hand_gun")
                    handGun = gun
                    gun.head = rightHand.head
                    gun.tail = rightHand.tail
                    gun.roll = rightHand.roll
                    gun.parent = self.getBone("ik_" + rootBone +"_root")
                    self.moveBoneLayer([gun], [31])

            for side in sides:
                bone = self.getBone(rootBone + "_" + side)
                if bone is not None:
                    if self.getBone("ik_" + rootBone + "_" + side) is None:
                        ik = editBones.new("ik_" + rootBone + "_" + side)
                        ik.head = bone.head
                        ik.tail = bone.tail
                        ik.roll = bone.roll
                        ik.parent = (self.getBone("ik_" + rootBone +"_root"), handGun)[handGun is not None]
                        self.moveBoneLayer([ik], [31])

        bpy.ops.armature.select_all(action="DESELECT")

        self.activeObject.data.use_mirror_x = oldMirror
        bpy.ops.object.mode_set(mode=oldMode)

    def removeTemporaryBone(self):
        """remove temporary bone (bone that have "ORIENT_" in name)

        :returns: None
        :rtype: None
        """

        oldMode = self.activeObject.mode
        bpy.ops.object.mode_set(mode="EDIT")

        bpy.ops.armature.select_all(action="DESELECT")

        editBones = self.activeObject.data.edit_bones

        # remove temporary bone
        for bone in [bone for bone in editBones if bone.name.startswith("ORIENT_")]:
            for chidlBone in [chidlBone for chidlBone in bone.children if not chidlBone.name.startswith("ORIENT_")]:
                chidlBone.parent = editBones.get(bone.name.replace("ORIENT_", ""))
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
        for bone in [bone for bone in editBones if bone.name.startswith("ORIENT_")]:
            for chidlBone in [chidlBone for chidlBone in bone.children if not chidlBone.name.startswith("ORIENT_")]:
                chidlBone.parent = editBones.get(bone.name.replace("ORIENT_", ""))
            editBones.remove(bone)

        # filter bone and parent for custom bone, tuple: (bone: editBones, parentName: str)
        customBones = [(editBone, editBone.parent.name) for editBone in editBones if editBone.get("rotateBone", None) is None and editBone.parent is not None and editBone.parent.get("rotateBone", False)]

        for bone in [editBone for editBone in editBones if self.activeObject.data.bones[editBone.name].rotateBone]:
            if self.getBone("ORIENT_" + bone.name) is None:
                # create new temporary bone
                newBone = editBones.new("ORIENT_" + bone.name)
                newBone.head = bone.head
                newBone.tail = bone.tail
                newBone.roll = bone.roll
                newBone.use_deform = bone.use_deform

                # rotate active bone
                bpy.ops.armature.select_all(action="DESELECT")
                editBones.active = newBone
                editBones.active.select = True
                editBones.active.select_head = True
                editBones.active.select_tail = True

                dataBone = self.activeObject.data.bones[bone.name]

                # bug on blender version 2.83
                # https://github.com/anasrar/Blender-UE4-Workspace/issues/5
                # https://blenderartists.org/t/why-i-got-difference-rotate-bone-result-in-version-2-82-and-2-83/1234794
                # I assume this bug wrong rotation bone only in 2.83 LTS version, so i decide to reverse the bone rotation only on 2.83 LTS
                rotationRadian = dataBone.rotationRadian if bpy.app.version[0:2] in [(2, 83)] else -dataBone.rotationRadian
                bpy.ops.transform.rotate(value=rotationRadian, orient_axis=dataBone.orientAxis, orient_type="NORMAL", mirror=False)
                # add roll
                newBone.roll += dataBone.orientRoll

                # move orient bone to last layer
                bpy.ops.armature.bone_layers(layers=(False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True))

                parentLists = bone.parent_recursive

                # FOOT
                if len(parentLists) > 1 and parentLists[1].get("UE4RIGTYPE") == "LEG_HUMAN":
                    newBone.tail[2] += (newBone.head[2]-newBone.tail[2])*0.95
                    bpy.ops.armature.select_all(action="DESELECT")
                    newBone.select = True
                    newBone.select_head = True
                    newBone.select_tail = True
                    bpy.ops.armature.calculate_roll(type="GLOBAL_NEG_X")
                # BALL
                elif len(parentLists) > 2 and parentLists[2].get("UE4RIGTYPE") == "LEG_HUMAN":
                    newBone.tail[1] = newBone.head[1]
                    newBone.tail[0] = newBone.head[0]
                # FACE JAW HUMANOID
                elif bone.get("UE4RIGTYPE") == "JAW":
                    newBone.tail[0] = newBone.head[0]
                    newBone.tail[1] = newBone.head[1] + bone.length
                    newBone.tail[2] = newBone.head[2]
                    newBone.roll = 0

                # set length bone
                newBone.length = 0.1 if newBone.length >= 0.1 else newBone.length

                # set parent
                if bone.parent:
                    orientBone = self.getBone("ORIENT_" + bone.parent.name)
                    newBone.parent = orientBone if orientBone else bone.parent

        # restore custom bone parent
        for editBone, parentName in customBones:
            editBone.parent = editBones.get("ORIENT_" + parentName)

        bpy.ops.armature.select_all(action="DESELECT")
        self.activeObject.data.layers[31] = True

        self.context.scene.tool_settings.transform_pivot_point = oldPivot
        self.activeObject.data.use_mirror_x = oldMirror
        bpy.ops.object.mode_set(mode=oldMode)

    def beforeExport(self):
        """do something before export character
        - unparent socket
        - uncheck deform bone and change bone name
        - rename temporary bone
        - rename vertex group (children mesh)
        - add IK bone
        - scale to unreal engine mannequin
        - restore socket
        - rename armature to root

        :returns: None
        :rtype: None
        """

        oldMode = self.activeObject.mode
        bpy.ops.object.mode_set(mode="EDIT")

        bpy.ops.armature.select_all(action="DESELECT")
        oldMirror = self.activeObject.data.use_mirror_x
        self.activeObject.data.use_mirror_x = False

        # unparent socket
        socketObjects = [obj for obj in self.activeObject.children if obj.type == "EMPTY" and obj.get("isSocket")]
        # socket info for restore (dict {socketObj, parent_type, parent_bone})
        socketArrInfo = []
        for socketObj in socketObjects:
            socketArrInfo.append({
                "socketObj": socketObj,
                "parent_type": socketObj.parent_type,
                "parent_bone": socketObj.parent_bone
            })
            socketObj.parent = None

        # uncheck deform bone and change bone name
        for bone in [bone for bone in self.activeObject.data.edit_bones if bone.get("boneOrient", False)]:
            bone.use_deform = False
            bone.name = "TWEAK_" + bone.name
        # rename temporary bone
        for bone in [bone for bone in self.activeObject.data.edit_bones if bone.name.startswith("ORIENT_")]:
            bone.name = bone.name.replace("ORIENT_", "")
        # rename vertex group (children mesh) because rename bone also affect vertex group name
        for mesh in [mesh for mesh in self.activeObject.children if mesh.type == "MESH"]:
            for group in [group for group in mesh.vertex_groups if group.name.startswith("TWEAK_")]:
                group.name = group.name.replace("TWEAK_", "")

        self.activeObject.data.use_mirror_x = oldMirror
        bpy.ops.object.mode_set(mode="OBJECT")
        # add IK bone
        if self.activeObject.get("UE4RIGTYPE") == "HUMANOID":
            self.addIKBone()
        # Deselect all object
        bpy.ops.object.select_all(action="DESELECT")
        # scale to unreal engine mannequin
        self.activeObject.select_set(state=True)
        self.activeObject.scale = (100, 100, 100)
        bpy.ops.object.transform_apply(location = False, scale = True, rotation = False)
        self.activeObject.scale = (0.01, 0.01, 0.01)
        self.activeObject.select_set(state=False)

        # restore socket
        for socketDict in socketArrInfo:
            socketObj = socketDict["socketObj"]
            socketObj.parent = self.activeObject
            socketObj.parent_type = socketDict["parent_type"]
            if socketDict["parent_type"] == "BONE":
                socketObj.parent_bone = socketDict["parent_bone"]
                bone = self.poseBone(socketDict["parent_bone"])
                if bone:
                    socketObj.matrix_parent_inverse = (self.activeObject.matrix_world @ Matrix.Translation(bone.tail - bone.head) @ bone.matrix).inverted() @ Matrix.Scale(100, 4)
            else:
                socketObj.matrix_parent_inverse = self.activeObject.matrix_world.inverted()

        # rename armature to root
        self.activeObject.name = "root"
        bpy.ops.object.mode_set(mode=oldMode)

    def afterExport(self):
        """do something after export character
        - unparent socket
        - remove IK bone
        - rename temporary bone
        - check deform bone and change bone name
        - rename vertex group (children mesh)
        - scale original
        - restore socket
        - rename armature to original name
        """

        oldMode = self.activeObject.mode
        bpy.ops.object.mode_set(mode="EDIT")

        # unparent socket
        socketObjects = [obj for obj in self.activeObject.children if obj.type == "EMPTY" and obj.get("isSocket")]
        # socket info for restore (dict {socketObj, parent_type, parent_bone})
        socketArrInfo = []
        for socketObj in socketObjects:
            socketArrInfo.append({
                "socketObj": socketObj,
                "parent_type": socketObj.parent_type,
                "parent_bone": socketObj.parent_bone
            })
            socketObj.parent = None

        editBones = self.activeObject.data.edit_bones
        oldMirror = self.activeObject.data.use_mirror_x
        self.activeObject.data.use_mirror_x = False

        # remove IK bone
        if self.activeObject.get("UE4RIGTYPE") == "HUMANOID":
            IKBonesName = ["ik_hand_l", "ik_hand_r", "ik_foot_l", "ik_foot_r", "ik_hand_gun", "ik_hand_root", "ik_foot_root"]
            for boneName in IKBonesName:
                bone = self.getBone(boneName)
                if bone is not None:
                    editBones.remove(bone)
        # rename temporary bone check deform bone
        for bone in [bone for bone in editBones if bone.name.startswith("TWEAK_") and bone.get("boneOrient", False)]:
            orientBone = self.getBone(bone.name.replace("TWEAK_", ""))
            orientBone.name = "ORIENT_" + orientBone.name
            bone.use_deform = True
            bone.name = bone.name.replace("TWEAK_", "")
        # rename vertex group (children mesh) because rename bone also affect vertex group name
        for mesh in [mesh for mesh in self.activeObject.children if mesh.type == "MESH"]:
            for group in [group for group in mesh.vertex_groups if group.name.startswith("ORIENT_")]:
                group.name = group.name.replace("ORIENT_", "")

        self.activeObject.data.use_mirror_x = oldMirror

        bpy.ops.object.mode_set(mode="OBJECT")
        # Deselect all object
        bpy.ops.object.select_all(action="DESELECT")
        # scale original
        self.activeObject.select_set(state=True)
        bpy.ops.object.transform_apply(location = False, scale = True, rotation = False)
        self.activeObject.select_set(state=False)

        # restore socket
        for socketDict in socketArrInfo:
            socketObj = socketDict["socketObj"]
            socketObj.parent = self.activeObject
            socketObj.parent_type = socketDict["parent_type"]
            if socketDict["parent_type"] == "BONE":
                socketObj.parent_bone = socketDict["parent_bone"]
                bone = self.poseBone(socketDict["parent_bone"])
                if bone:
                    socketObj.matrix_parent_inverse = (self.activeObject.matrix_world @ Matrix.Translation(bone.tail - bone.head) @ bone.matrix).inverted()
            else:
                socketObj.matrix_parent_inverse = self.activeObject.matrix_world.inverted()

        # rename armature to original name
        self.activeObject.name = self.armatureName

        bpy.ops.object.mode_set(mode=oldMode)

    def generateRig(self):
        """generate rig
        - uncheck deform bone and change bone name
        - rename temporary bone and make copy bone
        - rename vertex group (children mesh)
        - add IK bone if humanoid
        - create bone control and custom shape
        - scale to unreal engine mannequin
        - set inverse for eyelid

        :returns: None
        :rtype: None
        """

        oldMode = self.activeObject.mode
        bpy.ops.object.mode_set(mode="EDIT")
        editBones = self.activeObject.data.edit_bones

        bpy.ops.armature.select_all(action="DESELECT")
        oldMirror = self.activeObject.data.use_mirror_x
        self.activeObject.data.use_mirror_x = False

        # uncheck deform bone and change bone name
        for bone in [bone for bone in editBones if bone.get("rotateBone", False)]:
            bone.use_deform = False
            bone.name = "TWEAK_" + bone.name
        # rename temporary bone and make copy bone
        for bone in [bone for bone in editBones if bone.name.startswith("ORIENT_")]:
            bone.name = bone.name.replace("ORIENT_", "")
            copyBone = editBones.new("TARGET_" + bone.name)
            copyBone.use_deform = False
            copyBone.head = bone.head
            copyBone.tail = bone.tail
            copyBone.roll = bone.roll
            copyBone.parent = editBones.get("TWEAK_" + bone.name)
            copyBone.select = True
            copyBone.select_head = True
            copyBone.select_tail = True
            bpy.ops.armature.bone_layers(layers=(False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False))
            copyBone.select = False
            copyBone.select_head = False
            copyBone.select_tail = False
        # rename vertex group (children mesh) because rename bone also affect vertex group name
        for mesh in [mesh for mesh in self.activeObject.children if mesh.type == "MESH"]:
            for group in [group for group in mesh.vertex_groups if group.name.startswith("TWEAK_")]:
                group.name = group.name.replace("TWEAK_", "")

        self.activeObject.data.use_mirror_x = oldMirror
        bpy.ops.object.mode_set(mode="OBJECT")
        # add IK bone if humanoid
        if self.activeObject.data.UE4RIGTYPE == "HUMANOID":
            self.addIKBone()
        # create group bone
        boneGroups = self.activeObject.pose.bone_groups
        redGroup = boneGroups.new(name="red")
        redGroup.color_set = "CUSTOM"
        redGroup.colors.select = [0.9, 0.0, 0.0]
        redGroup.colors.normal = [0.8, 0.0, 0.0]
        redGroup.colors.active = [1, 0.0, 0.0]

        greenGroup = boneGroups.new(name="green")
        greenGroup.color_set = "CUSTOM"
        greenGroup.colors.select = [0.0, 0.9, 0.0]
        greenGroup.colors.normal = [0.0, 0.8, 0.0]
        greenGroup.colors.active = [0.0, 1, 0.0]

        yellowGroup = boneGroups.new(name="yellow")
        yellowGroup.color_set = "CUSTOM"
        yellowGroup.colors.select = [0.8, 0.8, 0.0]
        yellowGroup.colors.normal = [0.7, 0.7, 0.0]
        yellowGroup.colors.active = [1.0, 1.0, 0.0]

        blueGroup = boneGroups.new(name="blue")
        blueGroup.color_set = "CUSTOM"
        blueGroup.colors.select = [0.0, 0.3, 0.7]
        blueGroup.colors.normal = [0.0, 0.3, 0.5]
        blueGroup.colors.active = [0.0, 0.5, 1]

        leftSideGroup = boneGroups.new(name="leftSide")
        leftSideGroup.color_set = "CUSTOM"
        leftSideGroup.colors.select = [0.0, 0.4, 0.9]
        leftSideGroup.colors.normal = [0.0, 0.55, 0.9]
        leftSideGroup.colors.active = [0.0, 0.5, 1.0]

        rightSideGroup = boneGroups.new(name="rightSide")
        rightSideGroup.color_set = "CUSTOM"
        rightSideGroup.colors.select = [0.95, 0.57, 0.0]
        rightSideGroup.colors.normal = [0.93, 0.56, 0.0]
        rightSideGroup.colors.active = [1.0, 0.6, 0.0]

        propGroup = boneGroups.new(name="prop")
        propGroup.color_set = "CUSTOM"
        propGroup.colors.select = [1.0, 0.1, 0.95]
        propGroup.colors.normal = [0.95, 0.0, 1.0]
        propGroup.colors.active = [1.0, 0.0, 0.925]

        # add control bone
        bpy.ops.object.mode_set(mode="EDIT")
        # collection
        collection = bpy.data.collections.get("UE4WSBoneShape", False)
        if (not collection):
            collection = bpy.data.collections.new("UE4WSBoneShape")
            self.context.scene.collection.children.link(collection)
        # exclude bone shape collection and hide
        collection.hide_viewport = True
        self.context.view_layer.layer_collection.children.get(collection.name).exclude = True

        self.activeObject.data.use_mirror_x = False
        oldPivot = self.context.scene.tool_settings.transform_pivot_point
        self.context.scene.tool_settings.transform_pivot_point = "MEDIAN_POINT"

        # ROOT BONE
        if not editBones.get("root"):
            root = editBones.new("root")
            root.head = [0, 0, 0]
            root.tail = [0, 0.05, 0]
            root.roll = 0
            for bone in [bone for bone in editBones if bone.parent is None and bone.name != "root"]:
                bone.parent = root

            mesh = bpy.data.meshes.new("UE4WSBS_root")
            objRootShape = bpy.data.objects.new(mesh.name,mesh)
            collection.objects.link(objRootShape)
            mesh.from_pydata(*boneShape.root())
            bpy.ops.object.mode_set(mode="POSE")
            poseBone = self.poseBone("root")
            if poseBone is None:
               poseBone = self.poseBone("root")
            poseBone.custom_shape = objRootShape
            poseBone.use_custom_shape_bone_size = False
            poseBone.bone_group = redGroup
            bpy.ops.object.mode_set(mode="EDIT")

        # FINGER
        for bone in [bone for bone in editBones if bone.get("UE4RIGTYPE") == "FINGER"]:
            bpy.ops.armature.select_all(action="DESELECT")
            boneName = bone.name
            # CONTROL BONE
            control = editBones.new(boneName.replace("TWEAK_", "CONTROL_"))
            control.use_deform = False
            control.head = bone.head + (bone.z_axis * 0.025)
            control.tail = bone.tail + (bone.z_axis * 0.025)
            control.roll = bone.roll
            control.length = 0.05
            control.parent = bone.parent
            bone["subtargetRotation"] = control.name
            # CONTROL IK BONE
            # filter children with starts string "TWEAK_"
            filterChildren = [bone for bone in bone.children_recursive if bone.name.startswith("TWEAK_") and not bone.get("UE4RIGTYPE")]
            # get index bone that have RIGTYPE
            endIndex = next((index for (index, bn) in enumerate(filterChildren) if bn.get("UE4RIGTYPE")), None)
            if endIndex is not None:
                filterChildren = filterChildren[:endIndex:]
            for bn in filterChildren:
                bn.use_connect = False
            lastChildBone = filterChildren[-1]
            ikControl = editBones.new(boneName.replace("TWEAK_", "IKTARGET_"))
            ikControl.use_deform = False
            ikControl.head = lastChildBone.tail
            ikControl.tail = lastChildBone.tail + (lastChildBone.y_axis * 0.05)
            ikControl.roll = lastChildBone.roll
            ikControl.length = 0.05
            ikControl.parent = bone.parent
            self.moveBoneLayer([control, ikControl], [0])
            bone["subtargetIK"] = ikControl.name

        # LEG_HUMAN
        for bone in [bone for bone in editBones if bone.get("UE4RIGTYPE") == "LEG_HUMAN"]:
            bone.use_connect = False
            bpy.ops.armature.select_all(action="DESELECT")
            boneName = bone.name
            # POLE BONE
            canCreatePole = [bn for bn in bone.children if bn.name.startswith("TWEAK_") and not bn.get("UE4RIGTYPE") and not "_twist_" in bn.name]
            if canCreatePole:
                calfBone = canCreatePole[0]
                calfBone.use_connect = False

                # CHECK IF FOOT AND TOE EXIST
                footBone = [bn for bn in calfBone.children if bn.name.startswith("TWEAK_") and not bn.get("UE4RIGTYPE") and not "_twist_" in bn.name]
                footBone = footBone[0] if footBone else None
                toeBone = [bn for bn in footBone.children if bn.name.startswith("TWEAK_") and not bn.get("UE4RIGTYPE") and not "_twist_" in bn.name] if footBone else None
                toeBone = toeBone[0] if toeBone else None

                vA = calfBone.vector
                vB = calfBone.tail - bone.head

                vElbow = (vA.project(vB) - vA).normalized() * vB.length

                pole = editBones.new(boneName.replace("TWEAK_", "IKPOLE_"))
                pole.use_deform = False
                pole.head = bone.tail + vElbow
                pole.tail = pole.head - vElbow/8
                pole.roll = 0
                pole.length = 0.25

                # VIS POLE
                visPole = editBones.new(calfBone.name.replace("TWEAK_", "VISPOLE_"))
                visPole.use_deform = False
                visPole.head = pole.head
                visPole.tail = calfBone.head
                visPole.roll = 0

                # IK TARGET BONE
                ikTarget = editBones.new(calfBone.name.replace("TWEAK_", "IKTARGET_"))
                ikTarget.use_deform = False
                ikTarget.head = calfBone.tail if not footBone else footBone.head
                ikTarget.tail = (calfBone.tail + Vector((0, 0.15, 0))) if not footBone else footBone.tail
                ikTarget.roll = 0 if not footBone else footBone.roll
                # CONTROLLER BONE
                control = editBones.new((calfBone.name.replace("TWEAK_", "CONTROL_") if not footBone else footBone.name.replace("TWEAK_", "CONTROL_")))
                control.use_deform = False
                control.head = calfBone.tail if not footBone else footBone.head
                control.tail = control.head + Vector((0, 0.2, 0)) if not footBone else footBone.tail
                control.roll = 0 if not footBone else footBone.roll
                ikTarget.parent = control

                # IK BONE
                ikBone1 = editBones.new(boneName.replace("TWEAK_", "IK_"))
                ikBone1.use_deform = False
                ikBone1.head = bone.head
                ikBone1.tail = bone.tail
                ikBone1.roll = bone.roll
                ikBone1.parent = bone.parent
                ikBone2 = editBones.new(calfBone.name.replace("TWEAK_", "IK_"))
                ikBone2.use_deform = False
                ikBone2.head = calfBone.head
                ikBone2.tail = calfBone.tail
                ikBone2.roll = calfBone.roll
                ikBone2.parent = ikBone1
                ikBone2.use_connect = False

                # FK BONE
                fkBone1 = editBones.new(boneName.replace("TWEAK_", "FK_"))
                fkBone1.use_deform = False
                fkBone1.head = bone.head
                fkBone1.tail = bone.tail
                fkBone1.roll = bone.roll
                fkBone1.parent = bone.parent
                fkBone2 = editBones.new(calfBone.name.replace("TWEAK_", "FK_"))
                fkBone2.use_deform = False
                fkBone2.head = calfBone.head
                fkBone2.tail = calfBone.tail
                fkBone2.roll = calfBone.roll
                fkBone2.parent = fkBone1
                fkBone2.use_connect = False
                if footBone:
                    footBone.use_connect = False
                    fkBone3 = editBones.new(footBone.name.replace("TWEAK_", "FK_"))
                    fkBone3.use_deform = False
                    fkBone3.head = footBone.head
                    fkBone3.tail = footBone.tail
                    fkBone3.roll = footBone.roll
                    fkBone3.parent = fkBone2
                    fkBone3.use_connect = False

                # STRETCH BONE
                stretchBone1 = editBones.new(boneName.replace("TWEAK_", "STRETCH_"))
                stretchBone1.use_deform = False
                stretchBone1.head = bone.head
                stretchBone1.tail = bone.tail
                stretchBone1.roll = bone.roll
                stretchBone1.parent = ikBone1
                stretchBone2 = editBones.new(calfBone.name.replace("TWEAK_", "STRETCH_"))
                stretchBone2.use_deform = False
                stretchBone2.head = calfBone.head
                stretchBone2.tail = calfBone.tail
                stretchBone2.roll = calfBone.roll
                stretchBone2.parent = stretchBone1
                stretchBone2.use_connect = False

                bone["subtargetIK"] = ikTarget.name
                bone["subtargetPole"] = pole.name
                bone["footBone"] = bool(footBone)
                bone["toeBone"] = bool(toeBone)

                # move to 29 layer
                self.moveBoneLayer([bone, calfBone, ikTarget, ikBone1, ikBone2, stretchBone1, stretchBone2], [29])

                if footBone:
                    # PIVOT HEEL, FOOT AND CONTROL
                    pivotHeel = editBones.new(footBone.name.replace("TWEAK_", "PIVOTHEEL_"))
                    pivotHeel.use_deform = False
                    pivotHeel.head = footBone.head - Vector((0, -0.075, footBone.head[2]))
                    pivotHeel.tail = pivotHeel.head + Vector((0, 0.1, 0))
                    pivotHeel.roll = 0
                    pivotHeel.parent = control

                    heelControl = editBones.new(footBone.name.replace("TWEAK_", "HEELCONTROL_"))
                    heelControl.use_deform = False
                    heelControl.head = pivotHeel.head
                    heelControl.tail = pivotHeel.tail
                    heelControl.roll = 0
                    heelControl.parent = control

                    pivotFoot = editBones.new(footBone.name.replace("TWEAK_", "PIVOTFOOT_"))
                    pivotFoot.use_deform = False
                    pivotFoot.head = footBone.tail
                    pivotFoot.tail = footBone.tail + Vector((0, 0.1, 0))
                    pivotFoot.roll = 0
                    pivotFoot.parent = pivotHeel

                    ikTarget.parent = pivotFoot

                    # FLOOR FOOT
                    floorFoot = editBones.new(footBone.name.replace("TWEAK_", "FLOOR_"))
                    floorFoot.use_deform = False
                    floorFoot.head = footBone.head - Vector((0, 0, footBone.head[2]))
                    floorFoot.tail = floorFoot.head + Vector((0, 0.1, 0))
                    floorFoot.roll = 0
                    footBone["boneHasFloor"] = True

                    # move to 29 layer
                    self.moveBoneLayer([pivotHeel, pivotFoot, footBone], [29])

                    if toeBone:
                        # TOE PIVOT AND CONTROL
                        pivotToe = editBones.new(toeBone.name.replace("TWEAK_", "PIVOTTOE_"))
                        pivotToe.use_deform = False
                        pivotToe.head = toeBone.tail
                        pivotToe.tail = toeBone.tail + Vector((0, 0.1, 0))
                        pivotToe.roll = 0
                        pivotToe.parent = pivotHeel

                        toeControl = editBones.new(toeBone.name.replace("TWEAK_", "TOECONTROL_"))
                        toeControl.use_deform = False
                        toeControl.head = toeBone.tail
                        toeControl.tail = toeBone.tail + Vector((0, 0.1, 0))
                        toeControl.roll = 0
                        toeControl.parent = control

                        pivotFoot.parent = pivotToe

                        ballControl = editBones.new(toeBone.name.replace("TWEAK_", "CONTROL_"))
                        ballControl.use_deform = False
                        ballControl.head = toeBone.head
                        ballControl.tail = toeBone.tail
                        ballControl.roll = toeBone.roll
                        ballControl.parent = control

                        # move to 29 layer
                        self.moveBoneLayer([pivotToe, toeBone], [29])

        # ARM_HUMAN
        for bone in [bone for bone in editBones if bone.get("UE4RIGTYPE") == "ARM_HUMAN"]:
            bone.use_connect = False
            bpy.ops.armature.select_all(action="DESELECT")
            boneName = bone.name
            # POLE BONE
            canCreatePole = [bn for bn in bone.children if bn.name.startswith("TWEAK_") and not bn.get("UE4RIGTYPE") and not "_twist_" in bn.name]
            if canCreatePole:
                lowerarmBone = canCreatePole[0]
                lowerarmBone.use_connect = False
                # CHECK IF HAND EXIST
                handBone = [bn for bn in lowerarmBone.children if bn.name.startswith("TWEAK_") and not bn.get("UE4RIGTYPE") and not "_twist_" in bn.name]
                handBone = handBone[0] if handBone else None

                vA = lowerarmBone.vector
                vB = lowerarmBone.tail - bone.head

                vKnee = (vA.project(vB) - vA).normalized() * vB.length

                # IK POLE

                pole = editBones.new(boneName.replace("TWEAK_", "IKPOLE_"))
                pole.use_deform = False
                pole.head = bone.tail + vKnee
                pole.tail = pole.head - vKnee/8
                pole.roll = 0
                pole.length = 0.25

                # VIS POLE
                visPole = editBones.new(lowerarmBone.name.replace("TWEAK_", "VISPOLE_"))
                visPole.use_deform = False
                visPole.head = pole.head
                visPole.tail = lowerarmBone.head
                visPole.roll = 0

                # IK TARGET BONE
                ikTarget = editBones.new((lowerarmBone.name.replace("TWEAK_", "CONTROL_") if not handBone else handBone.name.replace("TWEAK_", "CONTROL_")))
                ikTarget.use_deform = False
                ikTarget.head = lowerarmBone.head if not handBone else handBone.head
                ikTarget.tail = lowerarmBone.tail if not handBone else handBone.tail
                ikTarget.roll = lowerarmBone.roll if not handBone else handBone.roll
                if not handBone:
                    tailLoc = (lowerarmBone.y_axis * 0.1) + lowerarmBone.tail
                    ikTarget.head = lowerarmBone.tail
                    ikTarget.tail = tailLoc

                # IK BONE
                ikBone1 = editBones.new(boneName.replace("TWEAK_", "IK_"))
                ikBone1.use_deform = False
                ikBone1.head = bone.head
                ikBone1.tail = bone.tail
                ikBone1.roll = bone.roll
                ikBone1.parent = bone.parent
                ikBone2 = editBones.new(lowerarmBone.name.replace("TWEAK_", "IK_"))
                ikBone2.use_deform = False
                ikBone2.head = lowerarmBone.head
                ikBone2.tail = lowerarmBone.tail
                ikBone2.roll = lowerarmBone.roll
                ikBone2.parent = ikBone1
                ikBone2.use_connect = False

                # FK BONE
                fkBone1 = editBones.new(boneName.replace("TWEAK_", "FK_"))
                fkBone1.use_deform = False
                fkBone1.head = bone.head
                fkBone1.tail = bone.tail
                fkBone1.roll = bone.roll
                fkBone1.parent = bone.parent
                fkBone2 = editBones.new(lowerarmBone.name.replace("TWEAK_", "FK_"))
                fkBone2.use_deform = False
                fkBone2.head = lowerarmBone.head
                fkBone2.tail = lowerarmBone.tail
                fkBone2.roll = lowerarmBone.roll
                fkBone2.parent = fkBone1
                fkBone2.use_connect = False
                if handBone:
                    handBone.use_connect = False
                    fkBone3 = editBones.new(handBone.name.replace("TWEAK_", "FK_"))
                    fkBone3.use_deform = False
                    fkBone3.head = handBone.head
                    fkBone3.tail = handBone.tail
                    fkBone3.roll = handBone.roll
                    fkBone3.parent = fkBone2
                    fkBone3.use_connect = False

                # STRETCH BONE
                stretchBone1 = editBones.new(boneName.replace("TWEAK_", "STRETCH_"))
                stretchBone1.use_deform = False
                stretchBone1.head = bone.head
                stretchBone1.tail = bone.tail
                stretchBone1.roll = bone.roll
                stretchBone1.parent = ikBone1
                stretchBone2 = editBones.new(lowerarmBone.name.replace("TWEAK_", "STRETCH_"))
                stretchBone2.use_deform = False
                stretchBone2.head = lowerarmBone.head
                stretchBone2.tail = lowerarmBone.tail
                stretchBone2.roll = lowerarmBone.roll
                stretchBone2.parent = stretchBone1
                stretchBone2.use_connect = False

                bone["subtargetIK"] = ikTarget.name
                bone["subtargetPole"] = pole.name
                bone["handBone"] = bool(handBone)

                if handBone:
                    # FLOOR HAND
                    floorFoot = editBones.new(handBone.name.replace("TWEAK_", "FLOOR_"))
                    floorFoot.use_deform = False
                    floorFoot.head = handBone.head - Vector((0, 0, handBone.head[2]))
                    floorFoot.tail = floorFoot.head + Vector((0, 0.1, 0))
                    floorFoot.roll = 0
                    handBone["boneHasFloor"] = True

                # move to 29 layer
                boneToMove = [bone, lowerarmBone, ikBone1, ikBone2, stretchBone1, stretchBone2]
                if handBone:
                    boneToMove.append(handBone)
                self.moveBoneLayer(boneToMove, [29])

        # PELVIS
        for bone in [bone for bone in editBones if bone.get("UE4RIGTYPE") == "PELVIS"]:
            bone.use_connect = False

            # CONTROL BONE
            control = editBones.new(bone.name.replace("TWEAK_", "CONTROL_"))
            control.use_deform = False
            control.head = bone.head
            control.tail = bone.tail
            control.roll = bone.roll

        # SPINE
        for bone in [bone for bone in editBones if bone.get("UE4RIGTYPE") == "SPINE"]:
            bone.use_connect = False

            targetBone = editBones.get(bone.name.replace("TWEAK_", "TARGET_"))

            childBone = next(iter([x for x in bone.children if x is not targetBone]), None)

            if childBone:
                # STRETCH BONE
                stretchBone = editBones.new(bone.name.replace("TWEAK_", "STRETCH_"))
                stretchBone.use_deform = False
                stretchBone.head = bone.head
                stretchBone.tail =  bone.tail
                stretchBone.roll = bone.roll
                stretchBone.parent = bone

                targetBone.parent = stretchBone

                bone["stretchBoneTarget"] = childBone.name

        # NECK
        for bone in [bone for bone in editBones if bone.get("UE4RIGTYPE") == "NECK"]:
            bone.use_connect = False

            targetBone = editBones.get(bone.name.replace("TWEAK_", "TARGET_"))

            childBone = next(iter([x for x in bone.children if x is not targetBone]), None)

            if childBone:
                # STRETCH BONE
                stretchBone = editBones.new(bone.name.replace("TWEAK_", "STRETCH_"))
                stretchBone.use_deform = False
                stretchBone.head = bone.head
                stretchBone.tail =  bone.tail
                stretchBone.roll = bone.roll
                stretchBone.parent = bone

                targetBone.parent = stretchBone

                bone["stretchBoneTarget"] = childBone.name

        # HEAD
        for bone in [bone for bone in editBones if bone.get("UE4RIGTYPE") == "HEAD"]:
            bone.use_connect = False

            # CONTROL BONE
            control = editBones.new("CONTROL_" + bone.name.replace("TWEAK_", ""))
            control.use_deform = False
            control.head = (bone.z_axis * 0.2) + bone.head
            control.tail =  control.head + Vector((0, 0.25, 0))
            control.roll = 0
            control.length = 0.01

            # VIS CONTROL
            visControl = editBones.new("VISCONTROL_" + bone.name.replace("TWEAK_", ""))
            visControl.use_deform = False
            visControl.head = control.head
            visControl.tail = bone.head
            visControl.roll = 0

        # switch case function for face bone
        def SC_Jaw(bone, faceAttach):
            """JAW CONTROL"""
            bone.name = bone.name.replace("TWEAK_", "") + "_TWEAK"
            # move to 0 layer
            self.moveBoneLayer([bone], [0])
            # CONTROL BONE
            control = editBones.new(bone.name.replace("_TWEAK", "_CONTROL"))
            control.use_deform = False
            control.head = [bone.tail[0], bone.tail[1] - 0.025, bone.tail[2]]
            control.tail = bone.tail
            control.roll = bone.roll
            control.length = 0.05
            control.parent = bone.parent

            bone["subtargetIK"] = control.name

        def SC_Landmark(bone, faceAttach):
            """LANDMARK CONTROL"""
            bone.name = bone.name.replace("TWEAK_", "") + "_TWEAK"
            # move to 29 layer
            self.moveBoneLayer([bone], [29])
            # CONTROL BONE
            control = editBones.new(bone.name.replace("_TWEAK", "_CONTROL"))
            control.use_deform = False
            control.head = bone.head
            control.tail = bone.tail
            control.roll = bone.roll
            control.length = 0.05
            control.parent = bone.parent

            bone["subtargetIK"] = control.name

        def SC_Eye(bone, faceAttach):
            """EYE CONTROL"""
            bone.name = bone.name.replace("TWEAK_", "") + "_TWEAK"
            headBone = faceAttach.parent
            controlHeadBone = editBones.get(headBone.name.replace("TWEAK_", "CONTROL_"))
            # CONTROL BONE
            control = editBones.new(bone.name.replace("_TWEAK", "_CONTROL"))
            control.use_deform = False
            control.head = (bone.y_axis * abs(controlHeadBone.head.y - bone.head.y)) + bone.head
            control.tail = bone.tail
            control.roll = bone.roll
            control.length = 0.05
            control.parent = controlHeadBone

            bone["subtargetIK"] = control.name

            # EYE MECHANISM
            eyeMCH = editBones.new(bone.name.replace("_TWEAK", "_MCH"))
            eyeMCH.use_deform = False
            eyeMCH.head = bone.head
            eyeMCH.tail = bone.tail
            eyeMCH.roll = bone.roll
            eyeMCH.parent = bone.parent
            # move to 29 layer
            self.moveBoneLayer([eyeMCH], [29])

            # EYELID OPEN<>CLOSE MECHANISM
            for part in ["UPPER", "LOWER"]:
                eyelidMCH = editBones.new(bone.name.replace("_TWEAK", "_EYELID_" + part + "_ROTATION"))
                eyelidMCH.use_deform = False
                eyelidMCH.head = bone.head
                eyelidMCH.tail = bone.tail
                eyelidMCH.roll = bone.roll
                eyelidMCH.parent = eyeMCH

                eyelidBones = [bn for bn in bone.children if bn.get("UE4RIGTYPE") == "EYELID_" + part]

                if eyelidBones:
                    zLoc = (max if part == "UPPER" else min)([lid.head.z for lid in eyelidBones])
                    eyelidPivotMCH = editBones.new(bone.name.replace("_TWEAK", "_EYELID_" + part + "_PIVOT_ROTATION"))
                    eyelidPivotMCH.use_deform = False
                    eyelidPivotMCH.head = (bone.head.x, (bone.head.y - bone.length) - 0.005, zLoc)
                    eyelidPivotMCH.tail = (bone.tail.x, (bone.tail.y - bone.length) - 0.005, zLoc)
                    eyelidPivotMCH.roll = bone.roll
                    eyelidPivotMCH.parent = eyelidMCH
                    # move to 29 layer
                    self.moveBoneLayer([eyelidPivotMCH], [29])

                    for eyelidBone in eyelidBones:
                        """EYELID CONTROL"""
                        eyelidBone.name = eyelidBone.name.replace("TWEAK_", "") + "_TWEAK"
                        # move to 29 layer
                        self.moveBoneLayer([eyelidBone], [29])
                        # CONTROL BONE
                        control = editBones.new(eyelidBone.name.replace("_TWEAK", "_CONTROL"))
                        control.use_deform = False
                        control.head = eyelidBone.head
                        control.tail = eyelidBone.tail
                        control.roll = eyelidBone.roll
                        control.length = 0.01
                        control.parent = eyelidMCH

                        # COPY BONE
                        eyelidBoneCopy = editBones.new(eyelidBone.name.replace("_TWEAK", "_COPY"))
                        eyelidBoneCopy.use_deform = False
                        eyelidBoneCopy.head = eyelidBone.head
                        eyelidBoneCopy.tail = eyelidBone.tail
                        eyelidBoneCopy.roll = eyelidBone.roll
                        eyelidBoneCopy.parent = control
                        # move to 29 layer
                        self.moveBoneLayer([eyelidBoneCopy], [29])

                        eyelidBone["subtargetIK"] = eyelidBoneCopy.name

        # FACE_ATTACH
        for bone in [bone for bone in editBones if bone.get("UE4RIGTYPE") == "FACE_ATTACH"]:
            # move to 29 layer
            self.moveBoneLayer([bone], [29])
            # filter bone
            arrFaceBones = [bone for bone in bone.children_recursive if bone.get("UE4RIGTYPE") in ["JAW", "LANDMARK", "EYE"]]
            # switch case with dict
            switchCaseRigType = {
                "JAW": SC_Jaw,
                "LANDMARK": SC_Landmark,
                "EYE": SC_Eye
            }
            for faceBone in arrFaceBones:
                doSwitch = switchCaseRigType.get(faceBone.get("UE4RIGTYPE"), None)
                if doSwitch is not None:
                    doSwitch(faceBone, bone)

        self.moveBoneLayer([eB for eB in editBones if eB.layers[0]], [0])

        bpy.ops.armature.select_all(action="DESELECT")
        self.context.scene.tool_settings.transform_pivot_point = oldPivot
        self.activeObject.data.use_mirror_x = oldMirror

        bpy.ops.object.mode_set(mode="POSE")
        poseBones = self.activeObject.pose.bones
        # copy transform from target bone
        for bone in [bone for bone in poseBones if bone.name.startswith("TARGET_")]:
            constraints = poseBones.get(bone.name.replace("TARGET_","")).constraints.new(type="COPY_TRANSFORMS")
            constraints.name = "TRANSFORM"
            constraints.show_expanded = False
            constraints.target = self.activeObject
            constraints.subtarget = bone.name
            constraints.mix_mode = "REPLACE"
            constraints.target_space = "POSE"
            constraints.owner_space = "POSE"

        # IK BONE
        for bone in [poseBones.get("ik_foot_root"), poseBones.get("ik_hand_root")]:
            if bone is not None:
                for bn in bone.children_recursive:
                    if poseBones.get(bn.name.replace("ik_", "")):
                        constraints = bn.constraints.new(type="COPY_TRANSFORMS")
                        constraints.name = "TRANSFORM"
                        constraints.show_expanded = False
                        constraints.target = self.activeObject
                        constraints.subtarget = bn.name.replace("ik_", "")
                        constraints.mix_mode = "REPLACE"
                        constraints.target_space = "POSE"
                        constraints.owner_space = "POSE"
                    elif bn.name == "ik_hand_gun" and poseBones.get("hand_r"):
                        constraints = bn.constraints.new(type="COPY_TRANSFORMS")
                        constraints.name = "TRANSFORM"
                        constraints.show_expanded = False
                        constraints.target = self.activeObject
                        constraints.subtarget = "hand_r"
                        constraints.mix_mode = "REPLACE"
                        constraints.target_space = "POSE"
                        constraints.owner_space = "POSE"

        # FINGER
        for bone in [bone for bone in poseBones if bone.bone.UE4RIGTYPE == "FINGER"]:
            constraint = bone.constraints.new(type="COPY_ROTATION")
            constraint.name = "fingerROTATION"
            constraint.show_expanded = False
            constraint.target = self.activeObject
            constraint.subtarget = bone.bone.subtargetRotation
            constraint.mix_mode = "ADD"
            constraint.target_space = "LOCAL"
            constraint.owner_space = "LOCAL"

            # generate tweak finger block shape
            getBoneShape = getattr(boneShape, bone.bone.customShapeType)
            getBoneShapeParam = bone.bone.customShapeParam[:len(inspect.getfullargspec(getBoneShape)[0])]
            self.generateCustomBoneShape(bone, collection, getBoneShape(*getBoneShapeParam), leftSideGroup if bone.bone.head_local.x >= 0 else rightSideGroup, False)

            # CONTROL bone
            controlBone = poseBones.get(constraint.subtarget)
            # lock location controller
            controlBone.lock_location = [True, True, True]

            # generate control rotation custom shape
            self.generateCustomBoneShape(controlBone, collection, boneShape.controlRotationFinger(), redGroup, False)

            # filter children with starts string "TWEAK_"
            filterChildren = [bone for bone in bone.children_recursive if bone.name.startswith("TWEAK_") and not bone.bone.UE4RIGTYPE]
            # get index bone that have RIGTYPE
            endIndex = next((index for (index, bn) in enumerate(filterChildren) if bn.bone.UE4RIGTYPE), None)
            if endIndex is not None:
                filterChildren = filterChildren[:endIndex:]
            for bn in filterChildren[::-1]:
                constraint = bn.constraints.new(type="COPY_ROTATION")
                constraint.name = "fingerROTATION"
                constraint.show_expanded = False
                constraint.target = self.activeObject
                constraint.subtarget = bone.bone.subtargetRotation
                constraint.mix_mode = "ADD"
                constraint.target_space = "LOCAL"
                constraint.owner_space = "LOCAL"
                constraint.use_y = False
                constraint.use_z = False

                # generate tweak finger block shape
                getBoneShape = getattr(boneShape, bn.bone.customShapeType)
                getBoneShapeParam = bn.bone.customShapeParam[:len(inspect.getfullargspec(getBoneShape)[0])]
                self.generateCustomBoneShape(bn, collection, getBoneShape(*getBoneShapeParam), leftSideGroup if bone.bone.head_local.x >= 0 else rightSideGroup, False)

            controlBone.custom_shape_transform = filterChildren[-1]
            constraint = filterChildren[-1].constraints.new(type="IK")
            constraint.name = "fingerIK"
            constraint.show_expanded = False
            constraint.target = self.activeObject
            constraint.subtarget = bone.bone.subtargetIK
            constraint.chain_count = len(filterChildren) + 1

            ikControl = poseBones.get(bone.bone.subtargetIK)
            ikControl.bone.controlFingerIK = True

            # IK INFLUENCE DRIVER
            influenceDriver = constraint.driver_add("influence").driver
            influenceDriver.type = "SCRIPTED"
            var = influenceDriver.variables.new()
            var.type = "SINGLE_PROP"
            target = var.targets[0]
            target.id_type = "ARMATURE"
            target.id = self.activeObject.data
            target.data_path = ikControl.bone.path_from_id("switchIK")
            influenceDriver.expression = var.name + " == 0"

            # generate control ik custom shape
            self.generateCustomBoneShape(ikControl, collection, boneShape.circle(16, 1, 0.25), redGroup, False)

            if ikControl.parent is not None and ikControl.parent.bone.boneHasFloor:
                # FLOOR FINGERTIP
                self.addFloorConstraint(ikControl, "FLOOR_" + ikControl.parent.name.replace("TWEAK_", ""), 0)

        # LEG_HUMAN
        for bone in [bone for bone in poseBones if bone.bone.UE4RIGTYPE == "LEG_HUMAN"]:
            boneChildren = [bn for bn in bone.children_recursive if bn.name.startswith("TWEAK_") and not "_twist_" in bn.name and not bn.bone.UE4RIGTYPE]
            if boneChildren:
                calf = None
                foot = None
                toe = None
                if len(boneChildren) != 0:
                    calf = boneChildren.pop(0)
                if len(boneChildren) != 0:
                    foot = boneChildren.pop(0)
                if len(boneChildren) != 0:
                    toe = boneChildren.pop(0)

                customPropertyName = None

                if calf is not None:
                    ikTargetBone = poseBones.get(bone.bone.subtargetIK)
                    ikPoleBone = poseBones.get(bone.bone.subtargetPole)

                    ikBone1 = poseBones.get("IK_" + bone.name.replace("TWEAK_", ""))
                    ikBone1.ik_stretch = 0.1
                    ikBone2 = poseBones.get("IK_" + calf.name.replace("TWEAK_", ""))
                    ikBone2.ik_stretch = 0.1

                    poleAngle = self.get_pole_angle(bone, calf, ikPoleBone.matrix.translation)

                    constraint = ikBone2.constraints.new(type="IK")
                    constraint.name = "IK"
                    constraint.show_expanded = False
                    constraint.chain_count = 2
                    constraint.target = self.activeObject
                    constraint.subtarget = bone.bone.subtargetIK
                    constraint.pole_target = self.activeObject
                    constraint.pole_subtarget = bone.bone.subtargetPole
                    constraint.pole_angle = poleAngle

                    # generate ik pole custom shape
                    self.generateCustomBoneShape(ikPoleBone, collection, boneShape.sphere(8, 4, 4), redGroup, False)

                    # CONTROL FOOT
                    controlBone = poseBones.get("CONTROL_" + foot.name.replace("TWEAK_", "")) if bone.bone.footBone and foot else poseBones.get("CONTROL_" + calf.name.replace("TWEAK_", ""))

                    # STRETCH IK DRIVER
                    for ikBoneStretch in [ikBone1, ikBone2]:
                        influenceIKStretch = ikBoneStretch.driver_add("ik_stretch").driver
                        influenceIKStretch.type = "SCRIPTED"
                        var = influenceIKStretch.variables.new()
                        var.type = "SINGLE_PROP"
                        target = var.targets[0]
                        target.id_type = "ARMATURE"
                        target.id = self.activeObject.data
                        target.data_path = controlBone.bone.path_from_id("stretchBone")
                        influenceIKStretch.expression =  "0 if " + var.name + " == 0 else 0.05"

                    # COPY TRASFORM STRETCH AND FK + DIRVER
                    # poseBone and target bone
                    for pB in [bone, calf]:
                        constraint = pB.constraints.new(type="COPY_TRANSFORMS")
                        constraint.name = "TRANSFORM"
                        constraint.show_expanded = False
                        constraint.target = self.activeObject
                        constraint.subtarget = "STRETCH_" + pB.name.replace("TWEAK_", "")
                        constraint.mix_mode = "REPLACE"
                        constraint.target_space = "POSE"
                        constraint.owner_space = "POSE"
                        # IK DRIVER
                        influenceDriver = constraint.driver_add("influence").driver
                        influenceDriver.type = "SCRIPTED"
                        var = influenceDriver.variables.new()
                        var.type = "SINGLE_PROP"
                        target = var.targets[0]
                        target.id_type = "ARMATURE"
                        target.id = self.activeObject.data
                        target.data_path = controlBone.bone.path_from_id("switchIK")
                        influenceDriver.expression = var.name + " == 0"

                        constraint = pB.constraints.new(type="COPY_TRANSFORMS")
                        constraint.name = "TRANSFORM_STRETCH"
                        constraint.show_expanded = False
                        constraint.target = self.activeObject
                        constraint.subtarget = "FK_" + pB.name.replace("TWEAK_", "")
                        constraint.mix_mode = "REPLACE"
                        constraint.target_space = "POSE"
                        constraint.owner_space = "POSE"

                        # FK DRIVER
                        influenceDriver = constraint.driver_add("influence").driver
                        influenceDriver.type = "SCRIPTED"
                        var = influenceDriver.variables.new()
                        var.type = "SINGLE_PROP"
                        target = var.targets[0]
                        target.id_type = "ARMATURE"
                        target.id = self.activeObject.data
                        target.data_path = controlBone.bone.path_from_id("switchIK")
                        influenceDriver.expression = var.name + " == 1"

                    stretchBone1 = poseBones.get("STRETCH_" + bone.name.replace("TWEAK_", ""))
                    stretchBone2 = poseBones.get("STRETCH_" + calf.name.replace("TWEAK_", ""))

                    # LIMIT SCALE FROM PARENT
                    for pB in [stretchBone1, stretchBone2]:
                        constraint = pB.constraints.new(type="LIMIT_SCALE")
                        constraint.name = "LIMIT_SCALE"
                        constraint.show_expanded = False
                        constraint.use_transform_limit = True
                        constraint.owner_space = "LOCAL_WITH_PARENT"
                        for axis in ["x", "y", "z"]:
                            setattr(constraint, "use_max_"+ axis, True)
                            setattr(constraint, "max_"+ axis, 1)

                    # DAMPED_TRACK stretchBone2 TO IK TARGET
                    constraint = stretchBone2.constraints.new(type="DAMPED_TRACK")
                    constraint.name = "DAMPED_TRACK"
                    constraint.show_expanded = False
                    constraint.head_tail = 1
                    constraint.target = self.activeObject
                    constraint.subtarget = ikBone2.name
                    constraint.track_axis = "TRACK_Y"

                    # STRETCH TO + DRIVER
                    for pB, tB in [(stretchBone1, ikBone1.name), (stretchBone2, ikBone2.name)]:
                        constraint = pB.constraints.new(type="STRETCH_TO")
                        constraint.show_expanded = False
                        constraint.head_tail = 1
                        constraint.target = self.activeObject
                        constraint.subtarget = tB
                        constraint.rest_length = pB.length * 100

                        # STRETCH INFLUENCE DRIVER
                        influenceDriver = constraint.driver_add("influence").driver
                        influenceDriver.type = "SCRIPTED"
                        var = influenceDriver.variables.new()
                        var.type = "SINGLE_PROP"
                        target = var.targets[0]
                        target.id_type = "ARMATURE"
                        target.id = self.activeObject.data
                        target.data_path = controlBone.bone.path_from_id("stretchBone")
                        influenceDriver.expression = var.name

                        # STRETCH VOLUME DRIVER
                        influenceDriver = constraint.driver_add("volume").driver
                        influenceDriver.type = "SCRIPTED"
                        var = influenceDriver.variables.new()
                        var.type = "SINGLE_PROP"
                        target = var.targets[0]
                        target.id_type = "ARMATURE"
                        target.id = self.activeObject.data
                        target.data_path = controlBone.bone.path_from_id("stretchBoneMode")
                        influenceDriver.expression = var.name

                    # VIS POLE
                    visPole = poseBones.get("VISPOLE_" + calf.name.replace("TWEAK_", ""))
                    visPole.bone.hide_select = True

                    visPoleLocation = visPole.constraints.new(type="COPY_LOCATION")
                    visPoleLocation.name = "GET_POLE_LOCATION"
                    visPoleLocation.show_expanded = False
                    visPoleLocation.target = self.activeObject
                    visPoleLocation.subtarget = bone.bone.subtargetPole
                    visPoleLocation.target_space = "POSE"
                    visPoleLocation.owner_space = "POSE"

                    visPoleStretch = visPole.constraints.new(type="STRETCH_TO")
                    visPoleStretch.name = "STRETCH_TO_CALF"
                    visPoleStretch.show_expanded = False
                    visPoleStretch.target = self.activeObject
                    visPoleStretch.subtarget = "STRETCH_" + calf.name.replace("TWEAK_", "")
                    visPoleStretch.rest_length = visPole.length * 100
                    visPoleStretch.volume = "NO_VOLUME"

                    # Vis Hide Driver
                    VisHideDriver = visPole.bone.driver_add("hide").driver
                    VisHideDriver.type = "SCRIPTED"
                    var = VisHideDriver.variables.new()
                    var.type = "SINGLE_PROP"
                    target = var.targets[0]
                    target.id_type = "ARMATURE"
                    target.id = self.activeObject.data
                    target.data_path = "hideVis"
                    VisHideDriver.expression = var.name

                    # generate line custom shape
                    self.generateCustomBoneShape(visPole, collection, boneShape.line, redGroup, True)

                    # FK THIGH

                    FKBone = poseBones.get("FK_" + bone.name.replace("TWEAK_", ""))

                    # generate fk custom shape
                    getBoneShape = getattr(boneShape, bone.bone.customShapeType)
                    getBoneShapeParam = bone.bone.customShapeParam[:len(inspect.getfullargspec(getBoneShape)[0])]
                    self.generateCustomBoneShape(FKBone, collection, getBoneShape(*getBoneShapeParam), leftSideGroup if FKBone.bone.head_local.x >= 0 else rightSideGroup, False)

                    # FK Hide Driver
                    FKHideDriver = FKBone.bone.driver_add("hide").driver
                    FKHideDriver.type = "SCRIPTED"
                    var = FKHideDriver.variables.new()
                    var.type = "SINGLE_PROP"
                    target = var.targets[0]
                    target.id_type = "ARMATURE"
                    target.id = self.activeObject.data
                    target.data_path = "hideFK"
                    FKHideDriver.expression = var.name

                    # FK CALF

                    FKBone = poseBones.get("FK_" + calf.name.replace("TWEAK_", ""))

                    # generate fk custom shape
                    getBoneShape = getattr(boneShape, calf.bone.customShapeType)
                    getBoneShapeParam = calf.bone.customShapeParam[:len(inspect.getfullargspec(getBoneShape)[0])]
                    self.generateCustomBoneShape(FKBone, collection, getBoneShape(*getBoneShapeParam), leftSideGroup if FKBone.bone.head_local.x >= 0 else rightSideGroup, False)

                    # FK Hide Driver
                    FKHideDriver = FKBone.bone.driver_add("hide").driver
                    FKHideDriver.type = "SCRIPTED"
                    var = FKHideDriver.variables.new()
                    var.type = "SINGLE_PROP"
                    target = var.targets[0]
                    target.id_type = "ARMATURE"
                    target.id = self.activeObject.data
                    target.data_path = "hideFK"
                    FKHideDriver.expression = var.name

                    if foot:
                        # FK FOOT

                        FKBone = poseBones.get("FK_" + foot.name.replace("TWEAK_", ""))

                        # generate fk custom shape
                        getBoneShape = getattr(boneShape, foot.bone.customShapeType)
                        getBoneShapeParam = foot.bone.customShapeParam[:len(inspect.getfullargspec(getBoneShape)[0])]
                        self.generateCustomBoneShape(FKBone, collection, getBoneShape(*getBoneShapeParam), leftSideGroup if FKBone.bone.head_local.x >= 0 else rightSideGroup, False)

                        # FK Hide Driver
                        FKHideDriver = FKBone.bone.driver_add("hide").driver
                        FKHideDriver.type = "SCRIPTED"
                        var = FKHideDriver.variables.new()
                        var.type = "SINGLE_PROP"
                        target = var.targets[0]
                        target.id_type = "ARMATURE"
                        target.id = self.activeObject.data
                        target.data_path = "hideFK"
                        FKHideDriver.expression = var.name

                    # register control ik to bone
                    controlBone.bone.controlIK = True
                    controlBone.bone.pointABoneIK = bone.name.replace("TWEAK_", "")
                    controlBone.bone.pointBBoneIK = calf.name.replace("TWEAK_", "")

                    if bone.bone.footBone and foot:
                        controlRotationFootIK = foot.constraints.new(type="COPY_TRANSFORMS")
                        controlRotationFootIK.name = "FOOT_CONTROL"
                        controlRotationFootIK.show_expanded = False
                        controlRotationFootIK.target = self.activeObject
                        controlRotationFootIK.subtarget = bone.bone.subtargetIK
                        controlRotationFootIK.mix_mode = "REPLACE"
                        controlRotationFootIK.target_space = "POSE"
                        controlRotationFootIK.owner_space = "POSE"
                        # IK DRIVER
                        influenceDriver = controlRotationFootIK.driver_add("influence").driver
                        influenceDriver.type = "SCRIPTED"
                        var = influenceDriver.variables.new()
                        var.type = "SINGLE_PROP"
                        target = var.targets[0]
                        target.id_type = "ARMATURE"
                        target.id = self.activeObject.data
                        target.data_path = controlBone.bone.path_from_id("switchIK")
                        influenceDriver.expression = var.name + " == 0"

                        # LIMIT LOCATION IN IK MODE
                        limitLocationIK = foot.constraints.new(type="LIMIT_LOCATION")
                        limitLocationIK.name = "LIMIT_LOCATION_IK"
                        limitLocationIK.show_expanded = False
                        limitLocationIK.owner_space = "LOCAL"
                        limitLocationIK.min_x = 0
                        limitLocationIK.min_y = 0
                        limitLocationIK.min_z = 0
                        limitLocationIK.max_x = 0
                        limitLocationIK.max_y = 0
                        limitLocationIK.max_z = 0
                        limitLocationIK.use_min_x = True
                        limitLocationIK.use_min_y = True
                        limitLocationIK.use_min_z = True
                        limitLocationIK.use_max_x = True
                        limitLocationIK.use_max_y = True
                        limitLocationIK.use_max_z = True
                        # IK DRIVER
                        influenceDriver = limitLocationIK.driver_add("influence").driver
                        influenceDriver.type = "SCRIPTED"
                        var = influenceDriver.variables.new()
                        var.type = "SINGLE_PROP"
                        target = var.targets[0]
                        target.id_type = "ARMATURE"
                        target.id = self.activeObject.data
                        target.data_path = controlBone.bone.path_from_id("switchIK")
                        influenceDriver.expression = var.name + " == 0"

                        controlRotationFootFK = foot.constraints.new(type="COPY_TRANSFORMS")
                        controlRotationFootFK.name = "FOOT_CONTROL_FK"
                        controlRotationFootFK.show_expanded = False
                        controlRotationFootFK.target = self.activeObject
                        controlRotationFootFK.subtarget = "FK_" + foot.name.replace("TWEAK_", "")
                        controlRotationFootFK.mix_mode = "REPLACE"
                        controlRotationFootFK.target_space = "POSE"
                        controlRotationFootFK.owner_space = "POSE"
                        # FK DRIVER
                        influenceDriver = controlRotationFootFK.driver_add("influence").driver
                        influenceDriver.type = "SCRIPTED"
                        var = influenceDriver.variables.new()
                        var.type = "SINGLE_PROP"
                        target = var.targets[0]
                        target.id_type = "ARMATURE"
                        target.id = self.activeObject.data
                        target.data_path = controlBone.bone.path_from_id("switchIK")
                        influenceDriver.expression = var.name + " == 1"

                        # Generate Custom Shape
                        mesh = bpy.data.meshes.new("UE4WSBS_" + controlBone.name)
                        objCustomShape = bpy.data.objects.new(mesh.name,mesh)
                        collection.objects.link(objCustomShape)
                        mesh.from_pydata(*boneShape.block(11, 3, 0, 15))

                        controlBone.custom_shape = objCustomShape
                        controlBone.use_custom_shape_bone_size = False
                        controlBone.bone_group = redGroup

                        # PIVOTHEEL
                        pivotHeel = poseBones.get("PIVOTHEEL_" + foot.name.replace("TWEAK_", ""))
                        pivotHeel.lock_location = [True, True, True]
                        pivotHeel.lock_rotation = [True, True, True]
                        pivotHeel.rotation_mode = "XYZ"
                        for index, rotAxis, expr in [(0, "ROT_X", "max(min(ROT_X, 0), -0.5)"), (1, "ROT_Y", "ROT_Y"), (2, "ROT_Z", "ROT_Z")]:
                            axisDriver = pivotHeel.driver_add("rotation_euler", index).driver
                            axisDriver.type = "SCRIPTED"
                            var = axisDriver.variables.new()
                            var.name = rotAxis
                            var.type = "TRANSFORMS"
                            target = var.targets[0]
                            target.id = self.activeObject
                            target.bone_target = "HEELCONTROL_" + foot.name.replace("TWEAK_", "")
                            target.transform_type = rotAxis
                            target.transform_space = "TRANSFORM_SPACE"
                            axisDriver.expression = expr

                        # HEEL CONTROL
                        heelControl = poseBones.get("HEELCONTROL_" + foot.name.replace("TWEAK_", ""))

                        # generate hell control custom shape
                        self.generateCustomBoneShape(heelControl, collection, boneShape.controlRotation(8, 2.5 , 0, False), redGroup, False)

                        # PIVOTFOOT
                        pivotHeel = poseBones.get("PIVOTFOOT_" + foot.name.replace("TWEAK_", ""))
                        pivotHeel.lock_location = [True, True, True]
                        pivotHeel.lock_rotation = [True, True, True]
                        pivotHeel.rotation_mode = "XYZ"
                        for index, rotAxis, expr in [(0, "ROT_X", "min(max(ROT_X, 0), 0.9)")]:
                            axisDriver = pivotHeel.driver_add("rotation_euler", index).driver
                            axisDriver.type = "SCRIPTED"
                            var = axisDriver.variables.new()
                            var.name = rotAxis
                            var.type = "TRANSFORMS"
                            target = var.targets[0]
                            target.id = self.activeObject
                            target.bone_target = "HEELCONTROL_" + foot.name.replace("TWEAK_", "")
                            target.transform_type = rotAxis
                            target.transform_space = "TRANSFORM_SPACE"
                            axisDriver.expression = expr

                        # FLOOR FOOT
                        floorFoot = poseBones.get("FLOOR_" + foot.name.replace("TWEAK_", ""))

                        # ADD FLOOR CONSTRAINT
                        self.addFloorConstraint(controlBone, floorFoot.name, foot.bone.head_local[2] * 100)

                        # generate floor custom shape
                        self.generateCustomBoneShape(floorFoot, collection, boneShape.floor(1, 1), yellowGroup, False)

                        if bone.bone.toeBone and toe:
                            controlToe = poseBones.get("CONTROL_" + toe.name.replace("TWEAK_", ""))

                            # generate control toe custom shape
                            getBoneShape = getattr(boneShape, toe.bone.customShapeType)
                            getBoneShapeParam = toe.bone.customShapeParam[:len(inspect.getfullargspec(getBoneShape)[0])]
                            self.generateCustomBoneShape(controlToe, collection, getBoneShape(*getBoneShapeParam), leftSideGroup if controlToe.bone.head_local.x >= 0 else rightSideGroup, False)

                            controlToe.custom_shape_transform = toe

                            # PIVOTTOE
                            pivotToe = poseBones.get("PIVOTTOE_" + toe.name.replace("TWEAK_", ""))
                            pivotToe.lock_location = [True, True, True]
                            pivotToe.lock_rotation = [True, True, True]
                            pivotToe.rotation_mode = "XYZ"

                            for index, rotAxis, expr in [(0, "ROT_X", "min(max(ROT_X, 0), 1)"), (1, "ROT_Y", "ROT_Y"), (2, "ROT_Z", "ROT_Z")]:
                                axisDriver = pivotToe.driver_add("rotation_euler", index).driver
                                axisDriver.type = "SCRIPTED"
                                var = axisDriver.variables.new()
                                var.name = rotAxis
                                var.type = "TRANSFORMS"
                                target = var.targets[0]
                                target.id = self.activeObject
                                target.bone_target = "TOECONTROL_" + toe.name.replace("TWEAK_", "")
                                target.transform_type = rotAxis
                                target.transform_space = "TRANSFORM_SPACE"
                                axisDriver.expression = expr

                            # TOE CONTROL
                            toeControl = poseBones.get("TOECONTROL_" + toe.name.replace("TWEAK_", ""))

                            # generate control toe custom shape
                            self.generateCustomBoneShape(toeControl, collection, boneShape.controlRotation(8, 2.5 , 0, True), redGroup, False)

                            # TWEAK BALL DRIVER LOCATION AND ROTATION
                            for index, transformAxis, expr in [(0, "LOC_X", "LOC_X"), (1, "LOC_Y", "LOC_Y"), (2, "LOC_Z", "LOC_Z")]:
                                axisDriver = toe.driver_add("location", index).driver
                                axisDriver.type = "SCRIPTED"

                                var = axisDriver.variables.new()
                                var.name = transformAxis
                                var.type = "TRANSFORMS"
                                target = var.targets[0]
                                target.id = self.activeObject
                                target.bone_target = "CONTROL_" + toe.name.replace("TWEAK_", "")
                                target.transform_type = transformAxis
                                target.transform_space = "TRANSFORM_SPACE"
                                axisDriver.expression = expr

                            toe.rotation_mode = "XYZ"
                            for index, transformAxis, expr in [(0, "ROT_X", "ROT_X"), (1, "ROT_Y", "ROT_Y"), (2, "ROT_Z", "ROT_Z")]:
                                axisDriver = toe.driver_add("rotation_euler", index).driver
                                axisDriver.type = "SCRIPTED"

                                var = axisDriver.variables.new()
                                var.name = transformAxis
                                var.type = "TRANSFORMS"
                                target = var.targets[0]
                                target.id = self.activeObject
                                target.bone_target = "CONTROL_" + toe.name.replace("TWEAK_", "")
                                target.transform_type = transformAxis
                                target.transform_space = "TRANSFORM_SPACE"

                                if transformAxis == "ROT_X":
                                    var = axisDriver.variables.new()
                                    var.name = "COPY_X"
                                    var.type = "TRANSFORMS"
                                    target = var.targets[0]
                                    target.id = self.activeObject
                                    target.bone_target = "HEELCONTROL_" + foot.name.replace("TWEAK_", "")
                                    target.transform_type = transformAxis
                                    target.transform_space = "TRANSFORM_SPACE"

                                axisDriver.expression = expr if not (transformAxis == "ROT_X") else "-min(max(COPY_X, 0), 0.9) + ROT_X"

                    # CALF CONTROL
                    else:
                        # generate control toe custom shape
                        self.generateCustomBoneShape(controlBone, collection, boneShape.block(10, 10, -5, 5), redGroup, False)

        # ARM_HUMAN
        for bone in [bone for bone in poseBones if bone.bone.UE4RIGTYPE == "ARM_HUMAN"]:
            boneChildren = [bn for bn in bone.children_recursive if bn.name.startswith("TWEAK_") and not "_twist_" in bn.name and not bn.bone.UE4RIGTYPE]
            if boneChildren:
                lowerarm = None
                hand = None
                if len(boneChildren) != 0:
                    lowerarm = boneChildren.pop(0)
                if len(boneChildren) != 0:
                    hand = boneChildren.pop(0)

                customPropertyName = None

                if lowerarm is not None:
                    ikBone = poseBones.get(bone.bone.subtargetIK)
                    poleBone = poseBones.get(bone.bone.subtargetPole)

                    ikBone1 = poseBones.get("IK_" + bone.name.replace("TWEAK_", ""))
                    ikBone1.ik_stretch = 0.1
                    ikBone2 = poseBones.get("IK_" + lowerarm.name.replace("TWEAK_", ""))
                    ikBone2.ik_stretch = 0.1

                    poleAngle = self.get_pole_angle(bone, lowerarm, poleBone.matrix.translation)

                    constraint = ikBone2.constraints.new(type="IK")
                    constraint.name = "IK"
                    constraint.show_expanded = False
                    constraint.chain_count = 2
                    constraint.target = self.activeObject
                    constraint.subtarget = bone.bone.subtargetIK
                    constraint.pole_target = self.activeObject
                    constraint.pole_subtarget = bone.bone.subtargetPole
                    constraint.pole_angle = poleAngle

                    # generate ik bone custom shape
                    self.generateCustomBoneShape(ikBone, collection, boneShape.block(9, 3, 0, 9), redGroup, False)

                    # generate pole bone custom shape
                    self.generateCustomBoneShape(poleBone, collection, boneShape.sphere(8, 4, 4), redGroup, False)

                    # STRETCH IK DRIVER
                    for ikBoneStretch in [ikBone1, ikBone2]:
                        influenceIKStretch = ikBoneStretch.driver_add("ik_stretch").driver
                        influenceIKStretch.type = "SCRIPTED"
                        var = influenceIKStretch.variables.new()
                        var.type = "SINGLE_PROP"
                        target = var.targets[0]
                        target.id_type = "ARMATURE"
                        target.id = self.activeObject.data
                        target.data_path = ikBone.bone.path_from_id("stretchBone")
                        influenceIKStretch.expression =  "0 if " + var.name + " == 0 else 0.05"

                    # COPY TRASFORM STRETCH AND FK + DIRVER
                    # poseBone and target bone
                    for pB in [bone, lowerarm]:
                        constraint = pB.constraints.new(type="COPY_TRANSFORMS")
                        constraint.name = "TRANSFORM_STRETCH"
                        constraint.show_expanded = False
                        constraint.target = self.activeObject
                        constraint.subtarget = "STRETCH_" + pB.name.replace("TWEAK_", "")
                        constraint.mix_mode = "REPLACE"
                        constraint.target_space = "POSE"
                        constraint.owner_space = "POSE"
                        # IK DRIVER
                        influenceDriver = constraint.driver_add("influence").driver
                        influenceDriver.type = "SCRIPTED"
                        var = influenceDriver.variables.new()
                        var.type = "SINGLE_PROP"
                        target = var.targets[0]
                        target.id_type = "ARMATURE"
                        target.id = self.activeObject.data
                        target.data_path = ikBone.bone.path_from_id("switchIK")
                        influenceDriver.expression = var.name + " == 0"

                        constraint = pB.constraints.new(type="COPY_TRANSFORMS")
                        constraint.name = "TRANSFORM_STRETCH"
                        constraint.show_expanded = False
                        constraint.target = self.activeObject
                        constraint.subtarget = "FK_" + pB.name.replace("TWEAK_", "")
                        constraint.mix_mode = "REPLACE"
                        constraint.target_space = "POSE"
                        constraint.owner_space = "POSE"

                        # FK DRIVER
                        influenceDriver = constraint.driver_add("influence").driver
                        influenceDriver.type = "SCRIPTED"
                        var = influenceDriver.variables.new()
                        var.type = "SINGLE_PROP"
                        target = var.targets[0]
                        target.id_type = "ARMATURE"
                        target.id = self.activeObject.data
                        target.data_path = ikBone.bone.path_from_id("switchIK")
                        influenceDriver.expression = var.name + " == 1"

                    stretchBone1 = poseBones.get("STRETCH_" + bone.name.replace("TWEAK_", ""))
                    stretchBone2 = poseBones.get("STRETCH_" + lowerarm.name.replace("TWEAK_", ""))

                    # LIMIT SCALE FROM PARENT
                    for pB in [stretchBone1, stretchBone2]:
                        constraint = pB.constraints.new(type="LIMIT_SCALE")
                        constraint.name = "LIMIT_SCALE"
                        constraint.show_expanded = False
                        constraint.use_transform_limit = True
                        constraint.owner_space = "LOCAL_WITH_PARENT"
                        for axis in ["x", "y", "z"]:
                            setattr(constraint, "use_max_"+ axis, True)
                            setattr(constraint, "max_"+ axis, 1)

                    # DAMPED_TRACK stretchBone2 TO IK TARGET
                    constraint = stretchBone2.constraints.new(type="DAMPED_TRACK")
                    constraint.name = "DAMPED_TRACK"
                    constraint.show_expanded = False
                    constraint.head_tail = 1
                    constraint.target = self.activeObject
                    constraint.subtarget = ikBone2.name
                    constraint.track_axis = "TRACK_Y"

                    # STRETCH TO + DRIVER
                    for pB, tB in [(stretchBone1, ikBone1.name), (stretchBone2, ikBone2.name)]:
                        constraint = pB.constraints.new(type="STRETCH_TO")
                        constraint.show_expanded = False
                        constraint.head_tail = 1
                        constraint.target = self.activeObject
                        constraint.subtarget = tB
                        constraint.rest_length = pB.length * 100

                        # STRETCH INFLUENCE DRIVER
                        influenceDriver = constraint.driver_add("influence").driver
                        influenceDriver.type = "SCRIPTED"
                        var = influenceDriver.variables.new()
                        var.type = "SINGLE_PROP"
                        target = var.targets[0]
                        target.id_type = "ARMATURE"
                        target.id = self.activeObject.data
                        target.data_path = ikBone.bone.path_from_id("stretchBone")
                        influenceDriver.expression = var.name

                        # STRETCH VOLUME DRIVER
                        influenceDriver = constraint.driver_add("volume").driver
                        influenceDriver.type = "SCRIPTED"
                        var = influenceDriver.variables.new()
                        var.type = "SINGLE_PROP"
                        target = var.targets[0]
                        target.id_type = "ARMATURE"
                        target.id = self.activeObject.data
                        target.data_path = ikBone.bone.path_from_id("stretchBoneMode")
                        influenceDriver.expression = var.name

                    # VIS POLE
                    visPole = poseBones.get("VISPOLE_" + lowerarm.name.replace("TWEAK_", ""))
                    visPole.bone.hide_select = True

                    visPoleLocation = visPole.constraints.new(type="COPY_LOCATION")
                    visPoleLocation.name = "GET_POLE_LOCATION"
                    visPoleLocation.show_expanded = False
                    visPoleLocation.target = self.activeObject
                    visPoleLocation.subtarget = bone.bone.subtargetPole
                    visPoleLocation.target_space = "POSE"
                    visPoleLocation.owner_space = "POSE"

                    visPoleStretch = visPole.constraints.new(type="STRETCH_TO")
                    visPoleStretch.name = "STRETCH_TO_LOWERARM"
                    visPoleStretch.show_expanded = False
                    visPoleStretch.target = self.activeObject
                    visPoleStretch.subtarget = "STRETCH_" + lowerarm.name.replace("TWEAK_", "")
                    visPoleStretch.rest_length = visPole.length * 100
                    visPoleStretch.volume = "NO_VOLUME"

                    # Vis Hide Driver
                    VisHideDriver = visPole.bone.driver_add("hide").driver
                    VisHideDriver.type = "SCRIPTED"
                    var = VisHideDriver.variables.new()
                    var.type = "SINGLE_PROP"
                    target = var.targets[0]
                    target.id_type = "ARMATURE"
                    target.id = self.activeObject.data
                    target.data_path = "hideVis"
                    VisHideDriver.expression = var.name

                    # generate line custom shape
                    self.generateCustomBoneShape(visPole, collection, boneShape.line, redGroup, True)

                    # FK UPPERARM

                    FKBone = poseBones.get("FK_" + bone.name.replace("TWEAK_", ""))

                    # generate fk custom shape
                    getBoneShape = getattr(boneShape, bone.bone.customShapeType)
                    getBoneShapeParam = bone.bone.customShapeParam[:len(inspect.getfullargspec(getBoneShape)[0])]
                    self.generateCustomBoneShape(FKBone, collection, getBoneShape(*getBoneShapeParam), leftSideGroup if FKBone.bone.head_local.x >= 0 else rightSideGroup, False)

                    # FK Hide Driver
                    FKHideDriver = FKBone.bone.driver_add("hide").driver
                    FKHideDriver.type = "SCRIPTED"
                    var = FKHideDriver.variables.new()
                    var.type = "SINGLE_PROP"
                    target = var.targets[0]
                    target.id_type = "ARMATURE"
                    target.id = self.activeObject.data
                    target.data_path = "hideFK"
                    FKHideDriver.expression = var.name

                    # FK LOWERARM

                    FKBone = poseBones.get("FK_" + lowerarm.name.replace("TWEAK_", ""))

                    # generate fk custom shape
                    getBoneShape = getattr(boneShape, lowerarm.bone.customShapeType)
                    getBoneShapeParam = lowerarm.bone.customShapeParam[:len(inspect.getfullargspec(getBoneShape)[0])]
                    self.generateCustomBoneShape(FKBone, collection, getBoneShape(*getBoneShapeParam), leftSideGroup if FKBone.bone.head_local.x >= 0 else rightSideGroup, False)

                    # FK Hide Driver
                    FKHideDriver = FKBone.bone.driver_add("hide").driver
                    FKHideDriver.type = "SCRIPTED"
                    var = FKHideDriver.variables.new()
                    var.type = "SINGLE_PROP"
                    target = var.targets[0]
                    target.id_type = "ARMATURE"
                    target.id = self.activeObject.data
                    target.data_path = "hideFK"
                    FKHideDriver.expression = var.name

                    if hand:
                        # FK HAND

                        FKBone = poseBones.get("FK_" + hand.name.replace("TWEAK_", ""))

                        # generate fk custom shape
                        getBoneShape = getattr(boneShape, hand.bone.customShapeType)
                        getBoneShapeParam = hand.bone.customShapeParam[:len(inspect.getfullargspec(getBoneShape)[0])]
                        self.generateCustomBoneShape(FKBone, collection, getBoneShape(*getBoneShapeParam), leftSideGroup if FKBone.bone.head_local.x >= 0 else rightSideGroup, False)

                        # FK Hide Driver
                        FKHideDriver = FKBone.bone.driver_add("hide").driver
                        FKHideDriver.type = "SCRIPTED"
                        var = FKHideDriver.variables.new()
                        var.type = "SINGLE_PROP"
                        target = var.targets[0]
                        target.id_type = "ARMATURE"
                        target.id = self.activeObject.data
                        target.data_path = "hideFK"
                        FKHideDriver.expression = var.name

                    # register control ik to bone
                    ikBone.bone.controlIK = True
                    ikBone.bone.pointABoneIK = bone.name.replace("TWEAK_", "")
                    ikBone.bone.pointBBoneIK = lowerarm.name.replace("TWEAK_", "")

                    if bone.bone.handBone and hand:
                        controlRotationHandIK = hand.constraints.new(type="COPY_TRANSFORMS")
                        controlRotationHandIK.name = "HAND_CONTROL_IK"
                        controlRotationHandIK.show_expanded = False
                        controlRotationHandIK.target = self.activeObject
                        controlRotationHandIK.subtarget = bone.bone.subtargetIK
                        controlRotationHandIK.mix_mode = "REPLACE"
                        controlRotationHandIK.target_space = "POSE"
                        controlRotationHandIK.owner_space = "POSE"
                        # IK DRIVER
                        influenceDriver = controlRotationHandIK.driver_add("influence").driver
                        influenceDriver.type = "SCRIPTED"
                        var = influenceDriver.variables.new()
                        var.type = "SINGLE_PROP"
                        target = var.targets[0]
                        target.id_type = "ARMATURE"
                        target.id = self.activeObject.data
                        target.data_path = ikBone.bone.path_from_id("switchIK")
                        influenceDriver.expression = var.name + " == 0"

                        # LIMIT LOCATION IN IK MODE
                        limitLocationIK = hand.constraints.new(type="LIMIT_LOCATION")
                        limitLocationIK.name = "LIMIT_LOCATION_IK"
                        limitLocationIK.show_expanded = False
                        limitLocationIK.owner_space = "LOCAL"
                        limitLocationIK.min_x = 0
                        limitLocationIK.min_y = 0
                        limitLocationIK.min_z = 0
                        limitLocationIK.max_x = 0
                        limitLocationIK.max_y = 0
                        limitLocationIK.max_z = 0
                        limitLocationIK.use_min_x = True
                        limitLocationIK.use_min_y = True
                        limitLocationIK.use_min_z = True
                        limitLocationIK.use_max_x = True
                        limitLocationIK.use_max_y = True
                        limitLocationIK.use_max_z = True
                        # IK DRIVER
                        influenceDriver = limitLocationIK.driver_add("influence").driver
                        influenceDriver.type = "SCRIPTED"
                        var = influenceDriver.variables.new()
                        var.type = "SINGLE_PROP"
                        target = var.targets[0]
                        target.id_type = "ARMATURE"
                        target.id = self.activeObject.data
                        target.data_path = ikBone.bone.path_from_id("switchIK")
                        influenceDriver.expression = var.name + " == 0"

                        controlRotationHandFK = hand.constraints.new(type="COPY_TRANSFORMS")
                        controlRotationHandFK.name = "HAND_CONTROL_FK"
                        controlRotationHandFK.show_expanded = False
                        controlRotationHandFK.target = self.activeObject
                        controlRotationHandFK.subtarget = "FK_" + hand.name.replace("TWEAK_", "")
                        controlRotationHandFK.mix_mode = "REPLACE"
                        controlRotationHandFK.target_space = "POSE"
                        controlRotationHandFK.owner_space = "POSE"
                        # FK DRIVER
                        influenceDriver = controlRotationHandFK.driver_add("influence").driver
                        influenceDriver.type = "SCRIPTED"
                        var = influenceDriver.variables.new()
                        var.type = "SINGLE_PROP"
                        target = var.targets[0]
                        target.id_type = "ARMATURE"
                        target.id = self.activeObject.data
                        target.data_path = ikBone.bone.path_from_id("switchIK")
                        influenceDriver.expression = var.name + " == 1"

                        # FLOOR HAND
                        floorHand = poseBones.get("FLOOR_" + hand.name.replace("TWEAK_", ""))

                        # ADD FLOOR CONSTRAINT
                        self.addFloorConstraint(ikBone, floorHand.name, 3)

                        # generate floor custom shape
                        self.generateCustomBoneShape(floorHand, collection, boneShape.floor(1, 1), yellowGroup, False)

        # TWIST BONE CUSTOM SHAPE
        for bone in [bone for bone in poseBones if bone.bone.UE4RIGTYPE == "TWIST_BONE" and bone.custom_shape is None]:
            # generate twist custom shape
            getBoneShape = getattr(boneShape, bone.bone.customShapeType)
            getBoneShapeParam = bone.bone.customShapeParam[:len(inspect.getfullargspec(getBoneShape)[0])]
            self.generateCustomBoneShape(bone, collection, getBoneShape(*getBoneShapeParam), greenGroup if bone.bone.head_local.x == 0 else leftSideGroup if bone.bone.head_local.x > 0 else rightSideGroup, False)

        # PELVIS
        for bone in [bone for bone in poseBones if bone.bone.UE4RIGTYPE == "PELVIS" and bone.custom_shape is None]:
            bone.lock_location = [True, True, True]
            control = poseBones.get("CONTROL_" + bone.name.replace("TWEAK_", ""))
            control.rotation_mode = "XYZ"
            control.lock_rotation =[True, True, True]

            # generate pelvis custom shape
            getBoneShape = getattr(boneShape, bone.bone.customShapeType)
            getBoneShapeParam = bone.bone.customShapeParam[:len(inspect.getfullargspec(getBoneShape)[0])]
            self.generateCustomBoneShape(bone, collection, getBoneShape(*getBoneShapeParam), greenGroup, False)

            locConstraint = bone.constraints.new("COPY_LOCATION")
            locConstraint.name = "LOCATION"
            locConstraint.show_expanded = False
            locConstraint.target = self.activeObject
            locConstraint.subtarget = control.name
            locConstraint.target_space = "POSE"
            locConstraint.owner_space = "POSE"

            # generate pelvis control custom shape
            diameterBlock = (bone.bone.customShapeParam[1] * 2) + 2.5
            self.generateCustomBoneShape(control, collection, boneShape.block(diameterBlock, diameterBlock, -1, 1), redGroup, False)

        # SPINE
        for bone in [bone for bone in poseBones if bone.bone.UE4RIGTYPE == "SPINE" and bone.custom_shape is None]:
            # generate spine custom shape
            getBoneShape = getattr(boneShape, bone.bone.customShapeType)
            getBoneShapeParam = bone.bone.customShapeParam[:len(inspect.getfullargspec(getBoneShape)[0])]
            self.generateCustomBoneShape(bone, collection, getBoneShape(*getBoneShapeParam), greenGroup, False)

            # STRETCH BONE + DRIVER
            if bone.bone.stretchBoneTarget:
                stretchBone = poseBones.get("STRETCH_" + bone.name.replace("TWEAK_", ""))
                stretchBoneConstraint = stretchBone.constraints.new("STRETCH_TO")
                stretchBoneConstraint.name = "STRETCH_TO_BONE"
                stretchBoneConstraint.show_expanded = False
                stretchBoneConstraint.target = self.activeObject
                stretchBoneConstraint.subtarget = bone.bone.stretchBoneTarget
                stretchBoneConstraint.rest_length = stretchBone.length * 100
                stretchBoneConstraint.influence = 0.5

                # generate stretch box custom shape
                self.generateCustomBoneShape(stretchBone, collection, boneShape.block(4, 4, 0, 4), redGroup, False)

                # STRETCH INFLUENCE DRIVER
                influenceDriver = stretchBoneConstraint.driver_add("influence").driver
                influenceDriver.type = "SCRIPTED"
                var = influenceDriver.variables.new()
                var.type = "SINGLE_PROP"
                target = var.targets[0]
                target.id_type = "ARMATURE"
                target.id = self.activeObject.data
                target.data_path = bone.bone.path_from_id("stretchBone")
                influenceDriver.expression = var.name

                # STRETCH VOLUME DRIVER
                influenceDriver = stretchBoneConstraint.driver_add("volume").driver
                influenceDriver.type = "SCRIPTED"
                var = influenceDriver.variables.new()
                var.type = "SINGLE_PROP"
                target = var.targets[0]
                target.id_type = "ARMATURE"
                target.id = self.activeObject.data
                target.data_path = bone.bone.path_from_id("stretchBoneMode")
                influenceDriver.expression = var.name

        # NECK
        for bone in [bone for bone in poseBones if bone.bone.UE4RIGTYPE == "NECK" and bone.custom_shape is None]:
            # generate neck custom shape
            getBoneShape = getattr(boneShape, bone.bone.customShapeType)
            getBoneShapeParam = bone.bone.customShapeParam[:len(inspect.getfullargspec(getBoneShape)[0])]
            self.generateCustomBoneShape(bone, collection, getBoneShape(*getBoneShapeParam), greenGroup, False)

            # STRETCH BONE
            if bone.bone.stretchBoneTarget:
                stretchBone = poseBones.get("STRETCH_" + bone.name.replace("TWEAK_", ""))
                stretchBoneConstraint = stretchBone.constraints.new("STRETCH_TO")
                stretchBoneConstraint.name = "STRETCH_TO_BONE"
                stretchBoneConstraint.show_expanded = False
                stretchBoneConstraint.target = self.activeObject
                stretchBoneConstraint.subtarget = bone.bone.stretchBoneTarget
                stretchBoneConstraint.rest_length = stretchBone.length * 100
                stretchBoneConstraint.influence = 1

                # generate stretch box custom shape
                self.generateCustomBoneShape(stretchBone, collection, boneShape.block(4, 4, 0, 4), redGroup, False)
                # STRETCH INFLUENCE DRIVER
                influenceDriver = stretchBoneConstraint.driver_add("influence").driver
                influenceDriver.type = "SCRIPTED"
                var = influenceDriver.variables.new()
                var.type = "SINGLE_PROP"
                target = var.targets[0]
                target.id_type = "ARMATURE"
                target.id = self.activeObject.data
                target.data_path = bone.bone.path_from_id("stretchBone")
                influenceDriver.expression = var.name

                # STRETCH VOLUME DRIVER
                influenceDriver = stretchBoneConstraint.driver_add("volume").driver
                influenceDriver.type = "SCRIPTED"
                var = influenceDriver.variables.new()
                var.type = "SINGLE_PROP"
                target = var.targets[0]
                target.id_type = "ARMATURE"
                target.id = self.activeObject.data
                target.data_path = bone.bone.path_from_id("stretchBoneMode")
                influenceDriver.expression = var.name

        # HEAD
        for bone in [bone for bone in poseBones if bone.bone.UE4RIGTYPE == "HEAD" and bone.custom_shape is None]:
            # generate head custom shape
            getBoneShape = getattr(boneShape, bone.bone.customShapeType)
            getBoneShapeParam = bone.bone.customShapeParam[:len(inspect.getfullargspec(getBoneShape)[0])]
            self.generateCustomBoneShape(bone, collection, getBoneShape(*getBoneShapeParam), greenGroup, False)

            lookConstraint = bone.constraints.new("DAMPED_TRACK")
            lookConstraint.name = "LOOK_CONTROL"
            lookConstraint.show_expanded = False
            lookConstraint.target = self.activeObject
            lookConstraint.subtarget = "CONTROL_" + bone.name.replace("TWEAK_", "")
            lookConstraint.track_axis = "TRACK_Z"

            controlBone = poseBones.get(lookConstraint.subtarget)

            # generate head control custom shape
            self.generateCustomBoneShape(controlBone, collection, boneShape.circle(16, 2.5, 0), redGroup, False)

            # VIS CONTROL
            visControl = poseBones.get("VISCONTROL_" + bone.name.replace("TWEAK_", ""))
            visControl.bone.hide_select = True

            visControlLocation = visControl.constraints.new(type="COPY_LOCATION")
            visControlLocation.name = "GET_CONTROL_LOCATION"
            visControlLocation.show_expanded = False
            visControlLocation.target = self.activeObject
            visControlLocation.subtarget = lookConstraint.subtarget
            visControlLocation.target_space = "POSE"
            visControlLocation.owner_space = "POSE"

            visControlStretch = visControl.constraints.new(type="STRETCH_TO")
            visControlStretch.name = "STRETCH_TO_LOWERARM"
            visControlStretch.show_expanded = False
            visControlStretch.target = self.activeObject
            visControlStretch.subtarget = bone.name
            visControlStretch.rest_length = visControl.length*100
            visControlStretch.volume = "NO_VOLUME"

            # generate line custom shape
            self.generateCustomBoneShape(visControl, collection, boneShape.line, redGroup, True)

            # Vis Hide Driver
            VisHideDriver = visControl.bone.driver_add("hide").driver
            VisHideDriver.type = "SCRIPTED"
            var = VisHideDriver.variables.new()
            var.type = "SINGLE_PROP"
            target = var.targets[0]
            target.id_type = "ARMATURE"
            target.id = self.activeObject.data
            target.data_path = "hideVis"
            VisHideDriver.expression = var.name

        # COPY_BONE
        for bone in [bone for bone in poseBones if bone.bone.UE4RIGTYPE == "COPY_BONE" and bone.custom_shape is None]:
            # generate copy_bone custom shape
            getBoneShape = getattr(boneShape, bone.bone.customShapeType)
            getBoneShapeParam = bone.bone.customShapeParam[:len(inspect.getfullargspec(getBoneShape)[0])]
            self.generateCustomBoneShape(bone, collection, getBoneShape(*getBoneShapeParam), greenGroup if bone.bone.head_local.x == 0 else leftSideGroup if bone.bone.head_local.x > 0 else rightSideGroup, False)

        # LANDMARK
        for bone in [bone for bone in poseBones if bone.bone.UE4RIGTYPE == "LANDMARK"]:
            boneControl = self.poseBone(bone.bone.subtargetIK)
            # constraint
            constraint = bone.constraints.new(type="COPY_TRANSFORMS")
            constraint.name = "TRANSFORM"
            constraint.show_expanded = False
            constraint.target = self.activeObject
            constraint.subtarget = bone.bone.subtargetIK
            constraint.mix_mode = "REPLACE"
            constraint.target_space = "LOCAL"
            constraint.owner_space = "LOCAL"
            # generate landmark control custom shape
            getBoneShape = getattr(boneShape, bone.bone.customShapeType)
            getBoneShapeParam = bone.bone.customShapeParam[:len(inspect.getfullargspec(getBoneShape)[0])]
            self.generateCustomBoneShape(boneControl, collection, getBoneShape(*getBoneShapeParam), greenGroup, False)

        # JAW
        for bone in [bone for bone in poseBones if bone.bone.UE4RIGTYPE == "JAW"]:
            boneControl = self.poseBone(bone.bone.subtargetIK)
            # generate jaw custom shape
            getBoneShape = getattr(boneShape, bone.bone.customShapeType)
            getBoneShapeParam = bone.bone.customShapeParam[:len(inspect.getfullargspec(getBoneShape)[0])]
            self.generateCustomBoneShape(bone, collection, getBoneShape(*getBoneShapeParam), greenGroup, False)
            # constraint
            constraint = bone.constraints.new(type="DAMPED_TRACK")
            constraint.name = "TRACK"
            constraint.show_expanded = False
            constraint.target = self.activeObject
            constraint.subtarget = bone.bone.subtargetIK
            constraint.track_axis = "TRACK_Y"
            constraint.head_tail = 0.5
            # generate jaw control custom shape
            self.generateCustomBoneShape(boneControl, collection, boneShape.rectangle(2.5, 2.5, 0), redGroup, False)

        # EYE
        for bone in [bone for bone in poseBones if bone.bone.UE4RIGTYPE == "EYE"]:
            boneControl = self.poseBone(bone.bone.subtargetIK)
            # generate eye custom shape
            getBoneShape = getattr(boneShape, bone.bone.customShapeType)
            getBoneShapeParam = bone.bone.customShapeParam[:len(inspect.getfullargspec(getBoneShape)[0])]
            self.generateCustomBoneShape(bone, collection, getBoneShape(*getBoneShapeParam), greenGroup, False)
            # generate eye control custom shape
            self.generateCustomBoneShape(boneControl, collection, boneShape.circle(16, 1, 0), redGroup, False)

            lookConstraint = bone.constraints.new("DAMPED_TRACK")
            lookConstraint.name = "LOOK_CONTROL"
            lookConstraint.show_expanded = False
            lookConstraint.target = self.activeObject
            lookConstraint.subtarget = bone.bone.subtargetIK
            lookConstraint.track_axis = "TRACK_Y"

            for part in ["UPPER", "LOWER"]:
                eyelidRotation = self.poseBone(bone.name.replace("_TWEAK", "_EYELID_" + part + "_ROTATION"))
                eyelidRotation.lock_location = (True, True, True)
                # generate eyelid rotation control custom shape
                self.generateCustomBoneShape(eyelidRotation, collection, boneShape.rectangle(0.5, 0.5, 0), redGroup, False)
                eyelidRotation.custom_shape_transform = self.poseBone(bone.name.replace("_TWEAK", "_EYELID_" + part + "_PIVOT_ROTATION"))

            for eyelid in [eyelid for eyelid in bone.children if eyelid.bone.UE4RIGTYPE in ["EYELID_UPPER", "EYELID_LOWER"]]:
                eyelidControl = self.poseBone(eyelid.name.replace("_TWEAK", "_CONTROL"))
                constraint = eyelid.constraints.new(type="COPY_TRANSFORMS")
                constraint.name = "TRANSFORM"
                constraint.show_expanded = False
                constraint.target = self.activeObject
                constraint.subtarget = eyelid.bone.subtargetIK
                constraint.mix_mode = "REPLACE"
                constraint.target_space = "POSE"
                constraint.owner_space = "POSE"
                # generate eyelid control custom shape
                self.generateCustomBoneShape(eyelidControl, collection, boneShape.block(0.5, 0.5, -0.25, 0.25), greenGroup, False)

        bpy.ops.armature.armature_layers(layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.ops.pose.select_all(action="DESELECT")
        bpy.ops.object.mode_set(mode="OBJECT")
        # Deselect all object
        bpy.ops.object.select_all(action="DESELECT")
        # scale to unreal engine mannequin
        self.activeObject.select_set(state=True)
        self.activeObject.scale = (100, 100, 100)
        bpy.ops.object.transform_apply(location = False, scale = True, rotation = False)
        self.activeObject.scale = (0.01, 0.01, 0.01)
        self.activeObject.select_set(state=False)
        self.activeObject.lock_scale = [True, True, True]

        self.activeObject.show_in_front = False
        self.activeObject.data.UE4RIG = False
        self.activeObject.data.UE4RIGGED = True

        bpy.ops.object.mode_set(mode=oldMode)