document.addEventListener("DOMContentLoaded", function () {
    const forms = document.querySelectorAll(".auto-update-cart-form");

    forms.forEach(function (form) {
        const input = form.querySelector(".cart-qty-input");
        let timer;

        input.addEventListener("input", function () {
            clearTimeout(timer);

            timer = setTimeout(function () {
                let quantity = parseInt(input.value, 10);

                if (!quantity || quantity < 1) {
                    input.value = 1;
                }

                form.submit();
            }, 500);
        });

        input.addEventListener("change", function () {
            clearTimeout(timer);

            let quantity = parseInt(input.value, 10);

            if (!quantity || quantity < 1) {
                input.value = 1;
            }

            form.submit();
        });
    });
});
