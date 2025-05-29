@echo off
echo Target UE Project Path, Example: "D:\LiuYang\Documents\Unreal Projects\TransferStation52\"
set /P target_path=path: 
PAUSE

rd "%target_path%\Content\Python" /s /q
rd "%target_path%\Content\WidgetTools" /s /q
mklink /j "%target_path%\Content\Python" "..\"
mklink /j "%target_path%\Content\WidgetTools" "..\..\WidgetTools"
PAUSE
