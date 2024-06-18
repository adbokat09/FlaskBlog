const mainUrl = 'http://127.0.0.1:5000';

document.getElementById('header__sing_in').onclick = function (){
    location.href = `${mainUrl}/auth/login`
};
document.getElementById('header__sing_out').onclick = function () {
    location.href = `${mainUrl}/auth/logout`
}