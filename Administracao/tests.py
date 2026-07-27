from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.template.loader import render_to_string
from django.urls import reverse

from .models import (
    ConfigPainel,
    MidiaPainel,
    UsuarioSetor,
    tb_Conexoes,
    tb_Setores,
)


class MidiasPorSetorTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username="usuario_teste",
            password="senha_teste",
        )
        self.setor_usuario = tb_Setores.objects.create(nome_setor="Setor A")
        self.outro_setor = tb_Setores.objects.create(nome_setor="Setor B")
        UsuarioSetor.objects.create(
            usuario=self.usuario,
            setor=self.setor_usuario,
        )
        self.usuario.user_permissions.add(
            *Permission.objects.filter(
                codename__in=("acesso_mideas", "gerenciar_mideas"),
            )
        )

        self.midia_permitida = MidiaPainel.objects.create(
            tipo="Texto",
            texto="MIDIA SETOR A",
        )
        self.midia_permitida.setores.add(self.setor_usuario)

        self.midia_bloqueada = MidiaPainel.objects.create(
            tipo="Texto",
            texto="MIDIA SETOR B",
        )
        self.midia_bloqueada.setores.add(self.outro_setor)
        self.client.force_login(self.usuario)

    def test_painel_lateral_respeita_tamanho_configurado_do_texto(self):
        self.midia_permitida.texto_tamanho_fonte = 73
        self.midia_permitida.save(update_fields=["texto_tamanho_fonte"])

        html = render_to_string(
            "Painel_Web/partials/template_padrao.html",
            {
                "midias": [self.midia_permitida],
                "senha_atual": None,
                "historico": [],
                "painel": None,
            },
        )

        self.assertIn("--tamanho-texto-midia: 73px", html)

    def test_listagem_exibe_apenas_midias_do_setor_do_usuario(self):
        resposta = self.client.get(reverse("administracao:gestao_midias"))

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "MIDIA SETOR A")
        self.assertNotContains(resposta, "MIDIA SETOR B")

    def test_detalhes_bloqueiam_midia_de_outro_setor(self):
        url_permitida = reverse(
            "administracao:midia_detalhada",
            kwargs={"midia_id": self.midia_permitida.pk},
        )
        url_bloqueada = reverse(
            "administracao:midia_detalhada",
            kwargs={"midia_id": self.midia_bloqueada.pk},
        )

        resposta_permitida = self.client.get(url_permitida)
        resposta_bloqueada = self.client.get(url_bloqueada)

        self.assertEqual(resposta_permitida.status_code, 200)
        self.assertIn("setores", resposta_permitida.context["form"].fields)
        self.assertQuerySetEqual(
            resposta_permitida.context["form"].fields["setores"].queryset,
            [self.setor_usuario],
        )
        self.assertEqual(resposta_bloqueada.status_code, 404)

    def test_cadastro_vincula_midia_ao_setor_do_usuario(self):
        resposta = self.client.post(
            reverse("administracao:midia_cadastro"),
            {
                "tipo": "Texto",
                "texto": "NOVA MIDIA",
                "texto_tamanho_fonte": "32",
                "texto_cor": "#ffffff",
                "texto_alinhamento": "center",
                "ordem": "0",
                "ativo": "on",
                "exibir_lateral": "0",
                "exibir_popup": "1",
                "setores": [str(self.setor_usuario.pk)],
            },
        )

        nova_midia = MidiaPainel.objects.get(texto="NOVA MIDIA")
        self.assertRedirects(
            resposta,
            reverse(
                "administracao:midia_detalhada",
                kwargs={"midia_id": nova_midia.pk},
            ),
        )
        self.assertQuerySetEqual(
            nova_midia.setores.all(),
            [self.setor_usuario],
        )

    def test_usuario_com_multiplos_setores_pode_selecionar_apenas_os_seus(self):
        UsuarioSetor.objects.create(
            usuario=self.usuario,
            setor=self.outro_setor,
        )

        resposta = self.client.get(
            reverse(
                "administracao:midia_detalhada",
                kwargs={"midia_id": self.midia_bloqueada.pk},
            )
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertQuerySetEqual(
            resposta.context["form"].fields["setores"].queryset,
            [self.setor_usuario, self.outro_setor],
            ordered=False,
        )

    def test_edicao_preserva_vinculos_de_setores_nao_permitidos(self):
        self.midia_permitida.setores.add(self.outro_setor)

        resposta = self.client.post(
            reverse(
                "administracao:midia_detalhada",
                kwargs={"midia_id": self.midia_permitida.pk},
            ),
            {
                "texto": self.midia_permitida.texto,
                "texto_tamanho_fonte": "32",
                "texto_cor": "#ffffff",
                "texto_alinhamento": "center",
                "ordem": "0",
                "ativo": "on",
                "exibir_lateral": "0",
                "exibir_popup": "1",
                "setores": [],
            },
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertQuerySetEqual(
            self.midia_permitida.setores.all(),
            [self.outro_setor],
        )

    def test_usuario_pode_excluir_midia_de_seu_setor(self):
        resposta = self.client.post(
            reverse(
                "administracao:midia_detalhada",
                kwargs={"midia_id": self.midia_permitida.pk},
            ),
            {"acao": "excluir"},
        )

        self.assertRedirects(
            resposta,
            reverse("administracao:gestao_midias"),
        )
        self.assertFalse(
            MidiaPainel.objects.filter(
                pk=self.midia_permitida.pk,
            ).exists()
        )

    def test_admin_pode_selecionar_todos_os_setores(self):
        grupo_admin, _ = Group.objects.get_or_create(name="Admin")
        self.usuario.groups.add(grupo_admin)

        resposta = self.client.get(
            reverse(
                "administracao:midia_detalhada",
                kwargs={"midia_id": self.midia_bloqueada.pk},
            )
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertQuerySetEqual(
            resposta.context["form"].fields["setores"].queryset,
            [self.setor_usuario, self.outro_setor],
            ordered=False,
        )


class PermissaoConexoesTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username="usuario_conexoes",
            password="senha_teste",
        )
        self.permissao = Permission.objects.get(
            codename="gerenciar_conexao",
        )
        self.conexao = tb_Conexoes.objects.create(
            nome_conexao="Conexão teste",
            url_origem="https://example.com/",
            ip_mercure="127.0.0.1",
            porta_mercure=3000,
            user_sga="usuario",
            pass_sga="senha",
            client_id="cliente",
            client_secret="segredo",
        )

    def test_usuario_sem_permissao_nao_ve_menu_nem_acessa_backend(self):
        self.client.force_login(self.usuario)
        url_lista = reverse("administracao:conexoes")
        url_cadastro = reverse("administracao:conexao_cadastro")
        url_detalhes = reverse(
            "administracao:conexao_detalhes",
            kwargs={"conexao_id": self.conexao.pk},
        )

        configuracoes = self.client.get(
            reverse("administracao:configuracoes")
        )

        self.assertNotContains(configuracoes, f'href="{url_lista}"')
        self.assertEqual(self.client.get(url_lista).status_code, 403)
        self.assertEqual(self.client.post(url_cadastro, {}).status_code, 403)
        self.assertEqual(self.client.put(url_detalhes, {}).status_code, 403)

    def test_usuario_com_permissao_ve_menu_e_pode_usar_get_post_put(self):
        self.usuario.user_permissions.add(self.permissao)
        self.client.force_login(self.usuario)
        url_lista = reverse("administracao:conexoes")
        url_detalhes = reverse(
            "administracao:conexao_detalhes",
            kwargs={"conexao_id": self.conexao.pk},
        )

        configuracoes = self.client.get(
            reverse("administracao:configuracoes")
        )
        self.assertContains(configuracoes, f'href="{url_lista}"')
        self.assertEqual(self.client.get(url_lista).status_code, 200)
        self.assertEqual(self.client.get(url_detalhes).status_code, 200)

        resposta_put = self.client.put(
            url_detalhes,
            urlencode(
                {
                    "nome_conexao": "Conexão atualizada",
                    "url_origem": "https://example.com/",
                    "ip_mercure": "127.0.0.1",
                    "porta_mercure": "3000",
                    "user_sga": "usuario",
                    "pass_sga": "senha",
                    "client_id": "cliente",
                    "client_secret": "segredo",
                }
            ),
            content_type="application/x-www-form-urlencoded",
        )

        self.assertEqual(resposta_put.status_code, 302)
        self.conexao.refresh_from_db()
        self.assertEqual(self.conexao.nome_conexao, "Conexão atualizada")
        self.assertEqual(self.client.delete(url_detalhes).status_code, 405)


class CadastroUsuariosTests(TestCase):
    def setUp(self):
        self.operador = get_user_model().objects.create_user(
            username="operador_usuarios",
            password="senha_teste",
        )
        self.permissao = Permission.objects.get(
            codename="cadastrar_usuarios",
        )
        self.operador.user_permissions.add(
            Permission.objects.get(codename="acesso_usuarios")
        )
        self.grupo = Group.objects.create(name="Perfil teste")
        self.setor = tb_Setores.objects.create(nome_setor="Setor teste")
        self.url_lista = reverse("administracao:gestao_users")
        self.url_cadastro = reverse("administracao:user_cadastro")

    def test_botao_e_backend_ficam_bloqueados_sem_permissao(self):
        self.client.force_login(self.operador)

        resposta_lista = self.client.get(self.url_lista)

        self.assertNotContains(
            resposta_lista,
            f'href="{self.url_cadastro}"',
        )
        self.assertEqual(
            self.client.get(self.url_cadastro).status_code,
            403,
        )

    def test_botao_cadastra_usuario_com_perfil_e_setor(self):
        self.operador.user_permissions.add(self.permissao)
        self.client.force_login(self.operador)

        resposta_lista = self.client.get(self.url_lista)
        self.assertContains(
            resposta_lista,
            f'href="{self.url_cadastro}"',
        )

        resposta = self.client.post(
            self.url_cadastro,
            {
                "username": "novo_usuario",
                "first_name": "Novo",
                "last_name": "Usuário",
                "email": "novo@example.com",
                "groups": [str(self.grupo.pk)],
                "setores": [str(self.setor.pk)],
                "is_active": "on",
                "password1": "SenhaForte123!",
                "password2": "SenhaForte123!",
            },
        )

        novo_usuario = get_user_model().objects.get(
            username="novo_usuario"
        )
        self.assertRedirects(
            resposta,
            self.url_lista,
        )
        self.assertTrue(novo_usuario.check_password("SenhaForte123!"))
        self.assertQuerySetEqual(
            novo_usuario.groups.all(),
            [self.grupo],
        )
        self.assertQuerySetEqual(
            novo_usuario.vinculos_setores.values_list(
                "setor",
                flat=True,
            ),
            [self.setor.pk],
        )


class PermissoesMenuBackendTests(TestCase):
    ROTAS_E_PERMISSOES = (
        (
            "administracao:gestao_paineis",
            ("gerenciar_paineis",),
        ),
        (
            "administracao:gestao_midias",
            ("acesso_mideas", "gerenciar_mideas"),
        ),
        (
            "administracao:configuracao_midias",
            ("acesso_mideas", "gerenciar_mideas"),
        ),
        (
            "administracao:gestao_sons",
            ("acesso_mideas", "gerenciar_sons"),
        ),
        (
            "administracao:gestao_setores",
            ("gerenciar_setores",),
        ),
        (
            "administracao:setor_cadastro",
            ("gerenciar_setores",),
        ),
        (
            "administracao:gestao_users",
            ("acesso_usuarios",),
        ),
    )

    def test_gets_do_menu_retornam_403_sem_as_permissoes(self):
        usuario = get_user_model().objects.create_user(
            username="sem_permissoes",
            password="senha_teste",
        )
        self.client.force_login(usuario)

        for nome_rota, _ in self.ROTAS_E_PERMISSOES:
            with self.subTest(rota=nome_rota):
                resposta = self.client.get(reverse(nome_rota))
                self.assertEqual(resposta.status_code, 403)

    def test_gets_do_menu_abrem_com_as_mesmas_permissoes(self):
        for indice, (nome_rota, codenames) in enumerate(
            self.ROTAS_E_PERMISSOES
        ):
            with self.subTest(rota=nome_rota):
                usuario = get_user_model().objects.create_user(
                    username=f"usuario_permitido_{indice}",
                    password="senha_teste",
                )
                usuario.user_permissions.add(
                    *Permission.objects.filter(codename__in=codenames)
                )
                self.client.force_login(usuario)

                resposta = self.client.get(reverse(nome_rota))

                self.assertEqual(resposta.status_code, 200)
                self.client.logout()


class CadastroSetoresTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username="gestor_setores",
            password="senha_teste",
        )
        self.usuario.user_permissions.add(
            Permission.objects.get(codename="gerenciar_setores")
        )
        self.client.force_login(self.usuario)
        self.url = reverse("administracao:setor_cadastro")

    def test_listagem_exibe_botao_de_cadastro(self):
        resposta = self.client.get(
            reverse("administracao:gestao_setores")
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, f'href="{self.url}"')

    def test_cadastro_cria_setor_e_abre_sua_ficha(self):
        resposta = self.client.post(
            self.url,
            {
                "nome_setor": "Atendimento",
                "status": "Ativo",
            },
        )

        setor = tb_Setores.objects.get(nome_setor="Atendimento")
        self.assertRedirects(
            resposta,
            reverse(
                "administracao:setor_detalhes",
                kwargs={"setor_id": setor.pk},
            ),
        )


class ConfiguracaoMidiasPorSetorTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username="configurador_midias",
            password="senha_teste",
        )
        self.setor_usuario = tb_Setores.objects.create(
            nome_setor="Setor próprio"
        )
        self.outro_setor = tb_Setores.objects.create(
            nome_setor="Outro setor"
        )
        UsuarioSetor.objects.create(
            usuario=self.usuario,
            setor=self.setor_usuario,
        )
        self.usuario.user_permissions.add(
            *Permission.objects.filter(
                codename__in=("acesso_mideas", "gerenciar_mideas")
            )
        )
        self.configuracao_usuario = ConfigPainel.objects.create(
            setor=self.setor_usuario,
            tempo_exibicao_imagem=8,
            tempo_popup=10,
        )
        self.configuracao_outro_setor = ConfigPainel.objects.create(
            setor=self.outro_setor,
            tempo_exibicao_imagem=15,
            tempo_popup=20,
        )
        self.url = reverse("administracao:configuracao_midias")
        self.client.force_login(self.usuario)

    def test_usuario_comum_lista_e_edita_apenas_o_proprio_setor(self):
        resposta_get = self.client.get(self.url)

        self.assertContains(resposta_get, "Setor próprio")
        self.assertNotContains(resposta_get, "Outro setor")

        resposta_post = self.client.post(
            self.url,
            {
                "form-TOTAL_FORMS": "1",
                "form-INITIAL_FORMS": "1",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
                "form-0-id": str(self.configuracao_usuario.pk),
                "form-0-tempo_exibicao_imagem": "20",
                "form-0-tempo_popup": "30",
            },
        )

        self.assertRedirects(resposta_post, self.url)
        self.configuracao_usuario.refresh_from_db()
        self.configuracao_outro_setor.refresh_from_db()
        self.assertEqual(
            self.configuracao_usuario.tempo_exibicao_imagem,
            20,
        )
        self.assertEqual(self.configuracao_usuario.tempo_popup, 30)
        self.assertEqual(
            self.configuracao_outro_setor.tempo_exibicao_imagem,
            15,
        )

    def test_admin_lista_configuracoes_de_todos_os_setores(self):
        self.usuario.groups.add(Group.objects.get(name="Admin"))

        resposta = self.client.get(self.url)

        self.assertContains(resposta, "Setor próprio")
        self.assertContains(resposta, "Outro setor")

    def test_post_nao_edita_configuracao_de_outro_setor(self):
        resposta = self.client.post(
            self.url,
            {
                "form-TOTAL_FORMS": "1",
                "form-INITIAL_FORMS": "1",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
                "form-0-id": str(self.configuracao_outro_setor.pk),
                "form-0-tempo_exibicao_imagem": "60",
                "form-0-tempo_popup": "60",
            },
        )

        self.assertEqual(resposta.status_code, 200)
        self.configuracao_outro_setor.refresh_from_db()
        self.assertEqual(
            self.configuracao_outro_setor.tempo_exibicao_imagem,
            15,
        )
        self.assertEqual(
            self.configuracao_outro_setor.tempo_popup,
            20,
        )
