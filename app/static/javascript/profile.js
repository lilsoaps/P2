let button_mudarPass = document.getElementById('change-password');
button_mudarPass.addEventListener('click', () => {
    let old_password = document.getElementById('old-password');
    let new_password = document.getElementById('new-password');
    let confirm_password = document.getElementById('confirm-password');
    
    // Clear previous errors
    let errorFields = document.querySelectorAll('.text-danger');
    errorFields.forEach(field => field.textContent = '');

    // Password validation
    if (new_password.value !== confirm_password.value) {
        document.getElementById('new-password-error').textContent = 'Passwords do not match.';
        new_password.style.borderColor = 'red';
        confirm_password.style.borderColor = 'red';
        return;
    }

    if (new_password.value.length < 12) {
        document.getElementById('new-password-error').textContent = 'Password must be at least 12 characters long.';
        new_password.style.borderColor = 'red';
        return;
    }

    // You can add more client-side validation here as needed

    // Send data to the server via AJAX
    const email = $("#email-input").val();
    $.ajax({
        type: "POST",
        url: "/profile",
        data: {
            'csrf_token': $('input[name="csrf_token"]').val(), // Ensure CSRF token is sent
            'op': '4',
            'email': email,
            'old-password': old_password.value,
            'new-password': new_password.value,
            'confirm-password': confirm_password.value
        },
        success: function (response) {
            if (response.errors) {
                // Show server-side errors
                if (response.errors['old-password']) {
                    document.getElementById('old-password-error').textContent = response.errors['old-password'];
                    old_password.style.borderColor = 'red';
                }
                if (response.errors['new-password']) {
                    document.getElementById('new-password-error').textContent = response.errors['new-password'];
                    new_password.style.borderColor = 'red';
                    confirm_password.style.borderColor = 'red';
                }
                if (response.errors['length']) {
                    document.getElementById('new-password-error').textContent = response.errors['length'];
                    new_password.style.borderColor = 'red';
                }
                if (response.errors['lowercase']) {
                    document.getElementById('new-password-error').textContent = response.errors['lowercase'];
                    new_password.style.borderColor = 'red';
                }
                if (response.errors['uppercase']) {
                    document.getElementById('new-password-error').textContent = response.errors['uppercase'];
                    new_password.style.borderColor = 'red';
                }
                if (response.errors['number']) {
                    document.getElementById('new-password-error').textContent = response.errors['number'];
                    new_password.style.borderColor = 'red';
                }
                if (response.errors['special']) {
                    document.getElementById('new-password-error').textContent = response.errors['special'];
                    new_password.style.borderColor = 'red';
                }

            } else {
                alert('Password changed successfully!');
                old_password.value = '';
                new_password.value = '';
                confirm_password.value = '';
                new_password.style.borderColor = 'white';
                confirm_password.style.borderColor = 'white';
            }
        }
    });
});
