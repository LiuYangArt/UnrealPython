import unreal



level_lib = unreal.EditorLevelLibrary()

actor_subsys = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

selected_actors = actor_subsys.get_selected_level_actors()





def rename_actors(actors, text, new_text):

    """重命名选中的actors"""

    success_num = 0

    for actor in actors:

        actor_name = actor.get_actor_label()

        actor_new_name = actor_name.replace(text, new_text)

        actor.set_actor_label(actor_new_name)

        print(actor_name + "==>" + actor_new_name)

        success_num += 1

    unreal.log("Renamed {} actors".format(str(success_num)))

    return success_num



