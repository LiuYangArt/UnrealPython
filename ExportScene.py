import unreal
import os
import json

editor_subsys= unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
level_subsys = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actor_subsys= unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
# unreal.EditorAssetSubsystem.set_dirty_flag

editor_util = unreal.EditorUtilityLibrary
selected_assets = editor_util.get_selected_assets()

def get_default_object(asset) -> unreal.Object:
    bp_gen_class = unreal.load_object(None, asset.generated_class().get_path_name())
    default_object = unreal.get_default_object(bp_gen_class)
    return default_object

def get_blueprint_class(path: str) -> unreal.Class:
    blueprint_asset = unreal.load_asset(path)
    blueprint_class = unreal.load_object(
        None, blueprint_asset.generated_class().get_path_name()
    )
    return blueprint_class

def get_actor_type(actor, class_name):
    """
    获取Actor的更有意义的类型描述。
    
    Args:
        actor: Actor对象
        class_name: Actor的类名
        
    Returns:
        str: 更有意义的类型描述
    """
    # 检查是否是常见的Actor类型
    if class_name == "StaticMeshActor":
        return "StaticMesh"
    elif class_name == "SkeletalMeshActor":
        return "SkeletalMesh"
    elif class_name == "CameraActor":
        return "Camera"
    elif class_name == "DirectionalLight":
        return "DirectionalLight"
    elif class_name == "PointLight":
        return "PointLight"
    elif class_name == "SpotLight":
        return "SpotLight"
    elif class_name == "SkyLight":
        return "SkyLight"
    elif class_name == "ReflectionCapture":
        return "ReflectionCapture"
    elif class_name == "PackedLevelActor":
        return "PackedLevel"
    elif class_name == "LevelInstance":
        return "LevelInstance"
    
    # 检查是否是蓝图Actor
    if "_C" in class_name:
        # 尝试获取父类
        try:
            parent_class = actor.get_class().get_super_class()
            if parent_class:
                parent_name = parent_class.get_name()
                if parent_name == "Actor":
                    # 如果父类是Actor，尝试检查组件
                    return get_actor_type_from_components(actor, class_name)
                else:
                    # 返回父类名称
                    return f"Blueprint ({parent_name})"
        except:
            pass
        
        # 如果无法获取更多信息，至少标记为蓝图
        return "Blueprint"
    
    # 默认返回原始类名
    return class_name

def get_actor_type_from_components(actor, class_name):
    """
    通过检查Actor的组件来确定其类型。
    
    Args:
        actor: Actor对象
        class_name: Actor的类名
        
    Returns:
        str: 基于组件的类型描述
    """
    try:
        # 获取所有组件
        components = actor.get_components_by_class(unreal.SceneComponent)
        
        # 检查是否有StaticMeshComponent
        static_mesh_components = [c for c in components if c.get_class().get_name() == "StaticMeshComponent"]
        if static_mesh_components:
            return "Blueprint (StaticMesh)"
        
        # 检查是否有SkeletalMeshComponent
        skeletal_mesh_components = [c for c in components if c.get_class().get_name() == "SkeletalMeshComponent"]
        if skeletal_mesh_components:
            return "Blueprint (SkeletalMesh)"
        
        # 检查是否有CameraComponent
        camera_components = [c for c in components if c.get_class().get_name() == "CameraComponent"]
        if camera_components:
            return "Blueprint (Camera)"
        
        # 检查是否有LightComponent
        light_components = [c for c in components if "LightComponent" in c.get_class().get_name()]
        if light_components:
            return "Blueprint (Light)"
    except:
        pass
    
    # 如果无法确定具体类型，返回通用蓝图类型
    return "Blueprint"


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

def export_current_level_json(output_path):
    """
    导出当前关卡的世界信息和所有Actor的信息到JSON文件。
    Actor信息包括Transform, 类型, FName和FGuid。
    """
    # current_level = level_subsys.get_current_level()
        # # 从Level获取World对象
        # if current_level:
        #     outer = current_level.get_outer()
        #     if outer:
        #         if outer.get_class().get_name() == "World":
        #             print(f"Current Active Level Asset: {outer}")
        #             return outer


    try:
        # 1. 获取当前编辑器世界和关卡信息
        main_level=level_subsys.get_editor_world()
        current_level = level_subsys.get_current_level()
        print(main_level.get_name())
        print(current_level.get_name())
        if current_level:
            print(current_level)
            level_asset = current_level.get_outer()
        if not current_level:
        #     outer = current_level.get_outer():
            unreal.log_error("无法获取当前编辑器世界。请确保在编辑器中打开了一个关卡。")
            return
        
        level_asset_path = level_asset.get_path_name()
        print (f"当前关卡: {level_asset_path}")
        # 使用关卡名作为文件名（去除路径和前缀，使其更简洁）
        level_name_for_file = unreal.SystemLibrary.get_object_name(level_asset).replace(" ", "_")
        # print (f"关卡名: {level_name_for_file}")
        unreal.log(f"开始导出关卡: {level_asset.get_name()}")
        # 2. 获取当前活动子关卡中的所有Actor
        # 使用get_actors_from_level方法，只获取特定关卡中的Actor
        all_actors = []
        try:
            # 尝试使用get_actors_from_level方法获取当前关卡中的Actor
            all_actors = actor_subsys.get_actors_from_level(current_level)
            unreal.log(f"从当前活动子关卡获取到 {len(all_actors)} 个Actor")
        except Exception as e:
            unreal.log_warning(f"无法使用get_actors_from_level获取Actor: {e}")
            # 如果上面的方法失败，尝试使用替代方法
            all_actors = actor_subsys.get_all_level_actors()
            # 过滤出属于当前关卡的Actor
            filtered_actors = []
            for actor in all_actors:
                if actor and actor.get_level() == current_level:
                    filtered_actors.append(actor)
            all_actors = filtered_actors
            unreal.log(f"通过过滤获取到 {len(all_actors)} 个属于当前关卡的Actor")

        actors_data = []
        # 3. 遍历所有Actor并提取信息
        for actor in all_actors:
            if actor is None: # 避免处理无效的actor
                continue
            actor_info = {}
            
            # Actor FName (对象实例名)
            actor_info["name"] = str(actor.get_actor_label())
            actor_info["fname"] = str(actor.get_fname())
            
            # Actor FGuid (全局唯一ID)
            actor_guid = actor.actor_guid
            actor_info["fguid"] = str(actor_guid)

            # Actor 类型 (类名)
            actor_class = actor.get_class()
            class_name = actor_class.get_name() if actor_class else "Unknown"
            
            # 获取更有意义的类型信息
            actor_type = get_actor_type(actor, class_name)

            actor_info["class"] = class_name  # 保留原始类名
            actor_info["actor_type"] = actor_type  # 添加更有意义的类型描述
            # Actor Transform
            transform = actor.get_actor_transform()
            location = transform.translation # unreal.Vector
            rotation = transform.rotation.rotator() # unreal.Rotator
            scale = transform.scale3d # unreal.Vector
            actor_info["transform"] = {
                "location": {"x": location.x, "y": location.y, "z": location.z},
                "rotation": {"x": rotation.roll,"y": rotation.pitch, "z": rotation.yaw},
                "scale": {"x": scale.x, "y": scale.y, "z": scale.z}
            }
            
            # 特别处理 Packed Level Actor，可以额外记录其引用的关卡资源
            # if isinstance(actor, unreal.PackedLevelActor):
            #     packed_level = actor.get_editor_property('packed_level')
            #     if packed_level:
            #         actor_info["packed_level_asset_path"] = packed_level.get_path_name()
            #     else:
            #         actor_info["packed_level_asset_path"] = "None"
            actors_data.append(actor_info)
        # 4. 组织最终的JSON数据
        level_export_data = {
            "level_path": level_asset_path,
            "level_name_for_file": level_name_for_file,
            "export_path": output_path,
            "actor_count": len(actors_data),
            "actors": actors_data
        }
        # 5. 定义输出路径并写入JSON文件
        # # 通常保存在项目的 Saved 目录下是一个不错的选择
        # output_dir = os.path.join(output_path, "LevelExports")
        # if not os.path.exists(output_dir):
        #     os.makedirs(output_dir)
            # 确保输出目录存在
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            print(f"创建输出目录: {output_path}")
        
        file_path = os.path.join(output_path, f"{level_name_for_file}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(level_export_data, f, indent=4, ensure_ascii=False)
        
        unreal.log(f"成功导出关卡数据到: {file_path}")
    except Exception as e:
        unreal.log_error(f"导出关卡数据时发生错误: {e}")
        import traceback
        unreal.log_error(traceback.format_exc())

def import_json(file_path):
    """     1.从json导入数据
    2.检查json的关卡是否与目前打开的关卡一致
    3.检查json里actor的transform是否与level中actor的transform一致（根据name , fname和guid校验是否同一个actor）
    4.如果json里有新actor，根据guid，创建一个actor，根据transform，设置actor的位置，旋转，缩放
    """

    return
    

# 主执行部分
output_path = r"C:\ue5temp"

export_current_level_json(output_path)
# 获取当前编辑器中的Level资产
level_asset = get_level_asset(type="EDITOR")
if level_asset:
    export_level_to_fbx(level_asset, output_path)
else:
    print("无法获取Level资产")
