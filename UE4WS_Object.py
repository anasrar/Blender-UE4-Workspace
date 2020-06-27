import bpy
from mathutils import Matrix
from bpy.props import (EnumProperty, StringProperty, PointerProperty)
from bpy.types import (Panel, Operator)

# PROPS

Props = [
    {
        "type": "scene",
        "name": "SM_CollsionPicker",
        "value": PointerProperty(
            name="Collision Picker",
            description="Make mesh into a custom collision",
            type=bpy.types.Object,
            poll=lambda self, obj: obj.type == "MESH" and not obj.get("isCollision") and not "ARMATURE" in [mod.type for mod in obj.modifiers]
            ),
        "resetVariable": True
    },
    {
        "type": "object",
        "name": "attachTo",
        "value": PointerProperty(
            name="Attach to",
            description="Attach object to socket",
            type=bpy.types.Object,
            poll=lambda self, obj: obj.type == "EMPTY" and obj.get("isSocket")
            ),
        "resetVariable": False
    }
]

# PANEL

class PANEL(Panel):
    bl_idname = "UE4WORKSPACE_PT_ObjectPanel"
    bl_label = "Object"
    bl_category = "UE4Workspace"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    remote = None

    @classmethod
    def poll(self, context):
        if context.active_object is not None and context.active_object.type == "MESH" and not "ARMATURE" in [mod.type for mod in context.active_object.modifiers]:
            return True
        elif context.active_object is not None and context.active_object.type == "ARMATURE":
            return True
        return False

    def drawSocketAttach(self, context):
        """draw socket attach layout for reuse (mesh and character object)"""
        layout = self.layout

        col = layout.box().column()
        row = col.row()
        split = row.split(factor=0.6)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text="Attach to")
        split = split.split()
        col = split.column()
        row = col.row()
        row.enabled = not context.active_object.get("isAttachToObject", False)
        row.prop(context.active_object, "attachTo", text="", icon="EMPTY_ARROWS")
        row = col.row()
        row.scale_y = 1.5
        row.operator("ue4workspace.attachobject",icon="CON_PIVOT", text=("Attach", "Detach")[context.active_object.get("isAttachToObject", False)])

        box = layout.box()
        row = box.row()
        row.scale_y = 1.5
        row.operator("ue4workspace.createsocket",icon="EMPTY_ARROWS", text="Add Socket")

        socketObjects = [obj for obj in context.scene.objects if obj.type == "EMPTY" and obj.get("isSocket") and obj.parent is context.active_object]

        if socketObjects:
            for obj in socketObjects:
                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.prop(obj, "name", text="")
                split = split.split()
                row = split.row()
                row.alignment = "RIGHT"
                row.operator("ue4workspace.togglevisibilityobject",icon=("HIDE_OFF", "HIDE_ON")[obj.hide_get()], text="", emboss=False).objName = obj.name
                row.operator("ue4workspace.removeobject",icon="TRASH", text="", emboss=False).objName = obj.name

                col = box.column()
                row = col.row()
                split = row.split(factor=0.6)
                col = split.column()
                col.alignment = "RIGHT"
                col.label(text="Size")
                split = split.split()
                col = split.column()
                col.prop(obj, "empty_display_size", text="")

                # Socket parent bone for character
                if obj.parent_type == "BONE":
                    col = box.column()
                    row = col.row()
                    split = row.split(factor=0.6)
                    col = split.column()
                    col.alignment = "RIGHT"
                    col.label(text="Bone")
                    split = split.split()
                    col = split.column()
                    col.prop_search(obj, "parent_bone", context.active_object.data, "bones", text="")

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons[__package__].preferences

        if context.active_object is not None:
            modifiersTypeList = [mod.type for mod in context.active_object.modifiers]

            if context.active_object is not None and context.active_object.type == "MESH" and not "ARMATURE" in modifiersTypeList and not context.active_object.get("isCollision"):
                # Static mesh
                layout.prop(preferences, "SM_OBJTabCustomCollision", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.SM_OBJTabCustomCollision], emboss=False)
                if preferences.SM_OBJTabCustomCollision:
                    row = layout.row()
                    row.scale_y = 1.5
                    row.operator("wm.url_open",icon="INFO", text="FBX Static Mesh Pipeline").url="https://docs.unrealengine.com/en-US/Engine/Content/Importing/FBX/StaticMeshes/#collision"
                    # Add Collision Button
                    row = layout.row()
                    row.scale_y = 1.5
                    row.operator("ue4workspace.makecollision",icon="OUTLINER_OB_MESH", text="Create Collision")

                    if context.mode == "OBJECT" and context.active_object is not None and not context.active_object.get("isCollision"):
                        col = layout.column()
                        row = col.row()
                        split = row.split(factor=0.6)
                        col = split.column()
                        col.alignment = "RIGHT"
                        col.label(text="Collision Picker")
                        split = split.split()
                        col = split.column()
                        col.prop(context.scene, "SM_CollsionPicker", text="")
                        col = col.row()
                        col.scale_y = 1.5
                        col.operator("ue4workspace.smcollisionpicker",icon="MOD_SOLIDIFY", text="Convert")

                    collisionObjects = [obj for obj in context.scene.objects if obj.type == "MESH" and obj.parent == context.active_object and obj.get("isCollision")]

                    if collisionObjects:
                        box = layout.box()
                        for obj in collisionObjects:
                            col = box.column()
                            row = col.row()
                            split = row.split(factor=0.6)
                            col = split.column()
                            col.prop(obj, "name", text="")
                            split = split.split()
                            row = split.row()
                            row.alignment = "RIGHT"
                            row.operator("ue4workspace.togglevisibilityobject",icon=("HIDE_OFF", "HIDE_ON")[obj.hide_get()], text="", emboss=False).objName = obj.name
                            row.operator("ue4workspace.removeobject",icon="TRASH", text="", emboss=False).objName = obj.name

                # Static mesh socket
                layout.prop(preferences, "SM_OBJTabSocket", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.SM_OBJTabSocket], emboss=False)
                if preferences.SM_OBJTabSocket:
                    self.drawSocketAttach(context)

                if preferences.devMode:
                    layout.prop(preferences, "SM_OBJTabLOD", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.SM_OBJTabLOD], emboss=False)
                    if preferences.SM_OBJTabLOD:
                        pass
            elif context.active_object is not None and context.active_object.type == "ARMATURE":
                # Character
                # Character socket
                layout.prop(preferences, "CHAR_OBJTabSocket", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.CHAR_OBJTabSocket], emboss=False)
                if preferences.CHAR_OBJTabSocket:
                    self.drawSocketAttach(context)

                if context.active_object.get("UE4RIG") and context.mode != "POSE":
                    # SKELETON PRESET
                    layout.prop(preferences, "CHAR_OBJTabSkeletonPreset", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.CHAR_OBJTabSkeletonPreset], emboss=False)
                    if preferences.CHAR_OBJTabSkeletonPreset:
                        row = layout.row()
                        row.scale_y = 1.5
                        # operator location on UE4WS_Character.py
                        row.operator("ue4workspace.generaterig",icon="CON_ARMATURE", text="Generate Rig")
                        row = layout.row()
                        row.scale_y = 1.5
                        # operator location on UE4WS_Character.py
                        row.operator("ue4workspace.rotatebone",icon="BONE_DATA", text=("Create Preview Orient Bone", "Update Preview Orient Bone")[context.active_object.get("UE4RIGHASTEMPBONE", False)])
                        if context.active_object.get("UE4RIGHASTEMPBONE", False):
                            row = layout.row()
                            row.scale_y = 1.5
                            # operator location on UE4WS_Character.py
                            row.operator("ue4workspace.characterremovetemporarybone",icon="BONE_DATA", text="Remove Preview Orient Bone")
                        # add twist bone
                        if context.mode == "EDIT_ARMATURE" and context.active_bone is not None and (context.active_bone.get("UE4RIGTYPE") in ["LEG_HUMAN", "ARM_HUMAN"] or context.active_bone.parent is not None and context.active_bone.parent.get("UE4RIGTYPE") in ["LEG_HUMAN", "ARM_HUMAN"]) and not "_twist_" in context.active_bone.name:
                            row = layout.row()
                            row.scale_y = 1.5
                            # operator location on UE4WS_Character.py
                            row.operator("ue4workspace.addtwistbone",icon="BONE_DATA", text="Add Twist Bone")
                            if len([child for child in context.active_bone.children if child.name.split("_")[1] == "twist"]) != 0:
                                row = layout.row()
                                row.scale_y = 1.5
                                # operator location on UE4WS_Character.py
                                row.operator("ue4workspace.removetwistbone",icon="BONE_DATA", text="Remove Twist Bone")

                if context.active_object.get("UE4RIGGED") and context.mode == "POSE":
                    # UE4RIGGED POSE
                    poseBones = context.active_object.pose.bones
                    IKBones = [b for b in poseBones if "IK" in b.constraints.keys()]
                    if IKBones:
                        layout.prop(preferences, "CHAR_OBJTabContolRig", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.CHAR_OBJTabContolRig], emboss=False)
                        if preferences.CHAR_OBJTabContolRig:
                            row = layout.row()
                            row.alignment = "RIGHT"
                            row.label(text="IK influence")
                            for b in IKBones:
                                label = b.child.name.replace("TWEAK_", "") if b.child else b.name.replace("TWEAK_", "")
                                IK = b.constraints.get("IK")
                                col = layout.column()
                                row = col.row()
                                split = row.split(factor=0.5)
                                col = split.column()
                                col.alignment = "RIGHT"
                                col.label(text=label)
                                split = split.split()
                                col = split.column()
                                col.prop(IK, "influence", text="")

# OPERATOR

class OP_SMCollisionPicker(Operator):
    bl_idname = "ue4workspace.smcollisionpicker"
    bl_label = "UE4Workspace Operator"
    bl_description = "Create mesh into a custom collision"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        obj = context.scene.SM_CollsionPicker
        if context.mode == "OBJECT":
            if context.active_object is not None and obj is not None and obj.type == "MESH" and not obj.get("isCollision") and context.active_object is not obj:
                return True
        return False

    def execute(self, context):
        obj = context.scene.SM_CollsionPicker
        context.scene.SM_CollsionPicker = None

        obj["isCollision"] = True
        obj.parent = context.active_object
        # Clear local transform
        obj.matrix_parent_inverse = context.active_object.matrix_world.inverted()
        obj.show_wire = True
        obj.display_type = "SOLID"
        obj.color = (0.15, 1.000000, 0, 0.200000)
        context.space_data.shading.color_type = "OBJECT"

        mat = bpy.data.materials.get("MAT_UE4CustomCollision")
        if mat is None:
            mat = bpy.data.materials.new(name="MAT_UE4CustomCollision")
            mat.blend_method = "BLEND"
            mat.use_nodes = True
            mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.15, 1.000000, 0, 1)
            mat.node_tree.nodes["Principled BSDF"].inputs[18].default_value = 0.1
            mat.use_fake_user = True

        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

        oldCollections = obj.users_collection
        collection = bpy.data.collections.get("UE4CustomCollision", False)
        if (not collection):
            collection = bpy.data.collections.new("UE4CustomCollision")
            context.scene.collection.children.link(collection)

        collection.objects.link(obj)
        for coll in oldCollections:
            coll.objects.unlink(obj)

        # # Collision name
        # collName = "UCX_" + context.active_object.name + "_"
        # # Collision filter from scene objects
        # collObjects = [obj for obj in context.scene.objects if obj.name.startswith(collName)]

        # obj.name = collName + ("", "0")[(len(collObjects) + 1) <= 9] + str((len(collObjects) + 1))

        return {"FINISHED"}

class OP_ToggleVisibilityObject(Operator):
    bl_idname = "ue4workspace.togglevisibilityobject"
    bl_label = "UE4Workspace Operator"
    bl_description = "Toggle Visibility Object"
    bl_options = {"UNDO"}

    objName: StringProperty(name="Object name")

    def execute(self, context):
        obj = context.scene.objects[self.objName]
        obj.hide_set(not obj.hide_get())
        return {"FINISHED"}

class OP_RemoveObject(Operator):
    bl_idname = "ue4workspace.removeobject"
    bl_label = "UE4Workspace Operator"
    bl_description = "Remove Object"
    bl_options = {"UNDO"}

    objName: StringProperty(name="Object name")

    def execute(self, context):
        obj = context.scene.objects[self.objName]
        bpy.data.objects.remove(obj, do_unlink=True)
        return {"FINISHED"}

class OP_MakeCollision(Operator):
    bl_idname = "ue4workspace.makecollision"
    bl_label = "Create Collsion From Vertices"
    bl_description = "Create Custom Collision Mesh\nSelect a Mesh > Edit Mode > Select Edge"
    bl_options = {"UNDO", "REGISTER"}

    CollisionName: bpy.props.StringProperty(
        name="Name",
        default="collisionName"
        )

    Size: bpy.props.FloatProperty(
        name="Size",
        min=1,
        default=1.015
        )

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.active_object is not None and context.active_object.mode == "EDIT" and context.active_object.type == "MESH" and (not context.active_object.get("isCollision"))

    def execute(self, context):
        parentObj = context.active_object

        collName = "UCX_" + context.active_object.name + "_"
        index = len([obj for obj in context.scene.objects if obj.name.startswith(collName)])
        collName += ("", "0")[index < 9] + str(index + 1)

        mode = context.active_object.mode
        bpy.ops.object.mode_set(mode="OBJECT")
        selected_verts = [verts for verts in context.active_object.data.vertices if verts.select]
        selected_verts = [verts.co for verts in selected_verts]

        # create collection (UE4CustomCollision) if not exist
        collection = bpy.data.collections.get("UE4CustomCollision", False)
        if (not collection):
            collection = bpy.data.collections.new("UE4CustomCollision")
            context.scene.collection.children.link(collection)

        mesh = bpy.data.meshes.new(self.CollisionName)
        obj = bpy.data.objects.new(self.CollisionName, mesh)
        collection.objects.link(obj)
        mesh.from_pydata(selected_verts, [], [])

        bpy.ops.object.mode_set(mode="OBJECT")
        obj["isCollision"] = True
        obj.parent = parentObj
        obj.location = [0, 0, 0]
        bpy.ops.object.select_all(action="DESELECT")
        obj.show_wire = True
        obj.display_type = "SOLID"
        obj.color = (0.15, 1.000000, 0, 0.200000)
        context.space_data.shading.color_type = "OBJECT"

        # create material (MAT_UE4CustomCollision) if not exist
        mat = bpy.data.materials.get("MAT_UE4CustomCollision")
        if mat is None:
            mat = bpy.data.materials.new(name="MAT_UE4CustomCollision")
            mat.blend_method = "BLEND"
            mat.use_nodes = True
            mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.15, 1.000000, 0, 1)
            mat.node_tree.nodes["Principled BSDF"].inputs[18].default_value = 0.1
            mat.use_fake_user = True

        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

        context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        oldPivot = bpy.context.scene.tool_settings.transform_pivot_point
        bpy.context.scene.tool_settings.transform_pivot_point = "MEDIAN_POINT"
        bpy.ops.transform.resize(value=(self.Size, self.Size, self.Size), orient_type="GLOBAL", orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type="GLOBAL", mirror=True, use_proportional_edit=False, proportional_edit_falloff="SMOOTH", proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
        bpy.ops.mesh.convex_hull()
        # bpy.ops.mesh.delete(type="ONLY_FACE")
        bpy.context.scene.tool_settings.transform_pivot_point = oldPivot

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        context.view_layer.objects.active = parentObj
        parentObj.select_set(state=True)
        bpy.ops.object.mode_set(mode=mode)

        # try:
        #     bpy.ops.ue4workspace.popup("INVOKE_DEFAULT", msg="Make Custom Collision Done")
        # except Exception: 
        #     pass

        return {"FINISHED"}

class OP_AttachObject(Operator):
    bl_idname = "ue4workspace.attachobject"
    bl_label = "Attach Object"
    bl_description = "Attach or Detach Object"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.attachTo is not None

    def execute(self, context):
        obj = context.active_object
        isAttach = not obj.get("isAttachToObject")

        if isAttach:
            # Attach
            constraint = obj.constraints.new(type="CHILD_OF")
            constraint.name = "AttachTo"
            constraint.target = obj.attachTo

            obj["attachLocationOriginal"] = obj.location
            obj["attachRotationOriginal"] = obj.rotation_euler
            obj["isAttachToObject"] = True
            obj.location = [0, 0, 0]
            obj.rotation_euler = [0, 0, 0]

        else:
            # Detach
            constraint = obj.constraints.get("AttachTo")
            if constraint:
                obj.constraints.remove(constraint)
            obj.location = obj["attachLocationOriginal"]
            obj.rotation_euler = obj["attachRotationOriginal"]
            obj.pop("isAttachToObject")
            obj.pop("attachLocationOriginal")
            obj.pop("attachRotationOriginal")

        try:
            bpy.ops.ue4workspace.popup("INVOKE_DEFAULT", msg=("Detach Object Success", "Attach Object Success")[isAttach])
        except Exception: 
            pass

        return {"FINISHED"}

class OP_CreateSocket(Operator):
    bl_idname = "ue4workspace.createsocket"
    bl_label = "Create Socket"
    bl_description = "Create socket for attach object"
    bl_options = {"UNDO", "REGISTER"}

    SocketName: bpy.props.StringProperty(
        name="Name",
        default="socketName"
        )

    Size: bpy.props.FloatProperty(
        name="Size",
        min=0.01,
        default=1
        )

    Rotation: bpy.props.FloatVectorProperty(
        name="Rotation",
        subtype="XYZ",
        unit="ROTATION",
        default=[0, 0, 0]
        )

    # @classmethod
    # def poll(cls, context):
    #     return True

    def execute(self, context):
        parentObj = context.active_object
        isBone = parentObj.type == "ARMATURE" and context.mode in ["POSE", "EDIT_ARMATURE"]
        bone = None
        if isBone:
            caseBone = {
                "EDIT_ARMATURE": context.active_bone,
                "POSE": context.active_pose_bone
            }
            bone = caseBone.get(context.mode)

        # create collection (UE4Socket) if not exist
        collection = bpy.data.collections.get("UE4Socket", False)
        if (not collection):
            collection = bpy.data.collections.new("UE4Socket")
            context.scene.collection.children.link(collection)

        socket = bpy.data.objects.new(name=self.SocketName, object_data=None)
        socket["isSocket"]  = True
        socket.rotation_euler = self.Rotation
        socket.location = context.scene.cursor.location

        socket.empty_display_type = "ARROWS"
        socket.empty_display_size = self.Size
        collection.objects.link(socket)
        socket.parent = parentObj
        if isBone and bone:
            socket.parent_type = "BONE"
            socket.parent_bone = bone.name
            # Clear Local Transform
            socket.matrix_parent_inverse = (parentObj.matrix_world @ Matrix.Translation(bone.tail - bone.head) @ bone.matrix).inverted()
        else:
            socket.parent_type = "OBJECT"
            # Clear Local Transform
            socket.matrix_parent_inverse = parentObj.matrix_world.inverted()

        return {"FINISHED"}

# operator export

Ops = [
    OP_SMCollisionPicker,
    OP_ToggleVisibilityObject,
    OP_RemoveObject,
    OP_MakeCollision,
    OP_AttachObject,
    OP_CreateSocket
]