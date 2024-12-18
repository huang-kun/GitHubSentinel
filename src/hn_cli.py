import shlex
import argparse
from hn_client import HackerNewsClient
from report_generator import ReportGenerator 
from llm import LLM
from logger import LOG 

class HackerNewsCommandHandler:

    def __init__(self, client, report_generator):
        self.client = client
        self.report_generator = report_generator
        self.parser = self.create_parser()  # 创建命令行解析器

    def create_parser(self):
        # 创建并配置命令行解析器
        parser = argparse.ArgumentParser(
            description='Hacker News Command Line Interface',
            formatter_class=argparse.RawTextHelpFormatter
        )
        subparsers = parser.add_subparsers(title='Commands', dest='command')

        # 导出每日top list命令
        parser_export = subparsers.add_parser('export', help='Export daily progress')
        # parser_export.add_argument('repo', type=str, help='The repository to export progress from (e.g., owner/repo)')
        parser_export.set_defaults(func=self.export_daily_top_list)

        # 生成日报命令
        parser_generate = subparsers.add_parser('generate', help='Generate daily report from markdown file')
        parser_generate.add_argument('file', type=str, help='The markdown file to generate report from')
        parser_generate.set_defaults(func=self.generate_daily_report)

        # 帮助命令
        parser_help = subparsers.add_parser('help', help='Show help message')
        parser_help.set_defaults(func=self.print_help)

        return parser  # 返回配置好的解析器

    def export_daily_top_list(self, args):
        stories = self.client.fetch_hackernews_top_stories()
        file_path = self.client.save_stories(stories)
        print(f"Exported daily top list stories to {file_path}")

    def generate_daily_report(self, args):
        self.report_generator.generate_daily_report(args.file)
        print(f"Generated daily report from file: {args.file}")

    def print_help(self, args=None):
        self.parser.print_help()  # 输出帮助信息


def main():
    client = HackerNewsClient()
    llm = LLM(prompt_filename='hacker_news_report_prompt.txt')
    report_generator = ReportGenerator(llm)  # 创建报告生成器实例
    command_handler = HackerNewsCommandHandler(client, report_generator)  # 创建命令处理器实例
    
    parser = command_handler.parser  # 获取命令解析器
    command_handler.print_help()  # 打印帮助信息

    while True:
        try:
            user_input = input("Hacker News> ")  # 等待用户输入
            if user_input in ['exit', 'quit', 'q']:  # 如果输入为退出命令，则结束循环
                break
            try:
                args = parser.parse_args(shlex.split(user_input))  # 解析用户输入的命令
                if args.command is None:  # 如果没有命令被解析，则继续循环
                    continue
                args.func(args)  # 执行对应的命令函数
            except SystemExit as e:  # 捕获由于错误命令引发的异常
                LOG.error("Invalid command. Type 'help' to see the list of available commands.")
        except Exception as e:
            LOG.error(f"Unexpected error: {e}")  # 记录其他未预期的错误

if __name__ == '__main__':
    main()  # 如果直接运行该文件，则执行main函数
