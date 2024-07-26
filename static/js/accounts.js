window.addEventListener('load', () => {

    let dateStart = $('.accounts-update-chosen-date').html();
    let dateStop = dateStart;

    $('.stats-update').on('click', (e) => {
        let [type, update, id] = e.target.id.split('-');
        $('.accounts-update').attr('id', `${type}-button-${id}`);
        $('.teams-background').css('display', 'flex');
        $('.teams-password-title').html(`${type == 'account' ? 'Аккаунт' : 'Кабинет'} - ${id}`);
    })

    $('.teams-background').on('click', (e) => {
        if(e.target.classList.contains('teams-background')) {
            $('.accounts-update').attr('id', '');
            $('.teams-background').css('display', '');
            $('.teams-password-title').html('');
        }
    })

    $('.accounts-update-accounts').on('click', (e) => {
        e.target.style.display = 'none';
        $('.stats-update-loading.accounts').css('display', '');
        const token = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            method: "post",
            url: '/main/update_accounts/',
            data: {csrfmiddlewaretoken: token},
            success: (data) => {
                window.location.reload();
            },
            error: (data) => {
            }
        });
    })

    $('.accounts-update').on('click', (e) => {
        let [type, button, id] = e.target.id.split('-');
        $(`#${type}-img-${id}`).css('display', '');
        $(`#${type}-update-${id}`).css('display', 'none');
        $('.accounts-update').attr('id', '');
        $('.teams-background').css('display', '');
        $('.teams-password-title').html('');
        const token = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            method: "post",
            url: `/main/get_${type}_costs/`,
            data: {id: id, date_start: dateStart, date_stop: dateStop, csrfmiddlewaretoken: token},
            success: (data) => {
                $(`#${type}-img-${id}`).css('display', 'none');
                $(`#${type}-update-${id}`).css('display', '');

                if(type == 'account') {
                    if(data['error']) {
                        $(`.error-${id}`).css('display', '');
                        $(`td.error-${id}`).html(data['error'].toString());
                    } else {
                        $(`.error-${id}`).css('display', 'none');
                        $(`td.error-${id}`).html('');
                    }
                }

                if(type == 'cabinet') {
                    if(data['error']) {
                        console.log(data['error'])
                        $(`.cab-error-${id}`).html(`<span>${data['error'].toString()}</span>`);
                        $(`.cell-error-${data['account']}`).css('display', '');
                        $(`.accounts-error-indicator.error-${data['account']}`).css('display', '');
                    } else {
                        $(`.cab-error-${id} > span`).remove();
                        if($(`.cell-error-${data['account']} > span`).length == 0) {
                            $(`.cell-error-${data['account']}`).css('display', 'none');
                            $(`.accounts-error-indicator.error-${data['account']}`).css('display', 'none');
                        }
                    }
                }
            },
            error: (data) => {
            }
        });
    })

    $('#daterangepicker').daterangepicker(
        {
            locale: {
                format: 'YYYY-MM-DD'
            }
        }, 
        function(start, end, label) {
            dateStart = start.format('YYYY-MM-DD');
            dateStop = end.format('YYYY-MM-DD');
            $('.accounts-update-date.active').removeClass('active');
            $('#daterangepicker').addClass('active');
            $('.accounts-update-chosen-date').html(dateStart + ' - ' + dateStop);
        }
    );

    $('.accounts-update-date.standart').on('click', (e) => {
        $('.accounts-update-date.active').removeClass('active');
        e.target.classList.add('active');
        $('.accounts-update-chosen-date').html(e.target.id);
        dateStart = e.target.id;
        dateStop = e.target.id;
    })
})