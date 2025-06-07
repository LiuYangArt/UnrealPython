import unreal
from pathlib import Path
import os
import time
from CommonFunctions import *
from HSPropMeshAssignMaterials import assign_materials

#reference docs:
#https://docs.unrealengine.com/5.3/en-US/PythonAPI/class/AssetImportTask.html#unreal-assetimporttask
#https://docs.unrealengine.com/5.3/en-US/PythonAPI/class/FbxStaticMeshImportData.html
#https://docs.unrealengine.com/5.3/en-US/PythonAPI/class/FbxFactory.html#unreal-fbxfactory

normalize_dir = unreal.Paths.normalize_directory_name
file_sdk = unreal.FileSDKBPLibrary
string_lib= unreal.StringLibrary
MESH_DIR = "/Meshes"
MAT_DIR = "/Materials"
MESH_PREFIX = "SM_"

# ue 5 import static mesh
def build_import_tasks(
    filename: str, destination_name: str, destination_path: str, options
):
    tasks = []
    task = unreal.AssetImportTask()
    task.set_editor_property("automated", True)
    task.set_editor_property("destination_name", destination_name)
    task.set_editor_property("destination_path", destination_path)
    task.set_editor_property("filename", filename)
    task.set_editor_property("options", options)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("factory", unreal.FbxFactory())
    # task.set_editor_property("save", True)
    tasks.append(task)
    return tasks



def build_import_options(static_mesh_data):
    options = unreal.FbxImportUI()
    options.set_editor_property("import_mesh", True)
    options.set_editor_property("import_textures", False)
    options.set_editor_property("import_materials", False)
    options.set_editor_property("import_as_skeletal", False)
    options.set_editor_property("static_mesh_import_data", static_mesh_data)
    options.set_editor_property("reset_to_fbx_on_material_conflict", True)

    return options


def build_static_mesh_data():
    static_mesh_data = unreal.FbxStaticMeshImportData()
    static_mesh_data.set_editor_property("build_nanite", False)
    static_mesh_data.set_editor_property("auto_generate_collision", True)
    static_mesh_data.set_editor_property("combine_meshes", True)
    static_mesh_data.set_editor_property("convert_scene", True)
    static_mesh_data.set_editor_property(
        "normal_import_method",
        unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS,
    )
    static_mesh_data.set_editor_property("compute_weighted_normals", True)
    static_mesh_data.set_editor_property(
        "normal_generation_method", unreal.FBXNormalGenerationMethod.MIKK_T_SPACE
    )
    static_mesh_data.set_editor_property("generate_lightmap_u_vs", False)
    static_mesh_data.set_editor_property(
        "vertex_color_import_option", unreal.VertexColorImportOption.REPLACE
    )

    static_mesh_data.set_editor_property("remove_degenerates", True)
    # static_mesh_data.set_editor_property("transform_vertex_to_absolute", False)
    # static_mesh_data.set_editor_property("vertex_override_color", None)
    static_mesh_data.set_editor_property("one_convex_hull_per_ucx", False)
    static_mesh_data.set_editor_property("reorder_material_to_fbx_order", True)
    static_mesh_data.set_editor_property("build_reversed_index_buffer", True)


    return static_mesh_data


def import_static_mesh(tasks):
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    asset_tools.import_asset_tasks(tasks)
    imported_object= unreal.AssetImportTask.get_objects(tasks[0])[0]
    return imported_object

def execute_import_static_mesh(file_path, name, target_dir):

    mesh_data = build_static_mesh_data()
    mesh_options = build_import_options(mesh_data)
    import_tasks = build_import_tasks(file_path, name, target_dir, mesh_options)
    imported_object = import_static_mesh(import_tasks)
    return imported_object


def list_import_files(file_dir):
    #PATHS
    all_files_path = file_sdk.get_files_from_directory(
        file_dir, filter_files_with_extension="fbx", search_subfolders=True
    )
    log_dir=unreal.Paths.project_log_dir()
    LOGFILE = log_dir + "/HardsurfacePropImport.log"

    last_import_log= read_log_file(LOGFILE) #read log file
    
    make_log_file(LOGFILE, "", "REPLACE") #write log file
    new_import_log = {}
    for file_path in all_files_path:
        time_modified = os.path.getmtime(file_path)
        modified_time = time.ctime(time_modified)
        new_import_log[file_path]=modified_time
        log_content = file_path + " | " + modified_time + "\n"
        make_log_file(LOGFILE, log_content, "APPEND")

    import_files = [] #make list from comapre result
    if last_import_log is None:
        import_files = all_files_path
    else:
        added, removed, modified, same = dict_compare(new_import_log, last_import_log)
        import_files=added + modified

    return import_files





def batch_import_hs_props(file_dir,target_dir,mesh_dir="/Meshes"):
    if file_dir=="":
        unreal.log_error("file_dir is Empty")
        return
    if target_dir=="":
        unreal.log_error("target_dir is Empty")
        return

    file_dir = normalize_dir(file_dir)
    target_dir = normalize_dir(target_dir)
    if mesh_dir not in target_dir:
        target_dir = target_dir + mesh_dir
    target_dir = normalize_dir(target_dir)

    import_files_paths = list_import_files(file_dir) #get files to import
    
    imported_objects = [] 
    if len(import_files_paths)==0:
        unreal.log_warning("No File To Import")
    else:
        for file_path in import_files_paths: #import files
            file_name= spilt_file_name(file_path)
            if not file_name.startswith(MESH_PREFIX):
                file_name = MESH_PREFIX + file_name
            subfolder=check_subfolder(file_path,mesh_dir=mesh_dir)
            if subfolder is not None and subfolder!="":
                target_dir = target_dir + subfolder
            unreal.log("importing file: " + file_path + " to: " + target_dir)
            imported_object=execute_import_static_mesh(file_path, file_name, target_dir)
            imported_objects.append(imported_object)
        
        unreal.log("import "+ str(len(import_files_paths))+ " files to :" + str(target_dir))

    if len(imported_objects)>0:
        assign_materials(assets=imported_objects, mesh_dir=mesh_dir, use_custom_path=False, custom_path="", replace_mat=False)
    
    unreal.log("DONE")
    return

