const mainUrl = 'http://127.0.0.1:5000';
const singInBtn = document.getElementById('header__sing_in');
const logOutBtn = document.getElementById('header__log_out');

if (singInBtn) {
    singInBtn.onclick = function () {
        location.href = `${mainUrl}/auth/login`;
    };
}

if (logOutBtn) {
    logOutBtn.onclick = function () {
        location.href = `${mainUrl}/auth/logout`;
    }
}