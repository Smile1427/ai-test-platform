"""AI生成测试数据"""
from zai import ZhipuAiClient
import config
import json
import os
import yaml


class DataGenerator:
    def __init__(self):
        self.client = ZhipuAiClient(api_key=config.ZHIPU_API_KEY)

    def generate_data(self, field_rule: str, count: int = 10) -> list:
        """
        输入字段规则，AI生成测试数据

        Args:
            field_rule: 字段规则描述，比如"用户名：6-20位，字母数字下划线"
            count: 生成数据条数

        Returns:
            测试数据列表
        """
        prompt = f"""你是一个测试数据生成专家。请根据以下字段规则，生成测试数据。

【字段规则】
{field_rule}

【要求】
1. 生成 {count} 条测试数据
2. 覆盖以下类型：
   - 正常值（3条）
   - 边界值（3条，比如最小值、最大值、刚好超出）
   - 异常值（4条，比如空值、特殊字符、超长、格式错误）
3. 返回JSON数组，每条数据包含 type 和 value 两个字段
4. 不要解释，直接返回JSON

【输出格式示例】
[
  {{"type": "正常", "value": "testuser123"}},
  {{"type": "边界", "value": "abc123"}},
  {{"type": "异常", "value": ""}}
]

请直接返回JSON数组。"""

        for attempt in range(3):
            response = self.client.chat.completions.create(
                model=config.ZHIPU_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )

            content = response.choices[0].message.content
            content = self._clean_json(content)

            try:
                data = json.loads(content)
                print(f"第 {attempt + 1} 次尝试解析成功")
                return data
            except json.JSONDecodeError as e:
                print(f"第 {attempt + 1} 次解析失败: {e}")
                if attempt == 2:
                    print("重试次数已达上限")
                    print(content)
                    return []

        return []

    def _clean_json(self, content: str) -> str:
        """清理AI返回的markdown标记"""
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

        return content

    def save_data(self, data: list, filename: str = "test_data/generated_data.json"):
        """保存测试数据"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"已保存 {len(data)} 条测试数据到 {filename}")


if __name__ == "__main__":
    generator = DataGenerator()

    # 示例：生成用户名测试数据
    data = generator.generate_data(
        field_rule="用户名：长度6-20位，只能包含字母、数字、下划线",
        count=10
    )

    print(f"\n生成了 {len(data)} 条测试数据：\n")
    for i, item in enumerate(data, 1):
        print(f"{i}. [{item.get('type')}] {repr(item.get('value'))}")

    generator.save_data(data)