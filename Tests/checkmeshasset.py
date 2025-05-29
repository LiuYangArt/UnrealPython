import unreal
selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
for asset in selected_assets:
    data=asset.get_editor_property('asset_import_data').extract_filenames()
    print(data)