import unreal
import os

editor_subsys= unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
level_subsys = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
editor_util = unreal.EditorUtilityLibrary
selected_assets = editor_util.get_selected_assets()

def export_selected_level_asset_to_fbx(assets,output_path):
    # 确保输出目录存在
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f"创建输出目录: {output_path}")
    
    for asset in assets:
        #检查是否是LevelAsset
        asset_class = asset.get_class().get_name()
        
        if asset_class=="World":
            level_name = asset.get_name()
            
            print (f"正在导出 Level: {level_name}")
            # 设置导出选项
            export_options = unreal.FbxExportOption()
            # 这里可以根据需要设置更多的导出选项，例如：
            export_options.export_source_mesh=True
            export_options.vertex_color = False
            export_options.level_of_detail = False
            export_options.collision = False
            # 导出Level到FBX

            # 构建完整的输出文件路径
            fbx_file_path = os.path.join(output_path, f"{level_name}.fbx")
            print(f"导出路径: {fbx_file_path}")
            
            # 导出Level到FBX
            export_task = unreal.AssetExportTask()
            export_task.object = asset  # 获取Level的包对象
            export_task.filename = fbx_file_path
            export_task.automated = True
            export_task.prompt = False
            export_task.options = export_options
            
            # 使用正确的导出器
            fbx_exporter = unreal.LevelExporterFBX()
            export_task.exporter = fbx_exporter
            
            # 执行导出任务
            result = fbx_exporter.run_asset_export_task(export_task)
            
            # 检查导出结果
            if result:
                print(f"✓ 成功导出 Level: {level_name} 到 {fbx_file_path}")
                # 验证文件是否存在
                if os.path.exists(fbx_file_path):
                    file_size = os.path.getsize(fbx_file_path)
                    print(f"  文件大小: {file_size} bytes")
                else:
                    print(f"  警告: 导出报告成功但文件不存在!")
            else:
                print(f"✗ 导出 Level 失败: {level_name}")
                print(f"  请检查是否有权限写入目标路径")

def export_current_level_to_fbx(output_path):
    """
    导出当前打开的Level到指定的FBX文件路径。
    Args:
        output_path (str): 导出的FBX文件的完整路径，包括文件名和扩展名（.fbx）。
    Returns:
        str: 成功导出后返回FBX文件的完整路径，否则返回None。
    """
    
    # 确保输出目录存在
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f"创建输出目录: {output_path}")

    # 获取当前打开的Level
    current_level = editor_subsys.get_editor_world()
    if current_level is None:
        unreal.log_error("没有打开的Level可以导出。")
        return None
    
    level_name = current_level.get_name()
    print(f"当前 Level: {level_name}")

    # 设置导出选项
    export_options = unreal.FbxExportOption()
    # 这里可以根据需要设置更多的导出选项，例如：
    export_options.export_source_mesh=True
    export_options.vertex_color = False
    export_options.level_of_detail = False
    export_options.collision = False
    
    
    # 构建完整的输出文件路径
    fbx_file_path = os.path.join(output_path, f"{level_name}.fbx")
    print(f"导出路径: {fbx_file_path}")
    
    # 导出Level到FBX
    export_task = unreal.AssetExportTask()
    export_task.object = current_level  # 直接使用World对象，不要使用get_outer()
    export_task.filename = fbx_file_path
    export_task.automated = True
    export_task.prompt = False
    export_task.options = export_options
    
    # 使用正确的导出器
    fbx_exporter = unreal.LevelExporterFBX()
    export_task.exporter = fbx_exporter
    
    # 执行导出任务
    result = fbx_exporter.run_asset_export_task(export_task)
    
    # 检查导出结果
    if result:
        print(f"✓ 成功导出 Level: {level_name} 到 {fbx_file_path}")
        # 验证文件是否存在
        if os.path.exists(fbx_file_path):
            file_size = os.path.getsize(fbx_file_path)
            print(f"  文件大小: {file_size} bytes")
            return fbx_file_path
        else:
            print(f"  警告: 导出报告成功但文件不存在!")
            return None
    else:
        print(f"✗ 导出 Level 失败: {level_name}")
        return None


def get_level_asset(type="EDITOR"):
    """ 获取Level Asset
    type='EDITOR' 时输出当前打开的Level的World对象
    type='CONTENTBROWSER' 时输出在Content Browser中选中的Level
    """
    if type == "EDITOR":
        # 获取当前打开的Level
        current_level = level_subsys.get_current_level()
        # 从Level获取World对象
        if current_level:
            outer = current_level.get_outer()
            if outer:
                if outer.get_class().get_name() == "World":
                    print(f"Current Active Level Asset: {outer}")
                    return outer

        
    if type == "CONTENTBROWSER":
        level_assets=[]
        editor_util = unreal.EditorUtilityLibrary
        selected_assets = editor_util.get_selected_assets()
        for asset in selected_assets:
        #检查是否是LevelAsset
            asset_class = asset.get_class().get_name()
            if asset_class=="World":
                level_assets.append(asset)
        return level_assets


def export_level_to_fbx(level_asset,output_path):
    """
    导出Level到指定的FBX文件路径。
    Args:
        level_asset: World对象或Level对象
        output_path (str): 导出的FBX文件的完整路径，包括文件名和扩展名（.fbx）。
    Returns:
        str: 成功导出后返回FBX文件的完整路径，否则返回None。
    """
    
    # 确保输出目录存在
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f"创建输出目录: {output_path}")

    if level_asset is None:
        print("错误: level_asset 为 None")
        return None

    current_level = level_asset
    print(f"Export object: {current_level}")
    print(f"Export object class: {current_level.get_class().get_name()}")
    
    # 如果传入的是Level对象，尝试获取World对象
    if current_level.get_class().get_name() == "Level":
        print("检测到Level对象，尝试获取对应的World对象...")
        world = get_level_asset(type="EDITOR")
        if world:
            current_level = world
            print(f"使用World对象: {current_level}")
        else:
            print("警告: 无法获取World对象，将尝试使用Level对象导出")
    
    level_name = current_level.get_name()

    # 设置导出选项
    export_options = unreal.FbxExportOption()
    # 这里可以根据需要设置更多的导出选项，例如：
    export_options.export_source_mesh=True
    export_options.vertex_color = False
    export_options.level_of_detail = False
    export_options.collision = False
    
    
    # 构建完整的输出文件路径
    fbx_file_path = os.path.join(output_path, f"{level_name}.fbx")
    print(f"导出路径: {fbx_file_path}")
    
    # 导出Level到FBX
    export_task = unreal.AssetExportTask()
    export_task.object = current_level
    export_task.filename = fbx_file_path
    export_task.automated = True
    export_task.prompt = False
    export_task.options = export_options
    
    # 使用正确的导出器
    fbx_exporter = unreal.LevelExporterFBX()
    export_task.exporter = fbx_exporter
    
    # 执行导出任务
    result = fbx_exporter.run_asset_export_task(export_task)
    
    # 检查导出结果
    if result:
        print(f"✓ 成功导出 Level: {level_name} 到 {fbx_file_path}")
        # 验证文件是否存在
        if os.path.exists(fbx_file_path):
            file_size = os.path.getsize(fbx_file_path)
            print(f"  文件大小: {file_size} bytes")
            return fbx_file_path
        else:
            print(f"  警告: 导出报告成功但文件不存在!")
            return None
    else:
        print(f"✗ 导出 Level 失败: {level_name}")
        return None


# 主执行部分
output_path = r"C:\ue5temp"
print("="*50)
print("开始导出 Level 到 FBX")
print(f"输出路径: {output_path}")
print("="*50)

# 获取当前编辑器中的Level资产
level_asset = get_level_asset(type="EDITOR")

if level_asset:
    export_level_to_fbx(level_asset, output_path)
else:
    print("无法获取Level资产")
