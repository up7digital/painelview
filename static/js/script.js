let ultimaSenha = null;

console.log("======================================");
console.log("🟦 SCRIPT DO PAINEL INICIADO");
console.log("PAINEL_ID:", window.PAINEL_ID);
console.log("======================================");

// 1) INICIAR CONEXÃO COM MERCURE
console.log("🔌 Iniciando conexão Mercure via proxy...");
console.log("URL usada:", `/mercure-proxy/${window.PAINEL_ID}/`);

const evtSource = new EventSource(`/mercure-proxy/${window.PAINEL_ID}/`);

// Evento ao abrir a conexão
evtSource.onopen = function() {
    console.log("🟢 SSE CONECTADO com sucesso!");
};

// Evento de erro
evtSource.onerror = function(err) {
    console.error("🔴 ERRO SSE:", err);
};

// RECEBEU EVENTO MERCURE
evtSource.onmessage = function(event) {
    console.log("======================================");
    console.log("📨 EVENTO MERCURE RECEBIDO (RAW):", event);
    console.log("📨 EVENTO MERCURE DATA:", event.data);
    console.log("======================================");

    let data;
    try {
        data = JSON.parse(event.data);
        console.log("🟢 JSON PARSE OK:", data);
    } catch (err) {
        console.error("❌ ERRO PARSE JSON:", err, "DATA:", event.data);
        return;
    }

    console.log("🔍 Tipo de evento recebido:", Object.keys(data));

    // 1) HTML pronto
    if (data.html) {
        console.log("📄 HTML recebido → substituindo área de exibição");
        try {
            document.getElementById("area-exibicao_senhas").innerHTML = data.html;
        } catch (err) {
            console.error("❌ ERRO ao aplicar HTML:", err);
        }

        const el = document.querySelector(".senha-atual_exbicao");
        if (el) {
            console.log("🔔 Chamando campainha para HTML...");
            mostrarSenhaComCampainha(el);
        } else {
            console.warn("⚠️ HTML não contém '.senha-atual_exbicao'");
        }
        return;
    }

    // 2) evento de ID → buscar dados completos
    if (data.id) {
        console.log("🆔 Evento contém ID. Chamando atualizarPainel()...");
        atualizarPainel();
        return;
    }

    // 3) dados de senha_atual
    if (!data.senha_atual) {
        console.warn("⚠️ Evento sem senha_atual. Ignorado.", data);
        return;
    }

    console.log("🔽 Atualizando senha atual:", data.senha_atual);

    const elSenha = document.querySelector(".senha-atual_exbicao");
    if (!elSenha) {
        console.error("❌ Elemento .senha-atual_exbicao NÃO encontrado!");
    } else {
        console.log("✏️ Atualizando elemento da senha atual...");
        elSenha.innerText = data.senha_atual.senha;

        const local = document.querySelector(".detalhes-atual_local");
        const prioridade = document.querySelector(".detalhes-atual_prioridade");

        if (local) {
            console.log("📍 Atualizando LOCAL:", data.senha_atual.local, data.senha_atual.numeroLocal);
            local.innerText = "Local: " + data.senha_atual.local + " " + data.senha_atual.numeroLocal;
        } else {
            console.warn("⚠️ '.detalhes-atual_local' NÃO encontrado!");
        }

        if (prioridade) {
            console.log("🏆 Atualizando PRIORIDADE:", data.senha_atual.prioridade);
            prioridade.innerText = data.senha_atual.prioridade;
        } else {
            console.warn("⚠️ '.detalhes-atual_prioridade' NÃO encontrado!");
        }

        mostrarSenhaComCampainha(elSenha);
    }

    // 4) Atualizar histórico
    if (Array.isArray(data.historico)) {
        console.log(`📜 Atualizando histórico (${data.historico.length} itens)...`);

        const ulHist = document.querySelector(".historico-lista");
        if (!ulHist) {
            console.error("❌ '.historico-lista' NÃO encontrado!");
        } else {
            ulHist.innerHTML = "";
            data.historico.slice(0, 7).forEach(item => {
                console.log("➕ Histórico item:", item);
                const li = document.createElement("li");
                li.className = "historico-senhas";
                li.innerHTML = `
                    <span class="historico-senha_atual">${item.senha}</span>
                    <span class="hist-local">Guichê ${item.numeroLocal}</span>`;
                ulHist.appendChild(li);
            });
        }
    } else {
        console.warn("⚠️ Historico não veio como array!", data.historico);
    }
};

// FUNÇÃO DE FETCH COMPLETO
function atualizarPainel() {
    console.log("🌐 Iniciando FETCH → /painel-dados/?painel=" + window.PAINEL_ID);

    fetch(`/painel-dados/?painel=${window.PAINEL_ID}`)
        .then(r => {
            console.log("📡 RESPOSTA FETCH (RAW):", r);
            return r.json();
        })
        .then(data => {
            console.log("🔄 FETCH JSON RECEBIDO:", data);

            const elSenha = document.querySelector(".senha-atual_exbicao");

            if (data.senha_atual && elSenha) {
                console.log("✏️ Atualizando senha atual via FETCH...", data.senha_atual);
                elSenha.innerText = data.senha_atual.senha;

                // ⭐ ATUALIZA A COR DA SENHA PRINCIPAL
                elSenha.classList.remove("color_convencional", "color_prioridade");

                if (data.senha_atual.prioridade === "Normal") {
                    elSenha.classList.add("color_convencional");
                } else if (data.senha_atual.prioridade === "Prioridade") {
                    elSenha.classList.add("color_prioridade");
                }

                // Atualiza local e prioridade
                const local = document.querySelector(".detalhes-atual_local");
                const prioridade = document.querySelector(".detalhes-atual_prioridade");

                if (local)
                    local.innerText = "Local: " + data.senha_atual.local + " " + data.senha_atual.numeroLocal;

                if (prioridade) {
                    prioridade.innerText = data.senha_atual.prioridade;

                    // ⭐ ATUALIZA A COR DA PRIORIDADE
                    prioridade.classList.remove("color_convencional", "color_prioridade");

                    if (data.senha_atual.prioridade === "Normal") {
                        prioridade.classList.add("color_convencional");
                    } else if (data.senha_atual.prioridade === "Prioridade") {
                        prioridade.classList.add("color_prioridade");
                    }
                }

                mostrarSenhaComCampainha(elSenha);
            }

            // HISTÓRICO
            if (Array.isArray(data.historico)) {
                console.log("📜 Atualizando histórico via FETCH:", data.historico.length, "itens");
                const ulHist = document.querySelector(".historico-lista");
                ulHist.innerHTML = "";

                data.historico.slice(0, 7).forEach(item => {
                    const li = document.createElement("li");
                    li.className = "historico-senhas";
                    li.innerHTML = `
                        <span class="historico-senha_atual">${item.senha}</span>
                        <span class="hist-local">Guichê ${item.numeroLocal}</span>`;
                    ulHist.appendChild(li);
                });
            } else {
                console.warn("⚠️ Historico não veio via FETCH:", data.historico);
            }
        })
        .catch(err => {
            console.error("❌ ERRO FETCH painel-dados:", err);
        });
}

function mostrarSenhaComCampainha(el) {
    console.log("🔔 Executando mostrarSenhaComCampainha");
    console.log("Elemento recebido:", el);

    // Campainha
    const audio = document.getElementById("audio-campainha");

    if (!audio) {
        console.warn("⚠️ Nenhum audio encontrado (id='audio-campainha')");
    } else {
        console.log("🔊 Tocando campainha...");
        audio.currentTime = 0;
        audio.play().catch(err => {
            console.warn("⚠️ Autoplay bloqueado:", err);
        });
    }

    // Animação piscar
    el.classList.remove("piscar");
    void el.offsetWidth;
    el.classList.add("piscar");
}

