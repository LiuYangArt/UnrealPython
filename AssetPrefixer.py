import unreal
import json
from pathlib import Path

CONTENT_DIR = unreal.Paths.project_content_dir()
CONTENT_DIR = unreal.Paths.convert_relative_path_to_full(CONTENT_DIR)
MAPPING_FILE = "python/Presets/PrefixMapping.json"
MAPPING_FILE_PATH = CONTENT_DIR + MAPPING_FILE

editor_util = unreal.EditorUtilityLibrary()
sys_lib = unreal.SystemLibrary()
string_lib = unreal.StringLibrary()
selected_assets = editor_util.get_selected_assets()


def asset_prefixer(assets, replace_prefix=False):
    """根据asset的class自动添加/修改命名前缀"""
    asset_count = len(selected_assets)
    prefixed = 0

    # 读取前缀映射文件
    prefix_mapping = {}
    with open(MAPPING_FILE_PATH, "r") as json_file:
        prefix_mapping = json.loads(json_file.read())
    TASK_NAME = "SETTING ASSET PREFIX： "
    current_step = 0

    # Slow Task 进度条
    with unreal.ScopedSlowTask(asset_count, TASK_NAME) as slow_task:
        slow_task.make_dialog(True)

        for asset in selected_assets:
            current_step += 1
            if slow_task.should_cancel():
                break
            slow_task.enter_progress_frame(
                1, TASK_NAME + str(current_step) + "/" + str(asset_count)
            )

            asset_name = sys_lib.get_object_name(asset)
            asset_class = asset.get_class()
            asset_class_name = sys_lib.get_class_display_name(asset_class)

            # 搜索匹配的前缀
            class_prefix = prefix_mapping.get(asset_class_name, None)
            if class_prefix is None:
                for index, class_name in enumerate(prefix_mapping):
                    if asset_class_name.startswith(class_name):
                        class_prefix = prefix_mapping[class_name]
                        break
                    else:
                        class_prefix = None

            if class_prefix is None:
                unreal.log_warning(
                    "No defined-mapping for asset {} of type {} | 没有预定义的物体类型".format(
                        asset_name, asset_class_name
                    )
                )
            else:  # 找到匹配的前缀之后，开始重命名
                if replace_prefix == False:  # 添加前缀
                    if not asset_name.startswith(str(class_prefix)):
                        new_name = class_prefix + asset_name
                        editor_util.rename_asset(asset, new_name)

                        prefixed += 1
                        unreal.log(
                            "{} of type {} ==> {} | 成功重命名".format(
                                asset_name, asset_class_name, new_name
                            )
                        )

                    else:
                        unreal.log(
                            "Asset {} of type {} already prefixed with {}. | 已有前缀".format(
                                asset_name, asset_class_name, class_prefix
                            )
                        )
                else:  # 替换前缀
                    if string_lib.split(asset_name, "_") is None:
                        unreal.log_warning(
                            "Asset {} of type {} has no prefix. | 没有前缀".format(
                                asset_name, asset_class_name
                            )
                        )
                    else:
                        if not asset_name.startswith(str(class_prefix)):
                            new_name = string_lib.split(asset_name, "_")
                            new_name = class_prefix + new_name[1]
                            editor_util.rename_asset(asset, new_name)
                            prefixed += 1
                            unreal.log(
                                "{} of type {} ==> {} | 成功重命名".format(
                                    asset_name, asset_class_name, new_name
                                )
                            )
                        else:
                            unreal.log(
                                "Asset {} of type {} already prefixed with {}. | 已有前缀".format(
                                    asset_name, asset_class_name, class_prefix
                                )
                            )

        unreal.log("Prefixed {} of {} assets. | 完成".format(prefixed, asset_count))


# asset_prefixer(assets=selected_assets, replace_prefix=True)
