document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       CURRENT YEAR
    ===================================================== */

    const yearElement = document.getElementById("currentYear");

    if (yearElement) {
        yearElement.textContent = new Date().getFullYear();
    }


    /* =====================================================
       PASSWORD SHOW / HIDE
    ===================================================== */

    const passwordButtons = document.querySelectorAll(".password-toggle");

    passwordButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const targetId = button.getAttribute("data-target");
            const input = document.getElementById(targetId);
            const icon = button.querySelector("i");

            if (!input) {
                return;
            }

            if (input.type === "password") {

                input.type = "text";

                icon.classList.remove("bi-eye");
                icon.classList.add("bi-eye-slash");

            } else {

                input.type = "password";

                icon.classList.remove("bi-eye-slash");
                icon.classList.add("bi-eye");

            }

        });

    });


    /* =====================================================
       PASSWORD CONFIRMATION
    ===================================================== */

    const registerForm = document.getElementById("registerForm");

    if (registerForm) {

        const password = document.getElementById("password");
        const confirmPassword =
            document.getElementById("confirm_password");

        const passwordMessage =
            document.getElementById("passwordMessage");


        function checkPasswords() {

            if (!confirmPassword.value) {

                confirmPassword.classList.remove("is-valid");
                confirmPassword.classList.remove("is-invalid");

                if (passwordMessage) {
                    passwordMessage.innerHTML = "";
                }

                return;
            }


            if (password.value === confirmPassword.value) {

                confirmPassword.classList.remove("is-invalid");
                confirmPassword.classList.add("is-valid");

                if (passwordMessage) {

                    passwordMessage.innerHTML =
                        '<small class="text-success">' +
                        '<i class="bi bi-check-circle me-1"></i>' +
                        'Passwords match.' +
                        '</small>';

                }

            } else {

                confirmPassword.classList.remove("is-valid");
                confirmPassword.classList.add("is-invalid");

                if (passwordMessage) {

                    passwordMessage.innerHTML =
                        '<small class="text-danger">' +
                        '<i class="bi bi-exclamation-circle me-1"></i>' +
                        'Passwords do not match.' +
                        '</small>';

                }

            }

        }


        password.addEventListener("input", checkPasswords);
        confirmPassword.addEventListener("input", checkPasswords);


        registerForm.addEventListener("submit", function (event) {

            if (password.value !== confirmPassword.value) {

                event.preventDefault();

                confirmPassword.classList.add("is-invalid");

                if (passwordMessage) {

                    passwordMessage.innerHTML =
                        '<small class="text-danger">' +
                        '<i class="bi bi-exclamation-circle me-1"></i>' +
                        'Passwords do not match.' +
                        '</small>';

                }

                confirmPassword.focus();

            }

        });

    }

});