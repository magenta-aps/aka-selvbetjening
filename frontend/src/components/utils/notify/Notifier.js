/* Method 'notify': Displays a notification on the page for 7 seconds
 * argument 'message': The message to be displayed, ex. 'Something was updated'
 */
function notify(message) {
    var notify_el = document.createElement('div')
    notify_el.className = 'notification'
    notify_el.role = 'alert'
    notify_el.innerHTML = `${ message }`
    document.appendChild(notify_el)
    setTimeout(function() {
        notify_el.classList.add('show')
        setTimeout(function() {
            notify_el.classList.remove('show')
        }, 7000)
    }, 100)
}

export { notify }