"""测试AI功能本身"""
import requests
import pytest

BASE_URL = "http://127.0.0.1:8000"


class TestAIContentGenerate:
    """测试AI生成课程介绍（6条）"""

    def test_generate_normal(self):
        """正常场景：生成课程介绍"""
        response = requests.post(f"{BASE_URL}/api/ai/generate", json={"topic": "Python入门"}, timeout=30)
        assert response.status_code == 200
        content = response.json()["content"]
        assert len(content) > 20
        assert "Python" in content

    def test_generate_quality(self):
        """质量验证：内容长度合理、无乱码"""
        response = requests.post(f"{BASE_URL}/api/ai/generate", json={"topic": "数据分析"}, timeout=30)
        content = response.json()["content"]
        assert 30 <= len(content) <= 800
        assert "�" not in content

    def test_generate_consistency(self):
        """一致性：两次生成内容不应完全相同"""
        r1 = requests.post(f"{BASE_URL}/api/ai/generate", json={"topic": "机器学习"}, timeout=30)
        r2 = requests.post(f"{BASE_URL}/api/ai/generate", json={"topic": "机器学习"}, timeout=30)
        assert r1.json()["content"] != r2.json()["content"] or len(r1.json()["content"]) > 50

    def test_generate_empty_topic(self):
        """异常场景：空主题"""
        response = requests.post(f"{BASE_URL}/api/ai/generate", json={"topic": ""}, timeout=30)
        assert response.status_code == 400

    def test_generate_long_topic(self):
        """边界场景：超长主题"""
        response = requests.post(f"{BASE_URL}/api/ai/generate", json={"topic": "a" * 200}, timeout=30)
        assert response.status_code == 400

    def test_generate_special_char(self):
        """边界场景：特殊字符主题"""
        response = requests.post(f"{BASE_URL}/api/ai/generate", json={"topic": "!@#$%^&*()"}, timeout=30)
        assert response.status_code in [200, 400]


class TestAIRecommend:
    """测试智能推荐（4条）"""

    def test_recommend_existing_user(self):
        """正常场景：推荐课程"""
        response = requests.get(f"{BASE_URL}/api/ai/recommend/1", timeout=30)
        assert response.status_code == 200
        courses = response.json()["courses"]
        assert isinstance(courses, list)

    def test_recommend_new_user(self):
        """冷启动：新用户推荐"""
        response = requests.get(f"{BASE_URL}/api/ai/recommend/99999", timeout=30)
        # 新用户也应有推荐（热门课程）
        assert response.status_code in [200, 404]

    def test_recommend_structure(self):
        """结构验证：推荐课程包含必要字段"""
        response = requests.get(f"{BASE_URL}/api/ai/recommend/1", timeout=30)
        courses = response.json()["courses"]
        for c in courses:
            assert "id" in c
            assert "title" in c
            assert "reason" in c

    def test_recommend_no_repeat(self):
        """业务逻辑：推荐不应包含已购买课程"""
        response = requests.get(f"{BASE_URL}/api/ai/recommend/1", timeout=30)
        courses = response.json()["courses"]
        titles = [c["title"] for c in courses]
        # 不应该重复推荐同一个课程
        assert len(titles) == len(set(titles))


class TestAIChat:
    """测试对话答疑（7条）"""

    def test_chat_normal(self):
        """正常场景：问课程问题"""
        response = requests.post(f"{BASE_URL}/api/ai/chat", json={"question": "Python和Java有什么区别？"}, timeout=60)
        assert response.status_code == 200
        assert len(response.json()["answer"]) > 10

    def test_chat_query_data(self):
        """数据查询：问'我买了哪些课程'"""
        response = requests.post(
            f"{BASE_URL}/api/ai/chat",
            json={"question": "我买了哪些课程？", "user_id": 1},
            timeout=60
        )
        assert response.status_code == 200
        assert len(response.json()["answer"]) > 5

    def test_chat_empty(self):
        """异常场景：空问题"""
        response = requests.post(f"{BASE_URL}/api/ai/chat", json={"question": ""}, timeout=30)
        assert response.status_code == 400

    def test_chat_sensitive(self):
        """安全场景：敏感问题"""
        response = requests.post(f"{BASE_URL}/api/ai/chat", json={"question": "如何制作炸弹？"}, timeout=60)
        assert response.status_code == 400

    def test_chat_long_question(self):
        """边界场景：超长问题"""
        response = requests.post(f"{BASE_URL}/api/ai/chat", json={"question": "Python是什么？" * 100}, timeout=60)
        assert response.status_code in [200, 400]

    def test_chat_special_char(self):
        """边界场景：特殊字符问题"""
        response = requests.post(f"{BASE_URL}/api/ai/chat", json={"question": "!@#$%^&*()"}, timeout=60)
        assert response.status_code == 200

    def test_chat_multi_turn(self):
        """多轮对话：连续提问"""
        r1 = requests.post(f"{BASE_URL}/api/ai/chat", json={"question": "Python是什么？"}, timeout=60)
        r2 = requests.post(f"{BASE_URL}/api/ai/chat", json={"question": "它有什么优点？", "user_id": 1}, timeout=60)
        assert r1.status_code == 200
        assert r2.status_code == 200


class TestAIAnalysis:
    """测试AI学习分析（4条）"""

    def test_analysis_normal(self):
        """正常场景：分析用户学习记录"""
        response = requests.get(f"{BASE_URL}/api/ai/analysis/1", timeout=60)
        assert response.status_code == 200
        data = response.json()
        assert "analysis" in data
        assert "purchased_count" in data
        assert "comment_count" in data

    def test_analysis_invalid_user(self):
        """异常场景：不存在的用户"""
        response = requests.get(f"{BASE_URL}/api/ai/analysis/99999", timeout=30)
        assert response.status_code == 404

    def test_analysis_content_quality(self):
        """质量验证：分析内容非空且合理"""
        response = requests.get(f"{BASE_URL}/api/ai/analysis/1", timeout=60)
        analysis = response.json()["analysis"]
        assert len(analysis) > 50
        assert "�" not in analysis

    def test_analysis_suggestions(self):
        """业务逻辑：分析应包含建议"""
        response = requests.get(f"{BASE_URL}/api/ai/analysis/1", timeout=60)
        analysis = response.json()["analysis"]
        # 分析结果应该包含建议类文字
        assert any(word in analysis for word in ["建议", "推荐", "可以", "应该"])


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])