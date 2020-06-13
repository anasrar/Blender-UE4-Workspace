import bpy
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
            ),
        "resetVariable": True
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
        elif context.active_object is not None and context.active_object.type == "ARMATURE" and context.active_object.get("UE4RIG") and context.mode != "POSE":
            return True
        elif context.active_object is not None and context.active_object.type == "ARMATURE" and context.active_object.get("UE4RIGGED") and context.mode == "POSE":
            return True
        return False 

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons[__package__].preferences

        if context.active_object is not None:
            modifiersTypeList = [mod.type for mod in context.active_object.modifiers]

            if context.active_object is not None and context.active_object.type == "MESH" and not "ARMATURE" in modifiersTypeList:

                layout.prop(preferences, "SM_OBJTabCustomCollision", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.SM_OBJTabCustomCollision], emboss=False)
                if preferences.SM_OBJTabCustomCollision:
                    row = layout.row()
                    row.scale_y = 1.5
                    row.operator("wm.url_open",icon="INFO", text="FBX Static Mesh Pipeline").url="https://docs.unrealengine.com/en-US/Engine/Content/Importing/FBX/StaticMeshes/#collision"
                    # Add Collision Button
                    row = layout.row()
                    row.scale_y = 1.5
                    row.operator("ue4workspace.makecollision",icon="OUTLINER_OB_MESH", text="Create Collision")

                    if context.mode == "OBJECT" and context.active_object is not None and not context.active_object.name.startswith("UCX_"):
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

                    collisionObjects = [obj for obj in context.scene.objects if obj.type == "MESH" and obj.name.startswith("UCX_" + context.active_object.name)]

                    if collisionObjects:
                        box = layout.box()
                        for obj in collisionObjects:
                            col = box.column()
                            row = col.row()
                            split = row.split(factor=0.6)
                            col = split.column()
                            col.label(text=obj.name)
                            split = split.split()
                            row = split.row()
                            row.alignment = "RIGHT"
                            row.operator("ue4workspace.togglevisibilityobject",icon=("HIDE_OFF", "HIDE_ON")[obj.hide_get()], text="", emboss=False).objName = obj.name
                            row.operator("ue4workspace.removeobject",icon="TRASH", text="", emboss=False).objName = obj.name

                if preferences.devMode:
                    layout.prop(preferences, "SM_OBJTabLOD", icon=("TRIA_RIGHT", "TRIA_DOWN")[preferences.SM_OBJTabLOD], emboss=False)
                    if preferences.SM_OBJTabLOD:
                        pass
            elif context.active_object is not None and context.active_object.type == "ARMATURE" and context.active_object.get("UE4RIG") and context.mode != "POSE":
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
            elif context.active_object is not None and context.active_object.type == "ARMATURE" and context.active_object.get("UE4RIGGED") and context.mode == "POSE":
                # UE4RIGGED POSE
                poseBones = context.active_object.pose.bones
                IKBones = [b for b in poseBones if "IK" in b.constraints.keys()]
                if IKBones:
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
            if context.active_object is not None and obj is not None and obj.type == "MESH" and not obj.name.startswith("UCX_") and context.active_object is not obj:
                return True
        return False

    def execute(self, context):
        obj = context.scene.SM_CollsionPicker
        context.scene.SM_CollsionPicker = None

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
        collection = bpy.data.collections.get("UE4CustomCollsion", False)
        if (not collection):
            collection = bpy.data.collections.new("UE4CustomCollsion")
            context.scene.collection.children.link(collection)

        collection.objects.link(obj)
        for coll in oldCollections:
            coll.objects.unlink(obj)

        # Collision name
        collName = "UCX_" + context.active_object.name + "_"
        # Collision filter from scene objects
        collObjects = [obj for obj in context.scene.objects if obj.name.startswith(collName)]

        obj.name = collName + ("", "0")[(len(collObjects) + 1) <= 9] + str((len(collObjects) + 1))

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

    Size: bpy.props.FloatProperty(
        name="Size",
        min=1,
        default=1.015
        )

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.active_object is not None and context.active_object.mode == "EDIT" and context.active_object.type == "MESH" and (not context.active_object.name.startswith("UCX_"))

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
        collection = bpy.data.collections.get("UE4CustomCollsion", False)
        if (not collection):
            collection = bpy.data.collections.new("UE4CustomCollsion")
            context.scene.collection.children.link(collection)

        mesh = bpy.data.meshes.new(collName)
        obj = bpy.data.objects.new(collName,mesh)
        collection.objects.link(obj)
        mesh.from_pydata(selected_verts, [], [])

        bpy.ops.object.mode_set(mode="OBJECT")
        obj.location = parentObj.location
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

# operator export

Ops = [
    OP_SMCollisionPicker,
    OP_ToggleVisibilityObject,
    OP_RemoveObject,
    OP_MakeCollision
]