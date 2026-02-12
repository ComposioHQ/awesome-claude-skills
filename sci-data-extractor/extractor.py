#!/usr/bin/env python3
"""
Sci-Data-Extractor: 科学文献数据提取工具
支持从 PDF 文件中提取结构化数据
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from typing import Optional, Dict, List, Any

try:
    import fitz  # PyMuPDF
except ImportError:
    print("错误: 需要安装 PyMuPDF")
    print("安装命令: pip install pymupdf")
    sys.exit(1)

try:
    from openai import OpenAI
except ImportError:
    print("错误: 需要安装 openai")
    print("安装命令: pip install openai")
    sys.exit(1)

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # 如果没有安装 python-dotenv，跳过加载


# ============================================
# 配置管理
# ============================================

class Config:
    """配置管理类"""

    def __init__(self):
        self.api_key = os.getenv('EXTRACTOR_API_KEY') or os.getenv('API_KEY')
        self.base_url = os.getenv('EXTRACTOR_BASE_URL') or os.getenv('BASE_URL')
        self.mathpix_app_id = os.getenv('MATHPIX_APP_ID')
        self.mathpix_app_key = os.getenv('MATHPIX_APP_KEY')
        self.default_model = os.getenv('EXTRACTOR_MODEL', 'claude-sonnet-4-5-20250929')
        self.default_temperature = float(os.getenv('EXTRACTOR_TEMPERATURE', '0.1'))
        self.default_max_tokens = int(os.getenv('EXTRACTOR_MAX_TOKENS', '16384'))

    def validate(self) -> bool:
        """验证配置"""
        if not self.api_key:
            print("警告: 未设置 API_KEY，请设置环境变量 EXTRACTOR_API_KEY")
            return False
        return True


# ============================================
# PDF 处理
# ============================================

class PDFProcessor:
    """PDF 处理类"""

    @staticmethod
    def extract_text_pymupdf(pdf_path: str) -> Optional[str]:
        """
        使用 PyMuPDF 提取 PDF 文本

        Args:
            pdf_path: PDF 文件路径

        Returns:
            提取的文本内容
        """
        try:
            doc = fitz.open(pdf_path)
            content = []

            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                text = page.get_text("text")
                content.append(f"--- Page {page_num + 1} ---\n{text}\n")

            doc.close()
            return "\n".join(content)

        except Exception as e:
            print(f"错误: 无法读取 PDF 文件: {e}")
            return None

    @staticmethod
    def extract_text_mathpix(pdf_path: str, app_id: str, app_key: str) -> Optional[str]:
        """
        使用 Mathpix OCR 提取 PDF 内容（需要 API）

        Args:
            pdf_path: PDF 文件路径
            app_id: Mathpix App ID
            app_key: Mathpix App Key

        Returns:
            提取的 Markdown 内容
        """
        try:
            import requests
            import time

            headers = {
                'app_id': app_id,
                'app_key': app_key,
            }

            options = {
                "conversion_formats": {"md": True},
                "math_inline_delimiters": ["$", "$"],
                "rm_spaces": True
            }

            # 上传 PDF
            print("上传 PDF 到 Mathpix...")
            url = 'https://api.mathpix.com/v3/pdf'

            with open(pdf_path, 'rb') as f:
                files = {
                    'file': f,
                    'options_json': (None, json.dumps(options))
                }
                response = requests.post(url, headers=headers, files=files)

            if response.status_code != 200:
                print(f"错误: Mathpix 上传失败，状态码: {response.status_code}")
                return None

            pdf_id = response.json().get('pdf_id')
            print(f"PDF ID: {pdf_id}")

            # 等待转换完成
            print("等待 OCR 转换完成...")
            max_retries = 60
            retry_interval = 5

            for _ in range(max_retries):
                status_url = f'https://api.mathpix.com/v3/pdf/{pdf_id}'
                status_response = requests.get(status_url, headers=headers)
                status_data = status_response.json()
                conversion_status = status_data.get('status', 'unknown')

                print(f"转换状态: {conversion_status}")

                if conversion_status == 'completed':
                    break
                elif conversion_status in ['loaded', 'split', 'processing']:
                    time.sleep(retry_interval)
                else:
                    print(f"错误: 转换失败，状态: {conversion_status}")
                    return None

            # 下载 Markdown
            md_url = f'https://api.mathpix.com/v3/pdf/{pdf_id}.md'
            md_response = requests.get(md_url, headers=headers)

            if md_response.status_code == 200:
                return md_response.text
            else:
                print(f"错误: 下载 Markdown 失败，状态码: {md_response.status_code}")
                return None

        except ImportError:
            print("错误: Mathpix OCR 需要安装 requests 库")
            print("安装命令: pip install requests")
            return None
        except Exception as e:
            print(f"错误: Mathpix OCR 处理失败: {e}")
            return None

    @staticmethod
    def remove_references(text: str) -> str:
        """删除参考文献部分"""
        patterns = [
            (r'\*.{0,5}(References|Reference|REFERENCES|LITERATURE CITED)(.*?)\\section\*{Tables', r'\section*{Tables\n'),
            (r'\*.{0,5}(References|Reference|REFERENCES|LITERATURE CITED)(.*)', ''),
            (r'#.{0,15}(References|Reference|REFERENCES)(.*?)(Table|Tables)', r'Tables'),
            (r'#.{0,15}(References|Reference|REFERENCES)(.*)', '')
        ]

        for pattern, replacement in patterns:
            matches = re.search(pattern, text, re.DOTALL)
            if matches:
                text = text.replace(matches[0], replacement)
                break

        return text


# ============================================
# 数据提取
# ============================================

class DataExtractor:
    """数据提取类"""

    def __init__(self, config: Config):
        self.config = config
        self.client = OpenAI(api_key=config.api_key, base_url=config.base_url)

    def call_llm(self, messages: List[Dict], model: str = None, temperature: float = None, max_tokens: int = None) -> Optional[str]:
        """
        调用 LLM API

        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大输出 token 数

        Returns:
            LLM 响应文本
        """
        model = model or self.config.default_model
        temperature = temperature or self.config.default_temperature
        max_tokens = max_tokens or self.config.default_max_tokens

        try:
            print(f"API 调用信息:")
            print(f"  - Model: {model}")
            print(f"  - Base URL: {self.config.base_url}")
            print(f"  - Messages: {len(messages)} 条")
            print(f"  - Temperature: {temperature}")
            print(f"  - Max Tokens: {max_tokens}")

            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )

            print(f"API 响应: {type(completion)}")

            if completion is None:
                print("错误: API 返回 None")
                return None

            if not hasattr(completion, 'choices') or not completion.choices:
                print(f"错误: API 返回没有 choices 字段. 响应: {completion}")
                return None

            return completion.choices[0].message.content

        except Exception as e:
            print(f"错误: LLM API 调用失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def extract_data(self, content: str, prompt: str, model: str = None,
                     temperature: float = None) -> Optional[str]:
        """
        从文本内容中提取数据

        Args:
            content: 文本内容
            prompt: 提取提示词
            model: 模型名称
            temperature: 温度参数

        Returns:
            提取的结果（Markdown 表格格式）
        """
        # 清理内容
        content = PDFProcessor.remove_references(content)

        messages = [
            {
                "role": "system",
                "content": "You are an expert in information extraction from scientific literature."
            },
            {
                "role": "user",
                "content": f"""Provided Text:
'''
{{\"\"\" {content} \"\"\"}}
'''
{prompt}"""
            }
        ]

        return self.call_llm(messages, model, temperature)


# ============================================
# 预设模板
# ============================================

PRESET_TEMPLATES = {
    "enzyme": """Please read the scientific article provided and extract detailed information about enzymes from a specific organism, focusing on variants or mutants.

Extract the following fields into a table:
- Enzyme: Name of the enzyme
- Organism: Source organism
- Substrate: Substrate name
- Km: Michaelis constant value (number only)
- Unit_Km: Unit for Km
- Kcat: Catalytic constant value (number only)
- Unit_Kcat: Unit for Kcat
- Kcat_Km: Kcat/Km ratio value (number only, use scientific notation if needed)
- Unit_Kcat_Km: Unit for Kcat/Km
- Temperature: Temperature in °C
- pH: pH value
- Mutant: Mutant information (use WT for wild type)
- Cosubstrate: Cofactor or cosubstrate

Important rules:
1. Separate numeric values from their units - put values in the value columns and units in the unit columns
2. For scientific notation in headers (e.g., "Kcat/Km × 10^4"), include the multiplier in the value (e.g., "1.4 × 10^4") and put the base unit in the unit column
3. Only include mean values, exclude standard deviations and errors (values after ± or in parentheses)
4. Output as a Markdown table using | as delimiter
5. Include ALL data rows without omissions or ellipses

Output format example:
| Enzyme | Organism | Substrate | Km | Unit_Km | Kcat | Unit_Kcat | Kcat_Km | Unit_Kcat_Km | Temperature | pH | Mutant | Cosubstrate |
|--------|----------|-----------|-----|---------|------|-----------|---------|--------------|-------------|-----|--------|-------------|
| Enzyme1 | Bacillus subtilis | Substrate_A | 7.3 | mM | 6.4 | s^-1 | 1.4 × 10^4 | M^-1s^-1 | 37°C | 5.0 | WT | NADP^+ |""",

    "experiment": """Please read the scientific article provided and extract experimental results data.

Extract the following fields into a table:
- Experiment: Experiment name or identifier
- Condition: Experimental conditions
- Result: Measured result value (number only)
- Unit: Unit of measurement
- Standard_Deviation: Standard deviation if available
- Sample_Size: Number of samples (n)
- p_value: Statistical significance p-value

Output as a Markdown table using | as delimiter.
Include ALL experimental data without omissions.""",

    "review": """Please read the scientific article provided and extract bibliographic information.

Extract the following fields into a table:
- Author: Author names
- Year: Publication year
- Journal: Journal name
- Title: Article title
- DOI: DOI if available
- Key_Findings: Main findings or conclusions
- Methodology: Research methods used

Output as a Markdown table using | as delimiter.
If the article contains multiple studies, create one row per study.""",
}


# ============================================
# 输出处理
# ============================================

class OutputHandler:
    """输出处理类"""

    @staticmethod
    def markdown_to_csv(markdown_table: str) -> str:
        """
        将 Markdown 表格转换为 CSV 格式

        Args:
            markdown_table: Markdown 格式的表格

        Returns:
            CSV 格式的字符串
        """
        lines = markdown_table.strip().split('\n')
        csv_lines = []

        for line in lines:
            # 跳过分隔行（包含 |---）
            if '|---' in line or not line.strip():
                continue

            # 移除首尾的 | 并按 | 分割
            cells = line.strip().strip('|').split('|')
            cells = [cell.strip() for cell in cells]
            csv_lines.append(','.join(cells))

        return '\n'.join(csv_lines)

    @staticmethod
    def save_output(content: str, output_path: str, format: str = 'markdown') -> bool:
        """
        保存输出到文件

        Args:
            content: 输出内容
            output_path: 输出文件路径
            format: 输出格式 (markdown, csv)

        Returns:
            是否保存成功
        """
        try:
            output_path = Path(output_path)

            if format == 'csv':
                content = OutputHandler.markdown_to_csv(content)

            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✓ 输出已保存到: {output_path}")
            return True

        except Exception as e:
            print(f"错误: 保存文件失败: {e}")
            return False


# ============================================
# 主程序
# ============================================

def main():
    parser = argparse.ArgumentParser(
        description='Sci-Data-Extractor: 科学文献数据提取工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用 PyMuPDF 提取文本
  %(prog)s input.pdf -o output.md

  # 使用 Mathpix OCR (需要设置 API)
  %(prog)s input.pdf -o output.md --ocr mathpix

  # 使用预设模板
  %(prog)s input.pdf --template enzyme -o results.md

  # 自定义提取提示
  %(prog)s input.pdf -p "提取所有表格数据" -o results.md

  # 输出 CSV 格式
  %(prog)s input.pdf --template enzyme -o results.csv --format csv
        """
    )

    parser.add_argument('input', help='输入 PDF 文件路径')
    parser.add_argument('-o', '--output', required=True, help='输出文件路径')
    parser.add_argument('--ocr', choices=['pymupdf', 'mathpix'], default='pymupdf',
                        help='OCR 方式 (默认: pymupdf)')
    parser.add_argument('--template', choices=['enzyme', 'experiment', 'review'],
                        help='使用预设模板')
    parser.add_argument('-p', '--prompt', help='自定义提取提示')
    parser.add_argument('--format', choices=['markdown', 'csv'], default='markdown',
                        help='输出格式 (默认: markdown)')
    parser.add_argument('--model', help='LLM 模型名称')
    parser.add_argument('--temperature', type=float, help='LLM 温度参数')
    parser.add_argument('--print', action='store_true', help='打印结果到终端')

    args = parser.parse_args()

    # 检查输入文件
    if not os.path.exists(args.input):
        print(f"错误: 输入文件不存在: {args.input}")
        return 1

    # 加载配置
    config = Config()
    if not config.validate():
        return 1

    # 检查 Mathpix 配置
    if args.ocr == 'mathpix':
        if not config.mathpix_app_id or not config.mathpix_app_key:
            print("错误: Mathpix OCR 需要设置 MATHPIX_APP_ID 和 MATHPIX_APP_KEY 环境变量")
            return 1

    # 确定提取提示
    prompt = args.prompt
    if args.template:
        prompt = PRESET_TEMPLATES.get(args.template)
        if not prompt:
            print(f"错误: 未知的模板: {args.template}")
            return 1
        print(f"使用预设模板: {args.template}")

    if not prompt:
        print("错误: 需要指定 --template 或 --prompt")
        parser.print_help()
        return 1

    # 步骤 1: 提取 PDF 内容
    print(f"\n{'='*60}")
    print(f"步骤 1: 提取 PDF 内容")
    print(f"{'='*60}")
    print(f"输入文件: {args.input}")
    print(f"OCR 方式: {args.ocr}")

    if args.ocr == 'mathpix':
        content = PDFProcessor.extract_text_mathpix(
            args.input,
            config.mathpix_app_id,
            config.mathpix_app_key
        )
    else:
        content = PDFProcessor.extract_text_pymupdf(args.input)

    if not content:
        print("错误: PDF 内容提取失败")
        return 1

    print(f"✓ 提取成功，内容长度: {len(content)} 字符")

    # 步骤 2: AI 数据提取
    print(f"\n{'='*60}")
    print(f"步骤 2: AI 数据提取")
    print(f"{'='*60}")

    extractor = DataExtractor(config)
    result = extractor.extract_data(content, prompt, args.model, args.temperature)

    if not result:
        print("错误: 数据提取失败")
        return 1

    print(f"✓ 提取成功，结果长度: {len(result)} 字符")

    # 步骤 3: 保存输出
    print(f"\n{'='*60}")
    print(f"步骤 3: 保存输出")
    print(f"{'='*60}")

    OutputHandler.save_output(result, args.output, args.format)

    # 打印结果
    if args.print:
        print(f"\n{'='*60}")
        print(f"提取结果:")
        print(f"{'='*60}\n")
        print(result)

    print(f"\n✓ 完成！")

    return 0


if __name__ == '__main__':
    sys.exit(main())
