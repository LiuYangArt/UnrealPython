import unreal
from pathlib import Path
import os

""" 常用功能/通用functions"""


sys_lib = unreal.SystemLibrary()
string_lib = unreal.StringLibrary()
editor_lib = unreal.EditorUtilityLibrary

staticmesh_subsys = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
subobject_subsys = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
editor_util_subsys = unreal.get_editor_subsystem(unreal.EditorUtilitySubsystem)


def get_asset_name(asset):
    """资产名"""
    asset_name = asset.get_name()
    return asset_name


def get_asset_dir(asset):
    """资产所在路径，剔除资产本身文件名"""
    asset_path_name = asset.get_path_name()
    asset_dir = unreal.Paths.get_path(asset_path_name)
    return asset_dir


def get_selected_dir():
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    selected_folders_path = unreal.EditorUtilityLibrary.get_selected_folder_paths()
    if len(selected_assets) != 0:
        asset = selected_assets[0]
        if isinstance(asset, unreal.Object):
            asset_dir_path = get_asset_dir(asset)
    if len(selected_folders_path) != 0:
        folder_path = selected_folders_path[0]
        asset_dir_path = string_lib.split(folder_path, "/All")[1]
    return asset_dir_path


def get_asset_path(asset):
    """资产完整路径，包含资产本身资源名"""
    asset_path = asset.get_path_name()
    return asset_path


def get_asset_class_name(asset):
    """资产Class名"""
    asset_class = asset.get_class()
    asset_class = sys_lib.get_class_display_name(asset_class)
    return asset_class


def filter_class(assets, class_name: str):
    """筛选某种类型的资产"""
    filtered_assets = []
    # filteredAssets = None
    for asset in assets:
        asset_class = asset.get_class()
        asset_class = sys_lib.get_class_display_name(asset_class)
        if asset_class == class_name:
            filtered_assets.append(asset)
    return filtered_assets


def get_materials(mesh):
    """获取StaticMesh的材质列表"""
    materials = None
    staticmesh_component = unreal.StaticMeshComponent()
    staticmesh_component.set_static_mesh(mesh)
    materials = unreal.StaticMeshComponent.get_materials(staticmesh_component)
    return materials


def get_material_slot_names(mesh):
    """获取StaticMesh的材质插槽列表"""
    staticmesh_component = unreal.StaticMeshComponent()
    staticmesh_component.set_static_mesh(mesh)
    mat_slot_names = unreal.StaticMeshComponent.get_material_slot_names(
        staticmesh_component
    )
    return mat_slot_names


def get_materials_data(mesh):
    """获取StaticMesh完整的材质信息，matIndex,matSlotName,material，输出Dict
    Example:
    matDict=getSMMateriaDict(staticMesh)
    for index in range(len(materials_data["index"])):
        slot_name = materials_data["slot_name"][index]
        material = materials_data["material"][index]
    """
    materials_data = {"index": [], "slot_name": [], "material": []}
    SM_component = unreal.StaticMeshComponent()
    SM_component.set_static_mesh(mesh)
    mat_slot_names = unreal.StaticMeshComponent.get_material_slot_names(SM_component)
    for slot_name in mat_slot_names:
        mat_index = unreal.StaticMeshComponent.get_material_index(
            SM_component, slot_name
        )
        material = unreal.StaticMeshComponent.get_material(SM_component, mat_index)
        materials_data["index"].append(mat_index)
        materials_data["slot_name"].append(slot_name)
        materials_data["material"].append(material)

    return materials_data


def get_blueprint_components(blueprint):
    """获取蓝图子物件列表"""
    components = []
    root_data_handle = subobject_subsys.k2_gather_subobject_data_for_blueprint(
        blueprint
    )
    for handle in root_data_handle:
        sub_object = subobject_subsys.k2_find_subobject_data_from_handle(handle)
        components.append(
            unreal.SubobjectDataBlueprintFunctionLibrary.get_object(sub_object)
        )

    return components


class Blueprint:
    def get_handels(blueprint):
        """获取蓝图子物件列表的handle"""
        # # components = []
        # handles=[]
        root_data_handle = subobject_subsys.k2_gather_subobject_data_for_blueprint(
            blueprint
        )
        # for handle in root_data_handle:
        #     sub_object = subobject_subsys.k2_find_subobject_data_from_handle(handle)
        #     handles.append(sub_object)

        return root_data_handle

    def get_handle_component(handle):
        """从handle得到components"""
        # components = []
        sub_object = subobject_subsys.k2_find_subobject_data_from_handle(handle)
        component = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(sub_object)

        return component

    def get_blueprint_class(path: str) -> unreal.Class:
        blueprint_asset = unreal.load_asset(path)
        blueprint_class = unreal.load_object(
            None, blueprint_asset.generated_class().get_path_name()
        )

        return blueprint_class

    def get_default_object(asset) -> unreal.Object:

        bp_gen_class = unreal.load_object(None, asset.generated_class().get_path_name())

        default_object = unreal.get_default_object(bp_gen_class)

        return default_object


def split_keywords(input_text) -> list:
    """分割输入的字符串，输出关键字列表"""
    input_text = string_lib.replace(input_text, " ", "")
    input_text = string_lib.replace(input_text, '"', "")
    keywords = input_text.split(",")
    return keywords


def run_widget(widget_path):
    """运行widget utility blueprint"""
    editor_util_subsys.spawn_and_register_tab(
        unreal.EditorAssetLibrary.load_asset(widget_path)
    )


def dict_compare(d1, d2):
    """比较两个字典，输出增加，删除，修改，相同的键值对"""
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    shared_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    added = list(added)
    removed = d2_keys - d1_keys
    removed = list(removed)
    modified = {o: (d1[o], d2[o]) for o in shared_keys if d1[o] != d2[o]}
    modified = set(modified.keys())
    modified = list(modified)
    same = set(o for o in shared_keys if d1[o] == d2[o])
    same = list(same)
    return added, removed, modified, same


def make_log_file(log_file_path, content, mode="APPEND"):
    if mode == "REPLACE":
        if os.path.exists(log_file_path):
            os.remove(log_file_path)
    elif mode == "APPEND":
        with open(log_file_path, "a") as f:
            f.write(str(content))  # 向文件中写入内容
            f.close()  # 关闭文件


def read_log_file(log_file_path):
    content = None
    log = {}
    if os.path.exists(log_file_path):
        f = open(log_file_path, "r")
        for line in f.readlines():
            content = line
            line_split = string_lib.split(line, " | ")
            value = line_split[1].replace("\n", "")
            log[line_split[0]] = value
        f.close()
        content = log
    else:
        print(log_file_path + " log not exist")
    return content


def check_subfolder(file_path, mesh_dir):
    mesh_dir = mesh_dir + "/"
    subfolder = ""
    file_dir = file_path.split(mesh_dir)
    if len(file_dir) > 1:
        if "/" in file_dir[1]:
            file_dir = string_lib.split(
                file_dir[1], "/", search_dir=unreal.SearchDir.FROM_END
            )[0]
            subfolder = "/" + file_dir

    return subfolder


def spilt_file_name(file_path):
    file_name = file_path.split("/")[-1]
    file_name = file_name.split(".")[0]
    return file_name
