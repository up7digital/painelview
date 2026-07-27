document.addEventListener("DOMContentLoaded", () => {
    const botaoExcluirMidia = document.querySelector(
        "[data-delete-media-button]",
    );

    botaoExcluirMidia?.form?.addEventListener("submit", (event) => {
        if (event.submitter !== botaoExcluirMidia) {
            return;
        }

        if (!window.confirm("Deseja realmente excluir esta mídia?")) {
            event.preventDefault();
        }
    });

    const controle = document.querySelector("[data-media-file-control]");

    if (controle) {
        const input = controle.querySelector('input[type="file"]');
        const nomeArquivo = controle.querySelector("[data-current-file-name]");

        if (input && nomeArquivo) {
            input.addEventListener("change", () => {
                nomeArquivo.textContent = (
                    input.files?.[0]?.name ||
                    nomeArquivo.dataset.originalName ||
                    "Nenhum arquivo selecionado"
                );
            });
        }
    }

    const editorTexto = document.querySelector("[data-text-preview]");
    const campoTexto = document.querySelector("#id_texto");

    if (editorTexto && campoTexto) {
        const contadorTexto = document.querySelector("[data-text-counter]");
        const controleTamanho = document.querySelector("[data-text-font-size]");
        const controleCor = document.querySelector("[data-text-color]");
        const botoesAlinhamento = Array.from(
            document.querySelectorAll("[data-text-align]"),
        );
        const campoTamanho = document.querySelector("#id_texto_tamanho_fonte");
        const campoCor = document.querySelector("#id_texto_cor");
        const campoAlinhamento = document.querySelector("#id_texto_alinhamento");
        const limiteTexto = Number(editorTexto.dataset.maxLength) || 100;

        const posicionarCursorNoFim = () => {
            const selecao = window.getSelection();
            const intervalo = document.createRange();
            intervalo.selectNodeContents(editorTexto);
            intervalo.collapse(false);
            selecao?.removeAllRanges();
            selecao?.addRange(intervalo);
        };

        const sincronizarTexto = () => {
            let texto = editorTexto.innerText.replace(/\r\n/g, "\n");

            if (texto.length > limiteTexto) {
                texto = texto.slice(0, limiteTexto);
                editorTexto.textContent = texto;
                posicionarCursorNoFim();
            }

            campoTexto.value = texto;

            if (contadorTexto) {
                contadorTexto.textContent = `${texto.length} / ${limiteTexto}`;
                contadorTexto.classList.toggle(
                    "is-at-limit",
                    texto.length >= limiteTexto,
                );
            }
        };

        editorTexto.addEventListener("input", sincronizarTexto);
        editorTexto.addEventListener("paste", (event) => {
            event.preventDefault();
            const textoColado = event.clipboardData?.getData("text/plain") || "";
            document.execCommand("insertText", false, textoColado);
        });

        if (controleTamanho && campoTamanho) {
            const aplicarTamanho = () => {
                const tamanho = Math.min(
                    120,
                    Math.max(12, Number(controleTamanho.value) || 32),
                );
                editorTexto.style.fontSize = `${tamanho}px`;
                campoTamanho.value = tamanho;
            };

            controleTamanho.value = campoTamanho.value || 32;
            controleTamanho.addEventListener("input", aplicarTamanho);
            controleTamanho.addEventListener("change", () => {
                aplicarTamanho();
                controleTamanho.value = campoTamanho.value;
            });
            aplicarTamanho();
        }

        if (controleCor && campoCor) {
            const aplicarCor = () => {
                editorTexto.style.color = controleCor.value;
                campoCor.value = controleCor.value;
            };

            controleCor.value = campoCor.value || "#ffffff";
            controleCor.addEventListener("input", aplicarCor);
            aplicarCor();
        }

        if (campoAlinhamento) {
            const aplicarAlinhamento = (alinhamento) => {
                const alinhamentoValido = ["left", "center", "right"].includes(
                    alinhamento,
                ) ? alinhamento : "center";

                editorTexto.style.textAlign = alinhamentoValido;
                campoAlinhamento.value = alinhamentoValido;

                botoesAlinhamento.forEach((botao) => {
                    const ativo = botao.dataset.textAlign === alinhamentoValido;
                    botao.classList.toggle("is-active", ativo);
                    botao.setAttribute("aria-pressed", String(ativo));
                });
            };

            botoesAlinhamento.forEach((botao) => {
                botao.addEventListener("click", () => {
                    aplicarAlinhamento(botao.dataset.textAlign);
                });
            });
            aplicarAlinhamento(campoAlinhamento.value);
        }

        campoTexto.form?.addEventListener("submit", sincronizarTexto);
        sincronizarTexto();
    }

    const seletorSetores = document.querySelector("[data-sector-selector]");

    if (!seletorSetores) {
        return;
    }

    const marcarTodos = seletorSetores.querySelector("[data-select-all-sectors]");
    const checkboxes = Array.from(
        seletorSetores.querySelectorAll(
            '[data-sector-checkboxes] input[type="checkbox"]',
        ),
    );

    if (!marcarTodos || checkboxes.length === 0) {
        return;
    }

    const sincronizarExibirEmTodos = () => {
        const selecionados = checkboxes.filter((checkbox) => checkbox.checked).length;
        marcarTodos.checked = selecionados === checkboxes.length;
        marcarTodos.indeterminate = selecionados > 0 && selecionados < checkboxes.length;
    };

    marcarTodos.addEventListener("change", () => {
        checkboxes.forEach((checkbox) => {
            checkbox.checked = marcarTodos.checked;
        });
        sincronizarExibirEmTodos();
    });

    checkboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", sincronizarExibirEmTodos);
    });

    sincronizarExibirEmTodos();
});
