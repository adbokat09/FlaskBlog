const mainUrl = 'http://127.0.0.1:5000';
const singInBtn = document.getElementById('header__sing_in');
const logOutBtn = document.getElementById('header__log_out');
const newPostBtn = document.getElementById('posts__new_post')
const titleBlogP = document.getElementById('title')
const deletePostBtn = document.getElementById('delete')
const loginOption = document.getElementById('login_option')
const signUpOption = document.getElementById('sign_up_option')

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

if (newPostBtn) {
    newPostBtn.onclick = function () {
        location.href = `${mainUrl}/create`;
    }
}

if (titleBlogP) {
    titleBlogP.onclick = function () {
        location.href = `${mainUrl}/`
    }
}

if (loginOption) {
    loginOption.onclick = function () {
        location.href = `${mainUrl}/auth/login`
    }
}

if (signUpOption) {
    signUpOption.onclick = function () {
        location.href = `${mainUrl}/auth/register`
    }
}
