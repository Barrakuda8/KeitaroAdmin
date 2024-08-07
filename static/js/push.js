window.addEventListener('load', () => {

    $('.push-execute').on('click', () => {
        const type = $('#select-type').val();
        const hours = $('#select-hours').val();
        const days = $('#select-days').val();
        const timedelta = $('#input-timedelta').val();
        const status = $('#select-status').val();
        let validated = true;
        if(type == 'timed' && (!days.length || !hours.length)) {
            validated = false;
            if(!days.length) {
                $('#select-days').addClass('incorrect');
            } else {
                $('#select-days').removeClass('incorrect');
            }
            if(!hours.length) {
                $('#select-hours').addClass('incorrect');
            } else {
                $('#select-hours').removeClass('incorrect');
            }
        }
        if(type == 'status' && (!timedelta || !status)) {
            validated = false;
            if(!timedelta) {
                $('#input-timedelta').addClass('incorrect');
            } else {
                $('#input-timedelta').removeClass('incorrect');
            }
            if(!status.length) {
                $('#select-status').addClass('incorrect');
            } else {
                $('#select-status').removeClass('incorrect');
            }
        }
        if (validated) {
            const languages = $('#select-languages').val();
            const countryFlags = $('#select-country-flags').val();
            const offers = $('#select-offers').val();
            const applications = $('#select-applications').val();
            const buyers = $('#select-buyers').val();
            const statuses = $('#select-statuses').val();
            const token = $('input[name=csrfmiddlewaretoken]').val();
            const title = $('#input-title').val();
            const text = $('#input-text').val();
            let formData = new FormData();
            formData.append('csrfmiddlewaretoken', token);
            formData.append('title', title);
            formData.append('text', text);
            formData.append('type', type);
            if(offers.length) {
                for (var i = 0; i < offers.length; i++) {
                    formData.append('offers[]', offers[i]);
                }
            }
            if(countryFlags.length) {
                for (var i = 0; i < countryFlags.length; i++) {
                    formData.append('country_flags[]', countryFlags[i]);
                }
            }
            if(languages.length) {
                for (var i = 0; i < languages.length; i++) {
                    formData.append('languages[]', languages[i]);
                }
            }
            if(applications.length) {
                for (var i = 0; i < applications.length; i++) {
                    formData.append('applications[]', applications[i]);
                }
            }
            if(buyers != undefined && buyers.length) {
                for (var i = 0; i < buyers.length; i++) {
                    formData.append('buyers[]', buyers[i]);
                }
            }
            if(type == 'status') {
                formData.append('statuses', status);
            } else if(statuses.length) {
                for (var i = 0; i < statuses.length; i++) {
                    formData.append('statuses[]', statuses[i]);
                }
            }
            if($('#input-launch-image')[0].files.length > 0) {
                formData.append('launch_image', $('#input-launch-image')[0].files[0]);
            }
            if(type == 'timed') {
                for (var i = 0; i < hours.length; i++) {
                    formData.append('hours[]', hours[i]);
                }
                for (var i = 0; i < days.length; i++) {
                    formData.append('days[]', days[i]);
                }
            }
            if(type == 'status') {
                formData.append('timedelta', timedelta);
            }
            $.ajax({
                method: "post",
                url: "/installs/execute_push/",
                contentType: false,
                processData: false,
                data: formData,
                success: (data) => {
                    if(data['result'] == 'ok') {
                        location.replace(location.origin + '/installs/applications/');
                    } else {
                        alert('Что-то пошло не так');
                    }
                },
                error: (data) => {
                }
            });
        }
    })

    function checkAudience() {
        const languages = $('#select-languages').val();
        const countryFlags = $('#select-country-flags').val();
        const offers = $('#select-offers').val();
        const applications = $('#select-applications').val();
        const buyers = $('#select-buyers').val();
        const statuses = $('#select-type').val() != 'status' ? $('#select-statuses').val() : [];
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

    $('#select-type').on('change', (e) => {
        let type = e.target.value;
        if(type == 'timed') {
            $('#days-subblock').css('display', '');
            $('#hours-subblock').css('display', '');
            $('#timedelta-subblock').css('display', 'none');
            $('#status-subblock').css('display', 'none');
            $('#statuses-subblock').css('display', '');
        } else if(type == 'status') {
            $('#days-subblock').css('display', 'none');
            $('#hours-subblock').css('display', 'none');
            $('#timedelta-subblock').css('display', '');
            $('#status-subblock').css('display', '');
            $('#statuses-subblock').css('display', 'none');
        } else if(type == 'normal') {
            $('#days-subblock').css('display', 'none');
            $('#hours-subblock').css('display', 'none');
            $('#timedelta-subblock').css('display', 'none');
            $('#status-subblock').css('display', 'none');
            $('#statuses-subblock').css('display', '');
        }
    })
})