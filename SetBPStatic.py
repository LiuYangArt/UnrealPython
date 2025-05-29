import unreal
from CommonFunctions import *
# from importlib import reload
# reload Blueprint

BASE_COLLISION: unreal.Name = unreal.Name("BlockAll")
DECAL_COLLISION: unreal.Name = unreal.Name("NoCollision")

sys_lib = unreal.SystemLibrary()
string_lib = unreal.StringLibrary()
bp_editor_lib = unreal.BlueprintEditorLibrary

staticmesh_subsys = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
subobj_subsys = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)


selectedAssets = unreal.EditorUtilityLibrary.get_selected_assets()

sk_component_class = unreal.SkeletalMeshComponent.static_class()
sm_component_class = unreal.StaticMeshComponent.static_class()

bp_class=unreal.BlueprintGeneratedClass.static_class()


def get_blueprint_assets(assets):
    # filter BPs
    blueprints = []
    for asset in assets:
        assetClass = asset.get_class()
        assetClass = sys_lib.get_class_display_name(asset.get_class())
        if assetClass == "Blueprint":
            blueprints.append(asset)

    return blueprints


def get_blueprint_components(blueprint):
    # 获取蓝图子物件列表
    components = []
    root_data_handle = subobj_subsys.k2_gather_subobject_data_for_blueprint(blueprint)
    for handle in root_data_handle:
        subObject = subobj_subsys.k2_find_subobject_data_from_handle(handle)
        component = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(subObject)
        if component not in components:
            components.append(component)

    return components



def set_components_static(components):
    class_bp="BlueprintGeneratedClass"
    for component in components:

        if class_bp not in str(component.get_class()):

            component.set_editor_property(
                name="mobility", value=unreal.ComponentMobility.STATIC
            )

            # print(f"{component.get_class()}")
            # print(f"mobility {component.get_editor_property(name='mobility')}")


 

def set_bp_static(assets):
    """在UE 里调用这个Function 对Prefab里的BP进行属性设置"""

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

            components = get_blueprint_components(blueprint)

            # for component in components:
            #     print(component.get_class())

            set_components_static(components)

    if assetCount == 0:
        unreal.log_error("selection no Blueprint, aborted. | 所选模型没有Blueprint")
    else:
        unreal.log(
            "{} BPs with its child assets done | 蓝图及对应资产属性设置完成".format(
                assetCount
            )
        )



## =================================================== ##


# testrun

# set_bp_static(selectedAssets)
