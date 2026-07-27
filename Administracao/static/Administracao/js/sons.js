document.addEventListener("DOMContentLoaded", () => {
    const botoes = document.querySelectorAll("[data-sound-button]");
    const formulariosExclusao = document.querySelectorAll("[data-delete-sound-form]");
    let audioAtual = null;

    const atualizarBotao = (audio, reproduzindo) => {
        const linha = audio.closest(".sound-row");
        const botao = linha?.querySelector("[data-sound-button]");
        const icone = botao?.querySelector("[data-play-icon]");

        if (!botao || !icone) {
            return;
        }

        icone.textContent = reproduzindo ? "❚❚" : "▶";
        botao.classList.toggle("playing", reproduzindo);
        botao.title = reproduzindo ? "Pausar" : "Reproduzir";
        botao.setAttribute(
            "aria-label",
            reproduzindo ? "Pausar campainha" : "Reproduzir campainha",
        );
    };

    botoes.forEach((botao) => {
        const linha = botao.closest(".sound-row");
        const audio = linha?.querySelector("[data-sound-audio]");

        if (!audio) {
            return;
        }

        botao.addEventListener("click", async () => {
            if (audioAtual && audioAtual !== audio) {
                audioAtual.pause();
                atualizarBotao(audioAtual, false);
            }

            if (audio.paused) {
                try {
                    await audio.play();
                    audioAtual = audio;
                    atualizarBotao(audio, true);
                } catch (error) {
                    console.error("Não foi possível reproduzir a campainha.", error);
                }
            } else {
                audio.pause();
                atualizarBotao(audio, false);
                audioAtual = null;
            }
        });

        audio.addEventListener("ended", () => {
            atualizarBotao(audio, false);
            audio.currentTime = 0;

            if (audioAtual === audio) {
                audioAtual = null;
            }
        });
    });

    formulariosExclusao.forEach((formulario) => {
        formulario.addEventListener("submit", (event) => {
            const nome = formulario.dataset.soundName || "este som";
            const confirmado = window.confirm(
                `Deseja realmente excluir "${nome}"?`,
            );

            if (!confirmado) {
                event.preventDefault();
            }
        });
    });
});
