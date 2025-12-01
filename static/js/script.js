let ultimaSenha = null;

// 1) INICIAR CONEXÃO COM MERCURE
console.log("🔌 Iniciando conexão Mercure via proxy...");
console.log("URL usada:", `/mercure-proxy/${window.PAINEL_ID}/`);

const evtSource = new EventSource(`/mercure-proxy/${window.PAINEL_ID}/`);

// Evento ao abrir a conexão
evtSource.onopen = function() {
    console.log("🟢 CONECTADO ao Mercure com sucesso!");
};

// Evento de erro
evtSource.onerror = function(err) {
    console.error("🔴 ERRO NA CONEXÃO SSE:", err);
};

// 2) RECEBEU UM EVENTO DO MERCURE

evtSource.onmessage = function(event) {
    console.log("📨 EVENTO MERCURE CRU:", event.data);

    let data;
    try {
        data = JSON.parse(event.data);
    } catch (err) {
        console.error("❌ ERRO: evento Mercure não é JSON válido!", event.data);
        return;
    }

    // Se veio HTML pronto
    if (data.html) {
        document.getElementById("area-exibicao_senhas").innerHTML = data.html;
        const el = document.querySelector(".senha-atual_exbicao");
        if (el) mostrarSenhaComCampainha(el);
        return;
    }

    // Se veio apenas o ID → buscar dados completos
    if (data.id) {
        atualizarPainel();
        return;
    }

    // Se não tem senha_atual → ignora
    if (!data.senha_atual) return;

    // Atualizar senha atual
    const elSenha = document.querySelector(".senha-atual_exbicao");
    if (elSenha) {
        elSenha.innerText = data.senha_atual.senha;

        const local = document.querySelector(".detalhes-atual_local");
        const prioridade = document.querySelector(".detalhes-atual_prioridade");

        if (local)
            local.innerText = "Local: " + data.senha_atual.local + " " + data.senha_atual.numeroLocal;

        if (prioridade)
            prioridade.innerText = data.senha_atual.prioridade;

        mostrarSenhaComCampainha(elSenha);
    }

    // Atualizar histórico **sempre com base no backend**
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
    }
};

// Função de fetch completo
function atualizarPainel() {
    fetch(`/painel-dados/?painel=${window.PAINEL_ID}`)
        .then(r => r.json())
        .then(data => {
            console.log("🔄 Dados completos recebidos:", data);

            const elSenha = document.querySelector(".senha-atual_exbicao");

            if (data.senha_atual && elSenha) {

                // Atualiza o número da senha
                elSenha.innerText = data.senha_atual.senha;

                // === ATUALIZAÇÃO DINÂMICA DA COR ===
                elSenha.classList.remove("color_convencional", "color_prioridade");

                const prioridadeSenha = data.senha_atual.prioridade;

                if (prioridadeSenha === "Normal") {
                    elSenha.classList.add("color_convencional");
                } else if (prioridadeSenha === "Prioridade") {
                    elSenha.classList.add("color_prioridade");
                }

                // Atualiza local e prioridade textual
                const local = document.querySelector(".detalhes-atual_local");
                const prioridade = document.querySelector(".detalhes-atual_prioridade");

                if (local)
                    local.innerText = "Local: " + data.senha_atual.local + " " + data.senha_atual.numeroLocal;

                if (prioridade)
                    prioridade.innerText = data.senha_atual.prioridade;

                mostrarSenhaComCampainha(elSenha);
            }

            // Atualização do histórico
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
            }
        })
        .catch(err => console.error("❌ Erro ao buscar dados do painel:", err));
}

function mostrarSenhaComCampainha(el) {

    // Tocar campainha
    const audio = document.getElementById("audio-campainha");
    if (!audio) {
        console.warn("⚠️ Nenhuma campainha configurada para este painel.");
        return;
    }

    audio.currentTime = 0;
    audio.play().catch(err => {
        console.warn("⚠️ Navegador bloqueou autoplay da campainha:", err);
    });
    // Piscar a senha
    el.classList.remove("piscar");  // remove caso já tenha
    void el.offsetWidth;             // força reflow (reset da animação)
    el.classList.add("piscar");      // adiciona novamente
}
