#!/usr/bin/env python3
"""
批量提取脚本 - 处理文件夹中的多个 PDF 文件
"""

import os
import sys
import argparse
from pathlib import Path
from extractor import PDFProcessor, DataExtractor, OutputHandler, Config, PRESET_TEMPLATES


def batch_extract(input_dir: str, output_dir: str, template: str = None,
                  custom_prompt: str = None, ocr: str = 'pymupdf',
                  output_format: str = 'markdown'):
    """
    批量提取 PDF 数据

    Args:
        input_dir: 输入文件夹路径
        output_dir: 输出文件夹路径
        template: 预设模板名称
        custom_prompt: 自定义提示
        ocr: OCR 方式
        output_format: 输出格式
    """
    # 确定提取提示
    prompt = custom_prompt
    if template:
        prompt = PRESET_TEMPLATES.get(template)

    if not prompt:
        print(f"错误: 无效的模板或缺少提示")
        return False

    # 加载配置
    config = Config()
    if not config.validate():
        return False

    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 扫描 PDF 文件
    input_path = Path(input_dir)
    pdf_files = list(input_path.glob('*.pdf'))

    if not pdf_files:
        print(f"错误: 在 {input_dir} 中未找到 PDF 文件")
        return False

    print(f"找到 {len(pdf_files)} 个 PDF 文件\n")

    # 初始化提取器
    extractor = DataExtractor(config)

    # 扩展名
    ext = '.csv' if output_format == 'csv' else '.md'

    # 处理每个文件
    success_count = 0
    failed_files = []

    for i, pdf_file in enumerate(pdf_files, 1):
        output_file = output_path / f"{pdf_file.stem}{ext}"

        print(f"[{i}/{len(pdf_files)}] 处理: {pdf_file.name}")
        print(f"  输出: {output_file}")

        try:
            # 提取 PDF 内容
            if ocr == 'mathpix':
                content = PDFProcessor.extract_text_mathpix(
                    str(pdf_file),
                    config.mathpix_app_id,
                    config.mathpix_app_key
                )
            else:
                content = PDFProcessor.extract_text_pymupdf(str(pdf_file))

            if not content:
                print(f"  ✗ PDF 提取失败")
                failed_files.append(pdf_file.name)
                continue

            # AI 数据提取
            result = extractor.extract_data(content, prompt)

            if not result:
                print(f"  ✗ 数据提取失败")
                failed_files.append(pdf_file.name)
                continue

            # 保存结果
            OutputHandler.save_output(result, str(output_file), output_format)
            print(f"  ✓ 成功\n")
            success_count += 1

        except Exception as e:
            print(f"  ✗ 错误: {e}\n")
            failed_files.append(pdf_file.name)

    # 总结
    print(f"{'='*60}")
    print(f"批量提取完成！")
    print(f"{'='*60}")
    print(f"总计: {len(pdf_files)} 个文件")
    print(f"成功: {success_count} 个")
    print(f"失败: {len(failed_files)} 个")

    if failed_files:
        print(f"\n失败的文件:")
        for f in failed_files:
            print(f"  - {f}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description='批量提取科学文献数据',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用酶动力学模板批量处理
  %(prog)s ./papers ./results --template enzyme

  # 使用自定义提示
  %(prog)s ./papers ./results -p "提取所有表格数据" --ocr mathpix

  # 输出 CSV 格式
  %(prog)s ./papers ./results --template experiment --format csv
        """
    )

    parser.add_argument('input', help='输入文件夹路径（包含 PDF 文件）')
    parser.add_argument('output', help='输出文件夹路径')
    parser.add_argument('--template', choices=['enzyme', 'experiment', 'review'],
                        help='使用预设模板')
    parser.add_argument('-p', '--prompt', help='自定义提取提示')
    parser.add_argument('--ocr', choices=['pymupdf', 'mathpix'], default='pymupdf',
                        help='OCR 方式 (默认: pymupdf)')
    parser.add_argument('--format', choices=['markdown', 'csv'], default='markdown',
                        help='输出格式 (默认: markdown)')

    args = parser.parse_args()

    if not os.path.isdir(args.input):
        print(f"错误: 输入路径不是文件夹: {args.input}")
        return 1

    if not args.template and not args.prompt:
        print("错误: 需要指定 --template 或 --prompt")
        parser.print_help()
        return 1

    success = batch_extract(
        args.input,
        args.output,
        args.template,
        args.prompt,
        args.ocr,
        args.format
    )

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
