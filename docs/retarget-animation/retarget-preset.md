---
title: Retarget Preset
---

# Retarget Preset

!!! info
    Remember to export all target preset before you remove or disable add-on, otherwise it will disappear forever.

## Import/Export Preset

Import or export retarget preset using JSON file.

!!! info
    You can download example preset on download page (gumroad / github).

## Parent Bones

Parenting bone to another bone.

!!! info
    Naming with `#!python ["_R", "_L", "_RIGHT", "_LEFT"]` in the end of name for mirroring in tweak bones

!!! note ""
    ![Parent Bone](../img/retarget-parent-bones.png "Parent Bone")

## Bone Maps

Mapping bone transform `#!python ["ROTATION", "LOCATION", "SCALE"]` and axis from target to source bone.

!!! info
    Naming with `#!python ["_R", "_L", "_RIGHT", "_LEFT"]` in the end of name for mirroring in tweak bones

!!! note ""
    ![Bone Map](../img/retarget-bone-maps.png "Bone Map")

## Tips and Tricks

### Mapping Bones

Mapping bones workflow.

!!! note ""
    <iframe width="760" height="415" src="https://www.youtube.com/embed/38d5Myrh3ic" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
