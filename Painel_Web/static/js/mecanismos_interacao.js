let intervaloSlidesLateral = null;
let intervaloSlidesPopup = null;
let timerTelaDescanso = null;
let revisaoMidias = null;
let atualizacaoMidiasEmAndamento = false;


function tempoValido(valor, fallback) {
    const numero = Number(valor);
    return Number.isFinite(numero) && numero > 0 ? numero : fallback;
}


function iniciarSlidesLateral() {
    if (intervaloSlidesLateral) {
        clearInterval(intervaloSlidesLateral);
        intervaloSlidesLateral = null;
    }

    const slides = Array.from(document.querySelectorAll(".slide-item"));
    slides.forEach((slide) => slide.classList.remove("active"));

    if (slides.length === 0) {
        return;
    }

    let index = 0;
    slides[index].classList.add("active");

    if (slides.length === 1) {
        return;
    }

    intervaloSlidesLateral = setInterval(() => {
        slides[index].classList.remove("active");
        index = (index + 1) % slides.length;
        slides[index].classList.add("active");
    }, tempoValido(window.TEMPO_IMAGEM, 5000));
}


function existeMidiaTelaDescanso() {
    return document.querySelectorAll(
        "#popup_banner .slide-item_tela_descanso",
    ).length > 0;
}


function pararSlideshowTelaDescanso() {
    if (intervaloSlidesPopup) {
        clearInterval(intervaloSlidesPopup);
        intervaloSlidesPopup = null;
    }
}


function iniciarSlideshowTelaDescanso(containerId, tempo) {
    pararSlideshowTelaDescanso();

    const slides = Array.from(
        document.querySelectorAll(
            `#${containerId} .slide-item_tela_descanso`,
        ),
    );
    slides.forEach((slide) => {
        slide.classList.remove("active", "saindo");
    });

    if (slides.length === 0) {
        return;
    }

    let index = 0;
    slides[index].classList.add("active");

    if (slides.length === 1) {
        return;
    }

    intervaloSlidesPopup = setInterval(() => {
        const atual = slides[index];
        atual.classList.remove("active");
        atual.classList.add("saindo");

        index = (index + 1) % slides.length;
        slides[index].classList.add("active");

        setTimeout(() => {
            atual.classList.remove("saindo");
        }, 800);
    }, tempoValido(tempo, 10000));
}


function ativarTelaDescanso() {
    if (!existeMidiaTelaDescanso()) {
        return;
    }

    document.getElementById("area-tela_descanso")?.classList.add("active");
    iniciarSlideshowTelaDescanso(
        "popup_banner",
        window.TEMPO_TELA_DESCANSO,
    );
}


function desativarTelaDescanso() {
    document.getElementById("area-tela_descanso")?.classList.remove("active");
    pararSlideshowTelaDescanso();
}


function resetarTimerTelaDescanso() {
    desativarTelaDescanso();

    if (timerTelaDescanso) {
        clearTimeout(timerTelaDescanso);
    }

    timerTelaDescanso = setTimeout(
        ativarTelaDescanso,
        tempoValido(window.TEMPO_TELA_DESCANSO, 10000),
    );
}


function aplicarMidiasAtualizadas(dados) {
    const containerLateral = document.getElementById("slide-container");
    const containerPopup = document.getElementById("slide-container_popup");
    const popupEstavaAtivo = document
        .getElementById("area-tela_descanso")
        ?.classList.contains("active");

    if (!containerLateral || !containerPopup) {
        return;
    }

    containerLateral.innerHTML = dados.lateral_html || "";
    containerPopup.innerHTML = dados.popup_html || "";
    window.TEMPO_IMAGEM = tempoValido(dados.tempo_imagem_ms, 5000);
    window.TEMPO_TELA_DESCANSO = tempoValido(
        dados.tempo_popup_ms,
        10000,
    );

    iniciarSlidesLateral();

    if (popupEstavaAtivo && existeMidiaTelaDescanso()) {
        iniciarSlideshowTelaDescanso(
            "popup_banner",
            window.TEMPO_TELA_DESCANSO,
        );
    } else if (!existeMidiaTelaDescanso()) {
        desativarTelaDescanso();
    }
}


async function atualizarMidiasPainel() {
    if (
        atualizacaoMidiasEmAndamento
        || !window.PAINEL_ID
        || !window.URL_MIDIAS_PAINEL
    ) {
        return;
    }

    atualizacaoMidiasEmAndamento = true;

    try {
        const url = new URL(
            window.URL_MIDIAS_PAINEL,
            window.location.origin,
        );
        url.searchParams.set("painel", window.PAINEL_ID);

        if (revisaoMidias) {
            url.searchParams.set("revisao", revisaoMidias);
        }

        const resposta = await fetch(url, {
            cache: "no-store",
            headers: {"Accept": "application/json"},
        });

        if (!resposta.ok) {
            throw new Error(`HTTP ${resposta.status}`);
        }

        const dados = await resposta.json();
        revisaoMidias = dados.revisao || revisaoMidias;

        if (dados.alterado) {
            aplicarMidiasAtualizadas(dados);
            console.log("🖼️ Mídias do painel atualizadas automaticamente.");
        }
    } catch (erro) {
        console.warn("Não foi possível atualizar as mídias do painel.", erro);
    } finally {
        atualizacaoMidiasEmAndamento = false;
    }
}


document.addEventListener("DOMContentLoaded", () => {
    iniciarSlidesLateral();
    resetarTimerTelaDescanso();
    atualizarMidiasPainel();

    setInterval(
        atualizarMidiasPainel,
        tempoValido(window.INTERVALO_ATUALIZACAO_MIDIAS, 10000),
    );
});
