"""运行所有测试"""
"""一键运行所有测试"""
import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def run_step(name, cmd, cwd=None):
    print(f"\n{'='*60}")
    print(f"▶ {name}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True, cwd=cwd or BASE_DIR)
    if result.returncode != 0:
        print(f"❌ {name} 失败")
        return False
    print(f"✅ {name} 完成")
    return True


def main():
    print("=" * 60)
    print("在线教育平台 - 一键测试")
    print("=" * 60)

    if not run_step("接口自动化测试", "python tests/case_runner.py"):
        print("\n⚠️ 接口测试失败，流程终止")
        sys.exit(1)

    run_step("AI功能测试", "python -m pytest test_ai/test_ai_features.py -v")
    run_step("生成测试报告", "python tests/report_generator.py")

    print("\n" + "=" * 60)
    print("✅ 所有测试执行完毕")
    print(f"📊 报告位置: reports/test_report.html")
    print("=" * 60)


if __name__ == "__main__":
    main()