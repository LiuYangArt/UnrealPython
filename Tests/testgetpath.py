from webbrowser import get

from pkg_resources import normalize_path
import unreal
from pathlib import Path
from CommonFunctions import get_asset_dir

# selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
# selected_folders = unreal.EditorUtilityLibrary.get_selected_folder_paths()
string_lib = unreal.StringLibrary()
editor_lib = unreal.EditorUtilityLibrary

def get_selected_dir():
    selected_assets = editor_lib .get_selected_assets()
    selected_folders_path = editor_lib .get_selected_folder_paths()

    if len(selected_assets) != 0:
        asset = selected_assets[0]
        asset_dir_path = get_asset_dir(asset)
    elif len(selected_folders_path) != 0:
        folder_path = selected_folders_path[0]
        asset_dir_path = string_lib.split(folder_path,"/All")[1]
    else: 
        asset_dir_path = editor_lib .get_current_content_browser_path()

    return asset_dir_path

print(get_selected_dir())

# dir_name = unreal.Paths.normalize_directory_name
# relative_path = unreal.Paths.make_path_relative_to

# get_dir = unreal.Paths.get_path

# string_lib = unreal.StringLibrary()


# def get_asset_path(asset):
#     """资产完整路径，剔除资产本身文件名"""
#     asset_path_name = asset.get_path_name()
#     asset_dir = str(Path(asset_path_name).parent)
#     asset_dirx = dir_name(asset_dir)

 
#     print(asset_path_name)
#     print(asset_dir)
#     print(asset_dirx)
#     print("getdir:" + get_dir(asset_path_name))


# gg=get_asset_dir(selected_asset[0])
# print(gg)
    
# mesh_dir_input = "/Meshes/"
# print("aa" + dir_name(mesh_dir_input))

# unreal python select a folder and get the path of the folder
