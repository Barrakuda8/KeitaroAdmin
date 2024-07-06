window.addEventListener('load', () => {

    $('.team-arrow').on('click', (e) => {
        if(e.target.classList.contains('active')) {
            $(`#${e.target.id.replace('arrow', 'hidden')}`).css('display', '');
            e.target.classList.remove('active');
        } else {
            $(`#${e.target.id.replace('arrow', 'hidden')}`).css('display', 'flex');
            e.target.classList.add('active');
        }
    })

    $('.cabinet-update').on('click', (e) => {
        let id = e.target.id.replace('update-', '');
        $(`#img-${id}`).css('display', '');
        e.target.style.display = 'none';
        const token = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            method: "post",
            url: '/main/get_cabinet_costs/',
            data: {cabinet: id, csrfmiddlewaretoken: token},
            success: (data) => {
                $(`#img-${id}`).css('display', 'none');
                e.target.style.display = '';
            },
            error: (data) => {
            }
        });
    })
})