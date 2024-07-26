window.addEventListener('load', () => {

    $('.push-execute').on('click', () => {
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
        if(offers.length) {
            formData.append('offers', offers);
        }
        if(countryFlags.length) {
            formData.append('country_flags', countryFlags);
        }
        if(languages.length) {
            formData.append('languages', languages);
        }
        if(applications.length) {
            formData.append('applications', applications);
        }
        if(buyers.length) {
            formData.append('buyers', buyers);
        }
        if(statuses.length) {
            formData.append('statuses', statuses);
        }
        if($('#input-launch-image')[0].files.length > 0) {
            formData.append('launch_image', $('#input-launch-image')[0].files[0]);
        }
        $.ajax({
            method: "post",
            url: "/installs/execute_push/",
            contentType: false,
            processData: false,
            data: formData,
            success: (data) => {
                // location.replace(location.origin + '/installs/applications/');
            },
            error: (data) => {
            }
        });
    })

    function checkAudience() {
        const languages = $('#select-languages').val();
        const countryFlags = $('#select-country-flags').val();
        const offers = $('#select-offers').val();
        const applications = $('#select-applications').val();
        const buyers = $('#select-buyers').val();
        const statuses = $('#select-statuses').val();
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

    $('.form-select').on('change', () => {
        checkAudience();
    })
})