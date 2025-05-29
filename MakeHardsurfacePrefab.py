import unreal
from pathlib import Path
from typing import Tuple
from CommonFunctions import *
from HardsurfacePropPrefabFix import *

string_lib = unreal.StringLibrary()
system_lib = unreal.SystemLibrary()

decal_suffix = "_Decal"
mesh_folder_name = "Meshes"

selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
# 路径构建
asset_pathname = selected_assets[0].get_path_name()
asset_path = Path(asset_pathname).parent

# 处理所选asset不在meshes下的情况
if string_lib.contains(str(asset_path), "\\Meshes") is True:
    asset_path_split = string_lib.split(
        source_string=str(asset_path), str="\\" + mesh_folder_name
    )
else:
    asset_path_split = string_lib.split(source_string=str(asset_path), str="\\")


level_path = string_lib.replace(asset_path_split[0], from_="\\", to="/")
asset_subpath = string_lib.replace(asset_path_split[1], from_="\\", to="/")

# 处理所选asset在meshes子目录下的情况，把subpath的值从 /AAA 变成 AAA/
if string_lib.starts_with(asset_subpath, "/") is True:
    asset_subpath_t = string_lib.split(asset_subpath, "/")
    asset_subpath = asset_subpath_t[1] + "/"


def add_subobject(
    subsystem: unreal.SubobjectDataSubsystem,
    blueprint: unreal.Blueprint,
    new_class,
    name: str,
) -> Tuple[unreal.SubobjectDataHandle, unreal.Object]:
    root_data_handle: unreal.SubobjectDataHandle = (
        subsystem.k2_gather_subobject_data_for_blueprint(context=blueprint)[0]
    )

    sub_handle, fail_reason = subsystem.add_new_subobject(
        params=unreal.AddNewSubobjectParams(
            parent_handle=root_data_handle,
            new_class=new_class,
            blueprint_context=blueprint,
        )
    )
    if not fail_reason.is_empty():
        raise Exception(
            "ERROR from sub_object_subsystem.add_new_subobject: {fail_reason}"
        )

    subsystem.rename_subobject(handle=sub_handle, new_name=unreal.Text(name))
    # subsystem.attach_subobject(owner_handle=root_data_handle, child_to_add_handle=sub_handle)

    BFL = unreal.SubobjectDataBlueprintFunctionLibrary
    obj: object = BFL.get_object(BFL.get_data(sub_handle))
    return sub_handle, obj


def load_mesh(path: str) -> unreal.StaticMesh:
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if not isinstance(asset, unreal.StaticMesh):
        raise Exception("Failed to load StaticMesh from {path}")
    return asset


# def make_hs_prop_blueprint(mesh_path: str, mesh_name: str, prefab_path: str, prefab_name: str):
#     # PhysicsActor: unreal.Name = unreal.Name("PhysicsActor")
#     BaseCollision = unreal.Name("BlockAll")
#     DecalCollision = unreal.Name("NoCollision")


#     basemesh_path = mesh_path + mesh_name
#     decalmesh_path = mesh_path + mesh_name + "_Decal"

#     factory = unreal.BlueprintFactory()
#     # this works, the saved blueprint is derived from Actor
#     factory.set_editor_property(name="parent_class", value=unreal.Actor)

#     # make the blueprint
#     asset_tools: unreal.AssetTools = unreal.AssetToolsHelpers.get_asset_tools()

#     asset = asset_tools.create_asset(
#         asset_name=prefab_name,
#         package_path=prefab_path,
#         asset_class=None,
#         factory=factory,
#     )
#     if not isinstance(asset, unreal.Blueprint):
#         raise Exception("Failed to create blueprint asset")
#     blueprint = asset  # noqa

#     subsystem: unreal.SubobjectDataSubsystem = unreal.get_engine_subsystem(
#         unreal.SubobjectDataSubsystem
#     )

#     # BASE

#     base_handle, base = add_subobject(
#         subsystem=subsystem,
#         blueprint=blueprint,
#         new_class=unreal.StaticMeshComponent,
#         name="BaseMesh",
#     )
#     mesh: unreal.StaticMesh = load_mesh(path=basemesh_path)
#     assert isinstance(base, unreal.StaticMeshComponent)
#     base.set_static_mesh(new_mesh=mesh)
#     base.set_editor_property(name="mobility", value=unreal.ComponentMobility.STATIC)
#     base.set_collision_profile_name(collision_profile_name=BaseCollision)

#     if unreal.EditorAssetLibrary.does_asset_exist(decalmesh_path) is True:
#         # 如果贴花模型存在， 在bp内创建贴花
#         sub_handle, decal = add_subobject(
#             subsystem=subsystem,
#             blueprint=blueprint,
#             new_class=unreal.StaticMeshComponent,
#             name="DecalMesh",
#         )
#         mesh: unreal.StaticMesh = load_mesh(path=decalmesh_path)
#         assert isinstance(decal, unreal.StaticMeshComponent)
#         decal.set_static_mesh(new_mesh=mesh)
#         # decal.set_editor_property(name="mobility", value=unreal.ComponentMobility.STATIC)
#         decal.set_editor_property(name="cast_shadow", value=False)
#         decal.set_editor_property(name="mobility", value=unreal.ComponentMobility.STATIC)
#         decal.set_collision_profile_name(collision_profile_name=DecalCollision)
#         decal.set_editor_property(name="world_position_offset_disable_distance", value=int(400))
#         subsystem.attach_subobject(
#             owner_handle=base_handle, child_to_add_handle=sub_handle
#         )


# def make_hardsurface_prop_prefabs(target_assets, prefab_folder, use_subfolder):
#     count = 0
#     if (
#         string_lib.contains(str(asset_path), "\\" + mesh_folder_name) is True
#     ):  # 检查asset是否在//Meshes路径下
#         for asset in target_assets:
#             mesh_name = asset.get_name()
#             aclass = asset.get_class()
#             asset_class = system_lib.get_class_display_name(aclass)

#             # 修正widget中textbox输入的prefab路径
#             if string_lib.ends_with(prefab_folder, "/") is not True:
#                 prefab_folder = prefab_folder + "/"

#             # prefab目标路径
#             if use_subfolder is True:
#                 prefab_path = level_path + prefab_folder + asset_subpath
#             else:
#                 prefab_path = level_path + prefab_folder
#             # Mesh路径
#             mesh_path = level_path + "/" + mesh_folder_name + "/" + asset_subpath

#             if asset_class != "StaticMesh":
#                 unreal.log_warning(
#                     "{} is not static mesh,skipped | 不是StaticMesh,跳过".format(mesh_name)
#                 )

#             else:
#                 if decal_suffix not in mesh_name:
#                     prefab_name_parts = mesh_name.split("_")
#                     prefab_name_start = "BP_"
#                     prefab_name_body = prefab_name_parts[1]
#                     prefab_name_end = "_SM"
#                     prefab_name = prefab_name_start + prefab_name_body + prefab_name_end
#                     if (
#                         unreal.EditorAssetLibrary.does_asset_exist(
#                             prefab_path + prefab_name
#                         )
#                         is False
#                     ):
#                         count += 1
#                         unreal.log(
#                             "{}:{} ==> {} | 创建Prefab".format(
#                                 count, mesh_name, prefab_name
#                             )
#                         )

#                         make_hsprop_blueprint(
#                             mesh_path=mesh_path,
#                             mesh_name=mesh_name,
#                             prefab_path=prefab_path,
#                             prefab_name=prefab_name,
#                         )
#                     else:
#                         unreal.log_warning(
#                             "Target blueprint {} already exists, skipped | 目标BP已存在，跳过".format(
#                                 prefab_name
#                             )
#                         )

#                 else:
#                     unreal.log_warning(mesh_name + " is decal mesh,skipped | 跳过Decal")

#         unreal.log("{} blueprint created. | 成功创建{}个蓝图".format(count, count))
#     else:
#         unreal.log_error(
#             "Seclected asset nor in /{}, stopped |  所选物体不在 /{} 下， 操作停止".format(
#                 mesh_folder_name, mesh_folder_name
#             )
#         )


def make_prop_blueprint(
    mesh_path: str,
    mesh_name: str,
    prefab_path: str,
    prefab_name: str,
    parent_bp_path: str,
):
    # PhysicsActor: unreal.Name = unreal.Name("PhysicsActor")
    BaseCollision = unreal.Name("CamToHiddenMesh") #"CamToHiddenMesh"可以实现相机穿透功能，使用Actor Tag"Camera_NoHide" 屏蔽
    DecalCollision = unreal.Name("NoCollision")

    parent_class = Blueprint.get_blueprint_class(parent_bp_path)

    basemesh_path = mesh_path + mesh_name
    decalmesh_path = mesh_path + mesh_name + "_Decal"

    factory = unreal.BlueprintFactory()
    # this works, the saved blueprint is derived from Actor
    factory.set_editor_property(name="parent_class", value=parent_class)

    # make the blueprint
    asset_tools: unreal.AssetTools = unreal.AssetToolsHelpers.get_asset_tools()

    asset = asset_tools.create_asset(
        asset_name=prefab_name,
        package_path=prefab_path,
        asset_class=None,
        factory=factory,
    )
    if not isinstance(asset, unreal.Blueprint):
        raise Exception("Failed to create blueprint asset")
    blueprint = asset  # noqa

    bp_actor = Blueprint.get_default_object(blueprint)

    base_mesh = load_mesh(path=basemesh_path)

    if isinstance(base_mesh, unreal.StaticMesh):
        bp_editor_lib.set_editor_property(bp_actor, name="Base", value=base_mesh)
        setBaseMesh(base_mesh)
    if unreal.EditorAssetLibrary.does_asset_exist(decalmesh_path) is True:
        decal_mesh = load_mesh(path=decalmesh_path)
        if isinstance(decal_mesh, unreal.StaticMesh):
            bp_editor_lib.set_editor_property(bp_actor, name="Decal", value=decal_mesh)
            setDecalMesh(decal_mesh)


def make_prop_prefabs(target_assets, prefab_folder, use_subfolder, parent_asset_path):
    count = 0
    if (
        string_lib.contains(str(asset_path), "\\" + mesh_folder_name) is True
    ):  # 检查asset是否在//Meshes路径下
        for asset in target_assets:
            mesh_name = asset.get_name()
            aclass = asset.get_class()
            asset_class = system_lib.get_class_display_name(aclass)

            # 修正widget中textbox输入的prefab路径
            if string_lib.ends_with(prefab_folder, "/") is not True:
                prefab_folder = prefab_folder + "/"

            # prefab目标路径
            if use_subfolder is True:
                prefab_path = level_path + prefab_folder + asset_subpath
            else:
                prefab_path = level_path + prefab_folder
            # Mesh路径
            mesh_path = level_path + "/" + mesh_folder_name + "/" + asset_subpath

            if asset_class != "StaticMesh":
                unreal.log_warning(
                    "{} is not static mesh,skipped | 不是StaticMesh,跳过".format(
                        mesh_name
                    )
                )

            else:
                if decal_suffix not in mesh_name:
                    prefab_name_parts = mesh_name.split("_")
                    prefab_name_start = "BP_"
                    prefab_name_body = prefab_name_parts[1]
                    prefab_name_end = "_SM"
                    prefab_name = prefab_name_start + prefab_name_body + prefab_name_end
                    if (
                        unreal.EditorAssetLibrary.does_asset_exist(
                            prefab_path + prefab_name
                        )
                        is False
                    ):
                        count += 1
                        unreal.log(
                            "{}:{} ==> {} | 创建Prefab".format(
                                count, mesh_name, prefab_name
                            )
                        )

                        make_prop_blueprint(
                            mesh_path=mesh_path,
                            mesh_name=mesh_name,
                            prefab_path=prefab_path,
                            prefab_name=prefab_name,
                            parent_bp_path=parent_asset_path,
                        )
                    else:
                        unreal.log_warning(
                            "Target blueprint {} already exists, skipped | 目标BP已存在，跳过".format(
                                prefab_name
                            )
                        )

                else:
                    unreal.log_warning(mesh_name + " is decal mesh,skipped | 跳过Decal")

        unreal.log("{} blueprint created. | 成功创建{}个蓝图".format(count, count))
    else:
        unreal.log_error(
            "Seclected asset nor in /{}, stopped |  所选物体不在 /{} 下， 操作停止".format(
                mesh_folder_name, mesh_folder_name
            )
        )


# test code
# make_prop_prefabs(
#     selected_assets,
#     prefab_folder="/Prefab",
#     use_subfolder=True,
#     parent_asset_path=SWATCH_PARENT,
# )
