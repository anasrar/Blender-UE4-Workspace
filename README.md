# Blender Unreal Engine Workspace

![Blender Unreal Engine Workspace](https://user-images.githubusercontent.com/38805204/82159825-4f99b080-98bb-11ea-8124-1437bb877022.png)

Blender **2.8x** add-on for export directly to Unreal Engine 4 with all setting in Blender (inspired by **send to unreal** add-on).

this add-on I make because I don't want to open file explorer and drag and drop to Unreal Engine, so I make this add-on with full control import setting on Blender.

and yeah, I don't really have any future plan. so if you have any suggest just open new issue.

## Main Feature

### Static Mesh

Export for Static Mesh.

![Static Mesh Tab](https://user-images.githubusercontent.com/38805204/84418086-d3d41f00-ac40-11ea-9d5b-6579843b3f3e.png)

### Character

Export for Character (Skeletal Mesh).

![Character Tab](https://user-images.githubusercontent.com/38805204/84418157-efd7c080-ac40-11ea-9be6-004c7b0ae70d.png)

### Animation

Export for Animation.

![Animation](https://user-images.githubusercontent.com/38805204/84418187-ffefa000-ac40-11ea-8303-a76a378a98cc.png)

**Feature and Tutorial** in [wiki page](https://github.com/anasrar/Blender-UE4-Workspace/wiki) or [youtube playlist](https://www.youtube.com/playlist?list=PLolnhUV-ZzXrXx1gJunoknuni8klsy0wH)

![GitHub release (latest by date)](https://img.shields.io/github/v/release/anasrar/Blender-UE4-Workspace?style=flat-square)

## How it works

Unreal Engine 4 allow to remote execute python script, with that we can execute python script import assets (FBX File) to Unreal Engine 4.

![Blender Unreal Engine Workspace FlowChart](https://user-images.githubusercontent.com/38805204/82159805-2d079780-98bb-11ea-92a2-9a9c1628b429.png)

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

Edit > Preferences > Add-ons > Install > Select **UE4Workspace.zip** > Install Add-ons

### Unreal Engine 4

Edit > Plugins > Type "Script" On Search Bar > Enabled **Python Editor Script** Plugin and **Editor Scripting Utilities** > Reset Project

Edit > Project Setting > Plugin|Python > Check **Enable Remote Execution?**

Then you can try to connect your project from blender

## Usage

Press **N** on Blender for open the tab menu.

tested with blender version

- **2.81**
- **2.82**
- **2.83** (make sure export folder path is absolute)
- **2.90 Alpha** (make sure export folder path is absolute)

## Support

You can support me through Gumroad

any donation will be appreciated.

## Contributing

For major changes or features request, please open an issue first to discuss what you would like to change or add.

## Changelog

Any changelog in [wiki page](https://github.com/anasrar/Blender-UE4-Workspace/wiki/Changelog) 

## License

This project is licensed under the **GPL-3.0** License - see the [LICENSE](LICENSE) file for details