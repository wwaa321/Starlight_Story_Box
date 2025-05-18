import flet as ft
#from manage_data import ManageData
import json
from content_generate import conversation_chat_stream,conversation_vision_stream
import audio_generate
import xml.etree.ElementTree as ET

instructions="""
1. 制作有声书
点击“制作有声书”按钮，进入故事创建页面。
在“输入故事名称”框中填写故事名称。
在“输入故事描述”框中填写故事描述，支持多行输入。
点击“下一步”按钮，进入图片上传页面。
2. 上传图片
在图片上传页面，点击“选择图片”按钮，上传一张图片。
上传成功后，图片会显示在左侧预览区域。
点击“分析图片”按钮，系统会自动分析图片内容并生成故事文本，显示在右侧文本框中。
3. 保存分析结果
如果对生成的内容满意，可以点击“保存结果”按钮，将当前分析结果保存为故事的一页。
如果需要清空所有已保存的结果，可以点击“清空结果”按钮。
4. 继续创作
点击“继续创作”按钮，保存当前所有分析结果并进入生成故事页面。
5. 生成故事
在生成故事页面，系统会显示故事名称、描述和章节数量。
点击“生成故事”按钮，系统会根据已保存的章节内容生成完整的故事文本，显示在左侧预览区域。
在右侧选择音色（如“龙书”、“龙妙”、“龙悦”），然后点击“创作故事音频”按钮，系统会生成有声故事音频。
6. 配置
如果需要配置 API 相关参数，可以点击“配置”按钮，在弹出的对话框中填写 API Key、API Secret、API Token、API Endpoint 和 API Model 等信息。
7. 注意事项
确保上传的图片清晰，以便系统能够准确分析图片内容。
生成音频时，请耐心等待，系统会显示进度环和提示信息。
如果遇到问题，可以查看页面底部的提示信息或重新操作。
"""
def create_story_data(name_field, desc_field): #故事初始数据管理
    story_data = {
            "name": name_field.value,
            "description": desc_field.value,
            "chapters": []
        }
    with open("data/story_data.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(story_data, indent=4,ensure_ascii=False))


def main(page: ft.Page): #故事初始窗口
    page.title = "星辉故事盒子"
    page.window.width=1280
    page.window.height=850
    page.window.maximizable = False
    page.window.center()

    # 设置全局默认字体
    page.theme = ft.Theme(font_family="黑体")

    def create_story(e=None): #创建故事窗口
        story_name_field = ft.TextField(label="输入故事名称", width=300, bgcolor="#FFFFFF",border=2,border_radius=5, border_color="#000000")
        story_desc_field = ft.TextField(label="输入故事描述", width=300,height=500,multiline=True,max_lines=19,border_color="transparent",)
        page.clean()
        page.bgcolor="#CCEAFD"
        page.title = "星辉故事盒子-制作有声书"
        layout_left=ft.Container(
            content=ft.Column(
                [   
                    ft.Text("制作有声书说明",size=16),
                    ft.Text(instructions)
                ]
            ),
            width=650,
            expand=True,
            alignment=ft.alignment.center_left,
            margin=20,
            padding=20,
            bgcolor="#FFF1B3",
            border=ft.border.all(2, "#000000"),
            border_radius=ft.border_radius.all(5)
    
        )
        layout_right=ft.Container(
            content=ft.Column(
                [
                    story_name_field,
                    ft.Container(
                        content=story_desc_field ,
                        alignment=ft.alignment.center_left,
                        height=500,
                        width=300,
                        border=ft.border.all(2, "#000000"),
                        border_radius=5,
                        bgcolor="#FFFFFF",
                
                    ),
                    
                    ft.ElevatedButton(text="下一步",color="#FFFFFF",bgcolor="#4CA2E3",width=300,height=50,on_click=lambda e: create_story_button_click(story_name_field, story_desc_field)
),
                ]
            ),
            width=650,
            expand=True,
            alignment=ft.alignment.center,
            margin=20,
            padding=20
        )
        page.add(ft.Row([layout_left,layout_right]))
        page.update()

    def uplode_page(e=None): #图片分析识别窗口
        page.clean()
        page.title = "星辉故事盒子-上传图片"
        page.bgcolor="#CCEAFD"
        
        # 创建图片预览容器
        image_preview = ft.Container(
            content=ft.Column(
                [
                    ft.Image(
                        src="img/placeholder.png",  # 默认占位图片
                        width=300,
                        height=300,
                        fit=ft.ImageFit.CONTAIN
                    ),
                    ft.Text(
                        "请上传图片",
                        size=16,
                        color="#666666",
                        weight=ft.FontWeight.NORMAL
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            width=400,
            height=400,
            border=ft.border.all(2, "#000000"),
            border_radius=5,
            bgcolor="#FFFFFF",
            alignment=ft.alignment.center
        )
        
        # 创建输出文本容器
        output_text = ft.TextField(
            label="故事内容",
            multiline=True,
            width=400,
            height=400,
            border_color="transparent",
            read_only=False
        )
        
        output_container = ft.Container(
            content=output_text,
            width=400,
            height=400,
            border=ft.border.all(2, "#000000"),
            border_radius=5,
            bgcolor="#FFFFFF",
            padding=10
        )
        
        page_number=ft.Text()
        img_analysis_result=ft.Text()
        output_result=ft.Container(
            content=[
                page_number,
                img_analysis_result
            ]
        )
        # 创建图片分析结果列表容器
        output_result_list = []  # 用于存储所有分析结果
        
        output_result_list_container = ft.Container(
            content=ft.Column(
                controls=output_result_list,
                scroll=ft.ScrollMode.AUTO,
                spacing=10
            ),
            width=400,
            height=600,
            border=ft.border.all(2, "#000000"),
            border_radius=5,
            bgcolor="#FFFFFF",
            padding=5,
            margin=5,
            alignment=ft.alignment.top_left
        )
        
        def save_output_result(e=None):
            if output_text.value:  # 确保有分析结果
                # 创建新的结果容器
                result_container = ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(f"第 {len(output_result_list) + 1} 页", 
                                  size=16, 
                                  weight=ft.FontWeight.BOLD,
                                  color="#4CA2E3"),
                            ft.Text(output_text.value,
                                  size=14,
                                  selectable=True)
                        ],
                        spacing=5
                    ),
                    border=ft.border.all(1, "#CCCCCC"),
                    border_radius=5,
                    padding=10,
                    bgcolor="#F5F5F5"
                )
                
                # 添加到结果列表
                output_result_list.append(result_container)
                
                # 更新容器显示
                output_result_list_container.content.controls = output_result_list
                output_result_list_container.update()
                
                # 清空当前分析结果
                output_text.value = ""
                output_text.update()
                
                # 显示保存成功提示
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("分析结果已保存！"),
                    action="好的",
                    duration=2000
                )
                page.snack_bar.open = True
                page.update()
            else:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("请先分析图片！"),
                    action="好的",
                    duration=2000
                )
                page.snack_bar.open = True
                page.update()
        
        def clear_results(e=None): #清空结果
            output_result_list.clear()
            output_result_list_container.content.controls = []
            output_result_list_container.update()
            page.snack_bar = ft.SnackBar(
                content=ft.Text("已清空所有结果！"),
                action="好的",
                duration=2000
            )
            page.snack_bar.open = True
            page.update()

        def save_to_json(e=None): #保存结果
            try:
                # 读取现有的 JSON 数据
                with open("data/story_data.json", "r", encoding="utf-8") as f:
                    story_data = json.load(f)
                
                # 将分析结果转换为章节数据
                chapters = []
                for i, result in enumerate(output_result_list):
                    chapter = {
                        "id": i + 1,
                        "title": f"第 {i + 1} 页",
                        "content": result.content.controls[1].value  # 获取文本内容
                    }
                    chapters.append(chapter)
                
                # 更新故事数据
                story_data["chapters"] = chapters
                
                # 保存到 JSON 文件
                with open("data/story_data.json", "w", encoding="utf-8") as f:
                    f.write(json.dumps(story_data, indent=4, ensure_ascii=False))
                
                # 显示保存成功提示
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("章节数据已保存！"),
                    action="好的",
                    duration=2000
                )
                page.snack_bar.open = True
                page.update()
                
                # 清空结果列表
                output_result_list.clear()
                output_result_list_container.content.controls = []
                output_result_list_container.update()
                
            except Exception as e:
                # 显示错误提示
                page.open(ft.SnackBar(ft.Text(f"保存失败：{str(e)}")))

               
                page.update()
        
        def pick_files_result(e: ft.FilePickerResultEvent):
            if e.files:
                # 更新文件名显示
                selected_files.value = ", ".join(map(lambda f: f.name, e.files))
                # 更新图片预览
                image_preview.content = ft.Image(
                    src=e.files[0].path,
                    width=400,
                    height=400,
                    fit=ft.ImageFit.CONTAIN
                )
                image_preview.update()
                selected_files.update()
            else:
                selected_files.value = "已取消！"
                # 恢复默认显示
                image_preview.content = ft.Column(
                    [
                        ft.Image(
                            src="img/placeholder.png",
                            width=300,
                            height=300,
                            fit=ft.ImageFit.CONTAIN
                        ),
                        ft.Text(
                            "请上传图片",
                            size=16,
                            color="#666666",
                            weight=ft.FontWeight.NORMAL
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                )
                image_preview.update()
                selected_files.update()
        
        def img_analysis(e=None):
            if pick_files_dialog.result and pick_files_dialog.result.files:
                img = pick_files_dialog.result.files[0]
                output_text.value = ""  # 初始化value为空字符串
                try:
                    for chunk in conversation_vision_stream("描述当前图片内容,如果图片中有文字，要提供文字内容", img.path):
                        output_text.value += chunk
                        output_text.update()
                except Exception as e:
                    output_text.value = f"分析出错: {str(e)}"
                    output_text.update()
        
        pick_files_dialog = ft.FilePicker(
            on_result=pick_files_result
        )
        
        selected_files = ft.Text()
        page.overlay.append(pick_files_dialog)
        
        # 创建布局
        layout_left = ft.Container(
            content=ft.Column(
                [
                    ft.Text("第一步，上传图片", size=16, weight=ft.FontWeight.BOLD),
                    image_preview,
                    ft.ElevatedButton(
                        "选择图片",
                        icon=ft.Icons.UPLOAD_FILE,
                        on_click=lambda _: pick_files_dialog.pick_files(
                            allow_multiple=False,
                            file_type=ft.FilePickerFileType.IMAGE
                        ),
                        width=350,
                        height=50,
                        color="#FFFFFF",
                        bgcolor="#4CA2E3",
                    ),
                    selected_files
                ],
                spacing=20,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            width=400,
            height=700,
            expand=True,
            alignment=ft.alignment.top_left,
            margin=5,
            padding=5,
        )
        
        layout_right = ft.Container(
            content=ft.Column(
                [
                    ft.Text("第二步，生成内容", size=16, weight=ft.FontWeight.BOLD),
                    output_container,
                    ft.ElevatedButton(
                        "分析图片",
                        icon=ft.Icons.ANALYTICS,
                        on_click=img_analysis,
                        width=350,
                        height=50,
                        color="#FFFFFF",
                        bgcolor="#4CA2E3"
                    ),
                    ft.ElevatedButton(
                        "保存结果",
                        icon=ft.Icons.SAVE_ALT_OUTLINED,
                        on_click=save_output_result,
                        width=350,
                        height=50,
                        color="#FFFFFF",
                        bgcolor="#4CA2E3"
                    ),
                    ft.ElevatedButton(
                        "清空结果",
                        icon=ft.Icons.DELETE_OUTLINE,
                        on_click=clear_results,
                        width=350,
                        height=50,
                        color="#FFFFFF",
                        bgcolor="#FF6B6B"
                    )
                ],
                spacing=20,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            width=400,
            expand=True,
            alignment=ft.alignment.center,
            margin=5,
            padding=5
        )
        def go_on_button_clicked(e=None):
            save_to_json()
            generate_story_page()
        go_on_create = ft.ElevatedButton(
            "继续创作",
            icon=ft.Icons.ARROW_FORWARD,
            on_click=go_on_button_clicked,
            width=200,
            height=50,
            color="#FFFFFF",
            bgcolor="#4CA2E3"
        )
        page.add(
            ft.Row(
                [
                    layout_left,
                    layout_right,
                    output_result_list_container,
                    ft.Container(
                        content=go_on_create,
                        alignment=ft.alignment.center,
                        padding=10
                    )
                ],
                spacing=20
            )
        )
        page.update()



    def generate_story_page(e=None): # 生成故事窗口
        page.clean()
        page.title = "星辉故事盒子-生成故事"
        page.bgcolor = "#CCEAFD"
        
        # 读取故事数据
        try:
            with open("data/story_data.json", "r", encoding="utf-8") as f:
                story_data = json.load(f)
        except Exception as e:
            page.open(ft.SnackBar(content=f"读取故事数据失败：{str(e)}"))
            page.update()
            return

        # 创建故事预览文本
        story_preview = ft.TextField(
            label="故事预览",
            multiline=True,
            width=600,
            height=400,
            border_color="transparent",
            read_only=False
        )
        
        # 创建故事内容容器
        story_container = ft.Container(
            content=story_preview,
            width=600,
            height=400,
            border=ft.border.all(2, "#000000"),
            border_radius=5,
            bgcolor="#FFFFFF",
            padding=10
        )

        audio_roles=ft.Dropdown(
                        value="龙书",
                        options=[
                            ft.dropdown.Option("龙书"),
                            ft.dropdown.Option("龙妙"),
                            ft.dropdown.Option("龙悦"),
                        ])

        # 创建左侧布局
        layout_left = ft.Container(
            content=ft.Column(
                [
                    ft.Text("故事内容预览", size=20, weight=ft.FontWeight.BOLD),
                    story_container,
                    ft.ElevatedButton(
                        "生成故事",
                        icon=ft.Icons.AUTO_STORIES,
                        on_click=lambda e: generate_story(story_preview, story_data),
                        width=200,
                        height=50,
                        color="#FFFFFF",
                        bgcolor="#4CA2E3"
                    ),
                            
                ],
                spacing=20,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            width=650,
            expand=True,
            alignment=ft.alignment.center,
            margin=20,
            padding=20
        )
        
        # 创建右侧布局
        layout_right = ft.Container(
            content=ft.Column(
                [
                    ft.Text("故事信息", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(f"故事名称：{story_data['name']}", size=16),
                    ft.Text(f"故事描述：{story_data['description']}", size=16),
                    ft.Text(f"章节数量：{len(story_data['chapters'])}", size=16),
                    ft.Row(
                        [
                            ft.Text("选择音色："),
                            audio_roles
                        ]                  
                    ),
                    ft.ElevatedButton("创作故事音频",
                                      icon=ft.Icons.AUTO_STORIES,
                                      on_click=lambda e: generate_audio(story_preview, audio_roles,story_data),
                                      width=200,
                                      height=50,
                                      color="#FFFFFF",
                                      bgcolor="#4CA2E3"),
                                      

                ],
                spacing=20,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            width=650,
            expand=True,
            alignment=ft.alignment.center,
            margin=20,
            padding=20
        )

        page.add(ft.Row([layout_left, layout_right]))
        page.update()

    def generate_story(story_preview, story_data): #生成故事内容
        """生成故事内容"""
        
        try:
           
            
            for chunk in  conversation_chat_stream(f"请根据提供的故事资料创作一个小故事。# 要求：仅需要根据提供的资料完成故事内容的创作，不要重复提供资料内容。# 创作资料：{story_data}。"):
                story_preview.value +=chunk
                story_preview.update()
            
            page.open(ft.SnackBar(content=f"生成故事成功！",action="好的"))
            page.update()
            
        except Exception as e:
            page.open(ft.SnackBar(content=f"生成故事失败：{str(e)}",action="好的"))
            page.update()
    
    def generate_audio(story_preview,audio_roles,story_data): #生成故事音频
        story_name=story_data['name']
        print(f"故事内容：{story_preview.value}")
        print(f"故事名称：{story_name}")
        pr=ft.ProgressRing()
        prl=ft.Text("生成音频中...")
        page.add(pr,prl)
        page.update()
        audio_generate.create_audio(story_preview.value,audio_roles.value,story_name)
        page.remove(pr,prl)
        completion_prompt=ft.Text("生成完成,你可以在“audio_flles”目录下查看生成的音频文件。")
        page.add(completion_prompt)
        page.update()
        
        
        print("生成音频成功")
        

    def create_story_button_click(name_field, desc_field): #创建故事数据
        if not name_field.value or not desc_field.value:
            page.open(ft.SnackBar(content=ft.Text("请输入故事名称和描述!"),action="好的"),)
            page.update()
            return
        else:
            create_story_data(name_field, desc_field)
            uplode_page()
    




    def confit_dialog(e): #配置对话框
        tree=ET.parse("configuration/configuration.xml")
        root=tree.getroot()
        api_key_info=root.find("llm_setting/apikey").text
        chat_model_info=root.find("llm_setting/chat_model").text
        vision_modei_info=root.find("llm_setting/vision_model").text
        base_url_info=root.find("llm_setting/base_url").text

        #定义一个弹窗内的表单容器
        dialog_form = ft.Container(
            content=ft.Column(
                [
                    ft.TextField(label="API Key", width=300,value=api_key_info),
                    ft.TextField(label="base_url", width=300,value=base_url_info),
                    ft.TextField(label="chat_model", width=300,value=chat_model_info),
                    ft.TextField(label="vision_model", width=300,value=vision_modei_info),
                ]
            )
            ,
            width=400,
            height=300,
        )
        def close_dialog(e):  
            dialog.open = False  
            page.update()
        dialog = ft.AlertDialog(
            title=ft.Text("配置"),
            content=dialog_form,
            actions=[  
                ft.TextButton("确定", on_click=lambda e: save_config(e)),  
                ft.TextButton("关闭",on_click=close_dialog)  
            ]  
        )

        def save_config(e):
            tree = ET.parse("configuration/configuration.xml")
            root = tree.getroot()
            root.find("llm_setting/apikey").text = dialog_form.content.controls[0].value
            root.find("llm_setting/base_url").text = dialog_form.content.controls[1].value
            root.find("llm_setting/chat_model").text = dialog_form.content.controls[2].value
            root.find("llm_setting/vision_model").text = dialog_form.content.controls[3].value
            tree.write("configuration/configuration.xml")
            dialog.open = False
            page.open(ft.SnackBar(content=ft.Text("保存成功！"),action="好的"),)
            page.update()

        
        page.add(dialog)
        dialog.open = True
        page.update()
    bg_image = ft.Image(src="img/bg.png", width=1280, height=800,top=0,left=0,fit=ft.ImageFit.FILL,expand=True,border_radius=10,) # 背景图片
    button=ft.ElevatedButton(text="制作有声书",color="#FFFFFF",bgcolor="#4CA2E3",width=300,height=50,on_click=create_story,right=90,top=500)    
    config_button=ft.ElevatedButton(text="配置",color="#FFFFFF",bgcolor="#4CA2E3",width=300,height=50,on_click=confit_dialog,right=90,top=600)
    st=ft.Stack(
        [bg_image,
         button,
         config_button
         ],
         width=1280,
         height=800


    )
    
    page.add(st)

ft.app(target=main)