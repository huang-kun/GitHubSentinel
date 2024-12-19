import gradio as gr  # 导入gradio库用于创建GUI

from hn_client import HackerNewsClient
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的LLM类
from logger import LOG  # 导入日志记录器

# 创建各个组件的实例
client = HackerNewsClient()
llm = LLM(prompt_filename='hacker_news_report_prompt.txt')
report_generator = ReportGenerator(llm)

def export_top_list_stories(report_type):
    # 定义一个函数，用于导出和生成指定时间范围内项目的进展报告
    stories = client.fetch_hackernews_top_stories()
    file_path = client.save_stories(stories) # 导出原始数据文件路径
    report, report_file_path = report_generator.generate_daily_report(file_path)  # 生成并获取报告内容及文件路径

    return report, report_file_path  # 返回报告内容和报告文件路径

# 创建Gradio界面
demo = gr.Interface(
    fn=export_top_list_stories,  # 指定界面调用的函数
    title="Hacker News",  # 设置界面标题
    inputs=[gr.Dropdown(["top list stories"], label="报告素材")],
    outputs=[gr.Markdown(), gr.File(label="下载报告")],  # 输出格式：Markdown文本和文件下载
)

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")  # 启动界面并设置为公共可访问
    # 可选带有用户认证的启动方式
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))