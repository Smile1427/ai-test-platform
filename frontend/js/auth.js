// 检查是否登录
function checkLogin() {
    const token = getToken();
    if (!token) {
        alert("请先登录");
        window.location.href = "login.html";
        return false;
    }
    return true;
}

// 退出登录
function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("userId");
    window.location.href = "login.html";
}