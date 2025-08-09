document.addEventListener('DOMContentLoaded', () => {
    const flashes = document.querySelectorAll('.flash');
    setTimeout(() => {
        flashes.forEach(flash => {
            flash.style.opacity = '0';
            setTimeout(() => flash.remove(), 500);
        });
    }, 4000);
});