from math import e
import unreal
from pathlib import Path
from CommonFunctions import get_asset_dir

string_lib = unreal.StringLibrary()
IGNORE_CASE = unreal.SearchCase.IGNORE_CASE
FROM_END = unreal.SearchDir.FROM_END
CASE_SENSITIVE = unreal.SearchCase.CASE_SENSITIVE

""" 资产改名 """


def refix_name(asset, prefix, suffix):
    """修改前后缀"""
    success = False

    # 拆分路径
    asset_name = asset.get_name()
    asset_dir = get_asset_dir(asset)
    asset_name_split_parts = string_lib.split(source_string=str(asset_name), str="_")

    if len(asset_name.split("_")) < 3:
        unreal.log_error("原名缺少前缀/后缀，无法正常识别")
        success = False

    else:
        # 拆分原名前后缀
        
        asset_name_split_suffix = string_lib.split(
            source_string=asset_name_split_parts[1],
            str="_",
            search_case=IGNORE_CASE,
            search_dir=FROM_END,
        )
        asset_name_split = asset_name_split_suffix[0]

        # 构建新名字
        asset_old_path = str(asset_dir) + "/" + asset_name
        asset_new_path = str(asset_dir) + "/" + prefix + asset_name_split + suffix
        asset_new_name = prefix + asset_name_split + suffix

        if unreal.EditorAssetLibrary.does_asset_exist(asset_new_path) is True:
            unreal.log_warning(
                "{} already have asset with same name, skipped | 已有同名资产，跳过".format(
                    asset_name
                )
            )
            success = False
        else:
            unreal.EditorAssetLibrary.rename_asset(asset_old_path, asset_new_path)
            unreal.log("{} ==> {} renamed | 成功重命名".format(asset_name, asset_new_name))
            success = True

    return success


def re_asset_name(asset, newname):
    """保留前后缀，只改变名字"""

    asset_name = asset.get_name()
    asset_dir = get_asset_dir(asset)

    asset_name_split = asset_name.split("_")
    namelen = len(asset_name_split)

    asset_name_p = asset_name_split[0] + "_"
    asset_name_s = "_" + asset_name_split[namelen - 1]

    asset_old_path = str(asset_dir) + "/" + asset_name
    asset_new_path = str(asset_dir) + "/" + asset_name_p + newname + asset_name_s

    unreal.EditorAssetLibrary.rename_asset(asset_old_path, asset_new_path)
    unreal.log("{} ==> {}".format(asset_old_path, asset_new_path))
    return asset_new_path


def batch_refix_name(assets, prefix, suffix):
    """同时修改前后缀"""
    success_num = 0
    current_step = 0
    slow_task_steps = len(assets)
    task_name = "Batch renaming multiple assets: "

    # Slow Task 进度条
    with unreal.ScopedSlowTask(slow_task_steps, task_name) as slow_task:
        slow_task.make_dialog(True)
        for asset in assets:
            current_step += 1
            if slow_task.should_cancel():
                break
            slow_task.enter_progress_frame(
                1, task_name + str(current_step) + "/" + str(slow_task_steps)
            )

            # 执行重命名，记录成功数
            if refix_name(asset, prefix, suffix) is True:
                success_num += 1

    unreal.log(
        "{} assets selected, {} renamed. | 总共选中{}个资产，其中{}个成功重命名".format(
            slow_task_steps, success_num, slow_task_steps, success_num
        )
    )
    return success_num


def batch_replace_name(assets, text, new_text):
    """替换名字内的文字"""
    success_num = 0
    current_step = 0
    slow_task_steps = len(assets)
    task_name = "Batch renaming multiple assets: "

    # Slow Task 进度条
    with unreal.ScopedSlowTask(slow_task_steps, task_name) as slow_task:
        slow_task.make_dialog(True)
        for asset in assets:
            current_step += 1
            if slow_task.should_cancel():
                break
            slow_task.enter_progress_frame(
                1, task_name + str(current_step) + "/" + str(slow_task_steps)
            )

            # 执行重命名，记录成功数
            if replace_name(asset, text, new_text) is True:
                success_num += 1

    unreal.log(
        "{} assets selected, {} renamed. | 总共选中{}个资产，其中{}个成功重命名".format(
            slow_task_steps, success_num, slow_task_steps, success_num
        )
    )
    return success_num


def replace_name(asset, text: str, new_text: str) -> str:
    """替换文件名中的字符"""
    asset_name = asset.get_name()
    asset_dir = get_asset_dir(asset)
    

    if string_lib.contains(asset_name, text) is False:
        unreal.log_warning(
            "{} does not contain {}, skipped | 不包含{}，跳过".format(
                asset_name, text, text
            )
        )
        return asset_name
    else:
        asset_new_name = string_lib.replace(
            source_string=asset_name,
            from_=text,
            to=new_text,
            search_case=CASE_SENSITIVE,
        )
        asset_old_path = str(asset_dir) + "/" + asset_name
        asset_new_path = str(asset_dir) + "/" + asset_new_name

        unreal.EditorAssetLibrary.rename_asset(asset_old_path, asset_new_path)
        unreal.log("{} ==> {}".format(asset_old_path, asset_new_path))

        return asset_new_name


def name_add_suffix(assets, suffix: str):
    """给名字添加后缀"""
    success_num = 0
    current_step = 0
    slow_task_steps = len(assets)
    task_name = "Batch renaming multiple assets: "
    if string_lib.contains(suffix, "_") is False:
        suffix = "_" + suffix

    # Slow Task 进度条
    with unreal.ScopedSlowTask(slow_task_steps, task_name) as slow_task:
        slow_task.make_dialog(True)
        for asset in assets:
            current_step += 1
            if slow_task.should_cancel():
                break
            slow_task.enter_progress_frame(
                1, task_name + str(current_step) + "/" + str(slow_task_steps)
            )

            # 执行重命名，记录成功数
            for asset in assets:
                asset_name = asset.get_name()
                asset_dir = get_asset_dir(asset)
                if string_lib.ends_with(asset_name, suffix) is True:
                    unreal.log_warning(
                        "{} already have suffix, skipped | 已有后缀，跳过".format(asset_name)
                    )
                    continue
                else:
                    asset_new_name = asset_name + suffix
                    asset_old_path = str(asset_dir) + "/" + asset_name
                    asset_new_path = str(asset_dir) + "/" + asset_new_name

                    unreal.EditorAssetLibrary.rename_asset(
                        asset_old_path, asset_new_path
                    )
                    unreal.log("{} ==> {}".format(asset_old_path, asset_new_path))
                    success_num += 1

    unreal.log(
        "{} assets selected, {} renamed. | 总共选中{}个资产，其中{}个成功重命名".format(
            slow_task_steps, success_num, slow_task_steps, success_num
        )
    )
    return success_num

def clean_name_underline(assets,has_suffix = True):
    success_num = 0
    current_step = 0
    slow_task_steps = len(assets)
    task_name = "Batch renaming multiple assets: "


    # Slow Task 进度条
    with unreal.ScopedSlowTask(slow_task_steps, task_name) as slow_task:
        slow_task.make_dialog(True)

        for asset in assets:
            current_step += 1
            rename = False
            if slow_task.should_cancel():
                break
            slow_task.enter_progress_frame(
                1, task_name + str(current_step) + "/" + str(slow_task_steps)
            )

            asset_name = asset.get_name()
            asset_dir = get_asset_dir(asset)

            if string_lib.contains(asset_name, "_") is False:
                unreal.log_warning(
                    "{} does not contain _, skipped | 不包含_，跳过".format(asset_name)
                )
                continue
            elif len(asset_name.split("_")) < 3:
                unreal.log_warning(
                    "{} can't dectect redundant underline in asset name, skipeed | 未检测到文件名中有多余的下划线，跳过".format(asset_name)
                )
                continue
            else:
                if has_suffix is False:
                    asset_name_split = asset_name.split("_")
                    asset_name_prefix = asset_name_split[0] + "_"
                    asset_name_old = string_lib.split(asset_name, "_")[1]
                    asset_name_clean = string_lib.replace(asset_name_old, "_", "")
                    asset_new_name = asset_name_prefix + asset_name_clean
                else:
                    asset_name_split = asset_name.split("_")
                    asset_name_prefix = asset_name_split[0] + "_"
                    asset_name_suffix = "_" + asset_name_split[len(asset_name_split) - 1]
                    asset_name_old= string_lib.split(asset_name, "_")
                    asset_name_old = string_lib.split(asset_name_old[1], "_", search_dir=FROM_END)[0]
                    asset_name_clean = string_lib.replace(asset_name_old, "_", "")
                    asset_new_name = asset_name_prefix + asset_name_clean + asset_name_suffix
                print(has_suffix)
                print(asset_name)
                print(asset_name_old)
                print(asset_new_name)

                asset_old_path = str(asset_dir) + "/" + asset_name
                asset_new_path = str(asset_dir) + "/" + asset_new_name
            if unreal.EditorAssetLibrary.does_asset_exist(asset_new_path) is True:
                unreal.log_warning(
                    "{} already have asset with same name, skipped | 已有同名资产，跳过".format(
                        asset_name
                    )
                )
            else:
                unreal.EditorAssetLibrary.rename_asset(asset_old_path, asset_new_path)
                unreal.log("{} ==> {}".format(asset_old_path, asset_new_path))
                success_num += 1

    unreal.log(
        "{} assets selected, {} renamed. | 总共选中{}个资产，其中{}个成功重命名".format(
            slow_task_steps, success_num, slow_task_steps, success_num
        )
    )
    return success_num