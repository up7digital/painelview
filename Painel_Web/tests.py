from django.test import TestCase
from django.urls import reverse

from Administracao.models import (
    ConfigPainel,
    MidiaPainel,
    tb_Conexoes,
    tb_Painel,
    tb_Setores,
)


class AtualizacaoPeriodicaMidiasTests(TestCase):
    def setUp(self):
        self.setor = tb_Setores.objects.create(nome_setor="Recepção")
        self.conexao = tb_Conexoes.objects.create(
            nome_conexao="Novo SGA",
            url_origem="https://sga.example.com",
            ip_mercure="127.0.0.1",
            porta_mercure=3000,
            user_sga="usuario",
            pass_sga="senha",
            client_id="cliente",
            client_secret="segredo",
        )
        self.painel = tb_Painel.objects.create(
            nome="Painel principal",
            setor=self.setor,
            conexao=self.conexao,
            unidade_sga=1,
            servicos_sga=[],
        )
        self.config = ConfigPainel.objects.create(
            setor=self.setor,
            tempo_exibicao_imagem=8,
            tempo_popup=10,
        )
        self.midia = MidiaPainel.objects.create(
            tipo="Texto",
            texto="AVISO INICIAL",
            texto_tamanho_fonte=48,
            texto_cor="#ffffff",
            texto_alinhamento="center",
            exibir_lateral=0,
            exibir_popup=0,
        )
        self.midia.setores.add(self.setor)
        self.url = reverse("painel_midias")

    def test_endpoint_entrega_fragmentos_e_tempos_do_setor(self):
        resposta = self.client.get(
            self.url,
            {"painel": self.painel.pk},
        )

        self.assertEqual(resposta.status_code, 200)
        dados = resposta.json()
        self.assertTrue(dados["alterado"])
        self.assertIn("AVISO INICIAL", dados["lateral_html"])
        self.assertIn("AVISO INICIAL", dados["popup_html"])
        self.assertIn("--tamanho-texto-midia: 48px", dados["lateral_html"])
        self.assertEqual(dados["tempo_imagem_ms"], 8000)
        self.assertEqual(dados["tempo_popup_ms"], 10000)

    def test_revisao_evitaria_download_quando_nada_mudou(self):
        primeira = self.client.get(
            self.url,
            {"painel": self.painel.pk},
        ).json()
        segunda = self.client.get(
            self.url,
            {
                "painel": self.painel.pk,
                "revisao": primeira["revisao"],
            },
        ).json()

        self.assertFalse(segunda["alterado"])
        self.assertNotIn("lateral_html", segunda)

    def test_alteracao_da_midia_gera_nova_revisao(self):
        primeira = self.client.get(
            self.url,
            {"painel": self.painel.pk},
        ).json()
        self.midia.texto = "AVISO ATUALIZADO"
        self.midia.save(update_fields=["texto"])

        segunda = self.client.get(
            self.url,
            {
                "painel": self.painel.pk,
                "revisao": primeira["revisao"],
            },
        ).json()

        self.assertTrue(segunda["alterado"])
        self.assertNotEqual(segunda["revisao"], primeira["revisao"])
        self.assertIn("AVISO ATUALIZADO", segunda["lateral_html"])

    def test_exclusao_remove_midia_dos_fragmentos(self):
        primeira = self.client.get(
            self.url,
            {"painel": self.painel.pk},
        ).json()
        self.midia.delete()

        segunda = self.client.get(
            self.url,
            {
                "painel": self.painel.pk,
                "revisao": primeira["revisao"],
            },
        ).json()

        self.assertTrue(segunda["alterado"])
        self.assertNotIn("AVISO INICIAL", segunda["lateral_html"])
