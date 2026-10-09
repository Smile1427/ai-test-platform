"""AI辅助生成测试用例 - 对接在线教育平台"""
from zai import ZhipuAiClient
import config
import json
import yaml
import os


class CaseGenerator:
    def __init__(self):
        self.client = ZhipuAiClient(api_key=config.ZHIPU_API_KEY)

    def load_requirement_doc(self, doc_path: str = "test_data/interface_doc.txt") -> str:
        """读取接口需求文档"""
        if not os.path.exists(doc_path):
            raise FileNotFoundError(f"接口文档不存在: {doc_path}")
        with open(doc_path, "r", encoding="utf-8") as f:
            return f.read()

    def generate_cases(self, requirement_doc: str, target_module: str = None, max_retries: int = 3) -> list:
        """根据接口文档，生成针对在线教育平台的测试用例"""
        module_hint = f"\n【重点模块】\n只生成「{target_module}」模块相关的测试用例。" if target_module else ""

        prompt = f"""你是一个资深测试工程师。请根据以下在线教育平台的接口文档，设计测试用例。

【接口文档】
{requirement_doc}
{module_hint}

【重要提示 - 数据库真实数据】
1. 数据库里已有的真实数据如下，请务必使用这些真实ID，不要自己编造：
   - 用户ID：1（已注册）、2（已注册）
   - 课程ID：1、2、3、4、5（共5门课程）
   - 订单ID：1（已存在）
   - 评论ID：1（已存在）
2. 如果要用"不存在的ID"测试异常场景，请统一用 99999，不要用101、102这种编造的ID
3. 如果需要"重复购买"场景，请用 user_id=1, course_id=1（该用户已购买过课程1）
4. 如果需要"未购买课程"场景，请用 user_id=1, course_id=3（该用户未购买课程3）

【要求】
1. 覆盖正常场景、异常场景、边界场景
2. 每个用例必须严格包含以下字段：
   - name：用例名称（字符串）
   - type：用例类型（正常/异常/边界）
   - module：所属模块（用户/课程/订单/AI/评论）
   - interface：接口路径（如 /api/user/login）
   - method：请求方法（GET/POST/DELETE）
   - params：请求参数（对象）
   - expected：预期结果（字符串，包含预期状态码）
3. 用例数量10-15条
4. 返回JSON数组，不要解释，不要markdown标记
5. 【重要】params里的值必须是实际的JSON值，不能写代码表达式。
   比如要写"content": ""，不能写"content": "a".repeat(256)；
   要写"username": "invaliduser!"，不能写"username": "x" * 20
6. 所有字符串用双引号，不能用单引号
7. 确保JSON格式完全合法
8. 【重要】expected里的状态码要和实际后端行为一致：
   - 参数类型错误（如字符串传给了int字段）后端会返回422，不是400
   - 路径参数为空后端会返回404，不是400
   - 后端的校验错误用400，但要注意区分

【输出格式示例】
[
  {{
    "name": "登录成功",
    "type": "正常",
    "module": "用户",
    "interface": "/api/user/login",
    "method": "POST",
    "params": {{"username": "test", "password": "123456"}},
    "expected": "返回200，包含token"
  }}
]

请直接返回JSON数组，确保每个对象都包含所有字段，params里的值都是实际值。"""

        for attempt in range(max_retries):
            response = self.client.chat.completions.create(
                model=config.ZHIPU_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            content = response.choices[0].message.content
            content = self._clean_json(content)

            try:
                cases = json.loads(content)
                cases = [self._normalize_case(c) for c in cases]
                print(f"第 {attempt + 1} 次尝试解析成功，生成 {len(cases)} 条用例")
                return cases
            except json.JSONDecodeError as e:
                print(f"第 {attempt + 1} 次解析失败: {e}")
                if attempt == max_retries - 1:
                    print("重试次数已达上限，放弃")
                    print("原始内容：")
                    print(content)
                    return []
                print("正在重试...\n")

        return []

    def _clean_json(self, content: str) -> str:
        """清理AI返回的markdown标记和多余字符"""
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        start = content.find("[")
        end = content.rfind("]")
        if start != -1 and end != -1:
            content = content[start:end + 1]

        # 修复常见的JSON语法错误
        import re
        # 修复 "a".repeat(N) → "aaa...a"
        def fix_repeat(match):
            char = match.group(1)
            count = int(match.group(2))
            return '"' + char * count + '"'
        content = re.sub(r'"([^"]*)"\s*\.repeat\((\d+)\)', fix_repeat, content)

        # 修复 "x" * N → "xxx...x"
        def fix_multiply(match):
            char = match.group(1)
            count = int(match.group(2))
            return '"' + char * count + '"'
        content = re.sub(r'"([^"]*)"\s*\*\s*(\d+)', fix_multiply, content)

        return content

    def _normalize_case(self, case: dict) -> dict:
        """兼容AI可能返回的中文字段名"""
        mapping = {
            "用例名称": "name", "name": "name",
            "用例类型": "type", "type": "type",
            "所属模块": "module", "module": "module",
            "接口路径": "interface", "interface": "interface",
            "请求方法": "method", "method": "method",
            "请求参数": "params", "params": "params",
            "预期结果": "expected", "expected": "expected",
        }
        return {mapping.get(k, k): v for k, v in case.items()}

    def save_cases(self, cases: list, filename: str = "test_data/cases.yaml"):
        """保存用例到YAML文件"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            yaml.dump(cases, f, allow_unicode=True, sort_keys=False)
        print(f"已保存 {len(cases)} 条用例到 {filename}")


if __name__ == "__main__":
    generator = CaseGenerator()

    print("正在读取接口文档...")
    doc = generator.load_requirement_doc()

    # 分批生成，每个模块单独生成
    modules = ["用户", "课程", "订单", "评论", "AI"]
    all_cases = []

    for module in modules:
        print(f"\n{'='*50}")
        print(f"正在生成「{module}」模块的测试用例...")
        print(f"{'='*50}")
        cases = generator.generate_cases(doc, target_module=module)
        print(f"✅ {module}模块生成 {len(cases)} 条用例")
        all_cases.extend(cases)

    print(f"\n{'='*50}")
    print(f"共生成 {len(all_cases)} 条测试用例")
    print(f"{'='*50}\n")

    for i, case in enumerate(all_cases, 1):
        print(f"{i}. [{case.get('type')}] [{case.get('module')}] {case.get('name')}")
        print(f"   接口: {case.get('method')} {case.get('interface')}")
        print(f"   参数: {case.get('params')}")
        print(f"   预期: {case.get('expected')}\n")

    generator.save_cases(all_cases)