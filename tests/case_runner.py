"""用例执行器 - 读取YAML用例，自动执行接口测试"""
import yaml
import requests
import os
import json
from datetime import datetime
import time


BASE_URL = "http://127.0.0.1:8000"


class CaseRunner:
    def __init__(self):
        self.results = []
        self.failed_logs = []

    def load_cases(self, filename: str = "test_data/cases.yaml") -> list:
        """加载YAML用例"""
        with open(filename, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def execute_case(self, case: dict) -> dict:
        """执行单条用例"""
        name = case.get("name")
        method = case.get("method", "GET").upper()
        interface = case.get("interface", "")
        params = dict(case.get("params", {}))
        if "超长" in case.get("name", "") and "content" in params:
            params["content"] = "a" * 600
        expected = case.get("expected", "")

        # 注册接口用动态用户名
        if interface == "/api/user/register" and "username" in params:
            # 只有预期返回200的用例，才替换成动态用户名
            if "返回200" in expected:
                params["username"] = f"user_{int(time.time() * 1000) % 1000000}"

        import re
        path_params = re.findall(r"\{(\w+)\}", interface)
        for p in path_params:
            if p in params:
                # params里有这个参数，用它替换
                interface = interface.replace(f"{{{p}}}", str(params[p]))
                params.pop(p)
            else:
                # params里没有，用默认值1
                interface = interface.replace(f"{{{p}}}", "1")

        url = BASE_URL + interface
        result = {
            "name": name,
            "module": case.get("module"),
            "type": case.get("type"),
            "interface": interface,
            "method": method,
            "params": params,
            "expected": expected,
            "actual_status": None,
            "actual_body": None,
            "passed": False,
            "error": None,
        }

        try:
            if method == "GET":
                response = requests.get(url, params=params, timeout=60)
            elif method == "POST":
                response = requests.post(url, json=params, timeout=60)
            elif method == "DELETE":
                response = requests.delete(url, params=params, timeout=60)
            elif method == "PUT":
                response = requests.put(url, json=params, timeout=60)
            else:
                result["error"] = f"不支持的方法: {method}"
                return result

            result["actual_status"] = response.status_code
            result["actual_body"] = response.text[:500]

            # 简单断言：从expected里提取预期状态码
            import re
            match = re.search(r"返回(\d+)", expected)
            if match:
                expected_code = int(match.group(1))
                result["passed"] = (response.status_code == expected_code)
                if not result["passed"]:
                    result["error"] = f"预期状态码{expected_code}，实际{response.status_code}"
            else:
                result["passed"] = (response.status_code < 500)

        except Exception as e:
            result["error"] = str(e)

        # 失败时收集日志
        if not result["passed"]:
            self.failed_logs.append({
                "case_name": name,
                "interface": f"{method} {interface}",
                "params": params,
                "expected": expected,
                "actual_status": result["actual_status"],
                "actual_body": result["actual_body"],
                "error": result["error"],
            })

        return result

    def run_all(self, cases: list) -> dict:
        """执行所有用例"""
        try:
            requests.delete(f"{BASE_URL}/api/comment/clean_test_data", timeout=5)
            print("已清理测试数据\n")
        except Exception as e:
            print(f"清理失败（可忽略）: {e}\n")

        print(f"开始执行 {len(cases)} 条用例...\n")
        passed = 0
        failed = 0

        for i, case in enumerate(cases, 1):
            result = self.execute_case(case)
            self.results.append(result)

            status = "✅" if result["passed"] else "❌"
            print(f"{i}. {status} [{result['module']}] {result['name']}")
            if not result["passed"]:
                print(f"   错误: {result['error']}")
                failed += 1
            else:
                passed += 1

        # 保存结果
        self.save_results()
        self.save_failed_logs()

        return {
            "total": len(cases),
            "passed": passed,
            "failed": failed,
        }

    def save_results(self, filename: str = "test_data/execution_results.json"):
        """保存执行结果"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n执行结果已保存到 {filename}")

    def save_failed_logs(self, filename: str = "test_data/failed_logs.json"):
        """保存失败日志，供AI缺陷分析使用"""
        if self.failed_logs:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.failed_logs, f, ensure_ascii=False, indent=2)
            print(f"失败日志已保存到 {filename}，共 {len(self.failed_logs)} 条")
        else:
            print("没有失败用例")


if __name__ == "__main__":
    runner = CaseRunner()
    cases = runner.load_cases()
    summary = runner.run_all(cases)

    print(f"\n{'='*50}")
    print(f"测试汇总: 总计 {summary['total']} 条，通过 {summary['passed']}，失败 {summary['failed']}")
    print(f"{'='*50}")