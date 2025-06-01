import unreal
bp_editor_lib = unreal.BlueprintEditorLibrary
asset_lib=unreal.EditorAssetLibrary
editor_util = unreal.EditorUtilityLibrary
sys_lib = unreal.SystemLibrary
actor_subsys = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

selected_actors = actor_subsys.get_selected_level_actors()
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

def get_level_instance_from_pla(target_actor):
    """
    对于在关卡中选中的Packed Level Actor，找到对应的Level Instance
    """

    # Check if the actor has a Level Instance Component
    has_level_instance = False
    components = target_actor.get_components_by_class(unreal.SceneComponent)
    for component in components:
        component_class = component.get_class()
        if "LevelInstance" in component_class.get_name():
            has_level_instance = True
            break
        
    # Add actor to packed_level_actors if it matches any of the criteria
    if has_level_instance:
        level_instance = bp_editor_lib.get_editor_property(target_actor, name="WorldAsset")
        return level_instance
        # packed_level_actors.append(target_actor)

    else:
        unreal.log_warning(f"Actor {target_actor.get_name()} does not have a Level Instance")
        return None



def replace_pla_with_level_instance(target_actor):
    """
    将关卡中的Packed Level Actor替换为对应的Level Instance
    """
    #检查是否有对应的Level Instance
    level_instance = get_level_instance_from_pla(target_actor)
    if not level_instance:
        return None
    
    location = target_actor.get_actor_location()
    rotation = target_actor.get_actor_rotation()
    unreal.log(f"Replacing {target_actor.get_actor_label()} with Level Instance {level_instance.get_name()}")
    actor_subsys.destroy_actor(target_actor)
    # Spawn the LevelInstance actor at the same location/rotation
    new_actor = actor_subsys.spawn_actor_from_object(level_instance, location, rotation)
    # new_actors.append(new_actor)
    return new_actor
                

# selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
def create_pla_from_level_instance(target_asset):
    """ 从Level Instance创建新的PLA """
    # 检查asset是否为Level Instance类型
    if not target_asset.get_class().get_name().endswith("World"):
        unreal.log_warning(f"Asset {name} 不是Level Instance，已跳过。")
        return None
    
    name = target_asset.get_name()
    asset_path_name = target_asset.get_path_name()
    target_dir = unreal.Paths.get_path(asset_path_name)
    target_name = "BPP_" + name

    # Create a Blueprint factory
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.PackedLevelActor)  # Set the parent class

    # Get the asset tools
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    # Create the Blueprint asset
    blueprint = asset_tools.create_asset(target_name, target_dir, None, factory)
    bp_actor = get_default_object(blueprint)
    bp_editor_lib.set_editor_property(bp_actor, name="WorldAsset", value=target_asset)
    return bp_actor

def copy_asset_to_dir(asset, target_dir):
    """
    复制目标asset到指定的新路径，返回新asset的路径
    """
    asset_path = asset.get_path_name()
    asset_name = asset.get_name()
    target_dir = unreal.Paths.normalize_directory_name(target_dir)
    new_asset_path = f"{target_dir}/{asset_name}"
    print(f"copy {asset_path} to {new_asset_path}")
    duplicated_asset = asset_lib.duplicate_asset(asset_path, new_asset_path)
    if duplicated_asset:
        new_asset = duplicated_asset
        unreal.log(f"Asset {asset_name} copied to {new_asset.get_path_name()}")
        return new_asset.get_path_name()
    else:
        unreal.log_warning(f"Failed to copy asset {asset_name} to {target_dir}")
        return None



# 在UE WidgetBP中调用以下Functions

def duplicate_pla_actors(target_actors, target_dir) -> list:
    """
    复制关卡中选中的PLA到目标路径

    Parameters:
    - target_actors (list): A list of PLA actors to duplicate.
    - target_dir (str): The directory to copy the assets to.

    Returns:
    - list: A list of paths to the copied assets.
    """


    #TODO：添加slow task
    count=0
    for actor in target_actors:
        level_instance = get_level_instance_from_pla(actor)
        if level_instance:
            new_level_instance=copy_asset_to_dir(level_instance, target_dir)
            create_pla_from_level_instance(new_level_instance)
            count+=1

    unreal.log_("成功复制了" + str(count) + "个PLA资产")

def duplicate_pla_assets(assets,target_dir):
    """复制ContentBrowser中选中的PLA资产"""
    level_instances=[]
    count=0
    for asset in assets:
        is_level_instance = False
        #检查类型， 是pla还是level instance， 如果是level instance， 直接复制， 如果是pla， 先从pla得到对应的level instance
        if asset.get_class().get_name().endswith("World"):
            is_level_instance = True
            level_instance=asset
        else:
            if asset.get_class().get_name() == "Blueprint":
                #检查parent class 的类型
                bp=get_default_object(asset)
                if isinstance(bp,unreal.PackedLevelActor):
                    level_instance=get_level_instance_from_pla(asset)
        
        if level_instance is not None:
            if level_instance not in level_instances:
                level_instances.append(level_instance)
    if len(level_instances) > 0:
        for instance in level_instances:
            new_level_instance=copy_asset_to_dir(level_instance, target_dir)
            create_pla_from_level_instance(new_level_instance)
            count+=1


def batch_replace_pla_to_level_instance(actors):
    """批量将PLA资产转为LevelInstance资产"""
    count = 0
    for actor in actors:
        new_actor=replace_pla_with_level_instance(actor)
        if new_actor:
            count+=1
    unreal.log_("成功替换了" + str(count) + "个Packed Level Actors为LevelInstance资产")



#Test Function
duplicate_pla_assets(selected_assets)
# get_level_instance_from_pla(selected_actors[0])
# replace_pla_with_level_instance(selected_actors[0])
# copy_asset_to_dir(selected_assets[0], "/Game/Blueprints/")
