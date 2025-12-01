// Controle dos Slides ====================================================
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


// Controle de atualização dos slides ===========================================
// Captura o ID do painel da URL (?painel=4)
const painelId = new URLSearchParams(window.location.search).get("painel");

// Abre o WebSocket apontando para o caminho correto:
const socket = new WebSocket(
    `ws://${window.location.host}/ws/painel/${painelId}/`
);

// Quando o servidor enviar uma atualização
socket.onmessage = function(event) {
    const data = JSON.parse(event.data);

    if (data.action === "update") {

        // Recarrega somente o conteúdo da div painel-lateral
        fetch(window.location.href)
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, "text/html");
                const updated = doc.querySelector("#painel-lateral");
                document.querySelector("#painel-lateral").innerHTML = updated.innerHTML;
            });
    }
};

// Apenas para debug
socket.onopen = () => console.log("🟢 WebSocket conectado");
socket.onerror = (e) => console.log("🔴 Erro WebSocket:", e);
socket.onclose = () => console.log("🟡 WebSocket fechado");
