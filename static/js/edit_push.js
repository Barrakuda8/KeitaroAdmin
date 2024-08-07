window.addEventListener('load', () => {

    const type = $('#id_type').val();

    $('#select-days').on('change', () => {
        $('#id_days').val($('#select-days').val().join('|') + '|');
    });

    $('#select-hours').on('change', () => {
        $('#id_hours').val($('#select-hours').val().join('|') + '|');
    });

    function checkAudience() {
        const languages = $('#id_languages').val();
        const countryFlags = $('#id_country_flags').val();
        const offers = $('#id_offers').val();
        const applications = $('#id_applications').val();
        const buyers = $('#id_buyers').val();
        const statuses = type != 'status' ? $('#id_statuses').val() : [];
        $.ajax({
            method: "get",
            url: "/installs/check_push_audience/",
            data: {languages: languages, country_flags: countryFlags, offers: offers, applications: applications, statuses: statuses, buyers: buyers},
            success: (data) => {
                $('.push-audience').html(data['audience']);
            },
            error: (data) => {
            }
        });
    }

    $('.form-select:not(.fake)').on('change', () => {
        checkAudience();
    })

    checkAudience();

    if(type == 'timed') {
        let hours = $('#id_hours').val().split('|');
        hours.pop();
        $('#select-hours').val(hours);
        
        let days = $('#id_days').val().split('|');
        hours.pop();
        $('#select-days').val(days);
    }
})