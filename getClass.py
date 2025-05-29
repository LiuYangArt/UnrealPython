import unreal

""" 查看所选Asset所属Class的工具 """

sysLib = unreal.SystemLibrary()

EditorSubsys = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
selectedAssets = unreal.EditorUtilityLibrary.get_selected_assets()


def getAssetClass(asset):
    """资产Class名"""
    assetClass = asset.get_class()
    assetClass = sysLib.get_class_display_name(assetClass)
    return assetClass


for asset in selectedAssets:
    if asset is not None:
        assetName = asset.get_name()




        print(assetName + " Class:" + getAssetClass(asset))
        print(asset.get_world())
        do=asset.get_default_object()

        # bp_class_default_object = unreal.get_default_object(asset)
        # print(f"bp_class_default_object: {bp_class_default_object}")
        # print(f"bp_gen_class: {bp_gen_class}")


    else:
        unreal.log_error("No vaild asset selected.")

#test run
for asset in selectedAssets:
    getAssetClass(asset)
