import unreal
from CommonFunctions import *
# from importlib import reload
# reload Blueprint

BASE_COLLISION: unreal.Name = unreal.Name("CamToHiddenMesh") # "CamToHiddenMesh"可以实现相机穿透功能，使用Actor Tag"Camera_NoHide" 屏蔽
DECAL_COLLISION: unreal.Name = unreal.Name("NoCollision")

sys_lib = unreal.SystemLibrary()
string_lib = unreal.StringLibrary()
bp_editor_lib = unreal.BlueprintEditorLibrary

staticmesh_subsys = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
subobj_subsys = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)


selectedAssets = unreal.EditorUtilityLibrary.get_selected_assets()

sk_component_class = unreal.SkeletalMeshComponent.static_class()
sm_component_class = unreal.StaticMeshComponent.static_class()


def get_blueprint_assets(assets):
    """ 筛选蓝图资产 """
    blueprints = []
    for asset in assets:
        assetClass = asset.get_class()
        assetClass = sys_lib.get_class_display_name(asset.get_class())
        if assetClass == "Blueprint":
            blueprints.append(asset)

    return blueprints


def get_blueprint_components(blueprint):
    """ 获取蓝图子物件列表 """
    components = []
    root_data_handle = subobj_subsys.k2_gather_subobject_data_for_blueprint(blueprint)
    for handle in root_data_handle:
        subObject = subobj_subsys.k2_find_subobject_data_from_handle(handle)
        component = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(subObject)
        if component not in components:
            components.append(component)

    return components


def checkMaterials(materials):
    """ 检查模型的材质属性，如果有透明材质返回0，不透明和masked材质返回1 """

    validBlendModes = ["OPAQUE", "MASKED"]
    blendModes = []
    count = 0
    # iterate over materials and collect blend mode info
    for material in materials:
        if isinstance(material, unreal.Material):
            blendModes.append(material.get_editor_property("blend_mode"))
        if isinstance(material, unreal.MaterialInstanceConstant):
            parentMaterial = material.get_base_material()
            blendModes.append(parentMaterial.get_editor_property("blend_mode"))
    # check to see if valid blend mode in material blend mode
    for vbm in validBlendModes:
        for bm in blendModes:
            if vbm in str(bm):
                count += 1
    if count == len(materials):
        return 1
    return 0


def setBaseMesh(staticMesh):
    """ 设置Base Mesh"""
    meshNaniteSettings = staticMesh.get_editor_property("nanite_settings")
    # 开启nanite，配置参数避免法线错误
    meshNaniteSettings.enabled = True
    meshNaniteSettings.fallback_relative_error = 0
    staticmesh_subsys.set_nanite_settings(
        staticMesh, meshNaniteSettings, apply_changes=True
    )


def setDecalMesh(staticMesh):
    """ 设置Decal Mesh"""
    # 关闭nanite
    print("set decal mesh")
    meshNaniteSettings = staticMesh.get_editor_property("nanite_settings")
    meshNaniteSettings.enabled = False
    # meshNaniteSettings.fallback_relative_error = 0
    staticmesh_subsys.set_nanite_settings(
        staticMesh, meshNaniteSettings, apply_changes=True
    )
    # 删除碰撞
    default_object = unreal.StaticMeshEditorSubsystem.get_default_object()
    default_object.remove_collisions(staticMesh)


def set_skeletalmesh_components(components):
    """ 设置SkeletalMeshComponent""" 
    # print("use skm settings")
    sk_components = []
    sm_components = []
    for component in components:
        if component.get_class() == sk_component_class:
            sk_components.append(component)
    for component in components:
        if component.get_class() == sm_component_class:
            sm_components.append(component)
    for sk_comp in sk_components:
        # unreal.SkeletalMeshComponent.set_visibility(sk_comp, False)
        sk_comp.set_editor_property(name="cast_shadow", value=False)
        sk_mesh = sk_comp.get_skeletal_mesh_asset()
        sk_name = sk_mesh.get_name()
        sk_name = sk_name.split("_")[1]
        for sm_comp in sm_components:
            staticMesh = sm_comp.get_editor_property("static_mesh")
            assetName = staticMesh.get_name()
            if sk_name in assetName:

                # if "Class 'SkeletalMeshComponent'" in str(component):  # 检查是否smcomponent
                #     staticMesh = component.get_editor_property(
                #         "static_mesh"
                #     )  # 从smcomponent中获取对应的static mesh
                #     assetName = staticMesh.get_name()

                #     if str(staticMesh) == "None":
                #         unreal.log_warning(
                #             "StaticMeshComponent: {} has no StaticMesh | 没有StaticMesh，跳过".format(
                #                 str(component)
                #             )
                #         )

                if string_lib.contains(str(assetName), "_Decal") is True:
                    # decal处理，关闭投影和碰撞
                    component.set_editor_property(name="cast_shadow", value=False)
                    component.set_collision_profile_name(
                        collision_profile_name=DECAL_COLLISION
                    )
                    setDecalMesh(staticMesh)
                    unreal.log(
                        "{} is decal mesh, turn off nanite and collision | 贴花模型处理".format(
                            assetName
                        )
                    )

                else:
                    materials = unreal.StaticMeshComponent.get_materials(component)
                    component.set_collision_profile_name(
                        collision_profile_name=BASE_COLLISION
                    )
                    component.set_editor_property(
                        name="mobility", value=unreal.ComponentMobility.STATIC
                    )
                    if checkMaterials(materials) == 1:
                        setBaseMesh(staticMesh)
                    unreal.log(
                        "{} is base mesh, turn on nanite | base模型处理".format(
                            assetName
                        )
                    )


def set_staticmesh_components(components):
    """ 设置StaticMeshComponent"""

    for component in components:
        if component.get_class() == sm_component_class:  # 检查是否smcomponent
            # component.set_component_tick_enabled(False)

            # tick_disable=unreal.ActorComponentTickFunction.set_editor_property(name="start_with_tick_enabled", value=False, notify_mode=unreal.PropertyAccessChangeNotifyMode.NEVER)
            # component.set_editor_property(name="primary_component_tick", value=tick_disable)

            staticMesh = component.get_editor_property("static_mesh")  # 从smcomponent中获取对应的static mesh

            if str(staticMesh) == "None":
                unreal.log_warning(
                    "StaticMeshComponent: {} has no StaticMesh | 没有StaticMesh，跳过".format(
                        str(component)
                    )
                )

            elif string_lib.contains(str(staticMesh), "_Decal") is True:
                # decal处理，关闭投影和碰撞
                assetName = staticMesh.get_name()
                component.set_editor_property(name="cast_shadow", value=False)
                component.set_collision_profile_name(
                    collision_profile_name=DECAL_COLLISION
                )
                component.set_editor_property(
                    name="mobility", value=unreal.ComponentMobility.STATIC
                )
                component.set_editor_property(
                    name="world_position_offset_disable_distance", value=int(400)
                )
                setDecalMesh(staticMesh)
                unreal.log(
                    "{} is decal mesh, turn off nanite and collision | 贴花模型处理".format(
                        assetName
                    )
                )

            else:  # set base mesh component
                assetName = staticMesh.get_name()
                materials = unreal.StaticMeshComponent.get_materials(component)
                component.set_collision_profile_name(
                    collision_profile_name=BASE_COLLISION
                )
                component.set_editor_property(
                    name="mobility", value=unreal.ComponentMobility.STATIC
                )

                if checkMaterials(materials) == 1:
                    setBaseMesh(staticMesh)
                unreal.log(
                    "{} is base mesh, turn on nanite | base模型处理".format(assetName)
                )


def set_components_static(components):
    """设置所有Component为Static"""

    class_bp="BlueprintGeneratedClass"
    for component in components:

        if class_bp not in str(component.get_class()):

            component.set_editor_property(
                name="mobility", value=unreal.ComponentMobility.STATIC
            )



def set_childs(components):
    """设置蓝图中的Components"""
    has_skm = False
    for component in components:
        if component.get_class() == sk_component_class:
            has_skm = True
            break
    if has_skm:
        set_skeletalmesh_components(components)
    else:
        set_components_static(components)
        set_staticmesh_components(components)


def attach_skm_components(blueprint):
    
    sk_handles = []
    sm_handles = []
    handles = Blueprint.get_handels(blueprint)
    for handle in handles:
        if Blueprint.get_handle_component(handle).get_class() == sk_component_class:
            sk_handles.append(handle)
        elif Blueprint.get_handle_component(handle).get_class() == sm_component_class:
            sm_handles.append(handle)
    if len(sk_handles) > 0:
        print("attach sk handles")
        for sk_handle in sk_handles:
            sk_component = Blueprint.get_handle_component(sk_handle)
            sk_mesh = unreal.SkeletalMeshComponent.get_skeletal_mesh_asset(sk_component)
            sk_name = str(sk_mesh.get_name())
            sk_name = sk_name.split("_")[1]
            for sm_handle in sm_handles:
                sm_name = Blueprint.get_handle_component(sm_handle).get_name()
                if sk_name in sm_name:
                    subobj_subsys.attach_subobject(sk_handle, sm_handle)

def fix_prefab_with_parent(blueprint)->bool:
    """fix prefab with parent"""
    has_parent_prefab_bp = True
    bp_actor = Blueprint.get_default_object(blueprint)
    try:
        base_sm=bp_editor_lib.get_editor_property(bp_actor,name="Base")
        decal_sm=bp_editor_lib.get_editor_property(bp_actor,name="Decal")
        setBaseMesh(base_sm)
        setDecalMesh(decal_sm)
    except:
        base_sm=None
        decal_sm=None
        has_parent_prefab_bp = False

    return has_parent_prefab_bp

def fix_prefab_assets(assets):
    """修复Prefab资产,自动配置对应的Mesh属性"""
    blueprints = get_blueprint_assets(assets)
    assetCount = len(blueprints)
    taskName = "Batch Processing BP Assets： "
    currentStep = 0

    # Slow Task 进度条
    with unreal.ScopedSlowTask(assetCount, taskName) as slowTask:
        slowTask.make_dialog(True)

        for blueprint in blueprints:
            # 进度条目前进度
            currentStep += 1
            if slowTask.should_cancel():
                break
            slowTask.enter_progress_frame(
                1, taskName + str(currentStep) + "/" + str(assetCount)
            )
            attach_skm_components(blueprint)
            has_parent=fix_prefab_with_parent(blueprint)
            if has_parent is False:
                components = get_blueprint_components(blueprint)
                set_childs(components)

    if assetCount == 0:
        unreal.log_error("selection no Blueprint, aborted. | 所选模型没有Blueprint")
    else:
        unreal.log(
            "{} BPs with its child assets done | 蓝图及对应资产属性设置完成".format(
                assetCount
            )
        )







def get_component_from_variable(variable_name: str, blueprint_cdo)->unreal.StaticMeshComponent:
    static_mesh = bp_editor_lib.get_editor_property(blueprint_cdo, name=variable_name)
    static_mesh_component = None
    if isinstance (static_mesh, unreal.StaticMesh):
        static_mesh_component = unreal.StaticMeshComponent()
        static_mesh_component.set_static_mesh(static_mesh)
    return static_mesh_component

def reparent_blueprints(blueprints,parent_asset_path)->None:
    """
    reparent blueprints
    """
    parent_class = Blueprint.get_blueprint_class(parent_asset_path)
    parent_class_name = sys_lib.get_display_name(parent_class)

    for blueprint in blueprints:
        components = get_blueprint_components(blueprint)
        has_target_parent = False
        for component in components:
            if parent_class_name in str(component):
                has_target_parent = True
                break

        if has_target_parent == False:
            bp_editor_lib.reparent_blueprint(blueprint, parent_class)


def set_bp_variables_staticmesh(static_meshes,blueprint)->None:
    """
    set bp variables staticmesh
    """

    bp_actor = Blueprint.get_default_object(blueprint)

    decal_mesh=None
    base_mesh=None
    for static_mesh in static_meshes:
        if "_Decal" in static_mesh.get_name():
            decal_mesh=static_mesh
        else:
            base_mesh=static_mesh

    if base_mesh:
        bp_editor_lib.set_editor_property(bp_actor,name="Base",value=base_mesh)
    if decal_mesh:
        bp_editor_lib.set_editor_property(bp_actor,name="Decal",value=decal_mesh)



def get_parent_basemat(parent_asset_path):
    parent_bp=unreal.load_asset(parent_asset_path)
    parent_components=get_blueprint_components(parent_bp)
    parent_base_mat=None
    for component in parent_components:
        if "BaseMesh" in component.get_name():
            component_basemesh=component.get_editor_property("static_mesh")
            if component_basemesh:
                parent_base_mat=get_materials(component_basemesh)[0]
                parent_base_mat=parent_base_mat.get_base_material()
                break
    return parent_base_mat
def get_bp_variables_staticmesh(blueprint,parent_asset_path,parent_base_mat)->list:
    """
    get bp variables staticmesh
    """

    bp_actor = Blueprint.get_default_object(blueprint)
    components = get_blueprint_components(blueprint)
    parent_class = Blueprint.get_blueprint_class(parent_asset_path)
    parent_class_name = sys_lib.get_display_name(parent_class)
    
    filtered_meshes=[]
    
    sm_components=[]
    for component in components:
        component_class = component.get_class()
        if (parent_class_name not in str(component) and component_class == sm_component_class):
            sm_components.append(component)


    for component in sm_components:
        static_mesh=component.get_editor_property("static_mesh")
        if static_mesh is not None:
            if "_Decal" not in static_mesh.get_name():
                if parent_base_mat is not None:
                    mats=get_materials(static_mesh)
                    for material in mats:
                        master_mat=material.get_base_material()
                        if master_mat==parent_base_mat:
                            filtered_meshes.append(static_mesh)
                            component.set_static_mesh(None)
                            component.set_visibility(False)
                            break
                else:
                    filtered_meshes.append(static_mesh)
                    component.set_static_mesh(None)
                    component.set_visibility(False)
                    break

    for component in sm_components:
        static_mesh=component.get_editor_property("static_mesh")
        if static_mesh is not None:
            if "_Decal" in static_mesh.get_name():
                filtered_meshes.append(static_mesh)
                component.set_static_mesh(None)
                component.set_visibility(False)
                break
            
    if len(filtered_meshes)>0:
        return filtered_meshes
    else:
        return None
    





    

def filter_target_components(blueprint,parent_class)->list:
    bp_actor = Blueprint.get_default_object(blueprint)
    parent_class_name = sys_lib.get_display_name(parent_class)
    components = get_blueprint_components(blueprint)
                
    target_components = []

    for component in components:
        component_class = component.get_class()
        component_class = sys_lib.get_display_name(component_class)
        if (
            parent_class_name not in str(component)
            and component_class == "StaticMeshComponent"
        ):
            target_components.append(component)

    try:
        base_component=get_component_from_variable(variable_name="Base",blueprint_cdo=bp_actor)
    except:
        base_component=None

    if base_component is not None:
        target_components.append(base_component)
    try:
        decal_component=get_component_from_variable(variable_name="Decal",blueprint_cdo=bp_actor)
    except:
        decal_component=None
    if decal_component is not None:
        target_components.append(decal_component)

    return target_components

def reparent_blueprint_assets(assets, parent_asset_path):
    "替换bp的parent class，并配置子模型参数"
    parent_asset_path=unreal.Paths.normalize_filename(parent_asset_path)
    parent_class = Blueprint.get_blueprint_class(parent_asset_path)
    parent_class_name = sys_lib.get_display_name(parent_class)
    parent_basemat=get_parent_basemat(parent_asset_path)
    print(f"ParentClass:{parent_class_name}")
    blueprints = get_blueprint_assets(assets)


    assetCount = len(blueprints)
    taskName = "Batch Processing BP Assets： "
    currentStep = 0

    # Slow Task 进度条
    with unreal.ScopedSlowTask(assetCount, taskName) as slowTask:

        slowTask.make_dialog(True)

        for blueprint in blueprints:
            # 进度条目前进度
            currentStep += 1
            if slowTask.should_cancel():
                break
            slowTask.enter_progress_frame(
                1, taskName + str(currentStep) + "/" + str(assetCount)
            )

            is_mesh_prefab_bp = False
            if "_SM" in blueprint.get_name():
                is_mesh_prefab_bp = True

            if is_mesh_prefab_bp is True:
                components = get_blueprint_components(blueprint)

                
                # 检查是否已有parent
                has_target_parent = False
                for component in components:
                    if parent_class_name in str(component):
                        has_target_parent = True
                        break
                if has_target_parent is False:

                    filtered_meshes=get_bp_variables_staticmesh(blueprint,parent_asset_path,parent_basemat)
                    
                    has_base_mesh=False
                    if filtered_meshes is not None:
                        for mesh in filtered_meshes:
                            if "_Decal" not in mesh.get_name():
                                has_base_mesh=True
                                break
                                    
                    if has_base_mesh is True:
                        bp_editor_lib.reparent_blueprint(blueprint, parent_class)
                        bp_editor_lib.compile_blueprint(blueprint)
                        set_bp_variables_staticmesh(filtered_meshes,blueprint)
                    else:
                        print(f"{blueprint.get_name()} cannot be auto processed, skipped")
                                    

            else:
                print(f"{blueprint.get_name()} does not have '_SM' suffix, is not a mesh prefab, ")


            
            target_components=filter_target_components(blueprint,parent_class)
            if target_components is not None:
                set_childs(target_components)



    if assetCount == 0:
        unreal.log_error("selection no Blueprint, aborted. | 所选模型没有Blueprint")
    else:
        unreal.log(
            "{} BPs with its child assets done | 蓝图及对应资产属性设置完成".format(
                assetCount
            )
        )
        
def batch_recompile_bps(assets):
    "批量重新编译蓝图"
    blueprints = get_blueprint_assets(assets)
    for bp in blueprints:
        bp_editor_lib.compile_blueprint(bp)

# testrun

# SWATCH_PARENT = "/Game/FDBattleEnvContent/prefab/Functions/BP_SwatchParent.BP_SwatchParent"
# reparent_blueprint_assets(selectedAssets,SWATCH_PARENT)
# fix_prefab_assets(selectedAssets)