"""AI辅助缺陷分析 - 批量分析真实失败日志"""
from zai import ZhipuAiClient
import config
import json
import os


class BatchDefectAnalyzer:
    def __init__(self):
        self.client = ZhipuAiClient(api_key=config.ZHIPU_API_KEY)

    def load_failed_logs(self, filename: str = "test_data/failed_logs.json") -> list:
        """加载失败日志"""
        if not os.path.exists(filename):
            print(f"失败日志文件不存在: {filename}")
            return []
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)

    def analyze_one(self, log: dict) -> dict:
        """分析单条失败日志"""
        prompt = f"""你是一个资深测试工程师。请分析以下测试失败日志。

【用例名称】
{log.get('case_name')}

【接口】
{log.get('interface')}

【请求参数】
{log.get('params')}

【预期结果】
{log.get('expected')}

【实际状态码】
{log.get('actual_status')}

【实际返回】
{log.get('actual_body')}

【错误信息】
{log.get('error')}

【要求】
请判断这是：
A. 真实缺陷（后端代码问题）
B. 用例问题（参数错误、路径错误、超时设置不合理）
C. 环境问题

返回JSON格式，包含：
- reason: 失败原因（一句话）
- category: 问题分类（真实缺陷/用例问题/环境问题）
- root_cause: 根因分析
- suggestion: 修复建议

直接返回JSON对象。"""

        for attempt in range(3):
            response = self.client.chat.completions.create(
                model=config.ZHIPU_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            content = self._clean_json(response.choices[0].message.content)
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                if attempt == 2:
                    return {"error": "解析失败"}

        return {}

    def _clean_json(self, content: str) -> str:
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1:
            content = content[start:end + 1]
        return content

    def analyze_all(self) -> list:
        """批量分析所有失败日志"""
        logs = self.load_failed_logs()
        if not logs:
            return []

        print(f"加载了 {len(logs)} 条失败日志，开始AI分析...\n")
        results = []

        for i, log in enumerate(logs, 1):
            print(f"[{i}/{len(logs)}] 分析: {log.get('case_name')}")
            result = self.analyze_one(log)
            result["case_name"] = log.get("case_name")
            result["interface"] = log.get("interface")
            results.append(result)

            print(f"  分类: {result.get('category')}")
            print(f"  原因: {result.get('reason')}")
            print(f"  建议: {result.get('suggestion')}\n")

        # 保存分析结果
        with open("test_data/defect_analysis.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"分析结果已保存到 test_data/defect_analysis.json")

        return results


if __name__ == "__main__":
    analyzer = BatchDefectAnalyzer()
    analyzer.analyze_all()