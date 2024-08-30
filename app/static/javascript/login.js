function togglePassword() {
    var passwordField = document.getElementById("password");
    var showPassword = document.getElementById("showPassword");
    if (passwordField.type === "password") {
        passwordField.type = "text";
    } else {
        passwordField.type = "password";
    }
}
