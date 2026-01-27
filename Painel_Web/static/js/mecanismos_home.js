// Confetes ---------------------------------------------------------------------------
function confettiWide() {
    const duration = 1500;
    const end = Date.now() + duration;

    (function frame() {
        confetti({
            particleCount: 8,
            angle: 90,
            spread: 180,
            origin: { x: Math.random(), y: 0 }
        });

        if (Date.now() < end) {
            requestAnimationFrame(frame);
        }
    })();
}

document.addEventListener("DOMContentLoaded", () => {
    confettiWide();
});

// Controle do Select dos Painéis-----------------------------------------------------------
document.getElementById("select_setor").addEventListener("change", function () {
    const setorId = this.value;
    const painelSelect = document.getElementById("select_painel");

    painelSelect.innerHTML = '<option value="">-- Escolher um painel --</option>';
    painelSelect.disabled = true;

    if (!setorId) return;

    fetch(`/selecionar/paineis-por-setor/?setor=${setorId}`)
        .then(response => response.json())
        .then(data => {
            data.forEach(painel => {
                const option = document.createElement("option");
                option.value = painel.id;
                option.textContent = painel.nome;
                painelSelect.appendChild(option);
            });
            painelSelect.disabled = false;
        });
});
