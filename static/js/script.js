let ultimaAssinaturaRecebida = "";
let ultimoIdChamada = null;
let atualizacaoEmAndamento = false;
let atualizacaoForcadaPendente = false;
let eventoIdPendente = null;
let chamadaEmExecucao = false;

const filaChamadas = [];
const idsNaFila = new Set();

console.log("===== Versão do Script: 1.3.1 =====");

function normalizarAssinatura(valor) {
    return String(valor ?? "").trim().replace(/\s+/g, " ").toLowerCase();
}

function criarAssinaturaChamada(chamada) {
    if (!chamada?.senha) {
        return "";
    }

    const destino = chamada.textoLocal || [
        chamada.local,
        chamada.numeroLocal,
    ].filter(
        (valor) => valor !== null && valor !== undefined && valor !== "",
    ).join(" ");

    return [
        normalizarAssinatura(chamada.senha),
        normalizarAssinatura(destino),
    ].join("|");
}

function obterIdChamada(chamada) {
    const id = Number(chamada?.id);
    return Number.isFinite(id) && id > 0 ? id : null;
}

function atualizarHistorico(historico) {
    if (!Array.isArray(historico)) {
        return;
    }

    const lista = document.querySelector(".historico-lista");
    if (!lista) {
        return;
    }

    lista.replaceChildren();

    historico.slice(0, 7).forEach((item) => {
        const linha = document.createElement("li");
        const senha = document.createElement("span");
        const local = document.createElement("span");

        linha.className = "historico-senhas";
        senha.className = "historico-senha_atual";
        senha.textContent = item.senha;
        local.className = "hist-local";
        local.textContent = `${item.local || "Guichê"} ${item.numeroLocal ?? ""}`;

        linha.append(senha, local);
        lista.appendChild(linha);
    });
}

function atualizarExibicaoChamada(chamada) {
    const senha = document.querySelector(".senha-atual_exbicao");
    const nomeCliente = document.querySelector(".detalhes-atual_cliente");
    const local = document.querySelector(".detalhes-atual_local");
    const prioridade = document.querySelector(".detalhes-atual_prioridade");

    if (!senha) {
        throw new Error("Elemento da senha atual não encontrado.");
    }

    senha.textContent = chamada.senha;
    senha.dataset.chamadaId = chamada.id || "";

    if (nomeCliente) {
        const nome = String(chamada.nomeCliente ?? "").trim();
        nomeCliente.textContent = nome;
        nomeCliente.hidden = !nome;
        nomeCliente.classList.remove(
            "color_convencional",
            "color_prioridade",
        );

        if (chamada.prioridade === "Normal") {
            nomeCliente.classList.add("color_convencional");
        } else if (chamada.prioridade === "Prioridade") {
            nomeCliente.classList.add("color_prioridade");
        }
    }

    senha.classList.remove("color_convencional", "color_prioridade");

    if (chamada.prioridade === "Normal") {
        senha.classList.add("color_convencional");
    } else if (chamada.prioridade === "Prioridade") {
        senha.classList.add("color_prioridade");
    }

    if (local) {
        const textoLocal = chamada.textoLocal
            || [chamada.local, chamada.numeroLocal].filter(
                (valor) => valor !== null
                    && valor !== undefined
                    && valor !== "",
            ).join(" ");
        local.textContent = textoLocal ? `Local: ${textoLocal}` : "";
    }

    if (prioridade) {
        prioridade.textContent = chamada.prioridade || "";
        prioridade.classList.remove("color_convencional", "color_prioridade");

        if (chamada.prioridade === "Normal") {
            prioridade.classList.add("color_convencional");
        } else if (chamada.prioridade === "Prioridade") {
            prioridade.classList.add("color_prioridade");
        }
    }

    senha.classList.remove("piscar");
    void senha.offsetWidth;
    senha.classList.add("piscar");
}

function tocarCampainha() {
    const audio = document.getElementById("audio-campainha");
    if (!audio || !audio.currentSrc) {
        return Promise.resolve();
    }

    return new Promise((resolve) => {
        let finalizado = false;

        const finalizar = () => {
            if (finalizado) {
                return;
            }
            finalizado = true;
            audio.removeEventListener("ended", finalizar);
            audio.removeEventListener("error", finalizar);
            resolve();
        };

        audio.pause();
        audio.currentTime = 0;
        audio.addEventListener("ended", finalizar, { once: true });
        audio.addEventListener("error", finalizar, { once: true });

        const reproducao = audio.play();
        if (reproducao?.catch) {
            reproducao.catch((erro) => {
                console.warn("⚠️ Autoplay da campainha bloqueado:", erro);
                finalizar();
            });
        }

        window.setTimeout(finalizar, 10000);
    });
}

async function processarFilaChamadas() {
    if (chamadaEmExecucao || filaChamadas.length === 0) {
        return;
    }

    chamadaEmExecucao = true;
    const chamada = filaChamadas.shift();
    const id = obterIdChamada(chamada);

    try {
        atualizarExibicaoChamada(chamada);
        resetarTimerTelaDescanso();

        console.log(
            `🔔 Executando chamada ${chamada.senha}. Restantes na fila: ${filaChamadas.length}.`,
        );

        const campainha = tocarCampainha();
        const vocalizacao = window.VocalizacaoPainel?.vocalizar(chamada)
            || Promise.resolve();

        await Promise.allSettled([campainha, vocalizacao]);
        console.log(`✅ Chamada ${chamada.senha} concluída.`);
    } catch (erro) {
        console.error("❌ Erro ao executar chamada da fila:", erro);
    } finally {
        if (id) {
            idsNaFila.delete(id);
        }
        chamadaEmExecucao = false;
        processarFilaChamadas();
    }
}

function enfileirarChamada(chamada) {
    if (!chamada?.senha) {
        return;
    }

    const id = obterIdChamada(chamada);
    if (id && idsNaFila.has(id)) {
        return;
    }

    if (id) {
        idsNaFila.add(id);
        ultimoIdChamada = Math.max(ultimoIdChamada || 0, id);
    }

    ultimaAssinaturaRecebida = criarAssinaturaChamada(chamada);
    filaChamadas.push({...chamada});

    console.log(
        `➕ Chamada ${chamada.senha} adicionada à fila. Total: ${filaChamadas.length}.`,
    );
    processarFilaChamadas();
}

function enfileirarNovasChamadas(data, forcarChamada, eventoId) {
    const chamadas = Array.isArray(data.chamadas) ? data.chamadas : [];
    const novasChamadas = chamadas
        .filter((chamada) => {
            const id = obterIdChamada(chamada);
            return id && (!ultimoIdChamada || id > ultimoIdChamada);
        })
        .sort((chamadaA, chamadaB) => (
            obterIdChamada(chamadaA) - obterIdChamada(chamadaB)
        ));

    if (novasChamadas.length) {
        novasChamadas.forEach(enfileirarChamada);
        return;
    }

    if (!data.senha_atual) {
        return;
    }

    const idEvento = Number(eventoId);
    const eventoJaRecebido = Number.isFinite(idEvento)
        && ultimoIdChamada
        && idEvento <= ultimoIdChamada;

    const assinatura = criarAssinaturaChamada(data.senha_atual);
    const chamadaMudou = assinatura
        && assinatura !== ultimaAssinaturaRecebida;

    if ((forcarChamada && !eventoJaRecebido) || chamadaMudou) {
        enfileirarChamada(data.senha_atual);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const senhaInicial = document.querySelector(".senha-atual_exbicao");
    const localInicial = document.querySelector(".detalhes-atual_local");

    ultimoIdChamada = obterIdChamada({
        id: senhaInicial?.dataset.chamadaId,
    });
    ultimaAssinaturaRecebida = criarAssinaturaChamada({
        senha: senhaInicial?.textContent,
        textoLocal: localInicial?.textContent.replace(/^Local:\s*/i, ""),
    });

    window.setInterval(() => atualizarPainel(false), 3000);
});

console.log("🔌 Iniciando conexão Mercure via proxy...");
const evtSource = new EventSource(`/mercure-proxy/${window.PAINEL_ID}/`);

evtSource.onerror = function (erro) {
    console.error("🔴 ERRO SSE:", erro);
    console.warn(
        "🔄 O EventSource tentará reconectar; a fila atual será preservada.",
    );
};

evtSource.onmessage = function (event) {
    let data;

    try {
        data = JSON.parse(event.data);
    } catch (erro) {
        console.error("❌ Evento Mercure com JSON inválido:", erro);
        return;
    }

    if (data.html) {
        const documento = new DOMParser().parseFromString(
            data.html,
            "text/html",
        );
        const senha = documento.querySelector(".senha-atual_exbicao");
        const nomeCliente = documento.querySelector(
            ".detalhes-atual_cliente",
        );
        const local = documento.querySelector(".detalhes-atual_local");
        const prioridade = documento.querySelector(
            ".detalhes-atual_prioridade",
        );

        enfileirarChamada({
            senha: senha?.textContent,
            nomeCliente: nomeCliente?.textContent.trim(),
            textoLocal: local?.textContent.replace(/^Local:\s*/i, ""),
            prioridade: prioridade?.textContent.trim(),
        });
        return;
    }

    if (data.id) {
        atualizarPainel(true, data.id);
        return;
    }

    if (data.senha_atual) {
        const id = obterIdChamada(data.senha_atual);
        if (!id || !ultimoIdChamada || id > ultimoIdChamada) {
            enfileirarChamada(data.senha_atual);
        }
        atualizarHistorico(data.historico);
    }
};

function atualizarPainel(forcarChamada = true, eventoId = null) {
    if (atualizacaoEmAndamento) {
        atualizacaoForcadaPendente =
            atualizacaoForcadaPendente || forcarChamada;
        eventoIdPendente = eventoIdPendente || eventoId;
        return;
    }

    atualizacaoEmAndamento = true;

    fetch(`/painel-dados/?painel=${window.PAINEL_ID}`)
        .then((response) => {
            if (!response.ok) {
                throw new Error(`Falha ao consultar painel: ${response.status}`);
            }
            return response.json();
        })
        .then((data) => {
            enfileirarNovasChamadas(data, forcarChamada, eventoId);
            atualizarHistorico(data.historico);
        })
        .catch((erro) => {
            console.error("❌ ERRO FETCH painel-dados:", erro);
        })
        .finally(() => {
            atualizacaoEmAndamento = false;

            if (atualizacaoForcadaPendente) {
                const idPendente = eventoIdPendente;
                atualizacaoForcadaPendente = false;
                eventoIdPendente = null;
                atualizarPainel(true, idPendente);
            }
        });
}
