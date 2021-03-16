function makeCollapsable(el) {
    const collapse_buttons = el.querySelectorAll('.js-collapse');
    for (const collapse_button of collapse_buttons) {
        collapse_button.addEventListener('click', function() {
            el.classList.toggle("collapsed");
        });
    }
}

const collapsables = document.querySelectorAll(".js-collapsable")

for (const el of collapsables) {
    makeCollapsable(el);
}