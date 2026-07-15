"""真实 AI provider 链路测试：假 Chat Completions 服务 + 失败回退。"""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from app.services import ai_provider

# 模型故意返回：markdown 围栏、字段不全、confidence 越界 —— 考验提取与归一化
MODEL_JSON = {
    "job_name": "大模型平台工程师",
    "required_skills": ["Python", "RAG", "Kubernetes"],
    "confidence": 1.7,
    "extra_field": "模型自己加的字段",
}


class _FakeOpenAI(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        assert "output_schema" in body["messages"][1]["content"]
        content = "好的，以下是结果：\n```json\n" + json.dumps(MODEL_JSON, ensure_ascii=False) + "\n```"
        data = json.dumps({"choices": [{"message": {"role": "assistant", "content": content}}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):  # 静默测试日志
        pass


def _configure(monkeypatch, base_url: str):
    monkeypatch.setattr(ai_provider, "AI_PROVIDER", "openai_compatible")
    monkeypatch.setattr(ai_provider, "AI_API_BASE_URL", base_url)
    monkeypatch.setattr(ai_provider, "AI_API_KEY", "test-key")
    monkeypatch.setattr(ai_provider, "AI_MODEL", "test-model")
    monkeypatch.setenv("NO_PROXY", "127.0.0.1")
    monkeypatch.setenv("no_proxy", "127.0.0.1")


def test_openai_compatible_call_and_normalization(monkeypatch):
    server = HTTPServer(("127.0.0.1", 0), _FakeOpenAI)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        _configure(monkeypatch, f"http://127.0.0.1:{server.server_address[1]}/v1")
        response = ai_provider.analyze_with_ai("jd_parse", {"text": "招聘大模型平台工程师，要求 Python、RAG、Kubernetes"})
        assert response["provider"] == "openai_compatible"
        assert response["fallback"] is False
        result = response["result"]
        assert result["job_name"] == "大模型平台工程师"
        assert result["required_skills"] == ["Python", "RAG", "Kubernetes"]
        assert result["confidence"] == 1.0  # 越界置信度被钳制到 0-1
        # 模型未返回的关键字段由本地基线补齐
        assert "evidence" in result and "domain" in result and "level" in result
        assert result["extra_field"] == "模型自己加的字段"
    finally:
        server.shutdown()


def test_fallback_to_mock_when_provider_unreachable(monkeypatch):
    _configure(monkeypatch, "http://127.0.0.1:1/v1")  # 不可达地址
    response = ai_provider.analyze_with_ai("jd_parse", {"text": "招聘数据分析师，要求 SQL、Python"})
    assert response["fallback"] is True
    assert response["provider"] == "mock"
    assert response["requested_provider"] == "openai_compatible"
    assert response["fallback_reason"]
    assert "confidence" in response["result"]
