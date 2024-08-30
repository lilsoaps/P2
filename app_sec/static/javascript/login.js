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
