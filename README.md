# Blender Unreal Engine Workspace

![Blender Unreal Engine Workspace](https://anasrar.github.io/Blender-UE4-Workspace/img/blender-unreal-engine-4-workspace-banner.png)

Blender **2.91** *(above)* add-on for export directly to Unreal Engine 4 (**4.26** *above*) with all setting in Blender (inspired by **send to unreal** add-on).

## Feature

Allow you export static mesh, skeletal mesh, and animation with single click directly to Unreal Engine 4 or to FBX file.

![Feature Node](https://anasrar.github.io/Blender-UE4-Workspace/img/feature-node.png "Feature Node")

and yeah, I don't really have any future plan. so if you have any suggest just open new issue.

## Main Feature

### Static Mesh

Export for Static Mesh.

- Export to FBX and Unreal Engine
- Custom collision from vertices
- Custom collision from mesh - ```v.1.2```
- Custom lightmaps
- **[ DEPRECATED - v.2.0 ]** Export profile - ```v.1.2```
- Socket System - ```v.1.3```
- Level of Detail - ```v.1.4```
- Generate Level of Detail - ```v.2.0```
- Import Static Mesh From Unreal Engine - ```v.1.4```

### Skeletal Mesh

Export for Skeletal Mesh.

- Export to FBX and Unreal Engine  
- Modular character
- **[ DEPRECATED - v.2.0 ]** Skeleton preset (Epic skeleton)
- **[ DEPRECATED - v.2.0 ]** Add twist bone for skeleton preset - ```v.1.2```
- **[ DEPRECATED - v.2.0 ]** Generate rig for skeleton preset - ```v.1.2```
- **Move To Another Add-on** : TBA
- **[ DEPRECATED - v.2.0 ]** Export profile - ```v.1.2```
- Socket System - ```v.1.3```
- Copy/Paste Socket Unreal Engine - ```v.2.0```
- Skeletal Mesh Part Manager - ```v.1.4```
- Import Skeletal Mesh From Unreal Engine ```v.1.4```

### Animation

Export for Animation.

- Export to FBX and Unreal Engine - ```v.1.2```  
- **[ DEPRECATED - v.2.0 ]** Export profile - ```v.1.2```
- Import Animation From Unreal Engine ```v.1.4```

### Retarget Animation

**[ DEPRECATED - v.2.0 ]** Retarget Animation to another skeleton - ```v.1.3``` **Experimental**, ```v.1.4``` **Production Ready**

**Move To Another Add-on** : https://github.com/anasrar/ReNim

### Groom Hair [Experimental]
Export Hair Particle From Blender and Import as Groom Hair In Unreal Engine (Not Support Direct Export To Unreal) - ```v.2.0```

Export Setting : [[Groom] unreal engine import setting](https://github.com/anasrar/Blender-UE4-Workspace/issues/22)

### Copy Transform To Unreal Engine Map

Copy Transform Selected Object To Unreal Engine Map - ```v.2.0```

#### Support

- Static Mesh

## Documentation

[documentation page](https://anasrar.github.io/Blender-UE4-Workspace/) or [YouTube playlist](https://www.youtube.com/playlist?list=PLolnhUV-ZzXrXx1gJunoknuni8klsy0wH)

![GitHub release (latest by date)](https://img.shields.io/github/v/release/anasrar/Blender-UE4-Workspace?style=flat-square)

## How it works

Unreal Engine 4 allow to remote execute python script, with that we can execute python script import assets (FBX File) to Unreal Engine 4.

![Blender Unreal Engine Workspace FlowChart](https://anasrar.github.io/Blender-UE4-Workspace/img/flowchart.png "Flowchart")

## Download

You can download from

- Gumroad for latest version
  - https://gumroad.com/l/BlenderUnrealEngineWorkspace

- GitHub for pervious version
  - https://github.com/anasrar/Blender-UE4-Workspace/releases

master branch is **unstable** and **bug fix version**

## Installation

You can watch this video https://www.youtube.com/watch?v=38d5Myrh3ic or simply follow this instruction below.

### Blender

Edit &nbsp; 🡆 &nbsp; Preferences &nbsp; 🡆 &nbsp; Add-ons &nbsp; 🡆 &nbsp; Install &nbsp; 🡆 &nbsp; Select **UE4Workspace.zip** &nbsp; 🡆 &nbsp; Install Add-ons

### Unreal Engine 4

Edit &nbsp; 🡆 &nbsp; Plugins &nbsp; 🡆 &nbsp; Type "Script" On Search Bar &nbsp; 🡆 &nbsp; Enabled **Python Editor Script Plugin** and **Editor Scripting Utilities** &nbsp; 🡆 &nbsp; Reset Project

Edit &nbsp; 🡆 &nbsp; Project Setting &nbsp; 🡆 &nbsp; Plugin &nbsp; 🡆 &nbsp; Python &nbsp; 🡆 &nbsp; Check **Enable Remote Execution**?

Then you can try to connect your project from blender

## Usage

Press **N** on Blender for open the tab menu.

## Compatibility Test

* **Blender 2.91** (make sure export folder path is absolute)

    **Unreal Engine 4.26**

using Blender latest version for better compatibility.

## Support

You can support me through Gumroad

any donation will be appreciated.

## Contributing

For major changes or features request, please open an issue first to discuss what you would like to change or add.

## Changelog

Any changelog in [documentation page](https://anasrar.github.io/Blender-UE4-Workspace/changelog/) 

## License

This project is licensed under the **GPL-3.0** License - see the [LICENSE](LICENSE) file for details