import gradio as gr  # 导入gradio库用于创建GUI

from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 导入用于GitHub API操作的客户端
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的LLM类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器

# 创建各个组件的实例
config = Config()
github_client = GitHubClient(config.github_token)
llm = LLM()
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)

def export_progress_by_date_range(repo, days):
    # 定义一个函数，用于导出和生成指定时间范围内项目的进展报告
    raw_file_path = github_client.export_progress_by_date_range(repo, days)  # 导出原始数据文件路径
    report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)  # 生成并获取报告内容及文件路径

    return report, report_file_path  # 返回报告内容和报告文件路径

def load_dropdown():
    """创建下拉菜单"""
    return gr.Dropdown(subscription_manager.list_subscriptions(), label="订阅列表", info="已订阅GitHub项目")

def reset_all():
    """清除报告"""
    return [load_dropdown(), gr.Markdown(), gr.File(label="下载报告")]

def contains_repo(repo):
    """该仓库是否已在订阅列表中"""
    for existed_repo in subscription_manager.list_subscriptions():
        if repo.lower() == existed_repo.lower():
            return True
    return False

def add_new_repo(repo):
    """订阅新仓库"""
    if not contains_repo(repo):
        subscription_manager.add_subscription(repo)
    return [load_dropdown(), load_dropdown()]

def delete_current_repo(repo):
    """删除当前选择的仓库"""
    if repo is not None and contains_repo(repo):
        subscription_manager.remove_subscription(repo)
    return [load_dropdown(), load_dropdown()]

# 创建Gradio界面
with gr.Blocks() as demo:
    with gr.Tab("生成报告"):
        with gr.Row():
            with gr.Column():
                repo_dropdown1 = load_dropdown()
                day_slider = gr.Slider(value=2, minimum=1, maximum=7, step=1, label="报告周期", info="生成项目过去一段时间进展，单位：天")
                with gr.Row():
                    reset_button = gr.Button("清除")
                    gen_report_button = gr.Button("提交")
            with gr.Column():
                markdown_preview = gr.Markdown()
                download_file = gr.File(label="下载报告")

    with gr.Tab("编辑订阅"):
        with gr.Row():
            with gr.Column():
                new_repo_textbox = gr.Textbox(label="输入新项目", info="e.g. owner/repo")
                add_button = gr.Button("添加至订阅列表")
            with gr.Column():
                repo_dropdown2 = gr.Dropdown(subscription_manager.list_subscriptions(), label="查看列表", info="已订阅GitHub项目")
                delete_button = gr.Button("移除当前订阅项目")
    
    reset_button.click(
        fn=reset_all,
        outputs=[repo_dropdown1, markdown_preview, download_file]
    )
    gen_report_button.click(
        fn=export_progress_by_date_range, 
        inputs=[repo_dropdown1, day_slider], 
        outputs=[markdown_preview, download_file]
    )
    add_button.click(
        fn=add_new_repo, 
        inputs=new_repo_textbox, 
        outputs=[repo_dropdown1, repo_dropdown2]
    )
    delete_button.click(
        fn=delete_current_repo, 
        inputs=repo_dropdown2, 
        outputs=[repo_dropdown1, repo_dropdown2]
    )

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")  # 启动界面并设置为公共可访问
    # 可选带有用户认证的启动方式
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))