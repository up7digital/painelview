// Controle dos Slides ====================================================
document.addEventListener("DOMContentLoaded", function () {
    let slides = document.querySelectorAll(".slide-item");
    let index = 0;

    if (slides.length === 0) return;

    // mostrar o primeiro slide
    slides[0].classList.add("active");

    setInterval(() => {
        slides[index].classList.remove("active");

        index = (index + 1) % slides.length;

        slides[index].classList.add("active");
    }, TEMPO_IMAGEM);  // agora usa o valor vindo do banco!
});

