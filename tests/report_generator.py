"""测试报告生成器"""
import json
import os
from datetime import datetime


class ReportGenerator:
    def __init__(self, result_file: str = "test_data/execution_results.json"):
        with open(result_file, "r", encoding="utf-8") as f:
            self.results = json.load(f)

    def generate_html(self, output: str = "reports/test_report.html"):
        """生成HTML测试报告"""
        os.makedirs(os.path.dirname(output), exist_ok=True)

        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0

        # 统计各模块
        modules = {}
        for r in self.results:
            m = r.get("module", "未知")
            if m not in modules:
                modules[m] = {"total": 0, "passed": 0}
            modules[m]["total"] += 1
            if r["passed"]:
                modules[m]["passed"] += 1

        rows = ""
        for r in self.results:
            status = "✅ 通过" if r["passed"] else "❌ 失败"
            color = "#28a745" if r["passed"] else "#dc3545"
            rows += f"""
            <tr>
                <td>{r.get('name')}</td>
                <td>{r.get('module')}</td>
                <td>{r.get('type')}</td>
                <td>{r.get('method')} {r.get('interface')}</td>
                <td style="color:{color};font-weight:bold;">{status}</td>
                <td>{r.get('actual_status')}</td>
            </tr>
            """

        module_rows = ""
        for m, data in modules.items():
            rate = data['passed'] / data['total'] * 100
            module_rows += f"""
            <tr>
                <td>{m}</td>
                <td>{data['total']}</td>
                <td>{data['passed']}</td>
                <td>{rate:.1f}%</td>
            </tr>
            """

        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>测试报告 - 在线教育平台</title>
    <style>
        body {{ font-family: "Microsoft YaHei", sans-serif; margin: 30px; background: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #4a90d9; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .summary-card {{ flex: 1; padding: 20px; border-radius: 8px; text-align: center; }}
        .card-total {{ background: #e3f2fd; }}
        .card-pass {{ background: #d4edda; }}
        .card-fail {{ background: #f8d7da; }}
        .summary-card .num {{ font-size: 32px; font-weight: bold; }}
        .summary-card .label {{ color: #666; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #4a90d9; color: white; }}
        tr:hover {{ background: #f9f9f9; }}
        .footer {{ margin-top: 30px; text-align: center; color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>在线教育平台 - 测试报告</h1>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <div class="summary">
            <div class="summary-card card-total">
                <div class="num">{total}</div>
                <div class="label">总用例数</div>
            </div>
            <div class="summary-card card-pass">
                <div class="num">{passed}</div>
                <div class="label">通过</div>
            </div>
            <div class="summary-card card-fail">
                <div class="num">{failed}</div>
                <div class="label">失败</div>
            </div>
            <div class="summary-card card-total">
                <div class="num">{pass_rate:.1f}%</div>
                <div class="label">通过率</div>
            </div>
        </div>

        <h2>模块统计</h2>
        <table>
            <thead>
                <tr><th>模块</th><th>总数</th><th>通过</th><th>通过率</th></tr>
            </thead>
            <tbody>{module_rows}</tbody>
        </table>

        <h2>用例详情</h2>
        <table>
            <thead>
                <tr><th>用例名称</th><th>模块</th><th>类型</th><th>接口</th><th>状态</th><th>实际状态码</th></tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>

        <div class="footer">
            本报告由AI辅助测试平台自动生成
        </div>
    </div>
</body>
</html>
        """

        with open(output, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"测试报告已生成: {output}")


if __name__ == "__main__":
    generator = ReportGenerator()
    generator.generate_html()