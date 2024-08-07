window.addEventListener('load', () => {
    let dateStart = $('.accounts-update-chosen-date').html();
    let dateStop = dateStart;

    $('.stats-update').on('click', (e) => {
        let id = e.target.id.replace('app-update-', '');
        let name = $(`#app-name-${id}`).html();
        $('.accounts-update').attr('id', `button-${id}`);
        $('.teams-background').css('display', 'flex');
        $('.teams-password-title').html(`Приложение - ${name}`);
    })

    $('.teams-background').on('click', (e) => {
        if(e.target.classList.contains('teams-background')) {
            $('.accounts-update').attr('id', '');
            $('.teams-background').css('display', '');
            $('.teams-password-title').html('');
        }
    })

    $('.accounts-update').on('click', (e) => {
        let id = e.target.id.replace('button-', '');
        $(`#app-img-${id}`).css('display', '');
        $(`#app-update-${id}`).css('display', 'none');
        $('.accounts-update').attr('id', '');
        $('.teams-background').css('display', '');
        $('.teams-password-title').html('');
        const token = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            method: "post",
            url: `/installs/get_installs/`,
            data: {id: id, date_start: dateStart, date_stop: dateStop, csrfmiddlewaretoken: token},
            success: (data) => {
                $(`#app-img-${id}`).css('display', 'none');
                $(`#app-update-${id}`).css('display', '');
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