from distutils.command import clean

import unreal

from CommonFunctions import (

    get_asset_dir,

    get_asset_name,

    get_materials_data,

    filter_class,

)





sys_lib = unreal.SystemLibrary()

string_lib = unreal.StringLibrary()

clean_dir_name = unreal.Paths.normalize_directory_name



staticmesh_subsys = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)

suboject_subsys = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)



selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()





def get_material_name(material_slot_name: str) -> str:

    """根据材质插槽获取材质名"""



    MAT_INST_PREFIX = "MI_"

    MAT_PREFIX = "M_"



    if (

        string_lib.starts_with(material_slot_name, MAT_INST_PREFIX) is not True

        and string_lib.starts_with(material_slot_name, MAT_PREFIX) is not True

    ):

        material_name = MAT_INST_PREFIX + str(material_slot_name)

    else:

        material_name = str(material_slot_name)

    return material_name





def get_material_dir(meshes, mesh_dir: str, material_dir: str) -> str:

    """自动获取材质路径"""

    mesh_dir_path = get_asset_dir(meshes[0])



    if mesh_dir is "" or None or "/":  # 当mesh_dir为空时，材质路径为模型路径

        mat_dir_path = mesh_dir_path

    else:  # 当mesh_dir不为空时，模型路径为AAA/mesh_dir,材质路径为AAA/mat_dir

        level_dir = string_lib.split(

            str(mesh_dir_path), mesh_dir, search_dir=unreal.SearchDir.FROM_END

        )[0]

        mat_dir_path = level_dir + material_dir



    return mat_dir_path










def assign_materials(

    assets,

    mesh_dir: str,

    use_custom_path: bool,

    custom_path: str,

    replace_mat: bool = False,

):

    EMPTY_MAT_SLOT = "WorldGridMaterial.WorldGridMaterial"

    DEFAULT_MATDIR = "/Materials/"

    static_meshes = filter_class(assets, "StaticMesh")

    # mat是material的缩写

    mesh_dir = clean_dir_name(mesh_dir)



    if len(static_meshes) > 0:

        # 获取材质路径

        if use_custom_path is False:  # 是否使用自定义路径

            mat_dir_path = get_material_dir(static_meshes, mesh_dir, DEFAULT_MATDIR)

        else:

            mat_dir_path = clean_dir_name(custom_path)

        mat_dir_path = mat_dir_path + "/"



        for mesh in static_meshes:

            mesh_name = get_asset_name(mesh)

            mat_data = get_materials_data(mesh)



            for index in range(len(mat_data["index"])):

                mat_slot_name = mat_data["slot_name"][index]

                material = mat_data["material"][index]

                to_set_material = False  # 该材质插槽是否要设置材质



                if replace_mat is True:  # 替换材质

                    mat_name = get_material_name(mat_slot_name)

                    new_material_path = mat_dir_path + mat_name

                    to_set_material = True

                else:  # 只替换空材质



                    if (

                        material is None

                        or string_lib.contains(str(material), EMPTY_MAT_SLOT) is True

                    ):  # 筛选空材质插槽

                        mat_name = get_material_name(mat_slot_name)

                        new_material_path = mat_dir_path + mat_name

                        to_set_material = True

                    else:

                        to_set_material = False

                        unreal.log_warning(

                            "{}: slot {}:{} has material assigned ,skipped | 已有材质，跳过".format(

                                mesh_name, index, mat_slot_name

                            )

                        )



                if to_set_material is True:

                    if unreal.EditorAssetLibrary.does_asset_exist(

                        new_material_path

                    ):  # 检查材质是否存在

                        new_material_path = new_material_path + "." + mat_name

                        newMat = unreal.load_asset(new_material_path)



                        unreal.log(

                            "{}: slot {}:{} assigned new material | 材质已配置".format(

                                mesh_name, index, mat_slot_name

                            )

                        )

                        unreal.StaticMesh.set_material(mesh, index, newMat)

                    else:

                        unreal.log_warning(

                            "{}: slot {}:{} couldn't find name-matching material in defined path | 未在指定路径找到符合插槽名字的材质".format(

                                mesh_name, index, mat_slot_name

                            )

                        )



    else:

        unreal.log_error("No static meshes selected，stopped. | 没有任何选中的模型")

