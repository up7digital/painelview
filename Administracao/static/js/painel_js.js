(function($) {
    $(document).ready(function() {
        const $conexao = $('#id_conexao');
        const $unidade = $('#id_unidade_sga');
        const $servicos = $('#id_servicos_sga_from'); // FilteredSelectMultiple "from" box

        function carregarUnidades() {
            const conexao_id = $conexao.val();
            if (!conexao_id) return;

            $.getJSON('/ajax/carregar-unidades/', { conexao_id }, function(data) {
                $unidade.empty().append($('<option>', {value: '', text: '---------'}));
                data.unidades.forEach(u => {
                    $unidade.append($('<option>', { value: u.id, text: u.text }));
                });

                // Se já existir unidade selecionada, carrega os serviços
                if ($unidade.val()) carregarServicos();
            });
        }

        function carregarServicos() {
            const conexao_id = $conexao.val();
            const unidade_id = $unidade.val();
            if (!conexao_id || !unidade_id) return;

            $.getJSON('/ajax/carregar-servicos/', { conexao_id, unidade_id }, function(data) {
                $servicos.empty();
                data.servicos.forEach(s => {
                    $servicos.append($('<option>', { value: s.id, text: s.text }));
                });
            });
        }

        $conexao.change(carregarUnidades);
        $unidade.change(carregarServicos);

        // Carrega os dados iniciais se for edição
        if ($conexao.val()) carregarUnidades();
    });
})(django.jQuery);
