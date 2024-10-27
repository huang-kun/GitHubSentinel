# src/llm.py

import os
from openai import OpenAI

class LLM:
    def __init__(self):
        self.client = OpenAI()

    def generate_daily_report(self, markdown_content, dry_run=False):
        system_prompt = "你是一名专业的项目助理，请根据输入的项目更新进展文本，总结并整合相同类别的内容，形成一份简报（用于汇报），至少包含的类别有：新增功能、主要改进、修复问题。要求使用中文。"

        if dry_run:
            with open("daily_progress/prompt.txt", "w+") as f:
                f.write(f"{system_prompt}\n\n{markdown_content}")
            return "DRY RUN"

        print("Before call GPT")
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": markdown_content}
            ]
        )
        print("After call GPT")
        print(response)
        return response.choices[0].message.content
