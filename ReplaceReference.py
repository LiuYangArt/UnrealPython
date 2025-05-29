import unreal
from CommonFunctions import get_asset_dir

selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
editor_lib = unreal.EditorAssetLibrary
asset_subsys = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
new_dir_path = "/Game/Developers/LiuYang/NewMesh/"

def replace_ref(assets):
    for asset in assets:
        if isinstance(asset,unreal.Object):
            asset_path = asset.get_path_name()
            asset_old = editor_lib.load_asset(asset_path)
            asset_name = asset.get_name()
            print("Asset")
            print([asset_old])


            asset_new_path = new_dir_path + asset_name + "." + asset_name
            if editor_lib.does_asset_exist(asset_new_path):
                print("Asset exists in the new directory")

                asset_new = editor_lib.load_asset(asset_new_path)

                print("New Asset")
                print(asset_new)
                # replace=asset_subsys.consolidate_assets(assets_to_consolidate=[asset_new],asset_to_consolidate_to=asset)
                replace = editor_lib.consolidate_assets(asset_to_consolidate_to=asset_new,assets_to_consolidate=[asset_old])
                print("done")
                print(replace)
            else:
                print("no target asset")
def check_ref(asset):
    if isinstance(asset,unreal.Object):
        asset_path = asset.get_path_name()
        asset_ref = editor_lib.find_package_referencers_for_asset(asset_path)
        print("Asset_Reference")
        print(asset_ref)

check_ref(selected_assets[0])

replace_ref(selected_assets)