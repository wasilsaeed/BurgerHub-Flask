document.addEventListener("DOMContentLoaded", function () {
  const flashMessages = document.querySelectorAll(".flash-message");

  flashMessages.forEach(function (message) {
    const closeButton = message.querySelector(".flash-close");

    if (closeButton) {
      closeButton.addEventListener("click", function () {
        message.classList.add("hide");

        setTimeout(function () {
          message.remove();
        }, 300);
      });
    }

    setTimeout(function () {
      message.classList.add("hide");

      setTimeout(function () {
        message.remove();
      }, 300);
    }, 3000);
  });
});
