import './notifier.css'

export function notifyError(error, language, i18n) {
  if (error.response) {
    const errors = error.response.data['errors'];
    const fieldErrors = error.response.data['fieldErrors'];
    if (errors) {
      errors.forEach(error => {
        notify(error[language]);
      })
    }
    if (fieldErrors) {
      for (let field in fieldErrors) {
        if (fieldErrors.hasOwnProperty(field)) {
          fieldErrors[field].forEach(error => {
            notify(i18n.t('attributes.' + field) + ": " + error[language]);
          });
        }
      }
    }
  } else if (message.message) {
    notify(message.message);
  }
}

export function notify (message) {
  /* Method 'notify': Displays a notification on the page for 7 seconds
     * argument 'message': The message to be displayed, ex. 'Something was updated'
     */








  let notify_container;

  let notify_el = document.createElement('div');

  // Check if notification container already exists
  if (!document.querySelector('.notification-container')) {
    notify_container = document.createElement('div');
    notify_container.className = 'notification-container';
    document.body.appendChild(notify_container)
  } else {
    notify_container = document.querySelector('.notification-container')
  }

  // Create notification
  notify_el.className = 'notification';
  notify_el.role = 'alert';
  notify_el.innerHTML = `${message}`;

  // Display notification
  notify_container.appendChild(notify_el);
  setTimeout(function () {
    notify_el.classList.add('show');
    setTimeout(function () {
      notify_el.classList.remove('show');
      setTimeout(function () {
        notify_container.removeChild(notify_el)
      }, 500)
    }, 7000)
  }, 100)
}
