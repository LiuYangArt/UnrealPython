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
    else:
        unreal.log_error("No vaild asset selected.")
