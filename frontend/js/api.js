// 后端API地址
const API_BASE = "http://127.0.0.1:8000";

// 获取token
function getToken() {
    return localStorage.getItem("token");
}

// 保存token
function saveToken(token) {
    localStorage.setItem("token", token);
}

// 通用请求方法
async function request(url, method = "GET", body = null) {
    const options = {
        method: method,
        headers: { "Content-Type": "application/json" }
    };
    if (body) options.body = JSON.stringify(body);
    const response = await fetch(API_BASE + url, options);
    const data = await response.json();
    return { status: response.status, data: data };
}

// 显示消息
function showMsg(text, type = "success") {
    const el = document.getElementById("msg");
    if (el) {
        el.textContent = text;
        el.className = "msg msg-" + type;
        setTimeout(() => { el.textContent = ""; el.className = ""; }, 3000);
    }
}