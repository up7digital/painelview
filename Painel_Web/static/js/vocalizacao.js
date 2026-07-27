(function () {
    "use strict";

    let player = null;
    let vozesDisponiveis = [];

    console.log("🔊 Módulo de vocalização carregado.");

    function textoLimpo(valor) {
        return valor == null ? "" : String(valor).trim().replace(/\s+/g, " ");
    }

    function senhaParaFala(senha) {
        return Array.from(textoLimpo(senha))
            .filter((caractere) => !/\s/.test(caractere))
            .join(" ");
    }

    function obterConfiguracao() {
        const configuracao = window.VOCALIZACAO_CONFIG || {};
        const velocidade = Number(configuracao.velocidade);
        const tom = Number(configuracao.tom);

        return {
            voz: textoLimpo(configuracao.voz),
            velocidade:
                Number.isFinite(velocidade) && velocidade >= 0.5 && velocidade <= 2
                    ? velocidade
                    : 0.9,
            tom:
                Number.isFinite(tom) && tom >= 0.5 && tom <= 2
                    ? tom
                    : 1,
        };
    }

    function obterVoz(configuracao) {
        const nomeConfigurado = textoLimpo(
            configuracao.voz,
        ).toLocaleLowerCase("pt-BR");
        const vozConfigurada = vozesDisponiveis.find(
            (voz) => textoLimpo(voz.name).toLocaleLowerCase("pt-BR")
                === nomeConfigurado,
        );

        if (vozConfigurada) {
            return vozConfigurada;
        }

        if (configuracao.voz) {
            console.warn(
                `🔊 A voz salva "${configuracao.voz}" não está disponível neste navegador.`,
            );
        }

        return vozesDisponiveis.find(
            (voz) => voz.lang.toLocaleLowerCase().startsWith("pt-br"),
        ) || vozesDisponiveis.find(
            (voz) => voz.lang.toLocaleLowerCase().startsWith("pt"),
        ) || null;
    }

    function atualizarVozesDisponiveis() {
        vozesDisponiveis = window.speechSynthesis?.getVoices() || [];
    }

    atualizarVozesDisponiveis();
    window.speechSynthesis?.addEventListener(
        "voiceschanged",
        atualizarVozesDisponiveis,
    );

    function aplicarConfiguracaoPlayer(talkifyPlayer) {
        atualizarVozesDisponiveis();

        const configuracao = obterConfiguracao();
        const voz = obterVoz(configuracao);

        talkifyPlayer.forceLanguage("pt-BR");
        if (voz) {
            talkifyPlayer.forceVoice(voz);
            console.log(
                `🔊 Voz aplicada à chamada: ${voz.name} (${voz.lang}).`,
            );
        }
        talkifyPlayer.setRate(configuracao.velocidade);
        talkifyPlayer.usePitch(configuracao.tom);
        talkifyPlayer.setVolume(1);

        return configuracao;
    }

    function montarTexto(chamada) {
        const textoBackend = textoLimpo(chamada?.vocalizacao?.texto);
        if (textoBackend) {
            return textoBackend;
        }

        const nomeCliente = textoLimpo(chamada?.nomeCliente);
        const senha = senhaParaFala(chamada?.senha);
        const destinoPronto = textoLimpo(chamada?.textoLocal);
        const destino = destinoPronto || [
            textoLimpo(chamada?.local),
            textoLimpo(chamada?.numeroLocal),
        ].filter(Boolean).join(" ");

        return [
            nomeCliente,
            senha ? `Senha ${senha}` : "",
            destino,
        ].filter(Boolean).join(" ");
    }

    function obterPlayer() {
        if (player) {
            return player;
        }

        if (!window.talkify?.Html5Player) {
            console.warn(
                "🔊 Talkify indisponível; usando a síntese de voz do navegador.",
            );
            return null;
        }

        if (window.talkify.config?.remoteService) {
            window.talkify.config.remoteService.active = false;
        }

        if (window.talkify.config?.ui?.audioControls) {
            window.talkify.config.ui.audioControls.enabled = false;
        }

        player = new window.talkify.Html5Player();

        return player;
    }

    function reproduzirComNavegador(texto) {
        if (
            !window.speechSynthesis ||
            typeof window.SpeechSynthesisUtterance !== "function"
        ) {
            console.error(
                "🔇 O navegador não oferece suporte à síntese de voz.",
            );
            return Promise.resolve();
        }

        window.speechSynthesis.cancel();

        const configuracao = obterConfiguracao();
        atualizarVozesDisponiveis();
        const fala = new window.SpeechSynthesisUtterance(texto);
        fala.lang = "pt-BR";
        fala.voice = obterVoz(configuracao);
        fala.rate = configuracao.velocidade;
        fala.pitch = configuracao.tom;
        fala.volume = 1;
        return new Promise((resolve) => {
            let finalizada = false;

            const finalizar = () => {
                if (finalizada) {
                    return;
                }
                finalizada = true;
                resolve();
            };

            fala.onend = finalizar;
            fala.onerror = function (event) {
                console.error(
                    "🔇 Erro na síntese de voz do navegador:",
                    event.error,
                );
                finalizar();
            };

            window.speechSynthesis.speak(fala);
            console.log("🔊 Vocalização nativa iniciada:", texto);
            window.setTimeout(finalizar, Math.max(10000, texto.length * 600));
        });
    }

    function aguardarFimTalkify(texto) {
        if (!window.speechSynthesis) {
            return Promise.resolve();
        }

        return new Promise((resolve) => {
            const inicio = Date.now();
            const limite = Math.min(
                60000,
                Math.max(10000, texto.length * 600),
            );
            let iniciou = false;

            const verificar = window.setInterval(() => {
                const sintetizadorOcupado = (
                    window.speechSynthesis.speaking
                    || window.speechSynthesis.pending
                );

                iniciou = iniciou || sintetizadorOcupado;

                if (
                    (iniciou && !sintetizadorOcupado)
                    || (!iniciou && Date.now() - inicio > 3000)
                    || Date.now() - inicio > limite
                ) {
                    window.clearInterval(verificar);
                    resolve();
                }
            }, 100);
        });
    }

    async function reproduzirTexto(texto) {
        const talkifyPlayer = obterPlayer();
        if (!texto) {
            return Promise.resolve();
        }

        if (!talkifyPlayer) {
            return reproduzirComNavegador(texto);
        }

        window.speechSynthesis?.cancel();
        aplicarConfiguracaoPlayer(talkifyPlayer);

        try {
            const reproducao = talkifyPlayer.playText(texto);
            console.log("🔊 Vocalização Talkify iniciada:", texto);

            if (reproducao?.catch) {
                const falhaTalkify = new Promise((resolve, reject) => {
                    reproducao.catch(reject);
                });

                try {
                    await Promise.race([
                        aguardarFimTalkify(texto),
                        falhaTalkify,
                    ]);
                } catch (erro) {
                    console.error(
                        "🔇 Não foi possível vocalizar a chamada:",
                        erro,
                    );
                    await reproduzirComNavegador(texto);
                }
            } else {
                await aguardarFimTalkify(texto);
            }
        } catch (erro) {
            console.error("🔇 Não foi possível vocalizar a chamada:", erro);
            await reproduzirComNavegador(texto);
        }
    }

    window.VocalizacaoPainel = {
        montarTexto,
        vocalizar(chamada) {
            const texto = montarTexto(chamada || {});
            if (!texto) {
                console.warn(
                    "🔇 Chamada sem dados suficientes para vocalização.",
                );
                return Promise.resolve();
            }

            console.log("🔊 Chamada recebida para vocalização:", texto);
            return reproduzirTexto(texto);
        },
    };
})();
