import unreal
from unreal import ToolMenuContext
from CommonFunctions import run_widget

tool_menus = unreal.ToolMenus.get()
WIDGET_PATH = "/Game/WidgetTools/"


def add_menu():
    """添加菜单"""

    main_menu = tool_menus.find_menu("LevelEditor.MainMenu")
    main_menu.add_sub_menu(
        owner="CustomTools",
        section_name="Toolkits",
        name="CustomTools",
        label="CustomTools",
        tool_tip="Custom Art Tools | 自定义美术工具",
    )
    tool_menus.refresh_all_widgets()


# 定义子菜单class，运行widget
@unreal.uclass()
class menu_asset_toolkit(unreal.ToolMenuEntryScript):
    @unreal.ufunction(override=True)
    def execute(self, context: ToolMenuContext) -> None:
        run_widget(WIDGET_PATH+"EUW_AssetToolkit.EUW_AssetToolkit")
        print("Asset Toolkit")
        return super().execute(context)


@unreal.uclass()
class hardsurface_prop_toolkit(unreal.ToolMenuEntryScript):
    @unreal.ufunction(override=True)
    def execute(self, context: ToolMenuContext) -> None:
        run_widget(WIDGET_PATH + 
            "EUW_HardsurfacePropToolkit.EUW_HardsurfacePropToolkit"
        )
        print("Hardsurface Prop Toolkit")
        return super().execute(context)
    
@unreal.uclass()
class level_editor_toolkit(unreal.ToolMenuEntryScript):
    @unreal.ufunction(override=True)
    def execute(self, context: ToolMenuContext) -> None:
        run_widget(WIDGET_PATH + 
            "EUW_LevelToolkit.EUW_LevelToolkit"
        )
        print("Level Editor Toolkit")
        return super().execute(context)


def add_menu_entries():
    """添加子菜单项到菜单中"""
    main_menu = tool_menus.find_menu("LevelEditor.MainMenu.CustomTools")

    menu_object_01 = menu_asset_toolkit()
    menu_object_01.init_entry(
        owner_name=main_menu.menu_name,
        menu=main_menu.menu_name,
        section="Toolkits",
        name="AssetToolkit",
        label="Asset Toolkit",
        tool_tip="资产工具箱",
    )
    menu_object_01.register_menu_entry()

    menu_object_02 = hardsurface_prop_toolkit()
    menu_object_02.init_entry(
        owner_name=main_menu.menu_name,
        menu=main_menu.menu_name,
        section="Toolkits",
        name="HardsurfacePropToolkit",
        label="Hardsurface Prop Toolkit",
        tool_tip="硬表面道具工具箱",
    )
    menu_object_02.register_menu_entry()

    menu_object_03 = level_editor_toolkit()
    menu_object_03.init_entry(
        owner_name=main_menu.menu_name,
        menu=main_menu.menu_name,
        section="Toolkits",
        name="LevelEditorToolkit",
        label="Level Editor Toolkit",
        tool_tip="关卡编辑工具箱",
    )
    menu_object_03.register_menu_entry()

    


add_menu()
add_menu_entries()
