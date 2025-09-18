from flask import Flask, request, jsonify, Response
import requests
import os

app = Flask(__name__)

# 支持的外部 API 映射
API_MAP = {
    "/openrouter": "https://openrouter.ai/api/v1",
    "/siliconflow": "https://api.siliconflow.cn",
    "/bigmodel": "https://open.bigmodel.cn/api/anthropic",
    "/openai": "https://api.openai.com/v1"
}

@app.route('/<api_name>/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(api_name, subpath):
    if api_name not in API_MAP:
        return jsonify({"error": "Unsupported API"}), 404

    target_base = API_MAP[api_name]
    target_url = f"{target_base}/{subpath}"

    try:
        # 转发请求
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers={key: value for key, value in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            timeout=30
        )

        # 构造响应
        response = Response(resp.content, resp.status_code)
        for key, value in resp.headers.items():
            if key.lower() not in ['content-encoding', 'content-length', 'transfer-encoding', 'connection']:
                response.headers[key] = value

        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return """
    <h2>内网大模型API代理服务</h2>
    <p>支持路径：</p>
    <ul>
        <li><code>/openrouter/...</code> → openrouter.ai</li>
        <li><code>/siliconflow/...</code> → api.siliconflow.cn</li>
        <li><code>/bigmodel/...</code> → open.bigmodel.cn</li>
        <li><code>/openai/...</code> → api.openai.com</li>
    </ul>
    <p>示例调用：<code>curl http://内网IP:5000/openai/chat/completions -H "Authorization: Bearer YOUR_KEY" -d '{"model": "gpt-4", ...}'</code></p>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
