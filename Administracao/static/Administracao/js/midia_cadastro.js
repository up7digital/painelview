document.addEventListener("DOMContentLoaded", () => {
    const seletorTipo = document.querySelector("[data-media-type]");
    const blocoArquivo = document.querySelector("[data-media-file-fields]");
    const blocoTexto = document.querySelector("[data-media-text-fields]");
    const campoArquivo = document.querySelector("[data-media-upload]");
    const editorTexto = document.querySelector("[data-text-preview]");

    if (!seletorTipo || !blocoArquivo || !blocoTexto || !campoArquivo) {
        return;
    }

    const atualizarCamposDoTipo = () => {
        const tipo = seletorTipo.value;
        const ehTexto = tipo === "Texto";

        blocoArquivo.hidden = ehTexto;
        blocoTexto.hidden = !ehTexto;
        campoArquivo.required = !ehTexto;

        if (tipo === "Imagem") {
            campoArquivo.accept = ".png,.jpg,.jpeg,.webp,image/png,image/jpeg,image/webp";
        } else if (tipo === "Vídeo") {
            campoArquivo.accept = ".mp4,.mov,video/mp4,video/quicktime";
        }

        if (ehTexto) {
            campoArquivo.value = "";
            editorTexto?.focus();
        }
    };

    seletorTipo.addEventListener("change", atualizarCamposDoTipo);
    atualizarCamposDoTipo();
});
