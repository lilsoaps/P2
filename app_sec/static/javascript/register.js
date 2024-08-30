$('#password1').on('keyup', function(){
    let passwordError = document.getElementById('password1-error');
    let password = document.getElementById('password1');
    let confPass = document.getElementById('password2');
    let strengthBar = document.getElementById('strength-bar');
    
    let strength = 0;
    if(password.value.length >= 12) strength++;
    if(/[a-z]/.test(password.value)) strength++;
    if(/[A-Z]/.test(password.value)) strength++;
    if(/[0-9]/.test(password.value)) strength++;
    if(/[@#$%^&+=_!]/.test(password.value)) strength++;

    if(strength === 1 || strength === 2) {
        strengthBar.className = "strength-bar weak";
    } else if (strength === 3) {
        strengthBar.className = "strength-bar fair";
    } else if (strength === 4) {
        strengthBar.className = "strength-bar good";
    } else if (strength === 5) {
        strengthBar.className = "strength-bar strong";
    } else {
        strengthBar.className = "strength-bar";
    }

    // Update password border color
    if(password.value.length > 0){
        if(password.value.length < 12 || strength < 3){
            password.style.borderColor = "red";
            confPass.style.borderColor = "red";
        }
        else{
            password.style.borderColor = "green";
            confPass.style.borderColor = "green";
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
    let password = document.getElementById('password1');
    let confPass = document.getElementById('password2');
    let passwordError = document.getElementById('password1-error');
    let confPassErr = document.getElementById('password2-error');
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
});

function togglePassword(id) {
    var passwordInput = document.getElementById(id);
    var originalType = passwordInput.type;
    var originalValue = passwordInput.value;

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
    } else {
        passwordInput.type = "password";
    }

    setTimeout(function() {
        passwordInput.type = originalType;
        passwordInput.value = originalValue;
    }, 200);  // Delay to ensure the change is noticeable
}

function toggleLastChar(id) {
    var passwordInput = document.getElementById(id);
    var originalType = passwordInput.type;
    var originalValue = passwordInput.value;

    if (originalValue.length > 0) {
        passwordInput.type = "text";  // Temporarily set to text to display the last character
        passwordInput.value = '*'.repeat(originalValue.length - 1) + originalValue.charAt(originalValue.length - 1);

        setTimeout(function() {
            passwordInput.type = originalType;
            passwordInput.value = originalValue;
        }, 200);  // Delay to ensure the change is noticeable
    }
}

