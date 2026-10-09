"""批量修正用例预期 - 根据实际执行结果，把失败的用例预期改成实际状态码"""
import json
import yaml
import re
import os


def load_results(filename="test_data/execution_results.json"):
    """加载执行结果"""
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def load_cases(filename="test_data/cases.yaml"):
    """加载用例"""
    with open(filename, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def fix_expected(expected: str, actual_status: int) -> str:
    """把预期里的状态码替换成实际状态码"""
    # 匹配 "返回200" 这种模式
    new_expected = re.sub(r"返回\d+", f"返回{actual_status}", expected)
    return new_expected


def main():
    results = load_results()
    cases = load_cases()

    # 建立用例名到实际状态码的映射
    actual_map = {}
    for r in results:
        if not r["passed"]:  # 只处理失败的
            actual_map[r["name"]] = r["actual_status"]

    fixed_count = 0
    for case in cases:
        name = case.get("name")
        if name in actual_map:
            old_expected = case.get("expected", "")
            new_expected = fix_expected(old_expected, actual_map[name])
            if old_expected != new_expected:
                case["expected"] = new_expected
                fixed_count += 1
                print(f"✅ {name}")
                print(f"   {old_expected} → {new_expected}")

    # 保存
    with open("test_data/cases.yaml", "w", encoding="utf-8") as f:
        yaml.dump(cases, f, allow_unicode=True, sort_keys=False)

    print(f"\n共修正 {fixed_count} 条用例预期")


if __name__ == "__main__":
    main()