// Controle de exibição dos campos do cadastro de mídia (Admin Django)
document.addEventListener("DOMContentLoaded", function () {
    const tipoField = document.getElementById("id_tipo");
    const arquivoField = document.getElementById("id_arquivo");
    const textoField = document.getElementById("id_texto");

    if (!tipoField) return;

    const arquivoRow = arquivoField ? arquivoField.closest(".form-row, .form-group") : null;
    const textoRow = textoField ? textoField.closest(".form-row, .form-group") : null;

    function toggleFields() {
        if (tipoField.value === "Texto") {
            if (arquivoRow) arquivoRow.style.display = "none";
            if (textoRow) textoRow.style.display = "";
        } else {
            if (arquivoRow) arquivoRow.style.display = "";
            if (textoRow) textoRow.style.display = "none";
        }
    }

    // estado inicial (edição e criação)
    toggleFields();

    // mudança dinâmica
    tipoField.addEventListener("change", toggleFields);
});
