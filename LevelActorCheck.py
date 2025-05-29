import unreal
import os
import time


level_lib = unreal.EditorLevelLibrary()
level_subsys = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actor_subsys = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor_subsys = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
layers_subsys = unreal.get_editor_subsystem(unreal.LayersSubsystem)
paths = unreal.Paths

SM_COMPONENT_CLASS = unreal.StaticMeshComponent.static_class()
CURRENT_LEVEL = editor_subsys.get_editor_world()
LOG_DIR = paths.project_log_dir()

selected_actors = actor_subsys.get_selected_level_actors()
all_level_actors = actor_subsys.get_all_level_actors()

DEBUG_LAYER = "Debug_BadPerformance_Mat_Settings"

class LevelActor:
    @staticmethod
    def filter_staticmesh_components(actors):
        filtered_components = []
        for actor in actors:
            # actor_label = actor.get_actor_label()
            staticmesh_components = actor.get_components_by_class(SM_COMPONENT_CLASS)
            if staticmesh_components:
                for component in staticmesh_components:
                    if component not in filtered_components:
                        filtered_components.append(component)

        return filtered_components

    def get_sm_components(actor):
        staticmesh_components = unreal.Actor.get_components_by_class(
            actor, SM_COMPONENT_CLASS
        )
        return staticmesh_components

    def filter_sm_actors(actors):
        """筛选出所有的StaticMeshActor"""
        filtered_actors = []
        for actor in actors:
            staticmesh_components = actor.get_components_by_class(SM_COMPONENT_CLASS)
            if staticmesh_components:
                filtered_actors.append(actor)
        return filtered_actors

    def check_sm_shadow_option(staticmesh_component):
        """检查模型的投影设置是否开启"""
        cast_shadow = staticmesh_component.get_editor_property("cast_shadow")
        return cast_shadow

    def check_nanite_settings(staticmesh_component):
        """检查模型的nanite设置是否开启"""
        staticmesh = staticmesh_component.get_editor_property("static_mesh")
        nanite_settings = "No StaticMesh"
        if staticmesh:
            nanite_settings = staticmesh.get_editor_property("nanite_settings")
            nanite_settings = nanite_settings.enabled
        return nanite_settings


class Materials:
    @staticmethod
    def get_all_mats(staticmesh_component):
        materials = []
        # if staticmesh_component:
        if staticmesh_component.get_class() == SM_COMPONENT_CLASS:
            materials = staticmesh_component.get_materials()
        return materials

    def check_nanite_mat(staticmesh_component):
        """检查模型的材质类型是否能够开启nanite"""
        # is_nanite_material = False
        nanite_blende_modes = ["OPAQUE", "MASKED"]
        mat_blend_modes = []
        good_mat_count = 0
        bad_mats = {}
        mats = {}
        materials = Materials.get_all_mats(staticmesh_component)

        if len(materials) > 0:
            # iterate over materials and collect blend mode info
            for material in materials:
                mat_blend_mode = None
                if isinstance(material, unreal.Material):
                    mat_blend_mode = unreal.Material.get_blend_mode(material)
                    mat_blend_modes.append(mat_blend_mode)
                if isinstance(material, unreal.MaterialInstanceConstant):
                    # parentMaterial = material.get_base_material()
                    # mat_blend_mode = parentMaterial.get_editor_property("blend_mode")
                    mat_blend_mode=unreal.MaterialInstanceConstant.get_blend_mode(material)
                    mat_blend_modes.append(mat_blend_mode)
                # check to see if valid blend mode in material blend mode
                if material is not None and mat_blend_mode is not None:
                    mat_name = material.get_name()
                    if material not in mats:
                        mats[mat_name] = mat_blend_mode

            for mat in mats: # 检查材质的blend mode是否符合要求
                is_good_mat = False
                if "Decal" in mat: #跳过decal材质
                    is_good_mat = True
                    good_mat_count += 1
                else:
                    for vbm in nanite_blende_modes:
                        if vbm in str(mats[mat]): #is good mat
                            good_mat_count += 1
                            is_good_mat = True
                    if is_good_mat == False:
                        # print(f"bad mat: {mat} vbm: {vbm} blend mode: {mats[mat]}")
                        bad_mats[mat] = mats[mat]

                        
        # print(f"good_mat_count: {good_mat_count} len(materials): {len(materials)}")

        if len(bad_mats) == 0:
            bad_mats = None
            # if good_mat_count != len(materials):
            #     print(f"check {staticmesh_component.get_name()} might have duplicated mat slots")
        else:
            bad_mats=bad_mats
        

        return bad_mats


class Log:

    def write_log(message):
        """写入日志文件"""
        level_name = CURRENT_LEVEL.get_name()
        current_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
        # logfile = LOG_DIR + "LevelCheck_" + CURRENT_LEVEL +"_" + current_time + ".log"
        logfile = f"{LOG_DIR}LevelCheck_{level_name}_{current_time}.log"
        with open(logfile, "a", encoding="utf-8") as file:
            file.write(message)
        msg = f"Log written to {logfile}"
        unreal.log(msg)
        return msg

    def component_check_log(component):
        log = None
        is_bad = False
        is_visible=unreal.StaticMeshComponent.is_visible(component)
        if is_visible is True:
            # component_label = component.get_name()
            static_mesh = component.get_editor_property("static_mesh")
            if static_mesh:
                component_label = static_mesh.get_name()
            else:
                component_label = component.get_name()
            bad_nanite_mats = Materials.check_nanite_mat(component)
            nanite = LevelActor.check_nanite_settings(component)
            shadow = LevelActor.check_sm_shadow_option(component)
            
            # RULES //IMPORTANT//
            if "_Decal" in component_label:
                if shadow is True:
                    is_bad = True
            else:
                if bad_nanite_mats is not None: #translucent or decal materials
                    if nanite is False and shadow is True:
                        is_bad = True
                if bad_nanite_mats is None: #opaque or mask materials
                    if nanite is False:
                        is_bad = True

            if is_bad == True:
                if bad_nanite_mats is None:
                    log = f"  Component: {component_label} Nanite: {nanite} Shadow: {shadow} \n"
                elif bad_nanite_mats is not None:

                    log = f"  Component: {component_label} Nanite: {nanite} Shadow: {shadow} has bad mats: \n"

                    for mat in bad_nanite_mats:
                        blend_mode = bad_nanite_mats[mat]
                        log += f"      Mat: {mat} BlendMode: {blend_mode} \n"
        
        return log

    def make_log(actors, add_layer=True, add_folder=False):
        """检查StaticMeshActor的nanite和shadow设置是否正确，并将不正确的actor移动到BadPerformance层，输出检查结果到日志文件"""
        
        current_level_path = CURRENT_LEVEL.get_path_name()
        current_level_path = current_level_path.split(".")[0]
        log_header = (
            "场景帧数优化规范文档：\n"
            + "https://u37194l9ibz.larksuite.com/wiki/LNCmwfXseiDQkpkurCxuCDTusoe?fromScene=spaceOverview\n"
            + "为优化场景性能，当材质类型为NaniteMat(不透明或mask)时开启nanite，当材质类型不为NaniteMat(Translucent/Decal)时应关闭nanite和投影\n"
        )

        log_header += f"\nCheckLevel: {current_level_path}\n\n"
        sm_actors = LevelActor.filter_sm_actors(actors)
        bad_actors = {}
        log_summary = ""
        log_message = ""

        task_name = "Checking Level Assets： "
        asset_count = len(sm_actors)
        current_step = 0

        with unreal.ScopedSlowTask(asset_count, task_name) as slowTask:
            slowTask.make_dialog(True)
            for actor in sm_actors:
                current_step += 1
                actor_label = actor.get_actor_label()
                components = actor.get_components_by_class(SM_COMPONENT_CLASS)
                
                # actor.remove_actor_from_layer(DEBUG_LAYER)

                bad_components_log = []
                for component in components:
                    c_log = Log.component_check_log(component)
                    if c_log:
                        bad_components_log.append(c_log)

                if len(bad_components_log) > 0:
                    bad_actors[actor_label] = bad_components_log
                    log_message += f"Actor: {actor_label} 的nanite/shadow设置不正确 \n"
                    # 把有问题的资产actor添加到'BadPerformance' Layer
                    if add_layer:
                        layers_subsys.add_actor_to_layer(actor, DEBUG_LAYER)
                    if add_folder:
                        actor.set_folder_path(DEBUG_LAYER)

                for log in bad_components_log:
                    log_message += log + "\n"
            if len(bad_actors) > 0:
                log_summary = f"Found {len(bad_actors)} actors has bad performance settings\n发现{len(bad_actors)}个actor的设置不在性能最优状态\n\n"
                unreal.log_warning(log_summary)
                
        check_log = log_header + log_summary + log_message
        check_log = str(check_log)

        return check_log


def check_level_actors(actors, add_layer=True, add_folder=False):
    check_log = Log.make_log(actors=actors, add_layer=add_layer, add_folder=add_folder)
    print(check_log)
    Log.write_log(check_log)


#测试功能

check_level_actors(actors=all_level_actors,add_layer=False,add_folder=False)
