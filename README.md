# Blender Unreal Engine Workspace

![Blender Unreal Engine Workspace](https://anasrar.github.io/Blender-UE4-Workspace/img/blender-unreal-engine-4-workspace-banner.png)

Blender **2.8x** *(above)* add-on for export directly to Unreal Engine 4 with all setting in Blender (inspired by **send to unreal** add-on).

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
- Export profile - ```v.1.2```
- Socket System - ```v.1.3```
- Level of Detail - ```v.1.4```
- Import Static Mesh From Unreal Engine ```v.1.4```

### Character

Export for Character (Skeletal Mesh).

- Export to FBX and Unreal Engine  
- Modular character
- Skeleton preset (Epic skeleton)
- Add twist bone for skeleton preset - ```v.1.2```
- Generate rig for skeleton preset - ```v.1.2```
- Export profile - ```v.1.2```
- Socket System (**Not Support Export**) - ```v.1.3```
- Character Part Manager ```v.1.4```
- Import Skeletal Mesh From Unreal Engine ```v.1.4```

### Animation

Export for Animation.

- Export to FBX and Unreal Engine - ```v.1.2```  
- Export profile - ```v.1.2```
- Import Animation From Unreal Engine ```v.1.4```

### Retarget Animation (Experimental)

Retarget Animation to another skeleton - ```v.1.3``` **Experimental**, ```v.1.4``` **Production Ready**

## Documetation

[documentation page](https://anasrar.github.io/Blender-UE4-Workspace/) or [youtube playlist](https://www.youtube.com/playlist?list=PLolnhUV-ZzXrXx1gJunoknuni8klsy0wH)

![GitHub release (latest by date)](https://img.shields.io/github/v/release/anasrar/Blender-UE4-Workspace?style=flat-square)

## How it works

Unreal Engine 4 allow to remote execute python script, with that we can execute python script import assets (FBX File) to Unreal Engine 4.

![Blender Unreal Engine Workspace FlowChart](https://anasrar.github.io/Blender-UE4-Workspace/img/flowchart.png "Flowchart")

## Download

You can download from

- Gumroad for latest version
  - https://gumroad.com/l/BlenderUnrealEngineWorkspace

- Github for pervious version
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

tested with blender version

* **2.81** - **DROP** from version `v.1.3`

* **2.82** - **DROP** from version `v.1.4`

* **2.83** (make sure export folder path is absolute)

* **2.90** (make sure export folder path is absolute)

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