import unreal
from CommonFunctions import filter_class,split_keywords

""" 批量自动配置选中的贴图资产，根据贴图名自动设置贴图压缩类型 """

def set_compression_type_masks(texture):
    texture.set_editor_property("sRGB", False)
    texture.set_editor_property(
        "CompressionSettings", unreal.TextureCompressionSettings.TC_MASKS
    )


def set_compression_type_normal(texture):
    texture.set_editor_property("sRGB", False)
    texture.set_editor_property(
        "CompressionSettings", unreal.TextureCompressionSettings.TC_NORMALMAP
    )


def set_compression_type_color(texture):
    texture.set_editor_property("sRGB", True)
    texture.set_editor_property(
        "CompressionSettings", unreal.TextureCompressionSettings.TC_DEFAULT
    )


def set_textures_compression(assets, masktex_suffix, normal_suffix, color_suffix):
    """根据贴图名自动设置贴图压缩类型"""

    masktex_suffix=split_keywords(masktex_suffix)
    normal_suffix=split_keywords(normal_suffix)
    color_suffix=split_keywords(color_suffix)

    textures = filter_class(assets, "Texture2D")

    if textures is None:
        unreal.log_warning("No textures selected. | 没有贴图被选中")
    else:
        for texture in textures:
            texture_name = texture.get_name()
            teturex_type = "unknown"
            set_success = False

            for suffix in masktex_suffix:
                if texture_name.endswith(suffix):
                    teturex_type = "mask tex"
                    set_compression_type_masks(texture)
                    set_success = True
                    break
            for suffix in normal_suffix:
                if texture_name.endswith(suffix):
                    teturex_type = "normal tex"
                    set_compression_type_normal(texture)
                    set_success = True
                    break
            for suffix in color_suffix:
                if texture_name.endswith(suffix):
                    teturex_type = "color tex"
                    set_compression_type_color(texture)
                    set_success = True
                    break

            if set_success is False:
                unreal.log_warning(
                    "{} of type {} not set. | 未设置".format(texture_name, teturex_type)
                )
            else:
                unreal.log(
                    "{} of type {} succesfully set. | 成功设置".format(texture_name, teturex_type)
                )


# set_textures_settings(selected_assets,tex_prefix,masktex_suffix,normal_suffix,color_suffix)
