$(function () {
    if (localStorage.getItem('darkMode') === 'true') {
        $('body').addClass('dark')
        $('meta[name="theme-color"]').attr('content', '#212121')
    }

    $('.dropdown-trigger').dropdown({
        constrainWidth: false,
        coverTrigger: false
    })

    $('#login-button').click(function() {
        const username = $('#username').val().trim()
        const password = $('#password').val().trim()
        if (username.length > 0 && password.length > 0) {
            const url = `${window.location.origin}/auth/basic?un=${username}&pw=${password}`
            window.location.href = url
        }
    })

    const param = getParameterByName('success')
    if (param === 'false') {
        toastError('Wrong username or password!', 'Please try again.')
    }
})