import math

class BuildStringMap:
    @classmethod
    def generate_string(cls, objects = []):
        string_actors = ''

        for obj in objects:
          if obj.type == 'MESH':
            string_actors += cls.static_mesh(obj, objects)

        string_clipboard ='''Begin Map
   Begin Level
{}
   End Level
Begin Surface
End Surface
End Map'''.format(string_actors)

        return string_clipboard

    @classmethod
    def static_mesh(cls, obj = None, objects = []):
        obj_location, obj_rotation_quaternion, obj_scale = obj.matrix_world.decompose()
        obj_location = obj_location * 100
        obj_location.y = obj_location.y*-1
        obj_rotation_euler = obj_rotation_quaternion.to_euler('XYZ')

        template_string = '''
      Begin Actor Class=/Script/Engine.StaticMeshActor Name={actor_name} Archetype=/Script/Engine.StaticMeshActor\'/Script/Engine.Default__StaticMeshActor\''''.format(actor_name=obj.name)

        if obj.parent is not None and obj.parent.type == 'MESH' and obj.parent in objects:
            template_string += ' ParentActor={}'.format(obj.parent.name)

        template_string += '''
         Begin Object Class=/Script/Engine.StaticMeshComponent Name="StaticMeshComponent0" Archetype=StaticMeshComponent'/Script/Engine.Default__StaticMeshActor:StaticMeshComponent0'
         End Object
         Begin Object Name="StaticMeshComponent0"
            StaticMesh=StaticMesh'"/Engine/BasicShapes/Cube.Cube"'
            RelativeLocation=(X={location.x},Y={location.y},Z={location.z})
            RelativeRotation=(Pitch={rotation[y]},Yaw={rotation[z]},Roll={rotation[x]})
            RelativeScale3D=(X={scale.x},Y={scale.y},Z={scale.z})
         End Object
         StaticMeshComponent="StaticMeshComponent0"
         RootComponent="StaticMeshComponent0"
         ActorLabel="{actor_label}"
      End Actor
'''.format(actor_label=obj.name, location=obj_location, rotation = { 'x': math.degrees(obj_rotation_euler.x), 'y': math.degrees(obj_rotation_euler.y * -1), 'z': math.degrees(obj_rotation_euler.z * -1) }, scale=obj_scale)

        return template_string