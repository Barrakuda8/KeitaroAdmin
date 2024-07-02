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
})