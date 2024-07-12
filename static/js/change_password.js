window.addEventListener('load', () => {

    $('.teams-change-password').on('click', (e) => {
        let [password, buyerId, pk] = e.target.id.split('-');
        $('.teams-password-title > span').html(buyerId);
        $('.teams-background').css('display', 'flex');
        $('.teams-background-change-password').attr('id', `password-${pk}`);
    })
    
    $('.teams-background-change-password').on('click', (e) => {
        const token = $('input[name=csrfmiddlewaretoken]').val();
        const userId = e.target.id.replace('password-', '');
        $.ajax({
            method: "post",
            url: "/main/change_password/",
            data: {user_id: userId, csrfmiddlewaretoken: token},
            success: (data) => {
                let password = data['result'];
                $('.teams-password').html(password);
                navigator.clipboard.writeText(password);
            },
            error: (data) => {
            }
        });
    })

    $('.teams-background').on('click', (e) => {
        if(e.target.classList.contains('teams-background')) {
            $('.teams-background-change-password').attr('id', '');
            $('.teams-password').html('');
            $('.teams-background').css('display', '');
            $('.teams-password-title > span').html('');
        }
    })
})