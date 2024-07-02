window.addEventListener('load', () => {

    $(document).on('click', '.teams-change-password', (e) => {
        const token = $('input[name=csrfmiddlewaretoken]').val();
        const userId = e.target.id.replace('password-', '');
        $.ajax({
            method: "post",
            url: "/main/change_password/",
            data: {user_id: userId, csrfmiddlewaretoken: token},
            success: (data) => {
                let password = data['result'];
                e.target.innerHTML = password;
                e.target.classList.remove('teams-change-password');
                navigator.clipboard.writeText(password);
            },
            error: (data) => {
            }
        });
    })
})