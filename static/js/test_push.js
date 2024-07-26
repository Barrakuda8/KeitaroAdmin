window.addEventListener('load', () => {

    $('.push-execute').on('click', () => {
        const application = $('#select-application').val();
        const externalId = $('#input-external-id').val();
        const sandbox = $('#input-sandbox').is(":checked");
        const token = $('input[name=csrfmiddlewaretoken]').val();
        const title = $('#input-title').val();
        const text = $('#input-text').val();
        $.ajax({
            method: "post",
            url: "/installs/execute_test_push/",
            data: {application: application, external_id: externalId, sandbox: sandbox, csrfmiddlewaretoken: token, title: title, text: text},
            success: (data) => {
                if(data['result'] == 'ok') {
                    location.replace(location.origin + '/installs/applications/');
                } else if(data['result'] == 'bad token') {
                    $('.push-notification').css('display', 'inline');
                }
            },
            error: (data) => {
            }
        });
    })
})