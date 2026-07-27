document.addEventListener("DOMContentLoaded", () => {
    const setorSelect = document.getElementById("select_setor");
    const painelSelect = document.getElementById("select_painel");

    if (!setorSelect || !painelSelect) {
        return;
    }

    setorSelect.addEventListener("change", async () => {
        const setorId = setorSelect.value;

        painelSelect.replaceChildren(new Option("Escolher um painel", ""));
        painelSelect.disabled = true;

        if (!setorId) {
            return;
        }

        try {
            const response = await fetch(
                `/selecionar/paineis-por-setor/?setor=${encodeURIComponent(setorId)}`,
            );

            if (!response.ok) {
                throw new Error(`Falha ao carregar os painéis: ${response.status}`);
            }

            const paineis = await response.json();

            paineis.forEach((painel) => {
                painelSelect.add(new Option(painel.nome, painel.id));
            });

            painelSelect.disabled = false;
        } catch (error) {
            console.error(error);
            painelSelect.replaceChildren(
                new Option("Não foi possível carregar os painéis", ""),
            );
        }
    });
});
