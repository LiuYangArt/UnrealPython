import unreal


level_lib = unreal.EditorLevelLibrary()


actor_subsys = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


selected_actors = actor_subsys.get_selected_level_actors()

# def collapse_folder_actors(actors):
#     """ 折叠选中的actors """
#     success_num = 0
#     for actor in actors:
#         if actor.is_a(unreal.Folder):
#             actor.set_editor_property("bExpanded", False)
#             success_num += 1
#     unreal.log("Collapsed {} actors".format(str(success_num)))
#     return success_num

# collapse_folder_actors(selected_actors)