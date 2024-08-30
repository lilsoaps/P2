let signUp = document.getElementById('sign-up')



$('#username').on("focusout", function () {
    let usernameError = document.getElementById('username-error');
    let username = document.getElementById('username');
    if(username.value.length > 0){
        if(username.value.length < 3){
            usernameError.innerHTML = "Username must have 3 or more characters."
            username.style.borderColor = "red";
        }
        else{
            username.style.borderColor = "green";
            usernameError.innerHTML = "";
        }
    }
    else{
        username.style.borderColor = "white";
        usernameError.innerHTML = "";
    }
});

$('#email').on("focusout", function(){
    let emailError = document.getElementById('email-error')
    let email = document.getElementById('email')
    if(email.value.length > 0){
        email.style.borderColor = "green"
        emailError.innerHTML = ""
    }
    else{
        email.style.borderColor = "white";
        emailError.innerHTML = "";
    }
});

$('#password1').on('keyup', function(){
    let passwordError = document.getElementById('password1-error')
    let password = document.getElementById('password1') 
    let confPass = document.getElementById('password2')
    if(password.value.length > 0){
        if(password.value.length < 12){
            password.style.borderColor = "red";
            confPass.style.borderColor = "red";
        }
        else{
            passwordError.innerHTML = "";
        }
        if(password.value != confPass.value){
            password.style.borderColor = "red";
            confPass.style.borderColor = "red";
        }
    }
    else if(confPass.value.length == 0){
        password.style.borderColor = "white";
        confPass.style.borderColor = "white";
        passwordError.innerHTML = "";
    }
});
$('#password2').on('keyup', function(){
    let password = document.getElementById('password1') 
    let confPass = document.getElementById('password2')
    let passwordError = document.getElementById('password1-error')
    let confPassErr = document.getElementById('password2-error')
    if(confPass.value.length > 0){
        if(password.value == confPass.value && password.value.length > 11){
            password.style.borderColor = "green";
            confPass.style.borderColor = "green";
            confPassErr.innerHTML = "";
        }
        else{
            password.style.borderColor = "red";
            confPass.style.borderColor = "red";
            confPassErr.innerHTML = "";
        }
    }
    else if(password.value.length == 0){
        password.style.borderColor = "white";
        confPass.style.borderColor = "white";
        passwordError.innerHTML = "";
    }
})