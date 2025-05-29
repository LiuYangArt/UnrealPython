import unreal
import importlib
#Functions



level_subsys = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actor_subsys = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor_subsys = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
layers_subsys = unreal.get_editor_subsystem(unreal.LayersSubsystem)
sys_lib = unreal.SystemLibrary

SM_COMPONENT_CLASS = unreal.StaticMeshComponent.static_class()
CURRENT_LEVEL = editor_subsys.get_editor_world()

selected_actors = actor_subsys.get_selected_level_actors()
all_level_actors = actor_subsys.get_all_level_actors()

def get_materials(actor):
    """
    Get the materials of a static mesh component.
    """
    materials = []
    if isinstance(actor, unreal.StaticMeshActor):
        static_mesh_component = actor.get_component_by_class(SM_COMPONENT_CLASS)
        if static_mesh_component:
            materials = static_mesh_component.get_materials()
    return materials

def get_materials_data(actor):
    """获取StaticMesh完整的材质信息，matIndex,matSlotName,material，输出Dict
    Example:
        materials_data = get_materials_data(actor)
        for index in range(len(materials_data["index"])):
            slot_name = materials_data["slot_name"][index]
            material = materials_data["material"][index]
    """
    materials_data = {"index": [], "slot_name": [], "material": []}
    if isinstance(actor, unreal.StaticMeshActor):
        static_mesh_component = actor.get_component_by_class(SM_COMPONENT_CLASS)
        mat_slot_names = unreal.StaticMeshComponent.get_material_slot_names(static_mesh_component)
        for slot_name in mat_slot_names:
            mat_index = unreal.StaticMeshComponent.get_material_index(
                static_mesh_component, slot_name
            )
            material = unreal.StaticMeshComponent.get_material(static_mesh_component, mat_index)
            materials_data["index"].append(mat_index)
            materials_data["slot_name"].append(slot_name)
            materials_data["material"].append(material)

    return materials_data

def set_sm_materials(static_mesh, materials_data):
    """
    Set the materials of a static mesh asset.
    """
    if isinstance(static_mesh, unreal.StaticMesh):
        print(f"replacing materials for {static_mesh.get_name()}")
        for index in range(len(materials_data["index"])):
            # slot_name = materials_data["slot_name"][index]
            material = materials_data["material"][index]
            unreal.StaticMesh.set_material(static_mesh, index, material)

def apply_material_changes(actors):
    """
    Replace the materials of static mesh components in the selected actors.
    """
    print(f"selected actors: {actors}")


    for actor in actors:
        if isinstance(actor, unreal.StaticMeshActor):
            static_mesh_component = actor.get_component_by_class(SM_COMPONENT_CLASS)
            if static_mesh_component:
                # get materials
                materials_data=get_materials_data(actor)
                #find static mesh asset
                static_mesh_asset = static_mesh_component.get_editor_property("static_mesh") 
                if static_mesh_asset:
                    set_sm_materials(static_mesh_asset, materials_data)



# apply_material_changes(selected_actors)