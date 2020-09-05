---
title: Tips and Tricks Retarget
---

# Tips and Tricks Retarget

## Retarget Mixamo Mannequin To Unreal Mannequin

Retarget any mixamo animation base on mixamo mannequin to unreal mannequin (root / in-place).

!!! note ""
    Import mixamo mannequin animation and unreal mannequin &nbsp; 🡆 &nbsp; duplicate IK foot bone and rename it to "**root**" &nbsp; 🡆 &nbsp; parent IK (foot and hand) and pelvis to root bone &nbsp; 🡆 &nbsp; set pose &nbsp; 🡆 &nbsp; BIND

!!! note ""
    <iframe width="760" height="415" src="https://www.youtube.com/embed/38d5Myrh3ic" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## Retarget Using IK Bone

You can use IK control bone for retargeting, to do that you have to parent IK control bone to bone that mimic the IK bone.

!!! note "IK Leg Retarget"
    <iframe width="760" height="415" src="https://www.youtube.com/embed/38d5Myrh3ic" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## Export Animation Without Bake

Because bake action operator is not really optimize and quite painful, you can do this trick.

!!! note ""
    Create new action on target armature &nbsp; 🡆 &nbsp; Keyframe one bone &nbsp; 🡆 &nbsp; Unassign the action from target armature &nbsp; 🡆 &nbsp; Export the action &nbsp; 🡆 &nbsp; If you export to unreal you can import the animation asset to blender or import regular FBX

!!! note ""
    <iframe width="760" height="415" src="https://www.youtube.com/embed/38d5Myrh3ic" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
