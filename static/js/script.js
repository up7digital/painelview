let ultimaSenha = null;
let paginaJaAtualizouPorErro = false;


console.log("===== Versão do Script: 1.2.0 =====");

// 1) INICIAR CONEXÃO COM MERCURE
console.log("🔌 Iniciando conexão Mercure via proxy...");
console.log("URL usada:", `/mercure-proxy/${window.PAINEL_ID}/`);

const evtSource = new EventSource(`/mercure-proxy/${window.PAINEL_ID}/`);

evtSource.onerror = function(err) {
    console.error("🔴 ERRO SSE:", err);

    // Se o servidor deu timeout, quebra inevitável
    if (err && err.target && err.target.readyState === EventSource.CLOSED) {
        console.warn("🔌 Conexão SSE fechada pelo servidor");
    }

    if (!paginaJaAtualizouPorErro) {
        paginaJaAtualizouPorErro = true;

        console.warn("🔄 Reload por erro SSE...");
        setTimeout(() => location.reload(), 1500);
    }
};


// RECEBEU EVENTO MERCURE
evtSource.onmessage = function(event) {
    let data;
    try {
        data = JSON.parse(event.data);
        console.log("🟢 JSON PARSE OK:", data);
    } catch (err) {
        console.error("❌ ERRO PARSE JSON:", err, "DATA:", event.data);
        return;
    }


    // 1) HTML pronto
    if (data.html) {
        try {
            document.getElementById("area-exibicao_senhas").innerHTML = data.html;
        } catch (err) {
            console.error("❌ ERRO ao aplicar HTML:", err);
        }

        const el = document.querySelector(".senha-atual_exbicao");
        if (el) {
            mostrarSenhaComCampainha(el);
            resetarTimerTelaDescanso();

        } else {
            console.warn("⚠️ HTML não contém '.senha-atual_exbicao'");
        }
        return;
    }

    // 2) evento de ID → buscar dados completos
    if (data.id) {
        atualizarPainel();
        return;
    }

    // 3) dados de senha_atual
    if (!data.senha_atual) {
        console.warn("⚠️ Evento sem senha_atual. Ignorado.", data);
        return;
    }


    const elSenha = document.querySelector(".senha-atual_exbicao");
    if (!elSenha) {
        console.error("❌ Elemento .senha-atual_exbicao NÃO encontrado!");
    } else {
        elSenha.innerText = data.senha_atual.senha;

        const local = document.querySelector(".detalhes-atual_local");
        const prioridade = document.querySelector(".detalhes-atual_prioridade");

        if (local) {
            local.innerText = "Local: " + data.senha_atual.local + " " + data.senha_atual.numeroLocal;
        } else {
            console.warn("⚠️ '.detalhes-atual_local' NÃO encontrado!");
        }

        if (prioridade) {
            prioridade.innerText = data.senha_atual.prioridade;
        } else {
            console.warn("⚠️ '.detalhes-atual_prioridade' NÃO encontrado!");
        }

        mostrarSenhaComCampainha(elSenha);
    }

    // 4) Atualizar histórico
    if (Array.isArray(data.historico)) {

        const ulHist = document.querySelector(".historico-lista");
        if (!ulHist) {
            console.error("❌ '.historico-lista' NÃO encontrado!");
        } else {
            ulHist.innerHTML = "";
            data.historico.slice(0, 5).forEach(item => {
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

    fetch(`/painel-dados/?painel=${window.PAINEL_ID}`)
        .then(r => {
            return r.json();
        })
        .then(data => {

            const elSenha = document.querySelector(".senha-atual_exbicao");

            if (data.senha_atual && elSenha) {
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
                resetarTimerTelaDescanso();
            }

            // HISTÓRICO
            if (Array.isArray(data.historico)) {
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

    // Campainha
    const audio = document.getElementById("audio-campainha");

    if (!audio) {
        console.warn("⚠️ Nenhum audio encontrado (id='audio-campainha')");
    } else {
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

