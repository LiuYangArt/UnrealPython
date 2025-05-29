import unreal

system_lib = unreal.SystemLibrary()
string_lib = unreal.StringLibrary()

SMSubsys = unreal.StaticMeshEditorSubsystem()
EditorSubsys = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)

# selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
# assets=selected_assets


def getSMAssets(assets):
    staticMeshes = []
    for asset in assets:
        asset_class = asset.get_class()
        asset_class = system_lib.get_class_display_name(asset_class)
        if asset_class == "StaticMesh":
            staticMeshes.append(asset)
    return staticMeshes


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
    meshNaniteSettings = staticMesh.get_editor_property("nanite_settings")
    # 开启nanite，配置参数避免法线错误
    meshNaniteSettings.enabled = True
    meshNaniteSettings.fallback_relative_error = 0
    unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).set_nanite_settings(
        staticMesh, meshNaniteSettings, apply_changes=True
    )


def setDecalMesh(staticMesh):
    # DecalCollision = unreal.CollisionProfileName("NoCollision")

    # 关闭nanite
    meshNaniteSettings = staticMesh.get_editor_property("nanite_settings")
    if meshNaniteSettings.enabled:
        meshNaniteSettings.enabled = False
        SMSubsys.set_nanite_settings(staticMesh, meshNaniteSettings, apply_changes=True)
    # 删除碰撞
    # EditorSubsys.remove_collisions(staticMesh)


# run this
def set_hardsurface_prop_meshes(assets):
    static_meshes = getSMAssets(assets)
    asset_count = len(static_meshes)

    TASK_NAME = "Batch Processing Mesh Nanite Settings： "
    current_step = 0

    # Slow Task 进度条
    with unreal.ScopedSlowTask(asset_count, TASK_NAME) as slow_task:
        slow_task.make_dialog(True)

        for static_mesh in static_meshes:
            # 进度条目前进度
            current_step += 1
            if slow_task.should_cancel():
                break
            slow_task.enter_progress_frame(
                1, TASK_NAME + str(current_step) + "/" + str(asset_count)
            )

            asset_name = static_mesh.get_name()
            # 处理decal模型
            if string_lib.contains(asset_name, "_Decal") is True:
                unreal.log(
                    "{} is decal mesh, turn off nanite and collision | 贴花模型处理".format(
                        asset_name
                    )
                )
                setDecalMesh(static_mesh)
            else:
                # 处理base模型
                SMComponent = unreal.StaticMeshComponent()
                SMComponent.set_static_mesh(static_mesh)
                materials = unreal.StaticMeshComponent.get_materials(SMComponent)
                if checkMaterials(materials) == 1:
                    setBaseMesh(static_mesh)
                    unreal.log(
                        "{} is base mesh, turn on nanite | base模型处理".format(asset_name)
                    )
                else:
                    unreal.log_warning(
                        "{}has non-opaque material, skipped | 有非不透明材质，跳过".format(
                            asset_name
                        )
                    )
    if asset_count == 0:
        unreal.log_error("selection no StaticMesh, aborted. | 所选模型没有StaticMesh")
    else:
        unreal.log("{} assets done | 模型属性设置完成".format(asset_count))



