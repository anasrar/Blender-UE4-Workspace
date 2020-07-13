import bpy, math
from mathutils import Matrix

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
            root.select_head = True
            root.select_tail = True
            root.select = True
            bpy.ops.armature.bone_layers(layers=(False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True))
            bpy.ops.armature.select_all(action="DESELECT")

            if rootBone == "hand" and self.getBone("hand_r") is not None:
                if self.getBone("ik_hand_gun") is None:
                    rightHand = self.getBone("hand_r")
                    gun = editBones.new("ik_hand_gun")
                    handGun = gun
                    gun.head = rightHand.head
                    gun.tail = rightHand.tail
                    gun.roll = rightHand.roll
                    gun.parent = self.getBone("ik_" + rootBone +"_root")
                    gun.select_head = True
                    gun.select_tail = True
                    gun.select = True
                    bpy.ops.armature.bone_layers(layers=(False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True))
                    bpy.ops.armature.select_all(action="DESELECT")

            for side in sides:
                bone = self.getBone(rootBone + "_" + side)
                if bone is not None:
                    if self.getBone("ik_" + rootBone + "_" + side) is None:
                        ik = editBones.new("ik_" + rootBone + "_" + side)
                        ik.head = bone.head
                        ik.tail = bone.tail
                        ik.roll = bone.roll
                        ik.parent = (self.getBone("ik_" + rootBone +"_root"), handGun)[handGun is not None]
                        ik.select_head = True
                        ik.select_tail = True
                        ik.select = True
                        bpy.ops.armature.bone_layers(layers=(False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True))
                        bpy.ops.armature.select_all(action="DESELECT")

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
            editBones.remove(bone)

        for bone in [editBone for editBone in editBones if editBone.get("boneOrient", False)]:
            if self.getBone("ORIENT_" + bone.name) is None:
                # create new temporary bone
                newBone = editBones.new("ORIENT_" + bone.name)
                newBone.head = bone.head
                newBone.tail = bone.tail
                newBone.roll = bone.roll

                # rotate active bone
                bpy.ops.armature.select_all(action="DESELECT")
                editBones.active = newBone
                editBones.active.select = True
                editBones.active.select_head = True
                editBones.active.select_tail = True

                orient = bone.get("boneOrient").split("|")
                # bug on blender version 2.83
                # https://github.com/anasrar/Blender-UE4-Workspace/issues/5
                # https://blenderartists.org/t/why-i-got-difference-rotate-bone-result-in-version-2-82-and-2-83/1234794
                rotationRadian = float(orient[0]) if bpy.app.version in [(2, 83, 0), (2, 83, 1)] else -float(orient[0])
                bpy.ops.transform.rotate(value=rotationRadian, orient_axis=orient[2], orient_type="NORMAL", mirror=False)
                # add roll
                newBone.roll += float(orient[1])

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
                elif bone.get("UE4RIGTYPE") == "FACE_JAW_HUMAN":
                    newBone.tail[0] = newBone.head[0]
                    newBone.tail[1] = newBone.head[1] + bone.length
                    newBone.tail[2] = newBone.head[2]
                    newBone.roll = 0

                # set parent
                if bone.parent:
                    orientBone = self.getBone("ORIENT_" + bone.parent.name)
                    newBone.parent = orientBone if orientBone else self.getBone(bone.parent.name)

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

    def spineRecursiveBone(self, children, collection, vertices, edges, group):
        """recursive function to make custom shape to spine

        :param children: list bpy.types.PoseBone
        :type children: bpy.types.PoseBone
        :param collection: collection to link object
        :type collection: bpy.types.Collection
        :param vertices: list tuple coordinate
        :type vertices: list tuple
        :param edges: list tuple edges line
        :type edges: list tuple
        :param group: bone group of armature to assign color
        :type group: bpy.types.BoneGroup
        :returns: None
        :rtype: None
        """

        for bone in children:
            # check is child have rig type and bone is connect with parent
            if not bone.get("UE4RIGTYPE") and bone.bone.use_connect:
                mesh = bpy.data.meshes.new("UE4WSBoneShape_" + bone.name)
                objSpine = bpy.data.objects.new(mesh.name,mesh)
                collection.objects.link(objSpine)
                mesh.from_pydata([(v[0] / bone.length, 0.5, v[2] / bone.length) for v in vertices], edges, [])
                bone.custom_shape = objSpine
                bone.bone_group = group
                self.spineRecursiveBone(bone.children, collection, vertices, edges, group)

    def neckRecursiveBone(self, children, collection, vertices, edges, group):
        """recursive function to make custom shape to neck

        :param children: list bpy.types.PoseBone
        :type children: bpy.types.PoseBone
        :param collection: collection to link object
        :type collection: bpy.types.Collection
        :param vertices: list tuple coordinate
        :type vertices: list tuple
        :param edges: list tuple edges line
        :type edges: list tuple
        :param group: bone group of armature to assign color
        :type group: bpy.types.BoneGroup
        :returns: None
        :rtype: None
        """

        for bone in children:
            # check is child have rig type and bone is connect with parent
            if not bone.get("UE4RIGTYPE") and bone.bone.use_connect:
                mesh = bpy.data.meshes.new("UE4WSBoneShape_" + bone.name)
                objNeck = bpy.data.objects.new(mesh.name,mesh)
                collection.objects.link(objNeck)
                mesh.from_pydata([(v[0] * 5, 0.5, v[2] * 5) for v in vertices], edges, [])
                bone.custom_shape = objNeck
                bone.bone_group = group
                self.neckRecursiveBone(bone.children, collection, vertices, edges, group)

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
        for bone in [bone for bone in editBones if bone.get("boneOrient", False)]:
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
        if self.activeObject.get("UE4RIGTYPE") == "HUMANOID":
            self.addIKBone()
        # create group bone
        boneGroups = self.activeObject.pose.bone_groups
        redGroup = boneGroups.new(name="red")
        redGroup.color_set = "CUSTOM"
        redGroup.colors.select = [0.6, 0.0, 0.0]
        redGroup.colors.normal = [0.5, 0.0, 0.0]
        redGroup.colors.active = [0.9, 0.0, 0.0]

        greenGroup = boneGroups.new(name="green")
        greenGroup.color_set = "CUSTOM"
        greenGroup.colors.select = [0.0, 0.45, 0.0]
        greenGroup.colors.normal = [0.0, 0.4, 0.0]
        greenGroup.colors.active = [0.0, 0.9, 0.0]

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
            root.tail = [0, 1, 0]
            root.roll = 0
            for bone in [bone for bone in editBones if bone.parent is None and bone.name != "root"]:
                bone.parent = root

            vertices = [(-0.10140155255794525, -0.7132686972618103, 0.0), (-0.18653807044029236, -0.7201929092407227, 0.0), (-0.1261064112186432, -0.7435259222984314, 0.0), (-0.15726853907108307, -0.7460603713989258, 0.0), (0.10140155255794525, -0.7132686972618103, 0.0), (0.18653807044029236, -0.7201929092407227, 0.0), (0.1261064112186432, -0.7435259222984314, 0.0), (0.15726853907108307, -0.7460603713989258, 0.0), (-0.03633283078670502, -0.5697637796401978, 0.0), (0.03633283078670502, -0.5697637796401978, 0.0), (-0.01329873874783516, -0.5404342412948608, 0.0), (0.01329873874783516, -0.5404342412948608, 0.0), (-0.7750394940376282, 0.28188955783843994, 0.0), (-0.8134618997573853, 0.22019290924072266, 0.0), (-0.8121141195297241, 0.27783632278442383, 0.0), (-0.826177716255188, 0.25525379180908203, 0.0), (-0.6891869306564331, 0.43808478116989136, 0.0), (-0.6637136936187744, 0.5, 0.0), (-0.70865398645401, 0.4690423905849457, 0.0), (-0.6993301510810852, 0.49170494079589844, 0.0), (-0.5812922120094299, 0.256325900554657, 0.0), (-0.5565749406814575, 0.3067322373390198, 0.0), (-0.5460538268089294, 0.2588665187358856, 0.0), (-0.537006676197052, 0.27731651067733765, 0.0), (0.6891869306564331, 0.43808478116989136, 0.0), (0.6637136936187744, 0.5, 0.0), (0.70865398645401, 0.4690423905849457, 0.0), (0.6993301510810852, 0.49170494079589844, 0.0), (0.7750394940376282, 0.28188955783843994, 0.0), (0.8134618997573853, 0.22019290924072266, 0.0), (0.8121141195297241, 0.27783632278442383, 0.0), (0.826177716255188, 0.25525379180908203, 0.0), (0.5565749406814575, 0.3067322373390198, 0.0), (0.5812922120094299, 0.256325900554657, 0.0), (0.537006676197052, 0.27731651067733765, 0.0), (0.5460538268089294, 0.2588665187358856, 0.0)]
            edges = [(0, 2), (2, 3), (3, 1), (4, 6), (6, 7), (7, 5), (8, 10), (10, 11), (11, 9), (12, 14), (14, 15), (15, 13), (16, 18), (18, 19), (19, 17), (20, 22), (22, 23), (23, 21), (24, 26), (26, 27), (27, 25), (28, 30), (30, 31), (31, 29), (32, 34), (34, 35), (35, 33), (0, 8), (1, 13), (4, 9), (5, 29), (12, 20), (16, 21), (17, 25), (24, 32), (28, 33)]

            mesh = bpy.data.meshes.new("UE4WSBoneShape_Root")
            objRootShape = bpy.data.objects.new(mesh.name,mesh)
            collection.objects.link(objRootShape)
            mesh.from_pydata(vertices, edges, [])
            bpy.ops.object.mode_set(mode="POSE")
            poseBone = self.poseBone("root")
            if poseBone is None:
               poseBone = self.poseBone("root")
            poseBone.custom_shape = objRootShape
            poseBone.bone_group = redGroup
            bpy.ops.object.mode_set(mode="EDIT")

        # transfer rig type to pose bone
        for bone in [bone for bone in editBones if bone.get("UE4RIGTYPE")]:
            poseBone = self.poseBone(bone.name)
            if poseBone is not None:
                poseBone["UE4RIGTYPE"] = bone.get("UE4RIGTYPE")

        # FINGER
        for bone in [bone for bone in editBones if bone.get("UE4RIGTYPE") == "FINGER"]:
            bpy.ops.armature.select_all(action="DESELECT")
            boneName = bone.name
            # CONTROL BONE
            control = editBones.new("CONTROL_" + boneName.replace("TWEAK_", ""))
            control.use_deform = False
            control.head = bone.head
            control.tail = bone.tail
            control.roll = bone.roll
            control.length = 0.05
            control.parent = bone.parent
            control.select = True
            control.select_head = True
            control.select_tail = True
            bpy.ops.transform.translate(value=(0, 0, 0.025), orient_type="NORMAL", orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type="GLOBAL", constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff="SMOOTH", proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            bpy.ops.armature.bone_layers(layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            control.select = False
            control.select_head = False
            control.select_tail = False
            poseBone = self.poseBone(boneName)
            if poseBone is not None:
                poseBone["subtargetRotation"] = control.name

        # LEG_HUMAN
        for bone in [bone for bone in editBones if bone.get("UE4RIGTYPE") == "LEG_HUMAN"]:
            bpy.ops.armature.select_all(action="DESELECT")
            boneName = bone.name
            # POLE BONE
            canCreatePole = [bn for bn in bone.children if bn.name.startswith("TWEAK_") and not "_twist_" in bn.name]
            if canCreatePole:
                pole = editBones.new("IKPOLE_" + boneName.replace("TWEAK_", ""))
                pole.use_deform = False
                pole.head = [bone.tail[0], bone.head[1] - bone.length -0.5, bone.tail[2]]
                pole.tail = [bone.tail[0], bone.tail[1], bone.tail[2]]
                pole.roll = 0
                pole.length = 0.25
                # IK TARGET BONE
                calfBone = canCreatePole[0]
                ikTarget = editBones.new("IKTARGET_" + calfBone.name.replace("TWEAK_", ""))
                ikTarget.use_deform = False
                ikTarget.head = [calfBone.tail[0], calfBone.tail[1], calfBone.tail[2]]
                ikTarget.tail = [calfBone.tail[0], calfBone.tail[1] + 0.15, calfBone.tail[2]]
                ikTarget.roll = 0
                # CONTROLLER BONE
                control = editBones.new("CONTROL_" + calfBone.name.replace("TWEAK_", ""))
                control.use_deform = False
                control.head = [calfBone.tail[0], calfBone.tail[1], 0]
                control.tail = [calfBone.tail[0], calfBone.tail[1] + 0.2, 0]
                control.roll = 0
                ikTarget.parent = control

                ikTarget.select = True
                ikTarget.select_head = True
                ikTarget.select_tail = True
                bpy.ops.armature.bone_layers(layers=(False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
                bpy.ops.armature.select_all(action="DESELECT")
                pole.select = True
                pole.select_head = True
                pole.select_tail = True
                control.select = True
                control.select_head = True
                control.select_tail = True
                bpy.ops.armature.bone_layers(layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
                bpy.ops.armature.select_all(action="DESELECT")

                # FK BONE
                fkBone1 = editBones.new("FK_" + boneName.replace("TWEAK_", ""))
                fkBone1.use_deform = False
                fkBone1.head = bone.head
                fkBone1.tail = bone.tail
                fkBone1.roll = bone.roll
                fkBone1.parent = bone.parent
                fkBone2 = editBones.new("FK_" + calfBone.name.replace("TWEAK_", ""))
                fkBone2.use_deform = False
                fkBone2.head = calfBone.head
                fkBone2.tail = calfBone.tail
                fkBone2.roll = calfBone.roll
                fkBone2.parent = fkBone1
                fkBone2.use_connect = calfBone.use_connect

                # Move to second layer
                fkBone1.select = True
                fkBone1.select_head = True
                fkBone1.select_tail = True
                fkBone2.select = True
                fkBone2.select_head = True
                fkBone2.select_tail = True
                bpy.ops.armature.bone_layers(layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
                bpy.ops.armature.select_all(action="DESELECT")

                # move to third layer
                bone.select = True
                bone.select_head = True
                bone.select_tail = True
                calfBone.select = True
                calfBone.select_head = True
                calfBone.select_tail = True
                bpy.ops.armature.bone_layers(layers=(False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
                bpy.ops.armature.select_all(action="DESELECT")

                poseBone = self.poseBone(boneName)
                if poseBone is not None:
                    poseBone["IKTarget"] = ikTarget.name
                    poseBone["IKPole"] = pole.name
                    poseBone["BoneSide"] = pole.head[0]
                # CHECK IF FOOT EXIST
                isFootExist = [bn for bn in calfBone.children if bn.name.startswith("TWEAK_") and not "_twist_" in bn.name]
                if isFootExist:
                    footBone = isFootExist[0]
                    mimikFoot = editBones.new("MIMIK_" + footBone.name.replace("TWEAK_", ""))
                    mimikFoot.use_deform = False
                    mimikFoot.head = [footBone.tail[0], footBone.tail[1], footBone.tail[2]]
                    mimikFoot.tail = [footBone.tail[0], footBone.tail[1] + 0.15, footBone.tail[2]]
                    mimikFoot.roll = 0
                    mimikFoot.parent = control
                    ikTarget.parent = mimikFoot
                    control.name = "CONTROL_" + footBone.name.replace("TWEAK_", "")

                    liftControl = editBones.new("CONTROLLIFT_" + footBone.name.replace("TWEAK_", ""))
                    liftControl.use_deform = False
                    liftControl.head = [control.head[0], control.head[1] + 0.15, 0]
                    liftControl.tail = [control.tail[0], control.tail[1] + 0.15, 0]
                    liftControl.roll = 0
                    liftControl.parent = control

                    rotationControl = editBones.new("CONTROLROTATION_" + footBone.name.replace("TWEAK_", ""))
                    rotationControl.use_deform = False
                    rotationControl.head = [calfBone.tail[0], footBone.tail[1] - 0.35, calfBone.tail[2]]
                    rotationControl.tail = [calfBone.tail[0], footBone.tail[1] - 0.2, calfBone.tail[2]]
                    rotationControl.roll = 0
                    rotationControl.parent = control
                    if poseBone is not None:
                        poseBone["FootController"] = True

                    mimikFoot.select = True
                    mimikFoot.select_head = True
                    mimikFoot.select_tail = True
                    bpy.ops.armature.bone_layers(layers=(False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
                    bpy.ops.armature.select_all(action="DESELECT")
                    liftControl.select = True
                    liftControl.select_head = True
                    liftControl.select_tail = True
                    rotationControl.select = True
                    rotationControl.select_head = True
                    rotationControl.select_tail = True
                    bpy.ops.armature.bone_layers(layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
                    bpy.ops.armature.select_all(action="DESELECT")

                    # CHECK IF TOE EXIST
                    isToeExist = [bn for bn in footBone.children if bn.name.startswith("TWEAK_") and not "_twist_" in bn.name]
                    if isToeExist:
                        toeBone = isToeExist[0]
                        toeControl = editBones.new("CONTROL_" + toeBone.name.replace("TWEAK_", ""))
                        toeControl.use_deform = False
                        toeControl.head = [toeBone.head[0], toeBone.head[1], 0]
                        toeControl.tail = [toeBone.tail[0], toeBone.tail[1], 0]
                        toeControl.roll = 0
                        toeControl.parent = footBone
                        if poseBone is not None:
                            poseBone["ToeController"] = True
                        toeControl.select = True
                        toeControl.select_head = True
                        toeControl.select_tail = True
                        bpy.ops.armature.bone_layers(layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
                        bpy.ops.armature.select_all(action="DESELECT")

        # ARM_HUMAN
        for bone in [bone for bone in editBones if bone.get("UE4RIGTYPE") == "ARM_HUMAN"]:
            bpy.ops.armature.select_all(action="DESELECT")
            boneName = bone.name
            # POLE BONE
            canCreatePole = [bn for bn in bone.children if bn.name.startswith("TWEAK_") and not "_twist_" in bn.name]
            if canCreatePole:
                pole = editBones.new("IKPOLE_" + boneName.replace("TWEAK_", ""))
                pole.use_deform = False
                pole.head = [bone.tail[0], bone.head[1] + bone.length + 0.2, bone.tail[2]]
                pole.tail = [bone.tail[0], bone.tail[1] + bone.length + 0.2, bone.tail[2]]
                pole.roll = 0
                pole.length = 0.25
                bpy.ops.armature.select_all(action="DESELECT")
                pole.select = True
                pole.select_head = True
                pole.select_tail = True
                bpy.ops.armature.bone_layers(layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
                bpy.ops.armature.select_all(action="DESELECT")
                # IK TARGET BONE
                lowerarmBone = canCreatePole[0]
                ikTarget = editBones.new("IKTARGET_" + lowerarmBone.name.replace("TWEAK_", ""))
                ikTarget.use_deform = False
                ikTarget.head = [lowerarmBone.tail[0], lowerarmBone.tail[1], lowerarmBone.tail[2]]
                ikTarget.tail = [lowerarmBone.tail[0], lowerarmBone.tail[1] + 0.15, lowerarmBone.tail[2]]
                ikTarget.roll = 0
                bpy.ops.armature.select_all(action="DESELECT")
                ikTarget.select = True
                ikTarget.select_head = True
                ikTarget.select_tail = True
                bpy.ops.armature.bone_layers(layers=(False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
                bpy.ops.armature.select_all(action="DESELECT")

                # FK BONE
                fkBone1 = editBones.new("FK_" + boneName.replace("TWEAK_", ""))
                fkBone1.use_deform = False
                fkBone1.head = bone.head
                fkBone1.tail = bone.tail
                fkBone1.roll = bone.roll
                fkBone1.parent = bone.parent
                fkBone2 = editBones.new("FK_" + lowerarmBone.name.replace("TWEAK_", ""))
                fkBone2.use_deform = False
                fkBone2.head = lowerarmBone.head
                fkBone2.tail = lowerarmBone.tail
                fkBone2.roll = lowerarmBone.roll
                fkBone2.parent = fkBone1
                fkBone2.use_connect = lowerarmBone.use_connect

                # Move to second layer
                fkBone1.select = True
                fkBone1.select_head = True
                fkBone1.select_tail = True
                fkBone2.select = True
                fkBone2.select_head = True
                fkBone2.select_tail = True
                bpy.ops.armature.bone_layers(layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
                bpy.ops.armature.select_all(action="DESELECT")

                # move to third layer
                bone.select = True
                bone.select_head = True
                bone.select_tail = True
                lowerarmBone.select = True
                lowerarmBone.select_head = True
                lowerarmBone.select_tail = True
                bpy.ops.armature.bone_layers(layers=(False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
                bpy.ops.armature.select_all(action="DESELECT")

                # CONTROLLER BONE
                isHandExist = [bn for bn in lowerarmBone.children if bn.name.startswith("TWEAK_") and not "_twist_" in bn.name]
                if isHandExist:
                    handBone = isHandExist[0]
                    control = editBones.new("CONTROL_" + handBone.name.replace("TWEAK_", ""))
                    control.use_deform = False
                    control.head = handBone.head
                    control.tail = handBone.tail
                    control.roll = handBone.roll
                    control.length = 0.2
                    ikTarget.parent = control
                    bpy.ops.armature.select_all(action="DESELECT")
                    control.select = True
                    control.select_head = True
                    control.select_tail = True
                    bpy.ops.armature.bone_layers(layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
                    bpy.ops.armature.select_all(action="DESELECT")
                else:
                    bpy.ops.armature.select_all(action="DESELECT")
                    control = editBones.new("CONTROL_" + lowerarmBone.name.replace("TWEAK_", ""))
                    control.use_deform = False
                    control.head = lowerarmBone.head
                    control.tail = lowerarmBone.tail
                    control.roll = lowerarmBone.roll
                    control.length = 0.2
                    control.select = True
                    control.select_head = True
                    control.select_tail = True
                    bpy.ops.transform.translate(value=(0, lowerarmBone.length, 0), orient_type="NORMAL", orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type="GLOBAL", constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff="SMOOTH", proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
                    control.select = False
                    control.select_head = False
                    control.select_tail = False
                    ikTarget.parent = control
                    bpy.ops.armature.select_all(action="DESELECT")
                    control.select = True
                    control.select_head = True
                    control.select_tail = True
                    bpy.ops.armature.bone_layers(layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
                    bpy.ops.armature.select_all(action="DESELECT")

                poseBone = self.poseBone(boneName)
                if poseBone is not None:
                    poseBone["IKTarget"] = ikTarget.name
                    poseBone["IKPole"] = pole.name
                    poseBone["BoneSide"] = pole.head[0]

        # switch case function for face bone
        def SC_FaceJawHuman(bone, faceAttach):
            """FACE JAW CONTROL"""
            # move to third layer
            bone.select = True
            bone.select_head = True
            bone.select_tail = True
            bpy.ops.armature.bone_layers(layers=(False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            bpy.ops.armature.select_all(action="DESELECT")
            # CONTROL BONE
            boneName = bone.name
            control = editBones.new(boneName.replace("TWEAK_", "") + "_CONTROL")
            control.use_deform = False
            control.head = [bone.tail[0], bone.tail[1] - 0.025, bone.tail[2]]
            control.tail = bone.tail
            control.roll = bone.roll
            control.length = 0.05
            control.parent = bone.parent
            control.select = True
            control.select_head = True
            control.select_tail = True
            # bpy.ops.transform.translate(value=(0, -0.025, 0), orient_type="NORMAL", orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type="GLOBAL", constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff="SMOOTH", proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            bpy.ops.armature.bone_layers(layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            control.select = False
            control.select_head = False
            control.select_tail = False

            poseBone = self.poseBone(boneName)
            if poseBone is not None:
                poseBone["BONE_CONTROL"] = boneName.replace("TWEAK_", "") + "_CONTROL"

        def SC_FaceControlHuman(bone, faceAttach):
            """FACE CONTROL"""
            # move to third layer
            bone.select = True
            bone.select_head = True
            bone.select_tail = True
            bpy.ops.armature.bone_layers(layers=(False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            bpy.ops.armature.select_all(action="DESELECT")
            # CONTROL BONE
            boneName = bone.name
            control = editBones.new(boneName.replace("TWEAK_", "") + "_CONTROL")
            control.use_deform = False
            control.head = bone.head
            control.tail = bone.tail
            control.roll = bone.roll
            control.length = 0.05
            control.parent = bone.parent
            control.select = True
            control.select_head = True
            control.select_tail = True
            bpy.ops.transform.translate(value=(0, -0.025, 0), orient_type="NORMAL", orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type="GLOBAL", constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff="SMOOTH", proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            bpy.ops.armature.bone_layers(layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            control.select = False
            control.select_head = False
            control.select_tail = False

            poseBone = self.poseBone(boneName)
            if poseBone is not None:
                poseBone["BONE_CONTROL"] = boneName.replace("TWEAK_", "") + "_CONTROL"

        def SC_FaceNoseHuman(bone, faceAttach):
            """FACE NOSE CONTROL"""
            # move to third layer
            bone.select = True
            bone.select_head = True
            bone.select_tail = True
            bpy.ops.armature.bone_layers(layers=(False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            bpy.ops.armature.select_all(action="DESELECT")
            # CONTROL BONE
            boneName = bone.name
            control = editBones.new(boneName.replace("TWEAK_", "") + "_CONTROL")
            control.use_deform = False
            control.head = bone.head
            control.tail = bone.tail
            control.roll = bone.roll
            control.length = 0.05
            control.parent = bone.parent
            control.select = True
            control.select_head = True
            control.select_tail = True
            bpy.ops.transform.translate(value=(0, -0.025, 0), orient_type="NORMAL", orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type="GLOBAL", constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff="SMOOTH", proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            bpy.ops.armature.bone_layers(layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            control.select = False
            control.select_head = False
            control.select_tail = False

            poseBone = self.poseBone(boneName)
            if poseBone is not None:
                poseBone["BONE_CONTROL"] = boneName.replace("TWEAK_", "") + "_CONTROL"

        def SC_FaceEyeHuman(bone, faceAttach):
            """FACE EYE CONTROL"""
            # move to third layer
            bone.select = True
            bone.select_head = True
            bone.select_tail = True
            bpy.ops.armature.bone_layers(layers=(False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            bpy.ops.armature.select_all(action="DESELECT")
            # BONE FOR LOOK CONTROL
            eyeControl = (editBones.get(faceAttach["BONE_LOOK_CONTROL"]), True) if faceAttach.get("BONE_LOOK_CONTROL") else (editBones.new("LOOK_CONTROL"), False)
            if eyeControl[1]:
                eyeControl = eyeControl[0]
            else:
                eyeControl = eyeControl[0]
                eyeControl.use_deform = False
                eyeControl.head = faceAttach.head
                eyeControl.tail = faceAttach.tail
                eyeControl.roll = faceAttach.roll
                eyeControl.length = 0.05
                eyeControl["UE4RIGTYPE"] = "FACE_LOOK_CONTROL_HUMAN"
                eyeControl.select = True
                eyeControl.select_head = True
                eyeControl.select_tail = True
                bpy.ops.transform.translate(value=(0, -0.5, 0), orient_type="NORMAL", orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type="GLOBAL", constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff="SMOOTH", proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
                bpy.ops.armature.bone_layers(layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
                eyeControl.select = False
                eyeControl.select_head = False
                eyeControl.select_tail = False

                faceAttach["BONE_LOOK_CONTROL"] = eyeControl.name
                poseBone = self.poseBone(faceAttach.name)
                if poseBone is not None:
                    poseBone["BONE_LOOK_CONTROL"] = eyeControl.name

            # CONTROL BONE
            boneName = bone.name
            control = editBones.new(boneName.replace("TWEAK_", "") + "_CONTROL")
            control.use_deform = False
            control.head = bone.head
            control.tail = bone.tail
            control.roll = bone.roll
            control.length = 0.05
            control.parent = eyeControl
            control.select = True
            control.select_head = True
            control.select_tail = True
            bpy.ops.transform.translate(value=(0, 0.25, 0), orient_type="NORMAL", orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type="GLOBAL", constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff="SMOOTH", proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            bpy.ops.armature.bone_layers(layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            control.select = False
            control.select_head = False
            control.select_tail = False

            poseBone = self.poseBone(boneName)
            if poseBone is not None:
                poseBone["BONE_CONTROL"] = boneName.replace("TWEAK_", "") + "_CONTROL"

        def SC_FaceTeethHuman(bone, faceAttach):
            """FACE TEETH CONTROL"""
            # move to third layer
            bone.select = True
            bone.select_head = True
            bone.select_tail = True
            bpy.ops.armature.bone_layers(layers=(False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            bpy.ops.armature.select_all(action="DESELECT")
            # CONTROL BONE
            boneName = bone.name
            control = editBones.new(boneName.replace("TWEAK_", "") + "_CONTROL")
            control.use_deform = False
            control.head = bone.head
            control.tail = bone.tail
            control.roll = bone.roll
            control.length = 0.05
            control.parent = bone.parent
            control.select = True
            control.select_head = True
            control.select_tail = True
            bpy.ops.armature.bone_layers(layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            control.select = False
            control.select_head = False
            control.select_tail = False

            poseBone = self.poseBone(boneName)
            if poseBone is not None:
                poseBone["BONE_CONTROL"] = boneName.replace("TWEAK_", "") + "_CONTROL"

        def SC_FaceTongueHuman(bone, faceAttach):
            """FACE TONGUE CONTROL"""
            # move to third layer
            bone.select = True
            bone.select_head = True
            bone.select_tail = True
            bpy.ops.armature.bone_layers(layers=(False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            bpy.ops.armature.select_all(action="DESELECT")
            # CONTROL BONE
            boneName = bone.name
            control = editBones.new(boneName.replace("TWEAK_", "") + "_CONTROL")
            control.use_deform = False
            control.head = bone.head
            control.tail = bone.tail
            control.roll = bone.roll
            control.length = 0.05
            control.parent = bone.parent
            control.select = True
            control.select_head = True
            control.select_tail = True
            bpy.ops.transform.translate(value=(0, 0, 0.01), orient_type="NORMAL", orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type="GLOBAL", constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff="SMOOTH", proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            bpy.ops.armature.bone_layers(layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            control.select = False
            control.select_head = False
            control.select_tail = False

            poseBone = self.poseBone(boneName)
            if poseBone is not None:
                poseBone["BONE_CONTROL"] = boneName.replace("TWEAK_", "") + "_CONTROL"

        def SC_FaceEyelidHuman(bone, faceAttach):
            """FACE EYELID CONTROL"""
            # move to third layer
            bone.select = True
            bone.select_head = True
            bone.select_tail = True
            bpy.ops.armature.bone_layers(layers=(False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            bpy.ops.armature.select_all(action="DESELECT")
            # CONTROL BONE
            boneName = bone.name
            control = editBones.new(boneName.replace("TWEAK_", "") + "_CONTROL")
            control.use_deform = False
            control.head = bone.head
            control.tail = bone.tail
            control.roll = bone.roll
            control.length = 0.05
            control.parent = faceAttach
            control.select = True
            control.select_head = True
            control.select_tail = True
            bpy.ops.transform.translate(value=(0, 0.025, 0), orient_type="NORMAL", orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type="GLOBAL", constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff="SMOOTH", proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            bpy.ops.armature.bone_layers(layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            control.select = False
            control.select_head = False
            control.select_tail = False

            poseBone = self.poseBone(boneName)
            if poseBone is not None:
                poseBone["BONE_CONTROL"] = boneName.replace("TWEAK_", "") + "_CONTROL"

        # FACE_HUMAN
        for bone in [bone for bone in editBones if bone.get("UE4RIGTYPE") == "FACE_HUMAN"]:
            # move to third layer
            bone.select = True
            bone.select_head = True
            bone.select_tail = True
            bpy.ops.armature.bone_layers(layers=(False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            bpy.ops.armature.select_all(action="DESELECT")
            # filter bone
            arrFaceBones = [bone for bone in bone.children_recursive if bone.get("UE4RIGTYPE") in ["FACE_JAW_HUMAN", "FACE_CONTROL_HUMAN", "FACE_NOSE_HUMAN", "FACE_EYE_HUMAN", "FACE_TEETH_HUMAN", "FACE_TONGUE_HUMAN", "FACE_EYELID_UPPER_HUMAN", "FACE_EYELID_LOWER_HUMAN"]]
            # switch case with dict
            switchCaseRigType = {
                "FACE_JAW_HUMAN": SC_FaceJawHuman,
                "FACE_CONTROL_HUMAN": SC_FaceControlHuman,
                "FACE_NOSE_HUMAN": SC_FaceNoseHuman,
                "FACE_EYE_HUMAN": SC_FaceEyeHuman,
                "FACE_TEETH_HUMAN": SC_FaceTeethHuman,
                "FACE_TONGUE_HUMAN": SC_FaceTongueHuman,
                "FACE_EYELID_UPPER_HUMAN": SC_FaceEyelidHuman,
                "FACE_EYELID_LOWER_HUMAN": SC_FaceEyelidHuman
            }
            for faceBone in arrFaceBones:
                doSwitch = switchCaseRigType.get(faceBone.get("UE4RIGTYPE"), None)
                if doSwitch is not None:
                    doSwitch(faceBone, bone)

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
            constraints.target_space = "LOCAL_WITH_PARENT"
            constraints.owner_space = "LOCAL_WITH_PARENT"

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

        # Generate Control Finger Shape
        verticesFingerShape = [(-0.19999998807907104, 0.0, 0.0), (0.19999998807907104, 0.0, 0.0), (-0.19999998807907104, 1.0, 0.0), (0.19999998807907104, 1.0, 0.0)]
        edgesFingerShape = [(2, 0), (0, 1), (1, 3), (3, 2)]
        objControlFingerShape = None

        # Generate Finger Shape
        fingerTweakVertices = [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.5, 0.20000000298023224), (-0.07653669267892838, 0.5, 0.18477590382099152), (-0.1414213627576828, 0.5, 0.1414213627576828), (-0.18477590382099152, 0.5, 0.07653668522834778), (-0.20000000298023224, 0.5, -8.742278012618954e-09), (-0.18477590382099152, 0.5, -0.07653670758008957), (-0.1414213627576828, 0.5, -0.1414213627576828), (-0.07653670012950897, 0.5, -0.18477590382099152), (-3.019916050561733e-08, 0.5, -0.20000000298023224), (0.0765366479754448, 0.5, -0.1847759336233139), (0.14142131805419922, 0.5, -0.14142140746116638), (0.18477590382099152, 0.5, -0.07653671503067017), (0.20000000298023224, 0.5, 2.384976216518453e-09), (0.18477588891983032, 0.5, 0.07653672248125076), (0.14142130315303802, 0.5, 0.14142140746116638), (0.07653659582138062, 0.5, 0.1847759485244751)]
        fingerTweakEdges = [(0, 1), (3, 2), (4, 3), (5, 4), (6, 5), (7, 6), (8, 7), (9, 8), (10, 9), (11, 10), (12, 11), (13, 12), (14, 13), (15, 14), (16, 15), (17, 16), (2, 17)]
        objFingerShape = None

        # FINGER
        for bone in [bone for bone in poseBones if bone.get("UE4RIGTYPE") == "FINGER"]:
            constraints = bone.constraints.new(type="COPY_ROTATION")
            constraints.name = "fingerROTATION"
            constraints.show_expanded = False
            constraints.target = self.activeObject
            constraints.subtarget = bone.get("subtargetRotation")
            constraints.mix_mode = "ADD"
            constraints.target_space = "LOCAL"
            constraints.owner_space = "LOCAL"
            # Generate Custom Shape
            if objFingerShape is None:
                mesh = bpy.data.meshes.new("UE4WSBoneShape_Finger_Tweak")
                objFingerShape = bpy.data.objects.new(mesh.name,mesh)
                collection.objects.link(objFingerShape)
                mesh.from_pydata([v if i < 2 else ((v[0] * 0.11) / bone.length, v[1], (v[2] * 0.11) / bone.length) for i, v in enumerate(fingerTweakVertices)], fingerTweakEdges, [])
            bone.custom_shape = objFingerShape
            bone.bone_group = yellowGroup
            # lock location controller
            poseBones.get(constraints.subtarget).lock_location = [True, True, True]
            # assign custom bone shape
            targetBone = poseBones.get(bone.get("subtargetRotation"))
            if targetBone is not None:
                if objControlFingerShape is None:
                    mesh = bpy.data.meshes.new("UE4WSBoneShape_Control_Finger")
                    objControlFingerShape = bpy.data.objects.new(mesh.name,mesh)
                    collection.objects.link(objControlFingerShape)
                    mesh.from_pydata(verticesFingerShape, edgesFingerShape, [])
                targetBone.custom_shape = objControlFingerShape
                targetBone.bone_group = redGroup
            # filter children with starts string "TWEAK_"
            filterChildren = [bone for bone in bone.children_recursive if bone.name.startswith("TWEAK_")]
            # get index bone that have RIGTYPE
            endIndex = next((index for (index, bn) in enumerate(filterChildren) if bn.get("UE4RIGTYPE", False)), None)
            if endIndex is not None:
                filterChildren = filterChildren[:endIndex:]
            for bn in filterChildren[::-1]:
                constraints = bn.constraints.new(type="COPY_ROTATION")
                constraints.name = "fingerROTATION"
                constraints.show_expanded = False
                constraints.target = self.activeObject
                constraints.subtarget = bn.parent.name
                constraints.mix_mode = "ADD"
                constraints.target_space = "LOCAL"
                constraints.owner_space = "LOCAL"
                constraints.use_y = False
                constraints.use_z = False
                if objFingerShape is not None:
                    bn.custom_shape = objFingerShape
                    bn.bone_group = yellowGroup

        # Generate Pole Shape
        verticesPoleShape = [(-0.19999998807907104, 0.1383724808692932, 0.0), (0.19999998807907104, 0.1383724808692932, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.0), (1.4901161193847656e-08, 0.1383724957704544, 0.19999998807907104), (-1.4901161193847656e-08, 0.1383724957704544, -0.19999998807907104), (0.0, 1.0, 0.0), (0.0, 2.9802322387695312e-08, 0.0)]
        edgesPoleShape = [(2, 0), (3, 1), (1, 2), (0, 3), (6, 4), (7, 5), (5, 6), (4, 7)]
        objPole = None

        # Generate FK Shape
        FKvertices = [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.5, 0.20000000298023224), (-0.07653669267892838, 0.5, 0.18477590382099152), (-0.1414213627576828, 0.5, 0.1414213627576828), (-0.18477590382099152, 0.5, 0.07653668522834778), (-0.20000000298023224, 0.5, -8.742278012618954e-09), (-0.18477590382099152, 0.5, -0.07653670758008957), (-0.1414213627576828, 0.5, -0.1414213627576828), (-0.07653670012950897, 0.5, -0.18477590382099152), (-3.019916050561733e-08, 0.5, -0.20000000298023224), (0.0765366479754448, 0.5, -0.1847759336233139), (0.14142131805419922, 0.5, -0.14142140746116638), (0.18477590382099152, 0.5, -0.07653671503067017), (0.20000000298023224, 0.5, 2.384976216518453e-09), (0.18477588891983032, 0.5, 0.07653672248125076), (0.14142130315303802, 0.5, 0.14142140746116638), (0.07653659582138062, 0.5, 0.1847759485244751)]
        FKedges = [(0, 1), (3, 2), (4, 3), (5, 4), (6, 5), (7, 6), (8, 7), (9, 8), (10, 9), (11, 10), (12, 11), (13, 12), (14, 13), (15, 14), (16, 15), (17, 16), (2, 17)]

        # Generate Foot Shape
        verticesFootShape = [(-0.39742353558540344, 0.38750335574150085, 0.0), (-0.2849268913269043, 0.5, 0.0), (-0.382351815700531, 0.4437516927719116, 0.0), (-0.3411751985549927, 0.48492833971977234, 0.0), (0.39742353558540344, 0.38750335574150085, 0.0), (0.2849268913269043, 0.5, 0.0), (0.382351815700531, 0.4437516927719116, 0.0), (0.3411751985549927, 0.48492833971977234, 0.0), (-0.39742353558540344, -0.7603926062583923, 0.0), (-0.33357056975364685, -0.8242455720901489, 0.0), (-0.38886886835098267, -0.7923190593719482, 0.0), (-0.36549705266952515, -0.815690815448761, 0.0), (0.33357056975364685, -0.8242455720901489, 0.0), (0.39742353558540344, -0.7603926062583923, 0.0), (0.36549705266952515, -0.815690815448761, 0.0), (0.38886886835098267, -0.7923190593719482, 0.0), (-0.2625647187232971, -0.8242455720901489, 0.0), (-0.15565043687820435, -0.7770977020263672, 0.0), (-0.22486911714076996, -0.8179289698600769, 0.0), (-0.1857357770204544, -0.8006716370582581, 0.0), (-0.04306132346391678, -0.6538237929344177, 0.0), (0.04306134954094887, -0.6538237929344177, 0.0), (-0.01576152816414833, -0.6365664601325989, 0.0), (0.01576155610382557, -0.6365664601325989, 0.0), (0.2625647187232971, -0.8242455720901489, 0.0), (0.15565043687820435, -0.7770977020263672, 0.0), (0.22486911714076996, -0.8179289698600769, 0.0), (0.1857357770204544, -0.8006716370582581, 0.0)]
        edgesFootShape = [(0, 2), (2, 3), (3, 1), (4, 6), (6, 7), (7, 5), (1, 5), (8, 10), (10, 11), (11, 9), (12, 14), (14, 15), (15, 13), (16, 18), (18, 19), (19, 17), (20, 22), (22, 23), (23, 21), (24, 26), (26, 27), (27, 25), (8, 0), (9, 16), (12, 24), (13, 4), (17, 20), (21, 25)]
        objFootShape = None

        # Generate Tweak Foot Shape
        verticesTweakFootShape = [(-0.3, 0.0, 0.0), (0.3, 0.0, 0.0), (-0.3, 1.0, 0.0), (0.3, 1.0, 0.0)]
        edgesTweakFootShape = [(2, 0), (0, 1), (1, 3), (3, 2)]

        # Generate Control Rotation Shape
        verticesControlRotationShape = [(0.0, 0.0, -0.5), (0.0, 0.0, 0.5), (-0.1249999925494194, 0.0, 0.1666666567325592), (-0.1249999925494194, 0.0, -0.1666666567325592), (0.1249999925494194, 0.0, -0.1666666567325592), (0.1249999925494194, 0.0, 0.1666666567325592), (-0.3749999701976776, 0.0, 0.1666666567325592), (0.3749999701976776, 0.0, 0.1666666567325592), (-0.3749999701976776, 0.0, -0.1666666567325592), (0.3749999701976776, 0.0, -0.1666666567325592)]
        edgesControlRotationShape = [(0, 8), (6, 1), (2, 3), (9, 0), (4, 5), (2, 6), (5, 7), (3, 8), (4, 9), (1, 7)]
        objControlRotationShape = None

        # Generate Control Lift Shape
        verticesControlLiftShape = [(0.0, 0.0, 0.4966666102409363), (-0.1249999925494194, 0.0, 0.16333331167697906), (-0.1249999925494194, 0.0, -0.003333345055580139), (0.1249999925494194, 0.0, -0.003333345055580139), (0.1249999925494194, 0.0, 0.16333331167697906), (-0.3749999701976776, 0.0, 0.16333331167697906), (0.3749999701976776, 0.0, 0.16333331167697906)]
        edgesControlLiftShape = [(5, 0), (1, 2), (3, 4), (1, 5), (4, 6), (2, 3), (0, 6)]
        objControlLiftShape = None

        # # Generate Toe Shape
        verticesToeShape = [(-1.0, 0.35884571075439453, 0.0), (-0.8312775492668152, 0.220088928937912, 0.0), (-0.9505823850631714, 0.24697744846343994, 0.0), (1.0, 0.35884571075439453, 0.0), (0.8312775492668152, 0.220088928937912, 0.0), (0.9505823850631714, 0.24697744846343994, 0.0), (-1.0, 1.328041911125183, 0.0), (-0.8280418515205383, 1.5, 0.0), (-0.9496345520019531, 1.4496347904205322, 0.0), (1.0, 1.328041911125183, 0.0), (0.8280418515205383, 1.5, 0.0), (0.9496345520019531, 1.4496347904205322, 0.0), (-0.6687224507331848, 0.252076655626297, 0.0), (-0.3849330246448517, 0.15749229490756989, 0.0), (-0.5157153606414795, 0.2381259948015213, 0.0), (-0.11506698280572891, -0.14220289885997772, 0.0), (0.11506698280572891, -0.14220289885997772, 0.0), (0.0, -0.19513346254825592, 0.0), (0.6687224507331848, 0.252076655626297, 0.0), (0.3849330246448517, 0.15749229490756989, 0.0), (0.5157153606414795, 0.2381259948015213, 0.0)]
        edgesToeShape = [(0, 2), (2, 1), (3, 5), (5, 4), (6, 8), (8, 7), (9, 11), (11, 10), (12, 14), (14, 13), (15, 17), (17, 16), (18, 20), (20, 19), (0, 6), (1, 12), (3, 9), (4, 18), (7, 10), (13, 15), (16, 19)]
        objToeShape = None

        # Generate Tweak Foot Shape
        verticesTweakToeShape = [(-0.7, 0.0, 0.0), (0.7, 0.0, 0.0), (-0.7, 1.0, 0.0), (0.7, 1.0, 0.0)]
        edgesTweakToeShape = [(2, 0), (0, 1), (1, 3), (3, 2)]

        # LEG_HUMAN
        for bone in [bone for bone in poseBones if bone.get("UE4RIGTYPE") == "LEG_HUMAN"]:
            boneChildren = [bn for bn in bone.children_recursive if bn.name.startswith("TWEAK_") and not "_twist_" in bn.name and not bn.get("UE4RIGTYPE")]
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

                if calf is not None:
                    constraints = calf.constraints.new(type="IK")
                    constraints.name = "IK"
                    constraints.show_expanded = False
                    constraints.chain_count = 2
                    constraints.target = self.activeObject
                    constraints.subtarget = bone.get("IKTarget")
                    constraints.pole_target = self.activeObject
                    constraints.pole_subtarget = bone.get("IKPole")
                    constraints.pole_angle = (0, -3.14159)[bone.get("BoneSide") < 0]
                    ikBone = poseBones.get(bone.get("IKTarget"))
                    poleBone = poseBones.get(bone.get("IKPole"))
                    IKInfluenceDrive = constraints.driver_add("influence").driver
                    if poleBone is not None:
                        if objPole is None:
                            mesh = bpy.data.meshes.new("UE4WSBoneShape_Pole")
                            objPole = bpy.data.objects.new(mesh.name,mesh)
                            collection.objects.link(objPole)
                            mesh.from_pydata(verticesPoleShape, edgesPoleShape, [])
                        poleBone.custom_shape = objPole
                        poleBone.bone_group = redGroup
                    if ikBone is not None:
                        ikBone.lock_scale = [True, True, True]
                        ikBone.lock_rotation = [True, True, True]
                        ikBone.lock_location = [True, True, True]
                        if foot is not None:
                            constraints = ikBone.constraints.new(type="TRANSFORM")
                            constraints.name = "ROTATION_CONTROL"
                            constraints.show_expanded = False
                            constraints.target = self.activeObject
                            constraints.subtarget = "CONTROLROTATION_" + foot.name.replace("TWEAK_", "")
                            constraints.from_min_z = -10
                            constraints.from_max_z = 10
                            constraints.map_to_x_from = "Z"
                            constraints.map_to_z_from = "X"
                            constraints.map_to = "ROTATION"
                            constraints.mix_mode_rot = "ADD"
                            constraints.to_min_x_rot = 1.5708
                            constraints.to_max_x_rot = -1.5708
                            constraints.target_space = "LOCAL"
                            constraints.owner_space = "LOCAL"
                    # FK
                    fk = bone.constraints.new(type="COPY_TRANSFORMS")
                    fk.name = "TRANSFORM"
                    fk.show_expanded = False
                    fk.target = self.activeObject
                    fk.subtarget = "FK_" + bone.name.replace("TWEAK_", "")
                    fk.mix_mode = "REPLACE"
                    fk.target_space = "LOCAL"
                    fk.owner_space = "LOCAL"
                    fk.influence = 0.0
                    FK1InfluenceDrive = fk.driver_add("influence").driver

                    # Generate Custom Shape
                    mesh = bpy.data.meshes.new("UE4WSBoneShape_FK_" + bone.name.replace("TWEAK_", ""))
                    objFKShape = bpy.data.objects.new(mesh.name,mesh)
                    collection.objects.link(objFKShape)
                    mesh.from_pydata([v if i < 2 else ((v[0] * 0.5) / bone.length, v[1], (v[2] * 0.5) / bone.length) for i, v in enumerate(FKvertices)], FKedges, [])

                    FKBone = poseBones.get("FK_" + bone.name.replace("TWEAK_", ""))
                    FKBone.custom_shape = objFKShape
                    FKBone.bone_group = greenGroup

                    fk = calf.constraints.new(type="COPY_TRANSFORMS")
                    fk.name = "TRANSFORM"
                    fk.show_expanded = False
                    fk.target = self.activeObject
                    fk.subtarget = "FK_" + calf.name.replace("TWEAK_", "")
                    fk.mix_mode = "REPLACE"
                    fk.target_space = "LOCAL"
                    fk.owner_space = "LOCAL"
                    fk.influence = 0.0
                    FK2InfluenceDrive = fk.driver_add("influence").driver

                    # Generate Custom Shape
                    mesh = bpy.data.meshes.new("UE4WSBoneShape_FK_" + calf.name.replace("TWEAK_", ""))
                    objFKShape = bpy.data.objects.new(mesh.name,mesh)
                    collection.objects.link(objFKShape)
                    mesh.from_pydata([v if i < 2 else ((v[0] * 0.5) / calf.length, v[1], (v[2] * 0.5) / calf.length) for i, v in enumerate(FKvertices)], FKedges, [])

                    FKBone = poseBones.get("FK_" + calf.name.replace("TWEAK_", ""))
                    FKBone.custom_shape = objFKShape
                    FKBone.bone_group = greenGroup

                    # CONTROL RIG
                    if not self.activeObject.get("_RNA_UI"): # set RNA UI
                        self.activeObject["_RNA_UI"] = {}

                    # IK and FK influence
                    customPropertyName = foot.name.replace("TWEAK", "CR_IK") if foot is not None else calf.name.replace("TWEAK", "CR_IK")
                    self.activeObject[customPropertyName] = 1.0
                    self.activeObject["_RNA_UI"][customPropertyName] = {
                        "description": "Influence For Use IK",
                        "default": 1.0,
                        "min": 0.0,
                        "max": 1.0,
                        "soft_min": 0.0,
                        "soft_max": 1.0,
                    }

                    # IK Driver
                    IKInfluenceDrive.type = "SCRIPTED"
                    var = IKInfluenceDrive.variables.new()
                    var.type = "SINGLE_PROP"
                    target = var.targets[0]
                    target.id = self.activeObject
                    target.data_path = "[\""+ customPropertyName + "\"]"
                    IKInfluenceDrive.expression = var.name

                    # FK Driver
                    FK1InfluenceDrive.type = "SCRIPTED"
                    var = FK1InfluenceDrive.variables.new()
                    var.type = "SINGLE_PROP"
                    target = var.targets[0]
                    target.id = self.activeObject
                    target.data_path = "[\""+ customPropertyName + "\"]"
                    FK1InfluenceDrive.expression = "abs("+ var.name + " - 1.0)"

                    FK2InfluenceDrive.type = "SCRIPTED"
                    var = FK2InfluenceDrive.variables.new()
                    var.type = "SINGLE_PROP"
                    target = var.targets[0]
                    target.id = self.activeObject
                    target.data_path = "[\""+ customPropertyName + "\"]"
                    FK2InfluenceDrive.expression = "abs("+ var.name + " - 1.0)"

                if foot is not None:
                    constraints = foot.constraints.new(type="COPY_ROTATION")
                    constraints.name = "FOOT_CONTROL_ROTATION"
                    constraints.show_expanded = False
                    constraints.target = self.activeObject
                    constraints.subtarget = "CONTROL_" + foot.name.replace("TWEAK_", "")
                    constraints.mix_mode = "ADD"
                    constraints.target_space = "POSE"
                    constraints.owner_space = "POSE"
                    constraints.use_x = True
                    constraints.use_y = True
                    constraints.use_z = True
                    constraints.invert_x = True
                    constraints.invert_y = True

                    mesh = bpy.data.meshes.new("UE4WSBoneShape_" + foot.name)
                    objTweakFootShape = bpy.data.objects.new(mesh.name,mesh)
                    collection.objects.link(objTweakFootShape)
                    mesh.from_pydata(verticesTweakFootShape, edgesTweakFootShape, [])
                    foot.custom_shape = objTweakFootShape
                    foot.bone_group = yellowGroup

                    targetBone = poseBones.get("CONTROL_" + foot.name.replace("TWEAK_", ""))
                    if targetBone is not None:
                        if objFootShape is None:
                            mesh = bpy.data.meshes.new("UE4WSBoneShape_Foot")
                            objFootShape = bpy.data.objects.new(mesh.name,mesh)
                            collection.objects.link(objFootShape)
                            mesh.from_pydata(verticesFootShape, edgesFootShape, [])
                        targetBone.custom_shape = objFootShape
                        targetBone.bone_group = redGroup

                    constraints = foot.constraints.new(type="COPY_ROTATION")
                    constraints.name = "FOOT_X_ROTATION"
                    constraints.show_expanded = False
                    constraints.target = self.activeObject
                    constraints.subtarget = bone.get("IKTarget")
                    constraints.mix_mode = "ADD"
                    constraints.target_space = "LOCAL"
                    constraints.owner_space = "LOCAL"
                    constraints.use_x = True
                    constraints.use_y = False
                    constraints.use_z = False
                    constraints.invert_x = True

                    constraints = foot.constraints.new(type="COPY_ROTATION")
                    constraints.name = "FOOT_MIMIK_ROTATION"
                    constraints.show_expanded = False
                    constraints.target = self.activeObject
                    constraints.subtarget = "MIMIK_" + foot.name.replace("TWEAK_", "")
                    constraints.mix_mode = "ADD"
                    constraints.target_space = "LOCAL"
                    constraints.owner_space = "LOCAL"
                    constraints.use_x = True
                    constraints.use_y = False
                    constraints.use_z = True
                    constraints.invert_x = True

                    controlRotation = poseBones.get("CONTROLROTATION_" + foot.name.replace("TWEAK_", ""))
                    if controlRotation is not None:
                        controlRotation.lock_scale = [True, True, True]
                        controlRotation.lock_rotation = [True, True, True]
                        controlRotation.lock_location = [True, True, False]
                        constraints = controlRotation.constraints.new(type="LIMIT_LOCATION")
                        constraints.show_expanded = False
                        constraints.owner_space = "LOCAL"
                        constraints.use_min_x = True
                        constraints.use_max_x = True
                        constraints.use_min_y = True
                        constraints.use_max_y = True
                        constraints.use_min_z = True
                        constraints.use_max_z = True
                        constraints.min_z = -10
                        constraints.max_z = 10
                        if objControlRotationShape is None:
                            mesh = bpy.data.meshes.new("UE4WSBoneShape_ControlRotation")
                            objControlRotationShape = bpy.data.objects.new(mesh.name,mesh)
                            collection.objects.link(objControlRotationShape)
                            mesh.from_pydata(verticesControlRotationShape, edgesControlRotationShape, [])
                        controlRotation.custom_shape = objControlRotationShape
                        controlRotation.bone_group = blueGroup
                    mimikFoot = poseBones.get("MIMIK_" + foot.name.replace("TWEAK_", ""))
                    if mimikFoot is not None:
                        mimikFoot.lock_scale = [True, True, True]
                        mimikFoot.lock_rotation = [True, True, True]
                        mimikFoot.lock_location = [True, True, True]
                        constraints = mimikFoot.constraints.new(type="LIMIT_ROTATION")
                        constraints.show_expanded = False
                        constraints.owner_space = "LOCAL"
                        constraints.use_limit_x = True
                        constraints.min_x = 0
                        constraints.max_x = 0.785398

                        constraints = mimikFoot.constraints.new(type="TRANSFORM")
                        constraints.name = "LIFT_CONTROL"
                        constraints.show_expanded = False
                        constraints.target = self.activeObject
                        constraints.subtarget = "CONTROLLIFT_" + foot.name.replace("TWEAK_", "")
                        constraints.from_min_z = -10
                        constraints.from_max_z = 10
                        constraints.map_to_x_from = "Z"
                        constraints.map_to_z_from = "X"
                        constraints.map_to = "ROTATION"
                        constraints.mix_mode_rot = "ADD"
                        constraints.to_min_x_rot = -0.785398
                        constraints.to_max_x_rot = 0.785398
                        constraints.target_space = "LOCAL"
                        constraints.owner_space = "LOCAL"
                    controlLift = poseBones.get("CONTROLLIFT_" + foot.name.replace("TWEAK_", ""))
                    if controlLift is not None:
                        controlLift.lock_scale = [True, True, True]
                        controlLift.lock_rotation = [True, True, True]
                        controlLift.lock_location = [True, True, False]
                        constraints = controlLift.constraints.new(type="LIMIT_LOCATION")
                        constraints.show_expanded = False
                        constraints.owner_space = "LOCAL"
                        constraints.use_min_x = True
                        constraints.use_max_x = True
                        constraints.use_min_y = True
                        constraints.use_max_y = True
                        constraints.use_min_z = True
                        constraints.use_max_z = True
                        constraints.min_z = 0
                        constraints.max_z = 10
                        if objControlLiftShape is None:
                            mesh = bpy.data.meshes.new("UE4WSBoneShape_ControlLift")
                            objControlLiftShape = bpy.data.objects.new(mesh.name,mesh)
                            collection.objects.link(objControlLiftShape)
                            mesh.from_pydata(verticesControlLiftShape, edgesControlLiftShape, [])
                        controlLift.custom_shape = objControlLiftShape
                        controlLift.bone_group = blueGroup

                if toe is not None:
                    constraints = toe.constraints.new(type="COPY_ROTATION")
                    constraints.name = "CONTROL_ROTATION"
                    constraints.show_expanded = False
                    constraints.target = self.activeObject
                    constraints.subtarget = "CONTROL_" + toe.name.replace("TWEAK_", "")
                    constraints.mix_mode = "ADD"
                    constraints.target_space = "LOCAL"
                    constraints.owner_space = "LOCAL"
                    constraints.use_x = True
                    constraints.use_y = True
                    constraints.use_z = True
                    constraints.invert_x = True
                    constraints.invert_y = False
                    constraints.invert_z = True

                    mesh = bpy.data.meshes.new("UE4WSBoneShape_" + toe.name)
                    objTweakToeShape = bpy.data.objects.new(mesh.name,mesh)
                    collection.objects.link(objTweakToeShape)
                    mesh.from_pydata(verticesTweakToeShape, edgesTweakToeShape, [])
                    toe.custom_shape = objTweakToeShape
                    toe.bone_group = yellowGroup

                    toeControl = poseBones.get("CONTROL_" + toe.name.replace("TWEAK_", ""))
                    if toeControl is not None:
                        toeControl.lock_scale = [True, True, True]
                        toeControl.lock_rotation = [False, False, False]
                        toeControl.lock_location = [True, True, True]
                        constraints = toeControl.constraints.new(type="COPY_ROTATION")
                        constraints.name = "COPY_ROTATION_FROM_MIMIK_FOOT"
                        constraints.show_expanded = False
                        constraints.target = self.activeObject
                        constraints.subtarget = "MIMIK_" + foot.name.replace("TWEAK_", "")
                        constraints.mix_mode = "ADD"
                        constraints.target_space = "LOCAL"
                        constraints.owner_space = "LOCAL"
                        constraints.use_x = True
                        constraints.use_y = True
                        constraints.use_z = True
                        constraints.invert_x = False
                        constraints.invert_y = False
                        constraints.invert_z = False
                        if objToeShape is None:
                            mesh = bpy.data.meshes.new("UE4WSBoneShape_Toe")
                            objToeShape = bpy.data.objects.new(mesh.name,mesh)
                            collection.objects.link(objToeShape)
                            mesh.from_pydata(verticesToeShape, edgesToeShape, [])
                        toeControl.custom_shape = objToeShape
                        toeControl.bone_group = redGroup

        # Generate Hand Shape
        verticeshandShape = [(0.1347789168357849, 0.8774998188018799, 0.25), (0.04295855015516281, 0.958526611328125, 0.25), (0.10367729514837265, 0.9347944259643555, 0.25), (-0.1347789168357849, 0.8774998188018799, 0.25), (-0.04295855015516281, 0.958526611328125, 0.25), (-0.10367729514837265, 0.9347944259643555, 0.25), (0.23906441032886505, 0.045745983719825745, 0.25), (0.18389254808425903, 0.01646287366747856, 0.25), (0.22743460536003113, 0.0010417178273200989, 0.25), (-0.18389254808425903, 0.01646287366747856, 0.25), (-0.23906441032886505, 0.045745983719825745, 0.25), (-0.22743460536003113, 0.0010417178273200989, 0.25), (-0.06610745936632156, 0.11968913674354553, 0.25), (0.06610745936632156, 0.11968913674354553, 0.25), (0.0, 0.14368712902069092, 0.25)]
        edgeshandShape = [(0, 2), (2, 1), (3, 5), (5, 4), (1, 4), (6, 8), (8, 7), (9, 11), (11, 10), (12, 14), (14, 13), (6, 0), (7, 13), (9, 12), (10, 3)]
        objHandShape = None
        handTweakVertices = [(0.0, 0.5, 0.20000000298023224), (-0.07653669267892838, 0.5, 0.18477590382099152), (-0.1414213627576828, 0.5, 0.1414213627576828), (-0.18477590382099152, 0.5, 0.07653668522834778), (-0.20000000298023224, 0.5, -8.742278012618954e-09), (-0.18477590382099152, 0.5, -0.07653670758008957), (-0.1414213627576828, 0.5, -0.1414213627576828), (-0.07653670012950897, 0.5, -0.18477590382099152), (-3.019916050561733e-08, 0.5, -0.20000000298023224), (0.0765366479754448, 0.5, -0.1847759336233139), (0.14142131805419922, 0.5, -0.14142140746116638), (0.18477590382099152, 0.5, -0.07653671503067017), (0.20000000298023224, 0.5, 2.384976216518453e-09), (0.18477588891983032, 0.5, 0.07653672248125076), (0.14142130315303802, 0.5, 0.14142140746116638), (0.07653659582138062, 0.5, 0.1847759485244751)]
        handTweakEdges = [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4), (6, 5), (7, 6), (8, 7), (9, 8), (10, 9), (11, 10), (12, 11), (13, 12), (14, 13), (15, 14), (0, 15)]
        objHandTweakShape = None

        # ARM_HUMAN
        for bone in [bone for bone in poseBones if bone.get("UE4RIGTYPE") == "ARM_HUMAN"]:
            boneChildren = [bn for bn in bone.children_recursive if bn.name.startswith("TWEAK_") and not "_twist_" in bn.name and not bn.get("UE4RIGTYPE")]
            if boneChildren:
                lowerarm = None
                hand = None
                if len(boneChildren) != 0:
                    lowerarm = boneChildren.pop(0)
                if len(boneChildren) != 0:
                    hand = boneChildren.pop(0)
                if lowerarm is not None:
                    constraints = lowerarm.constraints.new(type="IK")
                    constraints.name = "IK"
                    constraints.show_expanded = False
                    constraints.chain_count = 2
                    constraints.target = self.activeObject
                    constraints.subtarget = bone.get("IKTarget")
                    constraints.pole_target = self.activeObject
                    constraints.pole_subtarget = bone.get("IKPole")
                    constraints.pole_angle = (0, -3.14159)[bone.get("BoneSide") < 0]
                    ikBone = poseBones.get(bone.get("IKTarget"))
                    if ikBone is not None:
                        ikBone.lock_scale = [True, True, True]
                        ikBone.lock_rotation = [True, True, True]
                        ikBone.lock_location = [True, True, True]
                    poleBone = poseBones.get(bone.get("IKPole"))
                    IKInfluenceDrive = constraints.driver_add("influence").driver
                    if poleBone is not None:
                        if objPole is None:
                            mesh = bpy.data.meshes.new("UE4WSBoneShape_Pole")
                            objPole = bpy.data.objects.new(mesh.name,mesh)
                            collection.objects.link(objPole)
                            mesh.from_pydata(verticesPoleShape, edgesPoleShape, [])
                        poleBone.custom_shape = objPole
                        poleBone.bone_group = redGroup

                    # FK
                    fk = bone.constraints.new(type="COPY_TRANSFORMS")
                    fk.name = "TRANSFORM"
                    fk.show_expanded = False
                    fk.target = self.activeObject
                    fk.subtarget = "FK_" + bone.name.replace("TWEAK_", "")
                    fk.mix_mode = "REPLACE"
                    fk.target_space = "LOCAL"
                    fk.owner_space = "LOCAL"
                    fk.influence = 0.0
                    FK1InfluenceDrive = fk.driver_add("influence").driver

                    # Generate Custom Shape
                    mesh = bpy.data.meshes.new("UE4WSBoneShape_FK_" + bone.name.replace("TWEAK_", ""))
                    objFKShape = bpy.data.objects.new(mesh.name,mesh)
                    collection.objects.link(objFKShape)
                    mesh.from_pydata([v if i < 2 else ((v[0] * 0.5) / bone.length, v[1], (v[2] * 0.5) / bone.length) for i, v in enumerate(FKvertices)], FKedges, [])

                    FKBone = poseBones.get("FK_" + bone.name.replace("TWEAK_", ""))
                    FKBone.custom_shape = objFKShape
                    FKBone.bone_group = greenGroup

                    fk = lowerarm.constraints.new(type="COPY_TRANSFORMS")
                    fk.name = "TRANSFORM"
                    fk.show_expanded = False
                    fk.target = self.activeObject
                    fk.subtarget = "FK_" + lowerarm.name.replace("TWEAK_", "")
                    fk.mix_mode = "REPLACE"
                    fk.target_space = "LOCAL"
                    fk.owner_space = "LOCAL"
                    fk.influence = 0.0
                    FK2InfluenceDrive = fk.driver_add("influence").driver

                    # Generate Custom Shape
                    mesh = bpy.data.meshes.new("UE4WSBoneShape_FK_" + lowerarm.name.replace("TWEAK_", ""))
                    objFKShape = bpy.data.objects.new(mesh.name,mesh)
                    collection.objects.link(objFKShape)
                    mesh.from_pydata([v if i < 2 else ((v[0] * 0.4) / lowerarm.length, v[1], (v[2] * 0.4) / lowerarm.length) for i, v in enumerate(FKvertices)], FKedges, [])

                    FKBone = poseBones.get("FK_" + lowerarm.name.replace("TWEAK_", ""))
                    FKBone.custom_shape = objFKShape
                    FKBone.bone_group = greenGroup

                    # CONTROL RIG
                    if not self.activeObject.get("_RNA_UI"): # set RNA UI
                        self.activeObject["_RNA_UI"] = {}

                    # IK and FK influence
                    customPropertyName = hand.name.replace("TWEAK", "CR_IK") if hand is not None else lowerarm.name.replace("TWEAK", "CR_IK")
                    self.activeObject[customPropertyName] = 1.0
                    self.activeObject["_RNA_UI"][customPropertyName] = {
                        "description": "Influence For Use IK",
                        "default": 1.0,
                        "min": 0.0,
                        "max": 1.0,
                        "soft_min": 0.0,
                        "soft_max": 1.0,
                    }

                    # IK Driver
                    IKInfluenceDrive.type = "SCRIPTED"
                    var = IKInfluenceDrive.variables.new()
                    var.type = "SINGLE_PROP"
                    target = var.targets[0]
                    target.id = self.activeObject
                    target.data_path = "[\""+ customPropertyName + "\"]"
                    IKInfluenceDrive.expression = var.name

                    # FK Driver
                    FK1InfluenceDrive.type = "SCRIPTED"
                    var = FK1InfluenceDrive.variables.new()
                    var.type = "SINGLE_PROP"
                    target = var.targets[0]
                    target.id = self.activeObject
                    target.data_path = "[\""+ customPropertyName + "\"]"
                    FK1InfluenceDrive.expression = "abs("+ var.name + " - 1.0)"

                    FK2InfluenceDrive.type = "SCRIPTED"
                    var = FK2InfluenceDrive.variables.new()
                    var.type = "SINGLE_PROP"
                    target = var.targets[0]
                    target.id = self.activeObject
                    target.data_path = "[\""+ customPropertyName + "\"]"
                    FK2InfluenceDrive.expression = "abs("+ var.name + " - 1.0)"

                if hand is not None:
                    constraints = hand.constraints.new(type="COPY_ROTATION")
                    constraints.name = "HAND_CONTROL_ROTATION"
                    constraints.show_expanded = False
                    constraints.target = self.activeObject
                    constraints.subtarget = "CONTROL_" + hand.name.replace("TWEAK_", "")
                    constraints.mix_mode = "ADD"
                    constraints.target_space = "LOCAL"
                    constraints.owner_space = "LOCAL"
                    constraints.use_x = True
                    constraints.use_y = True
                    constraints.use_z = True
                    constraints.invert_x = False
                    constraints.invert_y = False
                    constraints.invert_z = False

                    if objHandTweakShape is None:
                        mesh = bpy.data.meshes.new("UE4WSBoneShape_Hand_Tweak")
                        objHandTweakShape = bpy.data.objects.new(mesh.name,mesh)
                        collection.objects.link(objHandTweakShape)
                        mesh.from_pydata([((v[0] * 0.3) / hand.length, v[1], (v[2] * 0.2) / hand.length) for i, v in enumerate(handTweakVertices)], handTweakEdges, [])
                    hand.custom_shape = objHandTweakShape
                    hand.bone_group = yellowGroup

                    poseBone = poseBones.get("CONTROL_" + hand.name.replace("TWEAK_", ""))
                    if poseBones is not None:
                        if objHandShape is None:
                            mesh = bpy.data.meshes.new("UE4WSBoneShape_Hand")
                            objHandShape = bpy.data.objects.new(mesh.name,mesh)
                            collection.objects.link(objHandShape)
                            mesh.from_pydata(verticeshandShape, edgeshandShape, [])
                        poseBone.custom_shape = objHandShape
                        poseBone.bone_group = redGroup

        TwistVertices = [(0.0, 0.5, 0.20000000298023224), (-0.07653669267892838, 0.5, 0.18477590382099152), (-0.1414213627576828, 0.5, 0.1414213627576828), (-0.18477590382099152, 0.5, 0.07653668522834778), (-0.20000000298023224, 0.5, -8.742278012618954e-09), (-0.18477590382099152, 0.5, -0.07653670758008957), (-0.1414213627576828, 0.5, -0.1414213627576828), (-0.07653670012950897, 0.5, -0.18477590382099152), (-3.019916050561733e-08, 0.5, -0.20000000298023224), (0.0765366479754448, 0.5, -0.1847759336233139), (0.14142131805419922, 0.5, -0.14142140746116638), (0.18477590382099152, 0.5, -0.07653671503067017), (0.20000000298023224, 0.5, 2.384976216518453e-09), (0.18477588891983032, 0.5, 0.07653672248125076), (0.14142130315303802, 0.5, 0.14142140746116638), (0.07653659582138062, 0.5, 0.1847759485244751)]
        TwistEdges = [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4), (6, 5), (7, 6), (8, 7), (9, 8), (10, 9), (11, 10), (12, 11), (13, 12), (14, 13), (15, 14), (0, 15)]
        # TWIST BONE CUSTOM SHAPE
        for bone in [bone for bone in poseBones if bone.name.startswith("TWEAK_") and "_twist_" in bone.name and bone.custom_shape is None]:
            mesh = bpy.data.meshes.new("UE4WSBoneShape_" + bone.name.replace("TWEAK_", ""))
            objCustomShape = bpy.data.objects.new(mesh.name,mesh)
            collection.objects.link(objCustomShape)
            mesh.from_pydata([((v[0] * 0.4) / bone.length, v[1], (v[2] * 0.4) / bone.length) for i, v in enumerate(TwistVertices)], TwistEdges, [])
            bone.custom_shape = objCustomShape
            bone.bone_group = yellowGroup

        # Generate Pelvis Shape
        pelvisVertices = [(-2.9555113911783337e-08, 0.0, 0.20663587749004364), (-0.07907618582248688, 0.0, 0.19090662896633148), (-0.14611367881298065, 0.0, 0.1461135596036911), (-0.19090674817562103, 7.450580596923828e-09, 0.07907604426145554), (-0.2066359966993332, 9.313225746154785e-09, -1.28688327549753e-07), (-0.19090674817562103, 1.4901161193847656e-08, -0.07907629758119583), (-0.14611367881298065, 1.4901161193847656e-08, -0.1461138278245926), (-0.07907618582248688, 1.4901161193847656e-08, -0.19090689718723297), (-6.075627823065588e-08, 1.4901161193847656e-08, -0.20663608610630035), (0.07907608151435852, 1.4901161193847656e-08, -0.19090689718723297), (0.14611361920833588, 1.4901161193847656e-08, -0.14611388742923737), (0.19090674817562103, 1.4901161193847656e-08, -0.07907629758119583), (0.20663593709468842, 9.313225746154785e-09, -1.1719187398284703e-07), (0.19090668857097626, 7.450580596923828e-09, 0.07907607406377792), (0.14611361920833588, 0.0, 0.14611361920833588), (0.07907605171203613, 0.0, 0.19090668857097626)]
        pelvisEdges = [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4), (6, 5), (7, 6), (8, 7), (9, 8), (10, 9), (11, 10), (12, 11), (13, 12), (14, 13), (15, 14), (0, 15)]
        # PELVIS
        for bone in [bone for bone in poseBones if bone.get("UE4RIGTYPE") == "PELVIS" and bone.custom_shape is None]:
            mesh = bpy.data.meshes.new("UE4WSBoneShape_" + bone.name)
            objPelvis = bpy.data.objects.new(mesh.name,mesh)
            collection.objects.link(objPelvis)
            mesh.from_pydata([(v[0] / bone.length, v[1], v[2] / bone.length) for v in pelvisVertices], pelvisEdges, [])
            bone.custom_shape = objPelvis
            bone.bone_group = yellowGroup

        # Generate Spine Shape
        spineVertices = [(-2.9555113911783337e-08, 0.0, 0.20663587749004364), (-0.07907618582248688, 0.0, 0.19090662896633148), (-0.14611367881298065, 0.0, 0.1461135596036911), (-0.19090674817562103, 7.450580596923828e-09, 0.07907604426145554), (-0.2066359966993332, 9.313225746154785e-09, -1.28688327549753e-07), (-0.19090674817562103, 1.4901161193847656e-08, -0.07907629758119583), (-0.14611367881298065, 1.4901161193847656e-08, -0.1461138278245926), (-0.07907618582248688, 1.4901161193847656e-08, -0.19090689718723297), (-6.075627823065588e-08, 1.4901161193847656e-08, -0.20663608610630035), (0.07907608151435852, 1.4901161193847656e-08, -0.19090689718723297), (0.14611361920833588, 1.4901161193847656e-08, -0.14611388742923737), (0.19090674817562103, 1.4901161193847656e-08, -0.07907629758119583), (0.20663593709468842, 9.313225746154785e-09, -1.1719187398284703e-07), (0.19090668857097626, 7.450580596923828e-09, 0.07907607406377792), (0.14611361920833588, 0.0, 0.14611361920833588), (0.07907605171203613, 0.0, 0.19090668857097626)]
        spineEdges = [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4), (6, 5), (7, 6), (8, 7), (9, 8), (10, 9), (11, 10), (12, 11), (13, 12), (14, 13), (15, 14), (0, 15)]
        # SPINE
        for bone in [bone for bone in poseBones if bone.get("UE4RIGTYPE") == "SPINE" and bone.custom_shape is None]:
            mesh = bpy.data.meshes.new("UE4WSBoneShape_" + bone.name)
            objSpine = bpy.data.objects.new(mesh.name,mesh)
            collection.objects.link(objSpine)
            mesh.from_pydata([(v[0] / bone.length, 0.5, v[2] / bone.length) for v in pelvisVertices], pelvisEdges, [])
            bone.custom_shape = objSpine
            bone.bone_group = yellowGroup
            self.spineRecursiveBone(bone.children, collection, spineVertices, spineEdges, yellowGroup)

        # Generate Neck Shape
        neckVertices = [(-2.9555113911783337e-08, 0.0, 0.20663587749004364), (-0.07907618582248688, 0.0, 0.19090662896633148), (-0.14611367881298065, 0.0, 0.1461135596036911), (-0.19090674817562103, 7.450580596923828e-09, 0.07907604426145554), (-0.2066359966993332, 9.313225746154785e-09, -1.28688327549753e-07), (-0.19090674817562103, 1.4901161193847656e-08, -0.07907629758119583), (-0.14611367881298065, 1.4901161193847656e-08, -0.1461138278245926), (-0.07907618582248688, 1.4901161193847656e-08, -0.19090689718723297), (-6.075627823065588e-08, 1.4901161193847656e-08, -0.20663608610630035), (0.07907608151435852, 1.4901161193847656e-08, -0.19090689718723297), (0.14611361920833588, 1.4901161193847656e-08, -0.14611388742923737), (0.19090674817562103, 1.4901161193847656e-08, -0.07907629758119583), (0.20663593709468842, 9.313225746154785e-09, -1.1719187398284703e-07), (0.19090668857097626, 7.450580596923828e-09, 0.07907607406377792), (0.14611361920833588, 0.0, 0.14611361920833588), (0.07907605171203613, 0.0, 0.19090668857097626)]
        neckEdges = [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4), (6, 5), (7, 6), (8, 7), (9, 8), (10, 9), (11, 10), (12, 11), (13, 12), (14, 13), (15, 14), (0, 15)]
        # Neck
        for bone in [bone for bone in poseBones if bone.get("UE4RIGTYPE") == "NECK" and bone.custom_shape is None]:
            mesh = bpy.data.meshes.new("UE4WSBoneShape_" + bone.name)
            objCustomShape = bpy.data.objects.new(mesh.name,mesh)
            collection.objects.link(objCustomShape)
            mesh.from_pydata([(v[0] * 5, 0.5, v[2] * 5) for v in pelvisVertices], pelvisEdges, [])
            bone.custom_shape = objCustomShape
            bone.bone_group = yellowGroup
            self.neckRecursiveBone(bone.children, collection, neckVertices, neckEdges, yellowGroup)

        # Generate Head Human Shape
        headVertices = [(-1.6763809895792292e-08, 1.0, 0.550000011920929), (-0.21047590672969818, 1.0, 0.5081337094306946), (-0.3889086842536926, 1.0, 0.3889087438583374), (-0.5081337094306946, 1.0, 0.21047590672969818), (-0.5499999523162842, 1.0, -2.273741372960103e-08), (-0.5081337094306946, 1.0, -0.21047592163085938), (-0.3889086842536926, 1.0, -0.3889087438583374), (-0.21047593653202057, 1.0, -0.5081337094306946), (-9.981150128623995e-08, 1.0, -0.550000011920929), (0.21047572791576385, 1.0, -0.5081338286399841), (0.38890859484672546, 1.0, -0.38890886306762695), (0.5081336498260498, 1.0, -0.21047595143318176), (0.5499998927116394, 1.0, 7.86253551154914e-09), (0.508133590221405, 1.0, 0.21047599613666534), (0.3889085650444031, 1.0, 0.38890886306762695), (0.2104756087064743, 1.0, 0.5081338882446289)]
        headEdges = [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4), (6, 5), (7, 6), (8, 7), (9, 8), (10, 9), (11, 10), (12, 11), (13, 12), (14, 13), (15, 14), (0, 15)]
        # HEAD_HUMAN
        for bone in [bone for bone in poseBones if bone.get("UE4RIGTYPE") == "HEAD_HUMAN" and bone.custom_shape is None]:
            mesh = bpy.data.meshes.new("UE4WSBoneShape_" + bone.name)
            objHeadHuman = bpy.data.objects.new(mesh.name,mesh)
            collection.objects.link(objHeadHuman)
            mesh.from_pydata(headVertices, headEdges, [])
            bone.custom_shape = objHeadHuman
            bone.bone_group= yellowGroup

        # Generate Copy Bone
        copyBoneVertices = [(-0.01, 0.0, -0.01), (0.01, 0.0, -0.01), (-0.01, 1.0, -0.01), (0.01, 1.0, -0.01), (-0.01, 0.0, 0.01), (0.01, 0.0, 0.01), (-0.01, 1.0, 0.01), (0.01, 1.0, 0.01)]
        copyBoneEdges = [(2, 0), (0, 1), (1, 3), (3, 2), (6, 4), (4, 5), (5, 7), (7, 6), (1, 5), (4, 0), (3, 7), (6, 2)]
        # COPY_BONE
        for bone in [bone for bone in poseBones if bone.get("UE4RIGTYPE") == "COPY_BONE" and bone.custom_shape is None]:
            mesh = bpy.data.meshes.new("UE4WSBoneShape_" + bone.name)
            objCopyBone = bpy.data.objects.new(mesh.name,mesh)
            collection.objects.link(objCopyBone)
            mesh.from_pydata([(v[0] / bone.length, v[1], v[2] / bone.length) for v in copyBoneVertices], copyBoneEdges, [])
            bone.custom_shape = objCopyBone
            bone.bone_group = yellowGroup

        # Generate Face Control Bone Humanoid
        faceControlHumanoidVertices = [(-5.3341501882187004e-08, 0.0, 0.04125000908970833), (-0.015785744413733482, 0.0, 0.03811003640294075), (-0.029168201610445976, 0.0, 0.029168162494897842), (-0.038110073655843735, 0.0, 0.01578569784760475), (-0.04125004634261131, 0.0, 3.137571091826885e-09), (-0.038110073655843735, 0.0, -0.015785690397024155), (-0.029168201610445976, 0.0, -0.029168155044317245), (-0.015785744413733482, 0.0, -0.03811001405119896), (-5.9570076871295896e-08, 0.0, -0.04124998673796654), (0.01578562892973423, 0.0, -0.03811004385352135), (0.029168086126446724, 0.0, -0.029168155044317245), (0.038109976798295975, 0.0, -0.015785690397024155), (0.04124993458390236, 0.0, 5.432567284913148e-09), (0.03810996189713478, 0.0, 0.01578570529818535), (0.029168086126446724, 0.0, 0.029168177396059036), (0.015785621479153633, 0.0, 0.038110051304101944)]
        faceControlHumanoidEdges = [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4), (6, 5), (7, 6), (8, 7), (9, 8), (10, 9), (11, 10), (12, 11), (13, 12), (14, 13), (15, 14), (0, 15)]
        # FACE_CONTROL_HUMAN
        for bone in [bone for bone in poseBones if bone.get("UE4RIGTYPE") == "FACE_CONTROL_HUMAN" and bone.get("BONE_CONTROL")]:
            boneControl = self.poseBone(bone.get("BONE_CONTROL"))
            # constraint
            constraints = bone.constraints.new(type="COPY_TRANSFORMS")
            constraints.name = "TRANSFORM"
            constraints.show_expanded = False
            constraints.target = self.activeObject
            constraints.subtarget = bone.get("BONE_CONTROL")
            constraints.mix_mode = "REPLACE"
            constraints.target_space = "LOCAL"
            constraints.owner_space = "LOCAL"
            # custom shape
            mesh = bpy.data.meshes.new("UE4WSBoneShape_" + boneControl.name)
            objFaceControl = bpy.data.objects.new(mesh.name,mesh)
            collection.objects.link(objFaceControl)
            mesh.from_pydata(faceControlHumanoidVertices, faceControlHumanoidEdges, [])
            boneControl.custom_shape = objFaceControl
            boneControl.bone_group= yellowGroup

        # Generate Face Jaw Control Bone Humanoid
        faceJawControlHumanoidVertices = [(-0.2499999850988388, 0.0, 0.25), (0.2499999850988388, 0.0, 0.25), (-0.2499999850988388, 0.0, -0.12901227176189423), (-0.12901225686073303, 0.0, -0.25), (0.12901225686073303, 0.0, -0.25), (0.2499999850988388, 0.0, -0.12901227176189423)]
        faceJawControlHumanoidEdges = [(1, 0), (2, 3), (4, 5), (2, 0), (3, 4), (5, 1)]
        # FACE_JAW_HUMAN
        for bone in [bone for bone in poseBones if bone.get("UE4RIGTYPE") == "FACE_JAW_HUMAN" and bone.get("BONE_CONTROL")]:
            boneControl = self.poseBone(bone.get("BONE_CONTROL"))
            # constraint
            constraints = bone.constraints.new(type="DAMPED_TRACK")
            constraints.name = "TRACK"
            constraints.show_expanded = False
            constraints.target = self.activeObject
            constraints.subtarget = bone.get("BONE_CONTROL")
            constraints.track_axis = "TRACK_Y"
            constraints.head_tail = 0.5
            # custom shape
            mesh = bpy.data.meshes.new("UE4WSBoneShape_" + boneControl.name)
            objFaceJawControl = bpy.data.objects.new(mesh.name,mesh)
            collection.objects.link(objFaceJawControl)
            mesh.from_pydata(faceJawControlHumanoidVertices, faceJawControlHumanoidEdges, [])
            boneControl.custom_shape = objFaceJawControl
            boneControl.bone_group= redGroup

        # Generate Face Nose Control Bone Humanoid
        faceNoseControlHumanoidVertices = [(-0.32910746335983276, 0.0, -0.32910752296447754), (0.32910746335983276, 0.0, -0.32910752296447754), (-0.16455373167991638, 0.0, 0.32910752296447754), (0.16455373167991638, 0.0, 0.32910752296447754)]
        faceNoseControlHumanoidEdges = [(2, 0), (0, 1), (1, 3), (3, 2)]
        # FACE_NOSE_HUMAN
        for bone in [bone for bone in poseBones if bone.get("UE4RIGTYPE") == "FACE_NOSE_HUMAN" and bone.get("BONE_CONTROL")]:
            boneControl = self.poseBone(bone.get("BONE_CONTROL"))
            # constraint
            constraints = bone.constraints.new(type="COPY_TRANSFORMS")
            constraints.name = "TRANSFORM"
            constraints.show_expanded = False
            constraints.target = self.activeObject
            constraints.subtarget = bone.get("BONE_CONTROL")
            constraints.mix_mode = "REPLACE"
            constraints.target_space = "LOCAL"
            constraints.owner_space = "LOCAL"
            # custom shape
            mesh = bpy.data.meshes.new("UE4WSBoneShape_" + boneControl.name)
            objFaceNoseControl = bpy.data.objects.new(mesh.name,mesh)
            collection.objects.link(objFaceNoseControl)
            mesh.from_pydata(faceNoseControlHumanoidVertices, faceNoseControlHumanoidEdges, [])
            boneControl.custom_shape = objFaceNoseControl
            boneControl.bone_group= yellowGroup

        # Generate Face Eye Control Bone Humanoid
        faceEyeControlHumanoidVertices = [(-0.3058179020881653, 0.0, -0.07159699499607086), (-0.03911216929554939, 0.0, -0.167062908411026), (0.03911216929554939, 0.0, -0.167062908411026), (0.3058179020881653, 0.0, -0.07159699499607086), (-0.3058179020881653, 0.0, 0.07159699499607086), (-0.03911216929554939, 0.0, 0.167062908411026), (0.3058179020881653, 0.0, 0.07159699499607086), (0.03911216929554939, 0.0, 0.167062908411026), (0.0, -6.119594164744058e-09, 0.14000000059604645), (-0.07000000029802322, -5.29972377094623e-09, 0.12124355137348175), (-0.12124356627464294, -3.059796860327424e-09, 0.06999999284744263), (-0.14000000059604645, 2.6749596935822344e-16, -6.119594164744058e-09), (-0.12124355137348175, 3.0597975264612387e-09, -0.07000000774860382), (-0.07000000774860382, 5.29972377094623e-09, -0.12124355137348175), (-2.1139411998660762e-08, 6.119594164744058e-09, -0.14000000059604645), (0.06999997049570084, 5.299725103213859e-09, -0.12124357372522354), (0.12124352902173996, 3.059799080773473e-09, -0.0700000450015068), (0.14000000059604645, 2.845074614335236e-15, -6.508771832614002e-08), (0.12124359607696533, -3.05979397374756e-09, 0.06999992579221725), (0.07000008225440979, -5.2997224386786e-09, 0.12124351412057877)]
        faceEyeControlHumanoidEdges = [(0, 1), (2, 3), (4, 5), (6, 7), (0, 4), (1, 2), (3, 6), (5, 7), (9, 8), (10, 9), (11, 10), (12, 11), (13, 12), (14, 13), (15, 14), (16, 15), (17, 16), (18, 17), (19, 18), (8, 19)]
        # FACE_EYE_HUMAN
        for bone in [bone for bone in poseBones if bone.get("UE4RIGTYPE") == "FACE_EYE_HUMAN" and bone.get("BONE_CONTROL")]:
            boneControl = self.poseBone(bone.get("BONE_CONTROL"))
            # constraint
            constraints = bone.constraints.new(type="TRACK_TO")
            constraints.name = "LOOK_TO"
            constraints.show_expanded = False
            constraints.target = self.activeObject
            constraints.subtarget = bone.get("BONE_CONTROL")
            constraints.target_space = "POSE"
            constraints.owner_space = "POSE"
            # custom shape
            mesh = bpy.data.meshes.new("UE4WSBoneShape_" + boneControl.name)
            objFaceEyeControl = bpy.data.objects.new(mesh.name,mesh)
            collection.objects.link(objFaceEyeControl)
            mesh.from_pydata(faceEyeControlHumanoidVertices, faceEyeControlHumanoidEdges, [])
            boneControl.custom_shape = objFaceEyeControl
            boneControl.bone_group= blueGroup

        # Generate Face Look Control Bone Humanoid
        faceLookControlHumanoidVertices = [(-0.25, -0.25, -0.25), (-0.25, -0.25, 0.25), (-0.25, 0.25, -0.25), (-0.25, 0.25, 0.25), (0.25, -0.25, -0.25), (0.25, -0.25, 0.25), (0.25, 0.25, -0.25), (0.25, 0.25, 0.25)]
        faceLookControlHumanoidEdges = [(2, 0), (0, 1), (1, 3), (3, 2), (6, 2), (3, 7), (7, 6), (4, 6), (7, 5), (5, 4), (0, 4), (5, 1)]
        # BONE_LOOK_CONTROL
        for bone, faceAttach in [(self.poseBone(bone.get("BONE_LOOK_CONTROL")), bone) for bone in poseBones if bone.get("UE4RIGTYPE") == "FACE_HUMAN" and bone.get("BONE_LOOK_CONTROL")]:
            bone["UE4RIGTYPE"]= "FACE_LOOK_CONTROL"
            # constraint
            constraints = bone.constraints.new(type="CHILD_OF")
            constraints.name = "LOOK_CONTROL_PARENT"
            constraints.show_expanded = False
            constraints.target = self.activeObject
            constraints.subtarget = faceAttach.name
            LookInfluenceDrive = constraints.driver_add("influence").driver
            # custom shape
            mesh = bpy.data.meshes.new("UE4WSBoneShape_" + boneControl.name)
            objFaceLookControl = bpy.data.objects.new(mesh.name,mesh)
            collection.objects.link(objFaceLookControl)
            mesh.from_pydata(faceLookControlHumanoidVertices, faceLookControlHumanoidEdges, [])
            bone.custom_shape = objFaceLookControl
            bone.bone_group= greenGroup

            # CONTROL RIG
            if not self.activeObject.get("_RNA_UI"): # set RNA UI
                self.activeObject["_RNA_UI"] = {}

            # LOOK influence
            customPropertyName = "CR_LOOK_" + bone.name
            self.activeObject[customPropertyName] = 1.0
            self.activeObject["_RNA_UI"][customPropertyName] = {
                "description": "Influence For Look Head Rotation",
                "default": 1.0,
                "min": 0.0,
                "max": 1.0,
                "soft_min": 0.0,
                "soft_max": 1.0,
            }

            # LOOK Driver
            LookInfluenceDrive.type = "SCRIPTED"
            var = LookInfluenceDrive.variables.new()
            var.type = "SINGLE_PROP"
            target = var.targets[0]
            target.id = self.activeObject
            target.data_path = "[\""+ customPropertyName + "\"]"
            LookInfluenceDrive.expression = var.name

        # Generate Face Teeth Control Bone Humanoid
        faceTeethControlHumanoidVertices = [(-0.42000001668930054, 1.8358782938321383e-08, -0.12920930981636047), (0.42000001668930054, 1.8358782938321383e-08, -0.12920930981636047), (-0.42000001668930054, -1.8358782938321383e-08, 0.12920930981636047), (0.42000001668930054, -1.8358782938321383e-08, 0.12920930981636047), (-0.42000001668930054, 0.23703818023204803, -0.12920930981636047), (0.42000001668930054, 0.23703818023204803, -0.12920930981636047), (-0.42000001668930054, 0.23703815042972565, 0.12920930981636047), (0.42000001668930054, 0.23703815042972565, 0.12920930981636047)]
        faceTeethControlHumanoidEdges = [(2, 0), (0, 1), (1, 3), (3, 2), (6, 4), (4, 5), (5, 7), (7, 6), (2, 6), (7, 3), (1, 5), (4, 0)]
        # FACE_TEETH_HUMAN
        for bone in [bone for bone in poseBones if bone.get("UE4RIGTYPE") == "FACE_TEETH_HUMAN" and bone.get("BONE_CONTROL")]:
            boneControl = self.poseBone(bone.get("BONE_CONTROL"))
            # constraint
            constraints = bone.constraints.new(type="COPY_TRANSFORMS")
            constraints.name = "TRANSFORM"
            constraints.show_expanded = False
            constraints.target = self.activeObject
            constraints.subtarget = bone.get("BONE_CONTROL")
            constraints.mix_mode = "REPLACE"
            constraints.target_space = "LOCAL"
            constraints.owner_space = "LOCAL"
            # custom shape
            mesh = bpy.data.meshes.new("UE4WSBoneShape_" + boneControl.name)
            objFaceTeethControl = bpy.data.objects.new(mesh.name,mesh)
            collection.objects.link(objFaceTeethControl)
            mesh.from_pydata(faceTeethControlHumanoidVertices, faceTeethControlHumanoidEdges, [])
            boneControl.custom_shape = objFaceTeethControl
            boneControl.bone_group= yellowGroup

        # Generate Face Tongue Control Bone Humanoid
        faceTongueControlHumanoidVertices = [(-0.3256967067718506, 0.47867369651794434, 0.0), (0.3256967067718506, 0.47867369651794434, 0.0), (0.0, 0.47867369651794434, 0.0), (-0.3039208650588989, -0.2570299506187439, 0.0), (-0.07561969757080078, -0.47867369651794434, 0.0), (-0.23433561623096466, -0.41375574469566345, 0.0), (0.3039208650588989, -0.2570299506187439, 0.0), (0.07561969757080078, -0.47867369651794434, 0.0), (0.23433561623096466, -0.41375574469566345, 0.0), (0.0, -0.15590238571166992, 0.0)]
        faceTongueControlHumanoidEdges = [(2, 1), (0, 2), (3, 5), (5, 4), (6, 8), (8, 7), (3, 0), (4, 7), (6, 1), (2, 9)]
        # FACE_TONGUE_HUMAN
        for bone in [bone for bone in poseBones if bone.get("UE4RIGTYPE") == "FACE_TONGUE_HUMAN" and bone.get("BONE_CONTROL")]:
            boneControl = self.poseBone(bone.get("BONE_CONTROL"))
            # constraint
            constraints = bone.constraints.new(type="COPY_TRANSFORMS")
            constraints.name = "TRANSFORM"
            constraints.show_expanded = False
            constraints.target = self.activeObject
            constraints.subtarget = bone.get("BONE_CONTROL")
            constraints.mix_mode = "REPLACE"
            constraints.target_space = "LOCAL"
            constraints.owner_space = "LOCAL"
            # custom shape
            mesh = bpy.data.meshes.new("UE4WSBoneShape_" + boneControl.name)
            objFaceTeethControl = bpy.data.objects.new(mesh.name,mesh)
            collection.objects.link(objFaceTeethControl)
            mesh.from_pydata(faceTongueControlHumanoidVertices, faceTongueControlHumanoidEdges, [])
            boneControl.custom_shape = objFaceTeethControl
            boneControl.bone_group= yellowGroup

        # Generate Face Eyelid Control Bone Humanoid
        EyelidUpperControlHumanoidVertices = [(0.2574883699417114, 2.849847078323364e-07, 1.8610592178447405e-07), (-0.25748831033706665, 2.849847078323364e-07, -6.331407575999037e-07), (0.08769719302654266, 2.849847078323364e-07, 0.22647202014923096), (0.2574883699417114, 2.849847078323364e-07, 0.05668110400438309), (-0.08769707381725311, 2.849847078323364e-07, 0.22647172212600708), (-0.25748831033706665, 2.849847078323364e-07, 0.056680239737033844)]
        EyelidLowerControlHumanoidVertices = [(-0.2574883699417114, 2.849847078323364e-07, -2.086162567138672e-07), (0.25748831033706665, 2.849847078323364e-07, 6.556510925292969e-07), (-0.08769716322422028, 2.849847078323364e-07, -0.22647202014923096), (-0.2574883699417114, 2.849847078323364e-07, -0.05668112635612488), (0.0876971036195755, 2.849847078323364e-07, -0.22647172212600708), (0.25748831033706665, 2.849847078323364e-07, -0.05668021738529205)]
        EyelidControlHumanoidEdges = [(0, 1), (2, 3), (4, 5), (2, 4), (3, 0), (5, 1)]
        # FACE_EYELID_UPPER_HUMAN and FACE_EYELID_LOWER_HUMAN
        for bone in [bone for bone in poseBones if bone.get("UE4RIGTYPE") in ["FACE_EYELID_UPPER_HUMAN", "FACE_EYELID_LOWER_HUMAN"] and bone.get("BONE_CONTROL")]:
            boneControl = self.poseBone(bone.get("BONE_CONTROL"))
            # constraint
            constraints = bone.constraints.new(type="LIMIT_LOCATION")
            constraints.name = "LIMIT_LOCATION"
            constraints.show_expanded = False
            constraints.use_min_y = True
            constraints.use_min_x = True
            constraints.use_min_z = True
            constraints.use_max_y = True
            constraints.use_max_x = True
            constraints.use_max_z = True
            constraints.use_transform_limit = True
            constraints.owner_space = "LOCAL_WITH_PARENT"

            constraints = bone.constraints.new(type="CHILD_OF")
            constraints.name = "LID_PARENT"
            constraints.show_expanded = False
            constraints.target = self.activeObject
            constraints.subtarget = boneControl.parent.name
            # constraints.mute = True

            constraints = bone.constraints.new(type="COPY_LOCATION")
            constraints.name = "LOCATION"
            constraints.show_expanded = False
            constraints.target = self.activeObject
            constraints.subtarget = bone.get("BONE_CONTROL")
            constraints.target_space = "LOCAL"
            constraints.owner_space = "LOCAL"
            constraints.use_offset = True

            constraints = bone.constraints.new(type="COPY_SCALE")
            constraints.name = "SCALE"
            constraints.show_expanded = False
            constraints.target = self.activeObject
            constraints.subtarget = bone.get("BONE_CONTROL")
            constraints.target_space = "LOCAL"
            constraints.owner_space = "LOCAL"

            constraints = bone.constraints.new(type="COPY_ROTATION")
            constraints.name = "ROTATION"
            constraints.show_expanded = False
            constraints.target = self.activeObject
            constraints.subtarget = bone.get("BONE_CONTROL")
            constraints.mix_mode = "REPLACE"
            constraints.target_space = "LOCAL_WITH_PARENT"
            constraints.owner_space = "LOCAL_WITH_PARENT"

            # custom shape
            mesh = bpy.data.meshes.new("UE4WSBoneShape_" + boneControl.name)
            objFaceEyelidControl = bpy.data.objects.new(mesh.name,mesh)
            collection.objects.link(objFaceEyelidControl)
            mesh.from_pydata((EyelidLowerControlHumanoidVertices, EyelidUpperControlHumanoidVertices)[bone.get("UE4RIGTYPE") == "FACE_EYELID_UPPER_HUMAN"], EyelidControlHumanoidEdges, [])
            boneControl.custom_shape = objFaceEyelidControl
            boneControl.bone_group= yellowGroup

        bpy.ops.armature.armature_layers(layers=(True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
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

        # set inverse for eyelid and look control
        bpy.ops.object.mode_set(mode="POSE")
        for pbone, constraint in [(bone, bone.constraints.get("LID_PARENT")) for bone in poseBones if bone.get("UE4RIGTYPE") in ["FACE_EYELID_UPPER_HUMAN", "FACE_EYELID_LOWER_HUMAN"] and bone.constraints.get("LID_PARENT")]:
            # show third layer
            self.activeObject.data.layers[2] = True
            context_copy = bpy.context.copy()
            context_copy["constraint"] = constraint
            self.activeObject.data.bones.active = pbone.bone
            bpy.ops.constraint.childof_set_inverse(context_copy, constraint=constraint.name, owner="BONE")
            # hide third layer
            self.activeObject.data.layers[2] = False
        for pbone, constraint in [(bone, bone.constraints.get("LOOK_CONTROL_PARENT")) for bone in poseBones if bone.get("UE4RIGTYPE") == "FACE_LOOK_CONTROL" and bone.constraints.get("LOOK_CONTROL_PARENT")]:
            # show third layer
            self.activeObject.data.layers[2] = True
            context_copy = bpy.context.copy()
            context_copy["constraint"] = constraint
            self.activeObject.data.bones.active = pbone.bone
            bpy.ops.constraint.childof_set_inverse(context_copy, constraint=constraint.name, owner="BONE")
            # hide third layer
            self.activeObject.data.layers[2] = False
        bpy.ops.object.mode_set(mode="OBJECT")

        self.activeObject.show_in_front = False
        del self.activeObject["UE4RIG"]
        self.activeObject["UE4RIGGED"] = True

        bpy.ops.object.mode_set(mode=oldMode)