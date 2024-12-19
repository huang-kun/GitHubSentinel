import schedule # 导入 schedule 实现定时任务执行器
import time  # 导入time库，用于控制时间间隔
import signal  # 导入signal库，用于信号处理
import sys  # 导入sys库，用于执行系统相关的操作

from hn_client import HackerNewsClient
from hn_notifier import EmailNotifier  # 导入通知器类，用于发送通知
from report_generator import ReportGenerator  # 导入报告生成器类
from llm import LLM  # 导入语言模型类，可能用于生成报告内容
from logger import LOG  # 导入日志记录器
from config import Config  # 导入配置管理类


def graceful_shutdown(signum, frame):
    # 优雅关闭程序的函数，处理信号时调用
    LOG.info("[优雅退出]守护进程接收到终止信号")
    sys.exit(0)  # 安全退出程序


def hacker_news_job(client, report_generator, notifier):
    LOG.info("[开始执行定时任务]")
    stories = client.fetch_hackernews_top_stories()
    file_path = client.save_stories(stories) # 导出原始数据文件路径
    report, report_file_path = report_generator.generate_daily_report(file_path)
    notifier.notify(report)
    LOG.info(f"[定时任务执行完毕]")


def main():
    # 设置信号处理器
    signal.signal(signal.SIGTERM, graceful_shutdown)

    config = Config()
    client = HackerNewsClient()  # 创建客户端实例
    notifier = EmailNotifier(config.email)  # 创建通知器实例
    llm = LLM(prompt_filename='hacker_news_report_prompt.txt')  # 创建语言模型实例
    report_generator = ReportGenerator(llm)  # 创建报告生成器实例

    # 启动时立即执行（如不需要可注释）
    hacker_news_job(client, report_generator, notifier)

    # 安排每天的定时任务
    schedule.every(1).days.at(
        config.exec_time
    ).do(hacker_news_job, client, report_generator, notifier)

    try:
        # 在守护进程中持续运行
        while True:
            schedule.run_pending()
            time.sleep(1)  # 短暂休眠以减少 CPU 使用
    except Exception as e:
        LOG.error(f"主进程发生异常: {str(e)}")
        sys.exit(1)



if __name__ == '__main__':
    main()
