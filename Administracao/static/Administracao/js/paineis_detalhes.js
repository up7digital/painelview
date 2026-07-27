document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector(".connection-form");
    const vozVocalizacao = document.querySelector("#id_voz_vocalizacao");
    const conexao = document.querySelector("#id_conexao");
    const unidade = document.querySelector("#id_unidade_sga");
    const servicos = document.querySelector("#id_servicos_sga");
    const disponiveis = document.querySelector("[data-services-available]");
    const selecionados = document.querySelector("[data-services-selected]");
    const filtroDisponiveis = document.querySelector("[data-filter-available]");
    const filtroSelecionados = document.querySelector("[data-filter-selected]");
    const botaoAdicionar = document.querySelector("[data-add-services]");
    const botaoRemover = document.querySelector("[data-remove-services]");
    const velocidadeVocalizacao = document.querySelector(
        "#id_velocidade_vocalizacao",
    );
    const tomVocalizacao = document.querySelector("#id_tom_vocalizacao");
    const botaoPreviewVocalizacao = document.querySelector(
        "#btn-preview-vocalizacao",
    );

    const carregarVozesVocalizacao = () => {
        if (!vozVocalizacao || !window.speechSynthesis) {
            return;
        }

        const vozSelecionada = vozVocalizacao.value;
        const vozes = window.speechSynthesis
            .getVoices()
            .filter((voz) => voz.lang.toLocaleLowerCase().startsWith("pt"))
            .sort((vozA, vozB) => vozA.name.localeCompare(vozB.name, "pt-BR"));

        vozVocalizacao.replaceChildren(
            new Option("Automática — voz em português", ""),
        );

        vozes.forEach((voz) => {
            const option = new Option(
                `${voz.name} (${voz.lang})`,
                voz.name,
            );
            option.selected = voz.name === vozSelecionada;
            vozVocalizacao.add(option);
        });

        if (
            vozSelecionada &&
            !vozes.some((voz) => voz.name === vozSelecionada)
        ) {
            const indisponivel = new Option(
                `${vozSelecionada} — indisponível neste navegador`,
                vozSelecionada,
                true,
                true,
            );
            vozVocalizacao.add(indisponivel);
        }
    };

    carregarVozesVocalizacao();
    window.speechSynthesis?.addEventListener(
        "voiceschanged",
        carregarVozesVocalizacao,
    );

    const obterConfiguracaoPreview = () => {
        const velocidade = Number(velocidadeVocalizacao?.value);
        const tom = Number(tomVocalizacao?.value);
        const vozes = window.speechSynthesis?.getVoices() || [];
        const voz = vozes.find(
            (item) => item.name === vozVocalizacao?.value,
        ) || vozes.find(
            (item) => item.lang.toLocaleLowerCase().startsWith("pt-br"),
        ) || vozes.find(
            (item) => item.lang.toLocaleLowerCase().startsWith("pt"),
        ) || null;

        return {
            velocidade:
                Number.isFinite(velocidade) && velocidade >= 0.5 && velocidade <= 2
                    ? velocidade
                    : 0.9,
            tom:
                Number.isFinite(tom) && tom >= 0.5 && tom <= 2
                    ? tom
                    : 1,
            voz,
        };
    };

    const reproduzirPreviewNativo = (texto, configuracao) => {
        if (
            !window.speechSynthesis ||
            typeof window.SpeechSynthesisUtterance !== "function"
        ) {
            console.error("O navegador não oferece suporte à síntese de voz.");
            return;
        }

        window.speechSynthesis.cancel();

        const fala = new window.SpeechSynthesisUtterance(texto);
        fala.lang = "pt-BR";
        fala.voice = configuracao.voz;
        fala.rate = configuracao.velocidade;
        fala.pitch = configuracao.tom;
        fala.volume = 1;
        window.speechSynthesis.speak(fala);
    };

    botaoPreviewVocalizacao?.addEventListener("click", () => {
        const texto = "Senha A 0 1, Guichê 1";
        const configuracao = obterConfiguracaoPreview();

        window.speechSynthesis?.cancel();

        if (!window.talkify?.Html5Player) {
            reproduzirPreviewNativo(texto, configuracao);
            return;
        }

        try {
            if (window.talkify.config?.remoteService) {
                window.talkify.config.remoteService.active = false;
            }

            if (window.talkify.config?.ui?.audioControls) {
                window.talkify.config.ui.audioControls.enabled = false;
            }

            const previewPlayer = new window.talkify.Html5Player();
            previewPlayer.forceLanguage("pt-BR");
            if (configuracao.voz) {
                previewPlayer.forceVoice(configuracao.voz);
            }
            previewPlayer.setRate(configuracao.velocidade);
            previewPlayer.usePitch(configuracao.tom);
            previewPlayer.setVolume(1);

            const reproducao = previewPlayer.playText(texto);
            if (reproducao?.catch) {
                reproducao.catch(() => {
                    reproduzirPreviewNativo(texto, configuracao);
                });
            }
        } catch (error) {
            console.error("Não foi possível reproduzir a prévia:", error);
            reproduzirPreviewNativo(texto, configuracao);
        }
    });

    if (
        !form || !conexao || !unidade || !servicos ||
        !disponiveis || !selecionados
    ) {
        return;
    }

    const filtrarLista = (select, termo) => {
        const busca = termo.trim().toLocaleLowerCase("pt-BR");

        Array.from(select.options).forEach((option) => {
            option.hidden = !option.text.toLocaleLowerCase("pt-BR").includes(busca);
        });
    };

    const renderizarServicos = () => {
        disponiveis.replaceChildren();
        selecionados.replaceChildren();

        Array.from(servicos.options).forEach((option) => {
            if (!option.value) {
                return;
            }

            const copia = new Option(option.text, option.value);

            if (option.selected) {
                selecionados.add(copia);
            } else {
                disponiveis.add(copia);
            }
        });

        filtrarLista(disponiveis, filtroDisponiveis?.value || "");
        filtrarLista(selecionados, filtroSelecionados?.value || "");
    };

    const moverServicos = (origem, marcarComoSelecionado) => {
        const valores = new Set(
            Array.from(origem.selectedOptions, (option) => option.value),
        );

        Array.from(servicos.options).forEach((option) => {
            if (valores.has(option.value)) {
                option.selected = marcarComoSelecionado;
            }
        });

        renderizarServicos();
    };

    const preencherSelect = (select, itens, placeholder) => {
        select.replaceChildren();

        if (placeholder) {
            select.add(new Option(placeholder, ""));
        }

        itens.forEach((item) => {
            select.add(new Option(item.text, String(item.id)));
        });
    };

    const carregarServicos = async () => {
        preencherSelect(servicos, [], null);
        renderizarServicos();

        if (!conexao.value || !unidade.value) {
            return;
        }

        servicos.disabled = true;

        try {
            const url = new URL(form.dataset.servicosUrl, window.location.origin);
            url.searchParams.set("conexao_id", conexao.value);
            url.searchParams.set("unidade_id", unidade.value);

            const response = await fetch(url, {
                headers: {"X-Requested-With": "XMLHttpRequest"},
            });

            if (!response.ok) {
                throw new Error("Falha ao carregar serviços.");
            }

            const data = await response.json();
            preencherSelect(servicos, data.servicos || [], null);
            renderizarServicos();
        } catch (error) {
            console.error(error);
        } finally {
            servicos.disabled = false;
        }
    };

    conexao.addEventListener("change", async () => {
        preencherSelect(unidade, [], "Carregando unidades...");
        preencherSelect(servicos, [], null);
        renderizarServicos();
        unidade.disabled = true;
        servicos.disabled = true;

        if (!conexao.value) {
            preencherSelect(unidade, [], "Selecione uma conexão primeiro");
            unidade.disabled = false;
            servicos.disabled = false;
            return;
        }

        try {
            const url = new URL(form.dataset.unidadesUrl, window.location.origin);
            url.searchParams.set("conexao_id", conexao.value);

            const response = await fetch(url, {
                headers: {"X-Requested-With": "XMLHttpRequest"},
            });

            if (!response.ok) {
                throw new Error("Falha ao carregar unidades.");
            }

            const data = await response.json();
            preencherSelect(
                unidade,
                data.unidades || [],
                "Selecione uma unidade",
            );
        } catch (error) {
            console.error(error);
            preencherSelect(unidade, [], "Não foi possível carregar as unidades");
        } finally {
            unidade.disabled = false;
            servicos.disabled = false;
        }
    });

    unidade.addEventListener("change", carregarServicos);
    botaoAdicionar?.addEventListener(
        "click",
        () => moverServicos(disponiveis, true),
    );
    botaoRemover?.addEventListener(
        "click",
        () => moverServicos(selecionados, false),
    );
    disponiveis.addEventListener(
        "dblclick",
        () => moverServicos(disponiveis, true),
    );
    selecionados.addEventListener(
        "dblclick",
        () => moverServicos(selecionados, false),
    );
    filtroDisponiveis?.addEventListener(
        "input",
        (event) => filtrarLista(disponiveis, event.target.value),
    );
    filtroSelecionados?.addEventListener(
        "input",
        (event) => filtrarLista(selecionados, event.target.value),
    );

    renderizarServicos();
});
