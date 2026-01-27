// Controle dos Slides Lateral ====================================================
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


// Controle da Tela de Descanso ====================================================
let timerTelaDescanso = null;

// Verifica se existe ao menos 1 mídia para a tela de descanso
function existeMidiaTelaDescanso() {
    return document.querySelectorAll(
        "#popup_banner .slide-item_tela_descanso"
    ).length > 0;
}

// Ativa tela de descanso
function ativarTelaDescanso() {
    if (!existeMidiaTelaDescanso()) return; // ⛔ não ativa sem mídias
    document.getElementById("area-tela_descanso")?.classList.add("active");
    iniciarSlideshowTelaDescanso("popup_banner", TEMPO_TELA_DESCANSO);

}

// Desativa tela de descanso
function desativarTelaDescanso() {
    document.getElementById("area-tela_descanso")?.classList.remove("active");
}

// Reseta contador de inatividade
function resetarTimerTelaDescanso() {
    desativarTelaDescanso();

    if (timerTelaDescanso) {
        clearTimeout(timerTelaDescanso);
    }

    timerTelaDescanso = setTimeout(() => {
        ativarTelaDescanso();
    }, TEMPO_TELA_DESCANSO);
}

// Inicializa ao carregar o painel
document.addEventListener("DOMContentLoaded", () => {
    resetarTimerTelaDescanso();
});

// Controle dos Slides Tela de Descanso ====================================================
function iniciarSlideshowTelaDescanso(containerId, tempo) {
    const slides = document.querySelectorAll(`#${containerId} .slide-item_tela_descanso`);
    if (!slides.length) return;

    let index = 0;
    slides[index].classList.add("active");

    setInterval(() => {
        const atual = slides[index];
        atual.classList.remove("active");
        atual.classList.add("saindo");

        index = (index + 1) % slides.length;
        const proximo = slides[index];

        proximo.classList.add("active");

        // Remove classe 'saindo' após a animação
        setTimeout(() => {
            atual.classList.remove("saindo");
        }, 800);
    }, tempo);
}
