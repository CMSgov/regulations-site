function makeStateful(el) {
    const state_change_target = el.getAttribute("data-target");
    const state_change_buttons = document.querySelectorAll(`[data-set-state][data-target='${state_change_target}']`);

    for (const state_change_button of state_change_buttons) {
        state_change_button.addEventListener('click', function() {
            el.setAttribute("data-state", this.getAttribute("data-set-state"));
        });
    }
}

function main() {
    const stateful_elements = document.querySelectorAll("[data-state]")

    for (const el of stateful_elements) {
        makeStateful(el);
    }
}

main();
