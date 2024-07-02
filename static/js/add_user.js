window.addEventListener('load', () => {

    let password = Math.random().toString(36).slice(-10);
    $('#id_password1').val(password);
    $('#id_password2').val(password);
    $('#password').html(password);
    navigator.clipboard.writeText(password);

})