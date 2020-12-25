# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "UE4Workspace",
    "author" : "Anas Rin",
    "description" : "Addon For UE4 Workspace",
    "blender" : (2, 91, 0),
    "version" : (2, 0, 0),
    "location" : "3D View > Tools",
    "warning" : "",
    "wiki_url": "https://github.com/anasrar/Blender-UE4-Workspace", # 2.82 below
    "doc_url": "https://github.com/anasrar/Blender-UE4-Workspace", # 2.83 above
    "tracker_url": "https://github.com/anasrar/Blender-UE4-Workspace/issues",
    "support": "COMMUNITY",
    "category" : "Workspace"
}

import bpy

from . utils import operator
from . preferences import main as preferences_main
from . export_option import main as export_option_main
from . import_asset import main as import_asset_main
from . object import main as object_main
from . static_mesh import main as static_mesh_main
from . skeletal_mesh import main as skeletal_mesh_main
from . animation import main as animation_main
from . groom import main as groom_main
from . credit import main as credit_main
from . copy_to_unreal_engine import main as copy_to_unreal_engine_main

list_class_to_register = [
    operator,
    preferences_main,
    export_option_main,
    import_asset_main,
    object_main,
    static_mesh_main,
    skeletal_mesh_main,
    animation_main,
    groom_main,
    credit_main,
    copy_to_unreal_engine_main
]

def register():
    for x in list_class_to_register:
        x.register()

def unregister():
    for x in list_class_to_register[::-1]:
        x.unregister()