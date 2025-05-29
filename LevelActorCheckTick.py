import unreal


level_lib = unreal.EditorLevelLibrary()
level_subsys = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actor_subsys = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor_subsys = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
layers_subsys = unreal.get_editor_subsystem(unreal.LayersSubsystem)
subobj_subsys = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
sys_lib = unreal.SystemLibrary()

paths = unreal.Paths

SM_COMPONENT_CLASS = unreal.StaticMeshComponent.static_class()
CURRENT_LEVEL = editor_subsys.get_editor_world()
LOG_DIR = paths.project_log_dir()

selected_actors = actor_subsys.get_selected_level_actors()
all_level_actors = actor_subsys.get_all_level_actors()

LAYER_TICK="Debug_EventTick_Enabled"




def filter_actors_tick(actors):
        """筛选出所有的StaticMeshActor"""

        filtered_actors = []

        for actor in actors:
            #检查是否Blueprint，不检查的话会包含UE自带组件“
            is_bp=False
            actor_class = actor.get_class()
            if "Blueprint" in str(actor_class):
                is_bp = True

            if is_bp:
                layers_subsys.remove_actor_from_layer(actor, LAYER_TICK) #清理上次检查添加的层
                has_tick=unreal.Actor.is_actor_tick_enabled(actor)
                # child_actors=actor.get_all_child_actors()
                # for child in child_actors:
                #     has_tick=unreal.Actor.is_actor_tick_enabled(child)

                if has_tick:
                    filtered_actors.append(actor)


        return filtered_actors

def check_bp_event_tick(actors):
    """检查蓝图是否使用EventTick"""
    
    current_level_path = CURRENT_LEVEL.get_path_name()
    current_level_path = current_level_path.split(".")[0]
    log_header = (
        "BP Actor Event Tick 检查：\n"
        + "蓝图使用 Event Tick会有CPU开销，如非必须请关闭或使用别的实现方式\n"
    )

    log_header += f"\nCheckLevel: {current_level_path}\n\n"
    tick_actors = filter_actors_tick(actors)

    log_summary = (f"关卡中有 {len(tick_actors)} 个蓝图开启了 EventTick\n\n")
    log_message = ""

    task_name = "Checking Level Assets： "
    asset_count = len(tick_actors)
    current_step = 0


    # blueprints=get_blueprint_assets(actors)
    # print(blueprints)
    # for blueprint in blueprints:
    #     components = get_blueprint_components(blueprint)
    #     print(blueprint)
    #     print(components)
    #     print("hi")



    if len(tick_actors)>0:
        





        with unreal.ScopedSlowTask(asset_count, task_name) as slowTask:
            
            slowTask.make_dialog(True)

            for actor in tick_actors:
                current_step += 1
                actor_label = actor.get_actor_label()


                log_message += actor_label + "\n"
                layers_subsys.add_actor_to_layer(actor, LAYER_TICK)

                

    check_log = log_header +log_summary + log_message
    check_log = str(check_log)
    actor_subsys.set_selected_level_actors(tick_actors)

    return check_log


def check_level_actors_event_tick(actors):
    check_log = check_bp_event_tick(actors=actors)
    print(check_log)



#测试功能

check_level_actors_event_tick(actors=all_level_actors)
