"""
========================================================================================
SISTEMA DE CAIXA ELETRÔNICO FULL STACK COM CUSTOMTKINTER
Inicia sempre LIMPO (sem dados pré-cadastrados).
O cliente preenche seus dados na tela de abertura e, após a validação,
os dados são mantidos durante a sessão. Toda nova abertura inicia do zero.

Interface 100% fiel ao design de referência (Menu Principal, Depositar, 
Comprovante de Depósito, Sacar, Comprovante de Saque, Extrato, Modais de Aviso/Erro/Cancelado).
========================================================================================
"""

import os
import sys
import re
from datetime import datetime
from PIL import Image, ImageDraw
import customtkinter as ctk

# ======================================================================================
# 1. CONFIGURAÇÕES VISUAIS E TEMA
# ======================================================================================
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

COLORS = {
    "sidebar_bg": "#002244",           # Navy escuro corporativo do sidebar
    "sidebar_btn_active": "#136dec",    # Azul vibrante do item ativo
    "sidebar_btn_hover": "#0c2c57",     # Hover sutil
    "sidebar_text": "#c2d1e0",          # Texto inativo
    "sidebar_subtext": "#728aa8",       # Subtítulo "Seu dinheiro, nosso compromisso!"
    
    "content_bg": "#f4f6fa",            # Fundo cinza-azulado muito suave
    "card_bg": "#ffffff",               # Fundo branco
    "card_border": "#e2e8f0",           # Borda suave
    
    "text_dark": "#1b2a4a",             # Títulos
    "text_muted": "#64748b",            # Legendas
    
    "primary_blue": "#1a73e8",          # Azul de ação primária
    "primary_blue_hover": "#1557b0",    # Hover azul
    "balance_gradient": "#1976d2",      # Card azul de saldo
    
    "badge_green_bg": "#e6f4ea",        # Fundo verde claro
    "badge_green_text": "#137333",      # Texto verde escuro
    "banner_green": "#1e8e3e",          # Banner verde de depósito
    
    "badge_red_bg": "#fce8e6",          # Fundo vermelho suave
    "badge_red_text": "#c5221f",        # Texto vermelho de saque
    "banner_red": "#ea4335",            # Banner vermelho de saque
    
    "info_blue_bg": "#e8f0fe",          # Box informativo azul
    "info_blue_border": "#c2d7f8",      # Borda informativa
    "info_blue_text": "#1967d2"         # Texto informativo
}

# ======================================================================================
# 2. GERADOR DE ÍCONES DE ALTA DEFINIÇÃO (PIL + Anti-aliasing LANCZOS)
# ======================================================================================
def _create_canvas(size=32, scale=3):
    w, h = size * scale, size * scale
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    return img, draw, w, h

def _finish(img, size):
    res = img.resize((size, size), Image.Resampling.LANCZOS)
    return ctk.CTkImage(light_image=res, dark_image=res, size=(size, size))

def icon_bank(size=44, color="#ffffff"):
    img, d, w, h = _create_canvas(size, 3)
    d.polygon([(w // 2, int(h * 0.10)), (int(w * 0.12), int(h * 0.38)), (int(w * 0.88), int(h * 0.38))], fill=color)
    d.rectangle([int(w * 0.10), int(h * 0.38), int(w * 0.90), int(h * 0.44)], fill=color)
    cols = 4
    col_w = int(w * 0.08)
    margin = int(w * 0.16)
    step = (w - 2 * margin - col_w) / (cols - 1)
    for i in range(cols):
        cx = int(margin + i * step)
        d.rectangle([cx, int(h * 0.46), cx + col_w, int(h * 0.78)], fill=color)
    d.rectangle([int(w * 0.10), int(h * 0.80), int(w * 0.90), int(h * 0.86)], fill=color)
    d.rectangle([int(w * 0.06), int(h * 0.87), int(w * 0.94), int(h * 0.94)], fill=color)
    return _finish(img, size)

def icon_home(size=20, color="#ffffff"):
    img, d, w, h = _create_canvas(size, 3)
    d.polygon([(w // 2, int(h * 0.15)), (int(w * 0.15), int(h * 0.48)), (int(w * 0.85), int(h * 0.48))], fill=color)
    d.rectangle([int(w * 0.22), int(h * 0.48), int(w * 0.78), int(h * 0.88)], fill=color)
    d.rectangle([int(w * 0.40), int(h * 0.62), int(w * 0.60), int(h * 0.88)], fill="#002244" if color == "#ffffff" else "#ffffff")
    return _finish(img, size)

def icon_eye(size=20, color="#ffffff"):
    img, d, w, h = _create_canvas(size, 3)
    d.ellipse([int(w * 0.10), int(h * 0.22), int(w * 0.90), int(h * 0.78)], outline=color, width=max(2, int(w * 0.08)))
    d.ellipse([int(w * 0.38), int(h * 0.38), int(w * 0.62), int(h * 0.62)], fill=color)
    return _finish(img, size)

def icon_statement(size=20, color="#ffffff"):
    img, d, w, h = _create_canvas(size, 3)
    d.rounded_rectangle([int(w * 0.18), int(h * 0.12), int(w * 0.82), int(h * 0.88)], radius=int(w * 0.08), outline=color, width=max(2, int(w * 0.06)))
    lw = max(2, int(w * 0.05))
    d.line([(int(w * 0.28), int(h * 0.32)), (int(w * 0.72), int(h * 0.32))], fill=color, width=lw)
    d.line([(int(w * 0.28), int(h * 0.48)), (int(w * 0.72), int(h * 0.48))], fill=color, width=lw)
    d.line([(int(w * 0.28), int(h * 0.64)), (int(w * 0.58), int(h * 0.64))], fill=color, width=lw)
    return _finish(img, size)

def icon_deposit_nav(size=20, color="#ffffff"):
    img, d, w, h = _create_canvas(size, 3)
    lw = max(2, int(w * 0.07))
    d.line([(int(w * 0.16), int(h * 0.60)), (int(w * 0.16), int(h * 0.84)), (int(w * 0.84), int(h * 0.84)), (int(w * 0.84), int(h * 0.60))], fill=color, width=lw)
    d.line([(w // 2, int(h * 0.16)), (w // 2, int(h * 0.64))], fill=color, width=lw)
    d.line([(int(w * 0.32), int(h * 0.46)), (w // 2, int(h * 0.64)), (int(w * 0.68), int(h * 0.46))], fill=color, width=lw)
    return _finish(img, size)

def icon_withdraw_nav(size=20, color="#ffffff"):
    img, d, w, h = _create_canvas(size, 3)
    lw = max(2, int(w * 0.07))
    d.line([(int(w * 0.16), int(h * 0.64)), (int(w * 0.16), int(h * 0.84)), (int(w * 0.84), int(h * 0.84)), (int(w * 0.84), int(h * 0.64))], fill=color, width=lw)
    d.line([(w // 2, int(h * 0.64)), (w // 2, int(h * 0.16))], fill=color, width=lw)
    d.line([(int(w * 0.32), int(h * 0.34)), (w // 2, int(h * 0.16)), (int(w * 0.68), int(h * 0.34))], fill=color, width=lw)
    return _finish(img, size)

def icon_logout(size=20, color="#ffffff"):
    img, d, w, h = _create_canvas(size, 3)
    lw = max(2, int(w * 0.07))
    d.line([(int(w * 0.38), int(h * 0.18)), (int(w * 0.16), int(h * 0.18)), (int(w * 0.16), int(h * 0.84)), (int(w * 0.38), int(h * 0.84))], fill=color, width=lw)
    d.line([(int(w * 0.28), h // 2), (int(w * 0.84), h // 2)], fill=color, width=lw)
    d.line([(int(w * 0.64), int(h * 0.32)), (int(w * 0.84), h // 2), (int(w * 0.64), int(h * 0.68))], fill=color, width=lw)
    return _finish(img, size)

def icon_shield(size=18, color="#5a82ad"):
    img, d, w, h = _create_canvas(size, 3)
    d.polygon([
        (w // 2, int(h * 0.10)),
        (int(w * 0.86), int(h * 0.22)),
        (int(w * 0.82), int(h * 0.60)),
        (w // 2, int(h * 0.90)),
        (int(w * 0.18), int(h * 0.60)),
        (int(w * 0.14), int(h * 0.22))
    ], outline=color, width=max(2, int(w * 0.08)))
    return _finish(img, size)

def icon_avatar(size=44):
    img, d, w, h = _create_canvas(size, 3)
    d.ellipse([int(w * 0.04), int(h * 0.04), int(w * 0.96), int(h * 0.96)], fill="#0f2b4c")
    d.ellipse([int(w * 0.32), int(h * 0.16), int(w * 0.68), int(h * 0.48)], fill="#ffffff")
    d.chord([int(w * 0.16), int(h * 0.44), int(w * 0.84), int(h * 0.98)], start=0, end=180, fill="#ffffff")
    return _finish(img, size)

def icon_calendar(size=18, color="#6b7280"):
    img, d, w, h = _create_canvas(size, 3)
    lw = max(2, int(w * 0.07))
    d.rounded_rectangle([int(w * 0.12), int(h * 0.18), int(w * 0.88), int(h * 0.88)], radius=int(w * 0.08), outline=color, width=lw)
    d.line([(int(w * 0.12), int(h * 0.38)), (int(w * 0.88), int(h * 0.38))], fill=color, width=lw)
    d.line([(int(w * 0.30), int(h * 0.08)), (int(w * 0.30), int(h * 0.22))], fill=color, width=lw)
    d.line([(int(w * 0.70), int(h * 0.08)), (int(w * 0.70), int(h * 0.22))], fill=color, width=lw)
    return _finish(img, size)

def icon_wallet(size=36, color="#ffffff"):
    img, d, w, h = _create_canvas(size, 3)
    d.rounded_rectangle([int(w * 0.12), int(h * 0.18), int(w * 0.88), int(h * 0.82)], radius=int(w * 0.10), fill=color)
    d.rounded_rectangle([int(w * 0.64), int(h * 0.34), int(w * 0.96), int(h * 0.66)], radius=int(w * 0.08), fill="#1976d2")
    d.ellipse([int(w * 0.72), int(h * 0.44), int(w * 0.84), int(h * 0.56)], fill="#ffffff")
    return _finish(img, size)

def icon_action_deposit(size=44):
    img, d, w, h = _create_canvas(size, 3)
    d.rounded_rectangle([int(w * 0.04), int(h * 0.04), int(w * 0.96), int(h * 0.96)], radius=int(w * 0.18), fill="#e8f5e9")
    lw = max(3, int(w * 0.08))
    d.line([(int(w * 0.22), int(h * 0.66)), (int(w * 0.22), int(h * 0.82)), (int(w * 0.78), int(h * 0.82)), (int(w * 0.78), int(h * 0.66))], fill="#2e7d32", width=lw)
    d.line([(w // 2, int(h * 0.20)), (w // 2, int(h * 0.68))], fill="#2e7d32", width=lw)
    d.line([(int(w * 0.32), int(h * 0.50)), (w // 2, int(h * 0.68)), (int(w * 0.68), int(h * 0.50))], fill="#2e7d32", width=lw)
    return _finish(img, size)

def icon_action_withdraw(size=44):
    img, d, w, h = _create_canvas(size, 3)
    d.rounded_rectangle([int(w * 0.04), int(h * 0.04), int(w * 0.96), int(h * 0.96)], radius=int(w * 0.18), fill="#e3f2fd")
    d.ellipse([int(w * 0.14), int(h * 0.14), int(w * 0.86), int(h * 0.86)], fill="#1976d2")
    lw = max(3, int(w * 0.07))
    d.line([(w // 2, int(h * 0.72)), (w // 2, int(h * 0.28))], fill="#ffffff", width=lw)
    d.line([(int(w * 0.34), int(h * 0.44)), (w // 2, int(h * 0.28)), (int(w * 0.66), int(h * 0.44))], fill="#ffffff", width=lw)
    return _finish(img, size)

def icon_action_statement(size=44):
    img, d, w, h = _create_canvas(size, 3)
    d.rounded_rectangle([int(w * 0.04), int(h * 0.04), int(w * 0.96), int(h * 0.96)], radius=int(w * 0.18), fill="#f3e5f5")
    d.rounded_rectangle([int(w * 0.20), int(h * 0.18), int(w * 0.80), int(h * 0.82)], radius=int(w * 0.10), fill="#7b1fa2")
    lw = max(2, int(w * 0.06))
    d.line([(int(w * 0.32), int(h * 0.36)), (int(w * 0.68), int(h * 0.36))], fill="#ffffff", width=lw)
    d.line([(int(w * 0.32), int(h * 0.50)), (int(w * 0.68), int(h * 0.50))], fill="#ffffff", width=lw)
    d.line([(int(w * 0.32), int(h * 0.64)), (int(w * 0.54), int(h * 0.64))], fill="#ffffff", width=lw)
    return _finish(img, size)

def icon_action_logout(size=44):
    img, d, w, h = _create_canvas(size, 3)
    d.rounded_rectangle([int(w * 0.04), int(h * 0.04), int(w * 0.96), int(h * 0.96)], radius=int(w * 0.18), fill="#f1f5f9")
    lw = max(3, int(w * 0.08))
    d.line([(int(w * 0.24), h // 2), (int(w * 0.76), h // 2)], fill="#64748b", width=lw)
    d.line([(int(w * 0.56), int(h * 0.32)), (int(w * 0.76), h // 2), (int(w * 0.56), int(h * 0.68))], fill="#64748b", width=lw)
    return _finish(img, size)

def icon_modal_warn(size=64):
    img, d, w, h = _create_canvas(size, 3)
    d.ellipse([int(w * 0.06), int(h * 0.06), int(w * 0.94), int(h * 0.94)], fill="#f59e0b")
    lw = max(4, int(w * 0.09))
    d.line([(w // 2, int(h * 0.24)), (w // 2, int(h * 0.58))], fill="#ffffff", width=lw)
    pr = int(w * 0.055)
    d.ellipse([(w // 2) - pr, int(h * 0.70) - pr, (w // 2) + pr, int(h * 0.70) + pr], fill="#ffffff")
    return _finish(img, size)

def icon_modal_error(size=64):
    img, d, w, h = _create_canvas(size, 3)
    d.ellipse([int(w * 0.06), int(h * 0.06), int(w * 0.94), int(h * 0.94)], fill="#ef4444")
    lw = max(4, int(w * 0.09))
    d.line([(int(w * 0.28), int(h * 0.28)), (int(w * 0.72), int(h * 0.72))], fill="#ffffff", width=lw)
    d.line([(int(w * 0.72), int(h * 0.28)), (int(w * 0.28), int(h * 0.72))], fill="#ffffff", width=lw)
    return _finish(img, size)

def icon_modal_info(size=64):
    img, d, w, h = _create_canvas(size, 3)
    d.ellipse([int(w * 0.06), int(h * 0.06), int(w * 0.94), int(h * 0.94)], fill="#3b82f6")
    pr = int(w * 0.055)
    d.ellipse([(w // 2) - pr, int(h * 0.28) - pr, (w // 2) + pr, int(h * 0.28) + pr], fill="#ffffff")
    lw = max(4, int(w * 0.09))
    d.line([(w // 2, int(h * 0.42)), (w // 2, int(h * 0.74))], fill="#ffffff", width=lw)
    return _finish(img, size)

def icon_success_check(size=44):
    img, d, w, h = _create_canvas(size, 3)
    d.ellipse([int(w * 0.06), int(h * 0.06), int(w * 0.94), int(h * 0.94)], fill="#ffffff")
    lw = max(3, int(w * 0.09))
    d.line([(int(w * 0.26), int(h * 0.52)), (int(w * 0.44), int(h * 0.70)), (int(w * 0.76), int(h * 0.32))], fill="#1e8e3e", width=lw)
    return _finish(img, size)

def icon_saque_check(size=44):
    img, d, w, h = _create_canvas(size, 3)
    d.ellipse([int(w * 0.06), int(h * 0.06), int(w * 0.94), int(h * 0.94)], fill="#ffffff")
    lw = max(3, int(w * 0.09))
    d.line([(w // 2, int(h * 0.72)), (w // 2, int(h * 0.28))], fill="#ea4335", width=lw)
    d.line([(int(w * 0.32), int(h * 0.44)), (w // 2, int(h * 0.28)), (int(w * 0.68), int(h * 0.44))], fill="#ea4335", width=lw)
    return _finish(img, size)

def icon_mini_check(size=18):
    img, d, w, h = _create_canvas(size, 3)
    d.ellipse([int(w * 0.06), int(h * 0.06), int(w * 0.94), int(h * 0.94)], fill="#1e8e3e")
    lw = max(2, int(w * 0.10))
    d.line([(int(w * 0.26), int(h * 0.52)), (int(w * 0.44), int(h * 0.70)), (int(w * 0.76), int(h * 0.32))], fill="#ffffff", width=lw)
    return _finish(img, size)

def icon_mini_info(size=18):
    img, d, w, h = _create_canvas(size, 3)
    d.ellipse([int(w * 0.06), int(h * 0.06), int(w * 0.94), int(h * 0.94)], fill="#1a73e8")
    pr = int(w * 0.07)
    d.ellipse([(w // 2) - pr, int(h * 0.26) - pr, (w // 2) + pr, int(h * 0.26) + pr], fill="#ffffff")
    lw = max(2, int(w * 0.10))
    d.line([(w // 2, int(h * 0.42)), (w // 2, int(h * 0.74))], fill="#ffffff", width=lw)
    return _finish(img, size)

def icon_badge_deposit(size=18):
    img, d, w, h = _create_canvas(size, 3)
    d.ellipse([int(w * 0.06), int(h * 0.06), int(w * 0.94), int(h * 0.94)], fill="#e6f4ea")
    lw = max(2, int(w * 0.10))
    d.line([(w // 2, int(h * 0.24)), (w // 2, int(h * 0.72))], fill="#137333", width=lw)
    d.line([(int(w * 0.30), int(h * 0.52)), (w // 2, int(h * 0.72)), (int(w * 0.70), int(h * 0.52))], fill="#137333", width=lw)
    return _finish(img, size)

def icon_badge_withdraw(size=18):
    img, d, w, h = _create_canvas(size, 3)
    d.ellipse([int(w * 0.06), int(h * 0.06), int(w * 0.94), int(h * 0.94)], fill="#fce8e6")
    lw = max(2, int(w * 0.10))
    d.line([(w // 2, int(h * 0.72)), (w // 2, int(h * 0.24))], fill="#c5221f", width=lw)
    d.line([(int(w * 0.30), int(h * 0.44)), (w // 2, int(h * 0.24)), (int(w * 0.70), int(h * 0.44))], fill="#c5221f", width=lw)
    return _finish(img, size)

# ======================================================================================
# 3. SEGURANÇA, VALIDAÇÃO E REGRAS DE NEGÓCIO
# ======================================================================================
class SecurityValidator:
    @staticmethod
    def validar_valor(valor_str: str):
        if not valor_str or not isinstance(valor_str, str):
            return False, 0.0, "Valor não informado."

        limpo = valor_str.strip()
        if limpo.upper().startswith("R$"):
            limpo = limpo[2:].strip()

        if "." in limpo and "," in limpo:
            limpo = limpo.replace(".", "").replace(",", ".")
        else:
            limpo = limpo.replace(",", ".")

        match = re.match(r"^\d+(\.\d{1,2})?$", limpo)
        if not match:
            return False, 0.0, "Digite apenas números válidos para o valor da transação."

        try:
            val = float(limpo)
        except ValueError:
            return False, 0.0, "Digite apenas números válidos para o valor da transação."

        if val <= 0:
            return False, 0.0, "O valor deve ser maior que zero."

        if val > 100000.0:
            return False, 0.0, "Valor excede o limite máximo permitido por operação (R$ 100.000,00)."

        return True, round(val, 2), ""

    @staticmethod
    def validar_saldo_inicial(valor_str: str):
        if not valor_str or not valor_str.strip():
            return True, 0.0, ""
        limpo = valor_str.strip()
        if limpo.upper().startswith("R$"):
            limpo = limpo[2:].strip()
        if "." in limpo and "," in limpo:
            limpo = limpo.replace(".", "").replace(",", ".")
        else:
            limpo = limpo.replace(",", ".")
        match = re.match(r"^\d+(\.\d{1,2})?$", limpo)
        if not match:
            return False, 0.0, "Digite um valor numérico válido para o saldo inicial."
        try:
            val = float(limpo)
            return True, round(val, 2), ""
        except ValueError:
            return False, 0.0, "Valor de saldo inicial inválido."


class CaixaEletronicoCore:
    def __init__(self):
        # Inicia sempre LIMPO (sem dados pré-cadastrados)
        self.usuario_principal = {
            'titular': '',
            'agencia': '',
            'conta': '',
            'tipo_conta': 'Conta Corrente'
        }
        self.saldo = 0.0
        self.historico = []
        self.logado = False

    def cadastrar_titular(self, titular, agencia, conta, tipo_conta, saldo_inicial=0.0):
        self.usuario_principal['titular'] = titular.strip().capitalize()
        self.usuario_principal['agencia'] = agencia.strip()
        self.usuario_principal['conta'] = conta.strip()
        self.usuario_principal['tipo_conta'] = tipo_conta.strip()
        self.saldo = float(saldo_inicial)
        self.historico = []
        self.logado = True

    def atualizar_dados_titular(self, titular, agencia, conta, tipo_conta):
        self.usuario_principal['titular'] = titular.strip().capitalize()
        self.usuario_principal['agencia'] = agencia.strip()
        self.usuario_principal['conta'] = conta.strip()
        self.usuario_principal['tipo_conta'] = tipo_conta.strip()

    def resetar_sessao(self):
        """Limpa todos os dados da sessão para um novo atendimento."""
        self.usuario_principal = {
            'titular': '',
            'agencia': '',
            'conta': '',
            'tipo_conta': 'Conta Corrente'
        }
        self.saldo = 0.0
        self.historico = []
        self.logado = False

    def depositar(self, valor: float, destinatario: dict = None):
        if destinatario is None:
            destinatario = {
                'titular': self.usuario_principal['titular'],
                'agencia': self.usuario_principal['agencia'],
                'conta': self.usuario_principal['conta'],
                'tipo_conta': self.usuario_principal['tipo_conta'],
                'propria_conta': True
            }

        saldo_anterior = self.saldo
        self.saldo += valor

        momento = datetime.now()
        operacao = {
            'tipo': 'Deposito',
            'valor': valor,
            'data': momento.date(),
            'hora': momento.time(),
            'saldo_anterior': saldo_anterior,
            'saldo_atual': self.saldo,
            'destinatario': destinatario
        }
        self.historico.append(operacao)
        return operacao

    def sacar(self, valor: float):
        if valor > self.saldo:
            return False, "Saldo Insuficiente!"

        saldo_anterior = self.saldo
        self.saldo -= valor

        momento = datetime.now()
        operacao = {
            'tipo': 'Saque',
            'valor': valor,
            'data': momento.date(),
            'hora': momento.time(),
            'saldo_anterior': saldo_anterior,
            'saldo_atual': self.saldo,
            'destinatario': None
        }
        self.historico.append(operacao)
        return True, operacao

    def gerar_recibo_texto(self, op: dict) -> str:
        linhas = [
            "=" * 45,
            f"{'BANCO DIGITAL - CAIXA ELETRÔNICO':^45}",
            f"{'COMPROVANTE DE ' + op['tipo'].upper():^45}",
            "=" * 45,
            f"TITULAR   : {self.usuario_principal['titular']}",
            f"AGÊNCIA   : {self.usuario_principal['agencia']} | CONTA: {self.usuario_principal['conta']} ({self.usuario_principal['tipo_conta']})",
        ]
        if op.get('destinatario') and not op['destinatario'].get('propria_conta', True):
            d = op['destinatario']
            linhas.append(f"DESTINO   : {d['titular']} (Ag: {d['agencia']} Ct: {d['conta']})")

        linhas.extend([
            f"DATA/HORA : {op['data'].strftime('%d/%m/%Y')} às {op['hora'].strftime('%H:%M:%S')}",
            "-" * 45,
            f"Saldo anterior  : R$ {op['saldo_anterior']:.2f}",
            f"Valor {'depositado' if op['tipo'] == 'Deposito' else 'sacado'}: R$ {op['valor']:.2f}",
            f"Saldo {'atual' if op['tipo'] == 'Deposito' else 'restante'}: R$ {op['saldo_atual']:.2f}",
            "=" * 45,
            "Transação concluída com sucesso!",
            f"Autenticação: {datetime.now().strftime('%Y%m%d%H%M%S')}-SEC-OK",
            "=" * 45
        ])
        return "\n".join(linhas)

    def gerar_extrato_texto(self) -> str:
        linhas = [
            "=" * 65,
            f"{'EXTRATO BANCÁRIO OFICIAL':^65}",
            "=" * 65,
            f"TITULAR DA CONTA : {self.usuario_principal['titular']}",
            f"AGÊNCIA          : {self.usuario_principal['agencia']} | CONTA: {self.usuario_principal['conta']} ({self.usuario_principal['tipo_conta']})",
            f"EMISSÃO          : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            "-" * 65,
            f"{'DATA/HORA':<18} | {'TIPO':<10} | {'VALOR':<14} | {'SALDO'}",
            "-" * 65
        ]
        total_dep = 0.0
        total_saq = 0.0
        for op in self.historico:
            dh = f"{op['data'].strftime('%d/%m/%Y')} {op['hora'].strftime('%H:%M')}"
            tipo = op['tipo']
            if tipo == 'Deposito':
                total_dep += op['valor']
                val_s = f"+ R$ {op['valor']:.2f}"
            else:
                total_saq += op['valor']
                val_s = f"- R$ {op['valor']:.2f}"
            linhas.append(f"{dh:<18} | {tipo:<10} | {val_s:<14} | R$ {op['saldo_atual']:.2f}")

        linhas.extend([
            "-" * 65,
            f"Total depositado : R$ {total_dep:.2f}",
            f"Total sacado     : R$ {total_saq:.2f}",
            f"Saldo em conta   : R$ {self.saldo:.2f}",
            "=" * 65
        ])
        return "\n".join(linhas)

# ======================================================================================
# 4. MODAIS CUSTOMIZADOS (Linha 3 da imagem)
# ======================================================================================
class ModalCustomizado(ctk.CTkToplevel):
    def __init__(self, parent, tipo="erro", titulo_janela="Caixa Eletrônico", titulo="Aviso", mensagem="", on_close=None):
        super().__init__(parent)
        self.title(titulo_janela)
        self.geometry("450x300")
        self.resizable(False, False)
        self.configure(fg_color="#f8fafc")
        self.on_close_callback = on_close

        self.transient(parent)
        self.grab_set()

        parent.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width() // 2) - 225
        py = parent.winfo_y() + (parent.winfo_height() // 2) - 150
        self.geometry(f"+{max(0, px)}+{max(0, py)}")

        card = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#e2e8f0")
        card.pack(fill="both", expand=True, padx=20, pady=20)

        if tipo == "aviso":
            ico = icon_modal_warn(56)
        elif tipo == "cancelado":
            ico = icon_modal_info(56)
        else:
            ico = icon_modal_error(56)

        ctk.CTkLabel(card, image=ico, text="").pack(pady=(25, 10))
        ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"), text_color="#1e293b").pack(pady=(0, 6))
        ctk.CTkLabel(card, text=mensagem, font=ctk.CTkFont(family="Segoe UI", size=13), text_color="#64748b", wraplength=360, justify="center").pack(pady=(0, 20), padx=20)

        ctk.CTkButton(
            card,
            text="✔  OK",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color=COLORS["primary_blue"],
            hover_color=COLORS["primary_blue_hover"],
            corner_radius=8,
            height=40,
            width=220,
            command=self._fechar
        ).pack(pady=(0, 20))

    def _fechar(self):
        self.grab_release()
        self.destroy()
        if self.on_close_callback:
            self.on_close_callback()


class ModalCadastroTitular(ctk.CTkToplevel):
    def __init__(self, parent, usuario_atual, on_save):
        super().__init__(parent)
        self.title("Caixa Eletrônico - Cadastro do Titular")
        self.geometry("480x560")
        self.resizable(False, False)
        self.configure(fg_color="#f8fafc")
        self.on_save = on_save

        self.transient(parent)
        self.grab_set()

        parent.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width() // 2) - 240
        py = parent.winfo_y() + (parent.winfo_height() // 2) - 280
        self.geometry(f"+{max(0, px)}+{max(0, py)}")

        card = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#e2e8f0")
        card.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(card, image=icon_bank(36, "#002244"), text="").pack(pady=(15, 5))
        ctk.CTkLabel(card, text="Dados do Titular da Conta", font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"), text_color="#1e293b").pack(pady=(0, 15))

        # Titular
        ctk.CTkLabel(card, text="Nome do Titular:", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#334155").pack(anchor="w", padx=30, pady=(4, 2))
        self.entry_titular = ctk.CTkEntry(card, height=36, corner_radius=8, border_color="#cbd5e1", placeholder_text="Digite o nome completo")
        self.entry_titular.insert(0, usuario_atual['titular'])
        self.entry_titular.pack(fill="x", padx=30, pady=(0, 8))

        # Agência
        ctk.CTkLabel(card, text="Agência (ex: 0001 ou 1234-5):", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#334155").pack(anchor="w", padx=30, pady=(4, 2))
        self.entry_agencia = ctk.CTkEntry(card, height=36, corner_radius=8, border_color="#cbd5e1", placeholder_text="0001")
        self.entry_agencia.insert(0, usuario_atual['agencia'])
        self.entry_agencia.pack(fill="x", padx=30, pady=(0, 8))

        # Conta
        ctk.CTkLabel(card, text="Conta com dígito (ex: 12345-6):", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#334155").pack(anchor="w", padx=30, pady=(4, 2))
        self.entry_conta = ctk.CTkEntry(card, height=36, corner_radius=8, border_color="#cbd5e1", placeholder_text="12345-6")
        self.entry_conta.insert(0, usuario_atual['conta'])
        self.entry_conta.pack(fill="x", padx=30, pady=(0, 8))

        # Tipo Conta
        ctk.CTkLabel(card, text="Tipo de Conta:", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color="#334155").pack(anchor="w", padx=30, pady=(4, 2))
        tipo_atual = usuario_atual.get('tipo_conta', 'Conta Corrente')
        self.combo_tipo = ctk.CTkSegmentedButton(card, values=["Conta Corrente", "Poupança"], selected_color=COLORS["primary_blue"], selected_hover_color=COLORS["primary_blue_hover"], corner_radius=8, height=34)
        self.combo_tipo.set(tipo_atual if tipo_atual in ["Conta Corrente", "Poupança"] else "Conta Corrente")
        self.combo_tipo.pack(fill="x", padx=30, pady=(0, 20))

        ctk.CTkButton(
            card,
            text="Confirmar Dados do Titular",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color=COLORS["primary_blue"],
            hover_color=COLORS["primary_blue_hover"],
            height=42,
            corner_radius=8,
            command=self._salvar
        ).pack(fill="x", padx=30, pady=(0, 10))

    def _salvar(self):
        nome = self.entry_titular.get().strip().capitalize()
        agencia = self.entry_agencia.get().strip()
        conta = self.entry_conta.get().strip()
        tipo = self.combo_tipo.get()

        if not nome or not agencia or not conta:
            ModalCustomizado(self, tipo="erro", titulo_janela="Caixa Eletrônico - Erro", titulo="Dados Incompletos!", mensagem="Por favor, preencha todos os campos do titular.")
            return

        self.on_save(nome, agencia, conta, tipo)
        self.grab_release()
        self.destroy()

# ======================================================================================
# 5. APLICAÇÃO PRINCIPAL COM CUSTOMTKINTER
# ======================================================================================
class CaixaEletronicoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Inicia o núcleo sempre limpo
        self.caixa = CaixaEletronicoCore()

        self.saldo_visivel = True
        self.tela_atual = "cadastro_inicial"
        self.ultima_operacao = None

        self.title("Caixa Eletrônico - Acesso à Conta")
        self.geometry("1024x700")
        self.minsize(980, 660)
        self.configure(fg_color=COLORS["content_bg"])

        self._centralizar_janela()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self._criar_sidebar()
        self._criar_area_conteudo()

        # Inicia sempre na tela de cadastro limpa para o cliente
        self.navegar_para("cadastro_inicial")
        self._atualizar_relogio()

    def _centralizar_janela(self):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw // 2) - (1024 // 2)
        y = (sh // 2) - (700 // 2) - 20
        self.geometry(f"1024x700+{max(0, x)}+{max(0, y)}")

    def _criar_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color=COLORS["sidebar_bg"], border_width=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        top_box = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        top_box.pack(fill="x", padx=16, pady=(24, 20))

        ctk.CTkLabel(top_box, image=icon_bank(42, "#ffffff"), text="").pack(pady=(0, 8))
        ctk.CTkLabel(top_box, text="Caixa Eletrônico", font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"), text_color="#ffffff").pack()
        ctk.CTkLabel(top_box, text="Seu dinheiro, nosso compromisso!", font=ctk.CTkFont(family="Segoe UI", size=10), text_color=COLORS["sidebar_subtext"]).pack(pady=(2, 0))

        ctk.CTkFrame(self.sidebar_frame, height=1, fg_color="#0c2a50").pack(fill="x", padx=20, pady=(0, 15))

        self.menu_buttons = {}
        items = [
            ("inicio", "Início", icon_home(18)),
            ("ver_saldo", "Ver Saldo", icon_eye(18)),
            ("extrato", "Extrato", icon_statement(18)),
            ("depositar", "Depositar", icon_deposit_nav(18)),
            ("sacar", "Sacar", icon_withdraw_nav(18)),
            ("sair", "Sair", icon_logout(18)),
        ]

        for chave, rotulo, icone in items:
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=f"  {rotulo}",
                image=icone,
                compound="left",
                anchor="w",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold" if chave == "inicio" else "normal"),
                fg_color="transparent",
                text_color=COLORS["sidebar_text"],
                hover_color=COLORS["sidebar_btn_hover"],
                corner_radius=8,
                height=42,
                command=lambda c=chave: self._clique_sidebar(c)
            )
            btn.pack(fill="x", padx=14, pady=3)
            self.menu_buttons[chave] = btn

        ctk.CTkFrame(self.sidebar_frame, fg_color="transparent").pack(fill="both", expand=True)

        self.btn_config_titular = ctk.CTkButton(
            self.sidebar_frame,
            text="⚙ Alterar Titular",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="#082952",
            hover_color="#0d386e",
            text_color="#9bb5d4",
            height=28,
            corner_radius=6,
            command=self._abrir_cadastro_titular
        )
        self.btn_config_titular.pack(fill="x", padx=20, pady=(0, 10))

        footer_box = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        footer_box.pack(fill="x", padx=16, pady=(0, 20))

        ctk.CTkLabel(footer_box, image=icon_shield(16), text="").pack(side="left", padx=(4, 6))
        ctk.CTkLabel(footer_box, text="Mais segurança\npara você!", font=ctk.CTkFont(family="Segoe UI", size=10), text_color=COLORS["sidebar_subtext"], justify="left").pack(side="left")

    def _criar_area_conteudo(self):
        self.content_frame = ctk.CTkFrame(self, fg_color=COLORS["content_bg"], corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=24, pady=20)

    def _atualizar_destaque_sidebar(self, tela):
        for chave, btn in self.menu_buttons.items():
            if chave == tela:
                btn.configure(fg_color=COLORS["sidebar_btn_active"], text_color="#ffffff", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"))
            else:
                btn.configure(fg_color="transparent", text_color=COLORS["sidebar_text"], font=ctk.CTkFont(family="Segoe UI", size=13, weight="normal"))

    def _clique_sidebar(self, acao):
        if not self.caixa.logado and acao != "sair":
            ModalCustomizado(
                self,
                tipo="aviso",
                titulo_janela="Caixa Eletrônico - Aviso",
                titulo="Identificação Necessária",
                mensagem="Por favor, preencha os dados da sua conta para iniciar o atendimento."
            )
            self.navegar_para("cadastro_inicial")
            return

        if acao == "ver_saldo":
            self.saldo_visivel = not self.saldo_visivel
            if self.tela_atual == "inicio":
                self._atualizar_label_saldo()
            else:
                self.navegar_para("inicio")
        elif acao == "sair":
            self._confirmar_saida()
        else:
            self.navegar_para(acao)

    def navegar_para(self, tela):
        self.tela_atual = tela
        self._atualizar_destaque_sidebar(tela)

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if tela == "cadastro_inicial":
            self.title("Caixa Eletrônico - Identificação do Titular")
            self._render_view_cadastro_inicial()
        elif tela == "inicio":
            self.title("Caixa Eletrônico - Menu Principal")
            self._render_view_menu_principal()
        elif tela == "depositar":
            self.title("Caixa Eletrônico - Depositar")
            self._render_view_depositar()
        elif tela == "comprovante_deposito":
            self.title("Caixa Eletrônico - Comprovante de Depósito")
            self._render_view_comprovante_deposito()
        elif tela == "sacar":
            self.title("Caixa Eletrônico - Sacar")
            self._render_view_sacar()
        elif tela == "comprovante_saque":
            self.title("Caixa Eletrônico - Comprovante de Saque")
            self._render_view_comprovante_saque()
        elif tela == "extrato":
            self.title("Caixa Eletrônico - Extrato")
            self._render_view_extrato()

    # =========================================================================
    # 0. VIEW: CADASTRO INICIAL DO CLIENTE (Começa sempre limpo!)
    # =========================================================================
    def _render_view_cadastro_inicial(self):
        head = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        head.pack(fill="x", pady=(0, 16))

        tx = ctk.CTkFrame(head, fg_color="transparent")
        tx.pack(side="left")

        ctk.CTkLabel(
            tx,
            text="Identificação do Titular",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["text_dark"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            tx,
            text="Por favor, informe os dados da sua conta para iniciar o atendimento.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w")

        right_h = ctk.CTkFrame(head, fg_color="transparent")
        right_h.pack(side="right")
        ctk.CTkLabel(right_h, image=icon_calendar(20), text="").pack(side="left", padx=(0, 8))
        ctk.CTkLabel(right_h, text=datetime.now().strftime("%d/%m/%Y\n%H:%M"), font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=COLORS["text_dark"], justify="right").pack(side="left")

        card_form = ctk.CTkFrame(self.content_frame, fg_color=COLORS["card_bg"], corner_radius=16, border_width=1, border_color=COLORS["card_border"])
        card_form.pack(fill="both", expand=True, pady=(0, 10), padx=20)

        inner = ctk.CTkFrame(card_form, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=40, pady=25)

        # 1. Nome do Titular
        ctk.CTkLabel(inner, text="Nome Completo do Titular:", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=COLORS["text_dark"]).pack(anchor="w", pady=(0, 4))
        self.init_entry_titular = ctk.CTkEntry(inner, height=40, corner_radius=8, placeholder_text="Ex: Carlos Silva ou seu nome", font=ctk.CTkFont(size=13))
        self.init_entry_titular.pack(fill="x", pady=(0, 14))
        self.init_entry_titular.focus_set()

        # Grid: Agência e Conta
        grid_ag_ct = ctk.CTkFrame(inner, fg_color="transparent")
        grid_ag_ct.pack(fill="x", pady=(0, 14))
        grid_ag_ct.grid_columnconfigure((0, 1), weight=1)

        # 2. Agência
        f_ag = ctk.CTkFrame(grid_ag_ct, fg_color="transparent")
        f_ag.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(f_ag, text="Agência:", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=COLORS["text_dark"]).pack(anchor="w", pady=(0, 4))
        self.init_entry_agencia = ctk.CTkEntry(f_ag, height=40, corner_radius=8, placeholder_text="Ex: 0001 ou 1234-5", font=ctk.CTkFont(size=13))
        self.init_entry_agencia.pack(fill="x")

        # 3. Conta
        f_ct = ctk.CTkFrame(grid_ag_ct, fg_color="transparent")
        f_ct.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        ctk.CTkLabel(f_ct, text="Conta com dígito:", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=COLORS["text_dark"]).pack(anchor="w", pady=(0, 4))
        self.init_entry_conta = ctk.CTkEntry(f_ct, height=40, corner_radius=8, placeholder_text="Ex: 12345-6", font=ctk.CTkFont(size=13))
        self.init_entry_conta.pack(fill="x")

        # 4. Tipo de Conta
        ctk.CTkLabel(inner, text="Tipo de Conta:", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=COLORS["text_dark"]).pack(anchor="w", pady=(0, 4))
        self.init_combo_tipo = ctk.CTkSegmentedButton(
            inner,
            values=["Conta Corrente", "Poupança"],
            selected_color=COLORS["primary_blue"],
            selected_hover_color=COLORS["primary_blue_hover"],
            corner_radius=8,
            height=36,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.init_combo_tipo.set("Conta Corrente")
        self.init_combo_tipo.pack(fill="x", pady=(0, 14))

        # 5. Saldo Inicial
        ctk.CTkLabel(inner, text="Saldo Inicial da Conta (R$):", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=COLORS["text_dark"]).pack(anchor="w", pady=(0, 4))
        box_saldo_init = ctk.CTkFrame(inner, fg_color="#f8fafc", corner_radius=8, border_width=1, border_color="#cbd5e1", height=42)
        box_saldo_init.pack(fill="x", pady=(0, 20))
        box_saldo_init.pack_propagate(False)

        ctk.CTkLabel(box_saldo_init, text="R$", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color="#475569", width=45).pack(side="left", padx=(10, 0))
        self.init_entry_saldo = ctk.CTkEntry(box_saldo_init, font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), placeholder_text="1000,00 ou 0,00", placeholder_text_color="#94a3b8", border_width=0, fg_color="transparent")
        self.init_entry_saldo.pack(side="left", fill="both", expand=True, padx=(4, 10))

        # Botão Acessar Conta
        btn_acessar = ctk.CTkButton(
            inner,
            text="✔  Acessar Minha Conta",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color=COLORS["primary_blue"],
            hover_color=COLORS["primary_blue_hover"],
            corner_radius=8,
            height=46,
            command=self._confirmar_cadastro_inicial
        )
        btn_acessar.pack(fill="x", pady=(0, 8))

    def _confirmar_cadastro_inicial(self):
        nome = self.init_entry_titular.get().strip().capitalize()
        agencia = self.init_entry_agencia.get().strip()
        conta = self.init_entry_conta.get().strip()
        tipo = self.init_combo_tipo.get()
        saldo_str = self.init_entry_saldo.get().strip()

        if not nome or not agencia or not conta:
            ModalCustomizado(
                self,
                tipo="erro",
                titulo_janela="Caixa Eletrônico - Erro",
                titulo="Dados Incompletos!",
                mensagem="Por favor, preencha o Nome do Titular, Agência e Conta."
            )
            return

        ok_s, saldo_val, msg_s = SecurityValidator.validar_saldo_inicial(saldo_str)
        if not ok_s:
            ModalCustomizado(
                self,
                tipo="erro",
                titulo_janela="Caixa Eletrônico - Erro",
                titulo="Valor Inválido!",
                mensagem=msg_s
            )
            return

        self.caixa.cadastrar_titular(nome, agencia, conta, tipo, saldo_val)
        self.navegar_para("inicio")

    # =========================================================================
    # 1. VIEW: MENU PRINCIPAL
    # =========================================================================
    def _render_view_menu_principal(self):
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 16))

        left_h = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_h.pack(side="left")

        ctk.CTkLabel(left_h, image=icon_avatar(44), text="").pack(side="left", padx=(0, 12))
        user_text_box = ctk.CTkFrame(left_h, fg_color="transparent")
        user_text_box.pack(side="left")

        titular = self.caixa.usuario_principal['titular'] or "Cliente"
        ctk.CTkLabel(user_text_box, text=f"Olá, {titular}!", font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"), text_color=COLORS["text_dark"]).pack(anchor="w")
        ctk.CTkLabel(user_text_box, text="Bem-vindo(a) ao seu Caixa Eletrônico.", font=ctk.CTkFont(family="Segoe UI", size=12), text_color=COLORS["text_muted"]).pack(anchor="w")

        right_h = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_h.pack(side="right")

        ctk.CTkLabel(right_h, image=icon_calendar(20), text="").pack(side="left", padx=(0, 8))
        self.lbl_data_hora = ctk.CTkLabel(right_h, text=datetime.now().strftime("%d/%m/%Y\n%H:%M"), font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=COLORS["text_dark"], justify="right")
        self.lbl_data_hora.pack(side="left")

        # Card de Saldo
        card_saldo = ctk.CTkFrame(self.content_frame, fg_color=COLORS["balance_gradient"], corner_radius=16, height=110)
        card_saldo.pack(fill="x", pady=(0, 18))
        card_saldo.pack_propagate(False)

        inner_saldo = ctk.CTkFrame(card_saldo, fg_color="transparent")
        inner_saldo.pack(fill="both", expand=True, padx=22, pady=16)

        ctk.CTkLabel(inner_saldo, image=icon_wallet(36), text="").pack(side="left", padx=(0, 16))
        saldo_box = ctk.CTkFrame(inner_saldo, fg_color="transparent")
        saldo_box.pack(side="left", fill="y", expand=True)

        ctk.CTkLabel(saldo_box, text="Saldo Atual", font=ctk.CTkFont(family="Segoe UI", size=12), text_color="#dbeafe").pack(anchor="w")
        self.lbl_saldo_valor = ctk.CTkLabel(saldo_box, text="", font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"), text_color="#ffffff")
        self.lbl_saldo_valor.pack(anchor="w")

        self.btn_toggle_saldo = ctk.CTkButton(
            inner_saldo,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            corner_radius=20,
            width=110,
            height=32,
            command=self._toggle_saldo_clique
        )
        self.btn_toggle_saldo.pack(side="right")
        self._atualizar_label_saldo()

        # Grade de Ações
        grid_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        grid_frame.pack(fill="x", pady=(0, 14))
        grid_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="actions")

        self._criar_card_acao(grid_frame, 0, icon_action_deposit(44), "Depositar", "Adicione um valor\nà sua conta", lambda: self.navegar_para("depositar"))
        self._criar_card_acao(grid_frame, 1, icon_action_withdraw(44), "Sacar", "Retire um valor\nda sua conta", lambda: self.navegar_para("sacar"))
        self._criar_card_acao(grid_frame, 2, icon_action_statement(44), "Extrato", "Veja o histórico de\nmovimentações", lambda: self.navegar_para("extrato"))

        # Card Sair
        card_sair = ctk.CTkFrame(self.content_frame, fg_color=COLORS["card_bg"], corner_radius=14, border_width=1, border_color=COLORS["card_border"], height=80)
        card_sair.pack(fill="x", pady=(6, 0))
        card_sair.pack_propagate(False)

        inner_sair = ctk.CTkFrame(card_sair, fg_color="transparent")
        inner_sair.pack(fill="both", expand=True, padx=20, pady=12)

        ctk.CTkLabel(inner_sair, image=icon_action_logout(42), text="").pack(side="left", padx=(0, 14))
        sair_tx = ctk.CTkFrame(inner_sair, fg_color="transparent")
        sair_tx.pack(side="left", fill="y", expand=True)

        ctk.CTkLabel(sair_tx, text="Sair", font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"), text_color=COLORS["text_dark"]).pack(anchor="w")
        ctk.CTkLabel(sair_tx, text="Finalize o atendimento", font=ctk.CTkFont(family="Segoe UI", size=11), text_color=COLORS["text_muted"]).pack(anchor="w")

        ctk.CTkButton(inner_sair, text="Finalizar Sessão", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), fg_color="#f1f5f9", hover_color="#e2e8f0", text_color="#475569", corner_radius=8, height=36, width=140, command=self._confirmar_saida).pack(side="right")

    def _criar_card_acao(self, parent, col, icone, titulo, subtitulo, comando):
        card = ctk.CTkFrame(parent, fg_color=COLORS["card_bg"], corner_radius=14, border_width=1, border_color=COLORS["card_border"], height=130)
        card.grid(row=0, column=col, padx=6, sticky="nsew")
        card.pack_propagate(False)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=14, pady=12)

        lbl_i = ctk.CTkLabel(inner, image=icone, text="")
        lbl_i.pack(anchor="w", pady=(0, 6))

        lbl_t = ctk.CTkLabel(inner, text=titulo, font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"), text_color=COLORS["text_dark"])
        lbl_t.pack(anchor="w")

        lbl_s = ctk.CTkLabel(inner, text=subtitulo, font=ctk.CTkFont(family="Segoe UI", size=10), text_color=COLORS["text_muted"], justify="left")
        lbl_s.pack(anchor="w")

        for w in (card, inner, lbl_i, lbl_t, lbl_s):
            w.bind("<Button-1>", lambda e, c=comando: c())
            w.configure(cursor="hand2")

    def _toggle_saldo_clique(self):
        self.saldo_visivel = not self.saldo_visivel
        self._atualizar_label_saldo()

    def _atualizar_label_saldo(self):
        if not hasattr(self, 'lbl_saldo_valor'):
            return
        if self.saldo_visivel:
            fmt = f"R$ {self.caixa.saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            self.lbl_saldo_valor.configure(text=fmt)
            self.btn_toggle_saldo.configure(text="👁 Ocultar")
        else:
            self.lbl_saldo_valor.configure(text="R$ ••••••••")
            self.btn_toggle_saldo.configure(text="👁 Ver saldo")

    # =========================================================================
    # 2. VIEW: DEPOSITAR
    # =========================================================================
    def _render_view_depositar(self):
        head = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        head.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(head, image=icon_action_deposit(46), text="").pack(side="left", padx=(0, 14))
        tx = ctk.CTkFrame(head, fg_color="transparent")
        tx.pack(side="left")
        ctk.CTkLabel(tx, text="Depósito", font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"), text_color=COLORS["text_dark"]).pack(anchor="w")
        ctk.CTkLabel(tx, text="Informe o valor que deseja depositar.", font=ctk.CTkFont(family="Segoe UI", size=13), text_color=COLORS["text_muted"]).pack(anchor="w")

        form_card = ctk.CTkFrame(self.content_frame, fg_color=COLORS["card_bg"], corner_radius=16, border_width=1, border_color=COLORS["card_border"])
        form_card.pack(fill="both", expand=True, pady=(0, 16), padx=10)

        inner_form = ctk.CTkFrame(form_card, fg_color="transparent")
        inner_form.pack(fill="both", expand=True, padx=30, pady=25)

        # Destino
        ctk.CTkLabel(inner_form, text="Conta de Destino:", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=COLORS["text_dark"]).pack(anchor="w", pady=(0, 6))
        self.seg_destino = ctk.CTkSegmentedButton(inner_form, values=["Minha Própria Conta", "Outro Destinatário"], selected_color=COLORS["primary_blue"], selected_hover_color=COLORS["primary_blue_hover"], corner_radius=8, height=34, command=self._ao_mudar_tipo_destino)
        self.seg_destino.set("Minha Própria Conta")
        self.seg_destino.pack(fill="x", pady=(0, 14))

        self.frame_destinatario_extra = ctk.CTkFrame(inner_form, fg_color="#f8fafc", corner_radius=10, border_width=1, border_color="#e2e8f0")
        ctk.CTkLabel(self.frame_destinatario_extra, text="Nome do Destinatário:", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, padx=12, pady=(8, 2), sticky="w")
        self.entry_dest_nome = ctk.CTkEntry(self.frame_destinatario_extra, height=32, corner_radius=6)
        self.entry_dest_nome.grid(row=1, column=0, padx=12, pady=(0, 8), sticky="ew")

        ctk.CTkLabel(self.frame_destinatario_extra, text="Agência (ex: 1234):", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=1, padx=12, pady=(8, 2), sticky="w")
        self.entry_dest_agencia = ctk.CTkEntry(self.frame_destinatario_extra, height=32, corner_radius=6)
        self.entry_dest_agencia.grid(row=1, column=1, padx=12, pady=(0, 8), sticky="ew")

        ctk.CTkLabel(self.frame_destinatario_extra, text="Conta (ex: 56789-0):", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=2, padx=12, pady=(8, 2), sticky="w")
        self.entry_dest_conta = ctk.CTkEntry(self.frame_destinatario_extra, height=32, corner_radius=6)
        self.entry_dest_conta.grid(row=1, column=2, padx=12, pady=(0, 8), sticky="ew")
        self.frame_destinatario_extra.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(inner_form, text="Valor do depósito:", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color=COLORS["text_dark"]).pack(anchor="w", pady=(10, 8))

        input_container = ctk.CTkFrame(inner_form, fg_color="#f8fafc", corner_radius=10, border_width=1, border_color="#cbd5e1", height=50)
        input_container.pack(fill="x", pady=(0, 16))
        input_container.pack_propagate(False)

        ctk.CTkLabel(input_container, text="R$", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), text_color="#475569", width=50).pack(side="left", padx=(10, 0))
        self.entry_valor_deposito = ctk.CTkEntry(input_container, font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"), placeholder_text="0,00", placeholder_text_color="#94a3b8", border_width=0, fg_color="transparent", text_color=COLORS["text_dark"])
        self.entry_valor_deposito.pack(side="left", fill="both", expand=True, padx=(4, 12))
        self.entry_valor_deposito.focus_set()

        info_card = ctk.CTkFrame(inner_form, fg_color=COLORS["info_blue_bg"], corner_radius=10, border_width=1, border_color=COLORS["info_blue_border"])
        info_card.pack(fill="x", pady=(8, 16))

        inner_info = ctk.CTkFrame(info_card, fg_color="transparent")
        inner_info.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(inner_info, image=icon_mini_info(20), text="").pack(side="left", padx=(0, 12))
        tx_info = ctk.CTkFrame(inner_info, fg_color="transparent")
        tx_info.pack(side="left")
        ctk.CTkLabel(tx_info, text="Digite apenas números.", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=COLORS["info_blue_text"]).pack(anchor="w")
        ctk.CTkLabel(tx_info, text="Exemplo: 250,00", font=ctk.CTkFont(family="Segoe UI", size=11), text_color="#3b82f6").pack(anchor="w")

        btn_bar = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        btn_bar.pack(fill="x", pady=(0, 8), padx=10)

        ctk.CTkButton(btn_bar, text="✕  Cancelar", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), fg_color="#ffffff", hover_color="#f1f5f9", text_color="#475569", border_width=1, border_color="#cbd5e1", corner_radius=8, height=44, width=150, command=self._cancelar_deposito).pack(side="left")
        ctk.CTkButton(btn_bar, text="✔  Confirmar", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), fg_color=COLORS["primary_blue"], hover_color=COLORS["primary_blue_hover"], text_color="#ffffff", corner_radius=8, height=44, width=160, command=self._confirmar_deposito).pack(side="right")

    def _ao_mudar_tipo_destino(self, valor):
        if valor == "Outro Destinatário":
            self.frame_destinatario_extra.pack(fill="x", pady=(0, 12))
        else:
            self.frame_destinatario_extra.pack_forget()

    def _confirmar_deposito(self):
        valor_str = self.entry_valor_deposito.get()
        sucesso, valor, msg = SecurityValidator.validar_valor(valor_str)
        if not sucesso:
            ModalCustomizado(self, tipo="erro", titulo_janela="Caixa Eletrônico - Erro", titulo="Valor Inválido!", mensagem=msg)
            return

        destinatario = None
        if self.seg_destino.get() == "Outro Destinatário":
            nome_d = self.entry_dest_nome.get().strip().capitalize()
            ag_d = self.entry_dest_agencia.get().strip()
            ct_d = self.entry_dest_conta.get().strip()
            if not nome_d or not ag_d or not ct_d:
                ModalCustomizado(self, tipo="erro", titulo_janela="Caixa Eletrônico - Erro", titulo="Dados do Destinatário Incompletos!", mensagem="Por favor, preencha o nome, agência e conta do destinatário.")
                return
            destinatario = {'titular': nome_d, 'agencia': ag_d, 'conta': ct_d, 'tipo_conta': 'Conta Corrente', 'propria_conta': False}

        self.ultima_operacao = self.caixa.depositar(valor, destinatario)
        self.navegar_para("comprovante_deposito")

    def _cancelar_deposito(self):
        ModalCustomizado(self, tipo="cancelado", titulo_janela="Caixa Eletrônico - Cancelado", titulo="Operação Cancelada", mensagem="A transação foi cancelada e nenhum valor foi debitado.", on_close=lambda: self.navegar_para("inicio"))

    # =========================================================================
    # 3. VIEW: COMPROVANTE DE DEPÓSITO
    # =========================================================================
    def _render_view_comprovante_deposito(self):
        op = self.ultima_operacao or {'tipo': 'Deposito', 'valor': 0.0, 'data': datetime.now().date(), 'hora': datetime.now().time(), 'saldo_anterior': 0.0, 'saldo_atual': 0.0}

        banner = ctk.CTkFrame(self.content_frame, fg_color=COLORS["banner_green"], corner_radius=12, height=64)
        banner.pack(fill="x", pady=(0, 16))
        banner.pack_propagate(False)

        inner_b = ctk.CTkFrame(banner, fg_color="transparent")
        inner_b.pack(fill="both", expand=True, padx=18, pady=8)

        ctk.CTkLabel(inner_b, image=icon_success_check(36), text="").pack(side="left", padx=(0, 12))
        tx_b = ctk.CTkFrame(inner_b, fg_color="transparent")
        tx_b.pack(side="left")
        ctk.CTkLabel(tx_b, text="Depósito Realizado!", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), text_color="#ffffff").pack(anchor="w")
        ctk.CTkLabel(tx_b, text="Seu depósito foi processado com sucesso.", font=ctk.CTkFont(family="Segoe UI", size=11), text_color="#e6f4ea").pack(anchor="w")

        card_comp = ctk.CTkFrame(self.content_frame, fg_color=COLORS["card_bg"], corner_radius=14, border_width=1, border_color=COLORS["card_border"])
        card_comp.pack(fill="both", expand=True, pady=(0, 12), padx=20)

        inner_comp = ctk.CTkFrame(card_comp, fg_color="transparent")
        inner_comp.pack(fill="both", expand=True, padx=30, pady=20)

        top_c = ctk.CTkFrame(inner_comp, fg_color="transparent")
        top_c.pack(anchor="w", pady=(0, 16))
        ctk.CTkLabel(top_c, image=icon_bank(28, "#002244"), text="").pack(side="left", padx=(0, 10))
        ctk.CTkLabel(top_c, text="Comprovante de Depósito", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), text_color=COLORS["text_dark"]).pack(side="left")

        itens = [
            ("Data / Hora:", f"{op['data'].strftime('%d/%m/%Y')} {op['hora'].strftime('%H:%M')}"),
            ("Agência:", self.caixa.usuario_principal['agencia']),
            ("Conta:", self.caixa.usuario_principal['conta'])
        ]
        if op.get('destinatario') and not op['destinatario'].get('propria_conta', True):
            d = op['destinatario']
            itens.append(("Destinatário:", d['titular']))
            itens.append(("Conta Destino:", f"Ag: {d['agencia']} | Ct: {d['conta']}"))

        itens.extend([
            ("Valor Depositado:", f"R$ {op['valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
            ("Saldo Atual:", f"R$ {op['saldo_atual']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        ])

        for rotulo, val in itens:
            row = ctk.CTkFrame(inner_comp, fg_color="transparent")
            row.pack(fill="x", pady=4)
            is_bold = rotulo in ["Valor Depositado:", "Saldo Atual:"]
            ctk.CTkLabel(row, text=rotulo, font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold" if is_bold else "normal"), text_color=COLORS["text_dark"]).pack(side="left")
            ctk.CTkLabel(row, text=val, font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold" if is_bold else "normal"), text_color=COLORS["text_dark"]).pack(side="right")

        box_ok = ctk.CTkFrame(inner_comp, fg_color=COLORS["badge_green_bg"], corner_radius=8)
        box_ok.pack(fill="x", pady=(18, 0))
        inner_box_ok = ctk.CTkFrame(box_ok, fg_color="transparent")
        inner_box_ok.pack(fill="x", padx=14, pady=10)
        ctk.CTkLabel(inner_box_ok, image=icon_mini_check(18), text="").pack(side="left", padx=(0, 10))
        tx_ok = ctk.CTkFrame(inner_box_ok, fg_color="transparent")
        tx_ok.pack(side="left")
        ctk.CTkLabel(tx_ok, text="Transação concluída com sucesso!", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=COLORS["badge_green_text"]).pack(anchor="w")
        ctk.CTkLabel(tx_ok, text="Obrigado por utilizar nossos serviços.", font=ctk.CTkFont(family="Segoe UI", size=10), text_color="#15803d").pack(anchor="w")

        btn_bar = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        btn_bar.pack(fill="x", pady=(0, 4), padx=20)
        ctk.CTkButton(btn_bar, text="🖨  Imprimir Comprovante", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), fg_color=COLORS["primary_blue"], hover_color=COLORS["primary_blue_hover"], corner_radius=8, height=42, command=lambda: self._imprimir_comprovante(op)).pack(fill="x", pady=(0, 8))
        ctk.CTkButton(btn_bar, text="🏠  Voltar ao Menu", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), fg_color="#ffffff", hover_color="#f1f5f9", text_color=COLORS["primary_blue"], border_width=1, border_color="#cbd5e1", corner_radius=8, height=38, command=lambda: self.navegar_para("inicio")).pack(fill="x")

    # =========================================================================
    # 4. VIEW: SACAR
    # =========================================================================
    def _render_view_sacar(self):
        head = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        head.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(head, image=icon_action_withdraw(46), text="").pack(side="left", padx=(0, 14))
        tx = ctk.CTkFrame(head, fg_color="transparent")
        tx.pack(side="left")
        ctk.CTkLabel(tx, text="Saque", font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"), text_color=COLORS["text_dark"]).pack(anchor="w")
        ctk.CTkLabel(tx, text="Informe o valor que deseja sacar.", font=ctk.CTkFont(family="Segoe UI", size=13), text_color=COLORS["text_muted"]).pack(anchor="w")

        form_card = ctk.CTkFrame(self.content_frame, fg_color=COLORS["card_bg"], corner_radius=16, border_width=1, border_color=COLORS["card_border"])
        form_card.pack(fill="both", expand=True, pady=(0, 16), padx=10)

        inner_form = ctk.CTkFrame(form_card, fg_color="transparent")
        inner_form.pack(fill="both", expand=True, padx=30, pady=25)

        ctk.CTkLabel(inner_form, text="Valor do saque:", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color=COLORS["text_dark"]).pack(anchor="w", pady=(0, 8))

        input_container = ctk.CTkFrame(inner_form, fg_color="#f8fafc", corner_radius=10, border_width=1, border_color="#cbd5e1", height=50)
        input_container.pack(fill="x", pady=(0, 16))
        input_container.pack_propagate(False)

        ctk.CTkLabel(input_container, text="R$", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), text_color="#475569", width=50).pack(side="left", padx=(10, 0))
        self.entry_valor_saque = ctk.CTkEntry(input_container, font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"), placeholder_text="0,00", placeholder_text_color="#94a3b8", border_width=0, fg_color="transparent", text_color=COLORS["text_dark"])
        self.entry_valor_saque.pack(side="left", fill="both", expand=True, padx=(4, 12))
        self.entry_valor_saque.focus_set()

        # Dica 1
        info1 = ctk.CTkFrame(inner_form, fg_color=COLORS["info_blue_bg"], corner_radius=10, border_width=1, border_color=COLORS["info_blue_border"])
        info1.pack(fill="x", pady=(0, 10))
        i1 = ctk.CTkFrame(info1, fg_color="transparent")
        i1.pack(fill="x", padx=16, pady=10)
        ctk.CTkLabel(i1, image=icon_mini_info(20), text="").pack(side="left", padx=(0, 12))
        t1 = ctk.CTkFrame(i1, fg_color="transparent")
        t1.pack(side="left")
        ctk.CTkLabel(t1, text="Digite apenas números.", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["info_blue_text"]).pack(anchor="w")
        ctk.CTkLabel(t1, text="Exemplo: 100,00", font=ctk.CTkFont(size=11), text_color="#3b82f6").pack(anchor="w")

        # Dica 2
        saldo_fmt = f"R$ {self.caixa.saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        info2 = ctk.CTkFrame(inner_form, fg_color=COLORS["info_blue_bg"], corner_radius=10, border_width=1, border_color=COLORS["info_blue_border"])
        info2.pack(fill="x", pady=(0, 16))
        i2 = ctk.CTkFrame(info2, fg_color="transparent")
        i2.pack(fill="x", padx=16, pady=10)
        ctk.CTkLabel(i2, image=icon_mini_info(20), text="").pack(side="left", padx=(0, 12))
        t2 = ctk.CTkFrame(info2, fg_color="transparent")
        t2.pack(side="left")
        ctk.CTkLabel(t2, text=f"Seu saldo atual é: {saldo_fmt}", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["info_blue_text"]).pack(anchor="w")
        ctk.CTkLabel(t2, text="O valor do saque não pode ser maior que o saldo.", font=ctk.CTkFont(size=11), text_color="#3b82f6").pack(anchor="w")

        btn_bar = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        btn_bar.pack(fill="x", pady=(0, 8), padx=10)

        ctk.CTkButton(btn_bar, text="✕  Cancelar", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), fg_color="#ffffff", hover_color="#f1f5f9", text_color="#475569", border_width=1, border_color="#cbd5e1", corner_radius=8, height=44, width=150, command=self._cancelar_saque).pack(side="left")
        ctk.CTkButton(btn_bar, text="✔  Confirmar", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), fg_color=COLORS["primary_blue"], hover_color=COLORS["primary_blue_hover"], text_color="#ffffff", corner_radius=8, height=44, width=160, command=self._confirmar_saque).pack(side="right")

    def _confirmar_saque(self):
        valor_str = self.entry_valor_saque.get()
        sucesso, valor, msg = SecurityValidator.validar_valor(valor_str)
        if not sucesso:
            ModalCustomizado(self, tipo="erro", titulo_janela="Caixa Eletrônico - Erro", titulo="Valor Inválido!", mensagem=msg)
            return

        ok, resultado = self.caixa.sacar(valor)
        if not ok:
            ModalCustomizado(self, tipo="aviso", titulo_janela="Caixa Eletrônico - Aviso", titulo="Saldo Insuficiente!", mensagem="O valor do saque é maior que o saldo disponível em sua conta.")
            return

        self.ultima_operacao = resultado
        self.navegar_para("comprovante_saque")

    def _cancelar_saque(self):
        ModalCustomizado(self, tipo="cancelado", titulo_janela="Caixa Eletrônico - Cancelado", titulo="Operação Cancelada", mensagem="A transação foi cancelada e nenhum valor foi debitado.", on_close=lambda: self.navegar_para("inicio"))

    # =========================================================================
    # 5. VIEW: COMPROVANTE DE SAQUE
    # =========================================================================
    def _render_view_comprovante_saque(self):
        op = self.ultima_operacao or {'tipo': 'Saque', 'valor': 0.0, 'data': datetime.now().date(), 'hora': datetime.now().time(), 'saldo_anterior': 0.0, 'saldo_atual': 0.0}

        banner = ctk.CTkFrame(self.content_frame, fg_color=COLORS["banner_red"], corner_radius=12, height=64)
        banner.pack(fill="x", pady=(0, 16))
        banner.pack_propagate(False)

        inner_b = ctk.CTkFrame(banner, fg_color="transparent")
        inner_b.pack(fill="both", expand=True, padx=18, pady=8)

        ctk.CTkLabel(inner_b, image=icon_saque_check(36), text="").pack(side="left", padx=(0, 12))
        tx_b = ctk.CTkFrame(inner_b, fg_color="transparent")
        tx_b.pack(side="left")
        ctk.CTkLabel(tx_b, text="Saque Realizado!", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), text_color="#ffffff").pack(anchor="w")
        ctk.CTkLabel(tx_b, text="Seu saque foi processado com sucesso.", font=ctk.CTkFont(family="Segoe UI", size=11), text_color="#fee2e2").pack(anchor="w")

        card_comp = ctk.CTkFrame(self.content_frame, fg_color=COLORS["card_bg"], corner_radius=14, border_width=1, border_color=COLORS["card_border"])
        card_comp.pack(fill="both", expand=True, pady=(0, 12), padx=20)

        inner_comp = ctk.CTkFrame(card_comp, fg_color="transparent")
        inner_comp.pack(fill="both", expand=True, padx=30, pady=20)

        top_c = ctk.CTkFrame(inner_comp, fg_color="transparent")
        top_c.pack(anchor="w", pady=(0, 16))
        ctk.CTkLabel(top_c, image=icon_bank(28, "#002244"), text="").pack(side="left", padx=(0, 10))
        ctk.CTkLabel(top_c, text="Comprovante de Saque", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), text_color=COLORS["text_dark"]).pack(side="left")

        itens = [
            ("Data / Hora:", f"{op['data'].strftime('%d/%m/%Y')} {op['hora'].strftime('%H:%M')}"),
            ("Agência:", self.caixa.usuario_principal['agencia']),
            ("Conta:", self.caixa.usuario_principal['conta']),
            ("Valor Sacado:", f"R$ {op['valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
            ("Saldo Restante:", f"R$ {op['saldo_atual']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        ]

        for rotulo, val in itens:
            row = ctk.CTkFrame(inner_comp, fg_color="transparent")
            row.pack(fill="x", pady=5)
            is_bold = rotulo in ["Valor Sacado:", "Saldo Restante:"]
            ctk.CTkLabel(row, text=rotulo, font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold" if is_bold else "normal"), text_color=COLORS["text_dark"]).pack(side="left")
            ctk.CTkLabel(row, text=val, font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold" if is_bold else "normal"), text_color=COLORS["text_dark"]).pack(side="right")

        box_ok = ctk.CTkFrame(inner_comp, fg_color=COLORS["badge_green_bg"], corner_radius=8)
        box_ok.pack(fill="x", pady=(20, 0))
        inner_box_ok = ctk.CTkFrame(box_ok, fg_color="transparent")
        inner_box_ok.pack(fill="x", padx=14, pady=10)
        ctk.CTkLabel(inner_box_ok, image=icon_mini_check(18), text="").pack(side="left", padx=(0, 10))
        tx_ok = ctk.CTkFrame(inner_box_ok, fg_color="transparent")
        tx_ok.pack(side="left")
        ctk.CTkLabel(tx_ok, text="Transação concluída com sucesso!", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=COLORS["badge_green_text"]).pack(anchor="w")
        ctk.CTkLabel(tx_ok, text="Obrigado por utilizar nossos serviços.", font=ctk.CTkFont(family="Segoe UI", size=10), text_color="#15803d").pack(anchor="w")

        btn_bar = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        btn_bar.pack(fill="x", pady=(0, 4), padx=20)
        ctk.CTkButton(btn_bar, text="🖨  Imprimir Comprovante", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), fg_color=COLORS["primary_blue"], hover_color=COLORS["primary_blue_hover"], corner_radius=8, height=42, command=lambda: self._imprimir_comprovante(op)).pack(fill="x", pady=(0, 8))
        ctk.CTkButton(btn_bar, text="🏠  Voltar ao Menu", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), fg_color="#ffffff", hover_color="#f1f5f9", text_color=COLORS["primary_blue"], border_width=1, border_color="#cbd5e1", corner_radius=8, height=38, command=lambda: self.navegar_para("inicio")).pack(fill="x")

    # =========================================================================
    # 6. VIEW: EXTRATO
    # =========================================================================
    def _render_view_extrato(self):
        head = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        head.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(head, image=icon_statement(44, COLORS["primary_blue"]), text="").pack(side="left", padx=(0, 14))
        tx = ctk.CTkFrame(head, fg_color="transparent")
        tx.pack(side="left")
        ctk.CTkLabel(tx, text="Extrato", font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"), text_color=COLORS["text_dark"]).pack(anchor="w")
        ctk.CTkLabel(tx, text="Histórico de movimentações da sua conta", font=ctk.CTkFont(family="Segoe UI", size=12), text_color=COLORS["text_muted"]).pack(anchor="w")

        resumo_card = ctk.CTkFrame(self.content_frame, fg_color=COLORS["card_bg"], corner_radius=10, border_width=1, border_color=COLORS["card_border"], height=54)
        resumo_card.pack(fill="x", pady=(0, 12))
        resumo_card.pack_propagate(False)

        inner_res = ctk.CTkFrame(resumo_card, fg_color="transparent")
        inner_res.pack(fill="both", expand=True, padx=20, pady=8)

        ctk.CTkLabel(inner_res, text=f"Conta: {self.caixa.usuario_principal['conta']}", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=COLORS["text_dark"]).pack(side="left")
        saldo_fmt = f"R$ {self.caixa.saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        ctk.CTkLabel(inner_res, text=f"Saldo Atual: {saldo_fmt}", font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"), text_color=COLORS["text_dark"]).pack(side="right")

        ctrl_bar = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        ctrl_bar.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(ctrl_bar, text="Movimentações", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color=COLORS["text_dark"]).pack(side="left")

        self.combo_filtro = ctk.CTkOptionMenu(
            ctrl_bar,
            values=["Últimos 10 registros", "Todos", "Apenas Depósitos", "Apenas Saques"],
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="#ffffff",
            button_color="#e2e8f0",
            button_hover_color="#cbd5e1",
            text_color="#1e293b",
            dropdown_fg_color="#ffffff",
            dropdown_text_color="#1e293b",
            corner_radius=6,
            height=28,
            width=180,
            command=lambda val: self._filtrar_extrato(val)
        )
        self.combo_filtro.set("Últimos 10 registros")
        self.combo_filtro.pack(side="right")

        tabela_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS["card_bg"], corner_radius=12, border_width=1, border_color=COLORS["card_border"])
        tabela_frame.pack(fill="both", expand=True, pady=(0, 10))

        header_tab = ctk.CTkFrame(tabela_frame, fg_color="#f8fafc", corner_radius=8, height=36)
        header_tab.pack(fill="x", padx=10, pady=(10, 4))
        header_tab.pack_propagate(False)

        cols = ["Data / Hora", "Descrição", "Valor (R$)", "Saldo (R$)"]
        for col_name in cols:
            ctk.CTkLabel(header_tab, text=col_name, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#475569").pack(side="left", expand=True, fill="x")

        self.scroll_linhas = ctk.CTkScrollableFrame(tabela_frame, fg_color="transparent")
        self.scroll_linhas.pack(fill="both", expand=True, padx=6, pady=(0, 8))

        self._popular_linhas_extrato()

        footer_ext = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        footer_ext.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(footer_ext, text=f"Total de {len(self.caixa.historico)} movimentações", font=ctk.CTkFont(family="Segoe UI", size=11), text_color=COLORS["text_muted"]).pack(side="left")
        ctk.CTkButton(footer_ext, text="⬇  Exportar Extrato", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), fg_color=COLORS["primary_blue"], hover_color=COLORS["primary_blue_hover"], corner_radius=8, height=36, command=self._exportar_extrato).pack(side="right")

    def _popular_linhas_extrato(self, filtro="Últimos 10 registros"):
        for w in self.scroll_linhas.winfo_children():
            w.destroy()

        if not self.caixa.historico:
            # Respeita estritamente o código original: "Não há movimentações recentes!"
            ctk.CTkLabel(
                self.scroll_linhas,
                text="Não há movimentações recentes nesta conta.",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=COLORS["text_muted"]
            ).pack(pady=40)
            return

        historico_filtrado = list(self.caixa.historico)
        if filtro == "Apenas Depósitos":
            historico_filtrado = [op for op in historico_filtrado if op['tipo'] == 'Deposito']
        elif filtro == "Apenas Saques":
            historico_filtrado = [op for op in historico_filtrado if op['tipo'] == 'Saque']
        elif filtro == "Últimos 10 registros":
            historico_filtrado = historico_filtrado[-10:]

        historico_filtrado = list(reversed(historico_filtrado))

        if not historico_filtrado:
            ctk.CTkLabel(self.scroll_linhas, text="Nenhuma movimentação encontrada para o filtro.", font=ctk.CTkFont(family="Segoe UI", size=12), text_color=COLORS["text_muted"]).pack(pady=40)
            return

        for op in historico_filtrado:
            linha = ctk.CTkFrame(self.scroll_linhas, fg_color="#ffffff", corner_radius=6, height=38)
            linha.pack(fill="x", pady=2)
            linha.pack_propagate(False)

            is_dep = op['tipo'] == 'Deposito'
            cor_val = COLORS["badge_green_text"] if is_dep else COLORS["badge_red_text"]
            sinal = "+" if is_dep else "-"
            ico = icon_badge_deposit(16) if is_dep else icon_badge_withdraw(16)

            data_str = f"{op['data'].strftime('%d/%m/%Y')} {op['hora'].strftime('%H:%M')}"
            val_str = f"{sinal} {op['valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            saldo_str = f"{op['saldo_atual']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            f1 = ctk.CTkFrame(linha, fg_color="transparent")
            f1.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(f1, text=data_str, font=ctk.CTkFont(size=11), text_color="#334155").pack(anchor="center")

            f2 = ctk.CTkFrame(linha, fg_color="transparent")
            f2.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(f2, image=ico, text=f"  {op['tipo']}", compound="left", font=ctk.CTkFont(size=11, weight="bold"), text_color="#1e293b").pack(anchor="center")

            f3 = ctk.CTkFrame(linha, fg_color="transparent")
            f3.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(f3, text=val_str, font=ctk.CTkFont(size=11, weight="bold"), text_color=cor_val).pack(anchor="center")

            f4 = ctk.CTkFrame(linha, fg_color="transparent")
            f4.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(f4, text=saldo_str, font=ctk.CTkFont(size=11), text_color="#475569").pack(anchor="center")

    def _filtrar_extrato(self, filtro):
        self._popular_linhas_extrato(filtro)

    def _imprimir_comprovante(self, op):
        recibo = self.caixa.gerar_recibo_texto(op)
        nome_arq = f"comprovante_{op['tipo'].lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), nome_arq)

        with open(caminho, "w", encoding="utf-8") as f:
            f.write(recibo)

        ModalCustomizado(self, tipo="cancelado", titulo_janela="Caixa Eletrônico - Impressão", titulo="Comprovante Emitido!", mensagem=f"Comprovante gerado com sucesso!\nArquivo salvo em:\n{nome_arq}")

    def _exportar_extrato(self):
        extrato_txt = self.caixa.gerar_extrato_texto()
        nome_arq = f"extrato_{self.caixa.usuario_principal['conta']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), nome_arq)

        with open(caminho, "w", encoding="utf-8") as f:
            f.write(extrato_txt)

        ModalCustomizado(self, tipo="cancelado", titulo_janela="Caixa Eletrônico - Exportação", titulo="Extrato Exportado!", mensagem=f"Extrato completo exportado com sucesso!\nArquivo:\n{nome_arq}")

    def _confirmar_saida(self):
        def encerrar():
            self.caixa.resetar_sessao()
            self.navegar_para("cadastro_inicial")

        ModalCustomizado(
            self,
            tipo="cancelado",
            titulo_janela="Caixa Eletrônico - Finalizar",
            titulo="Sessão Finalizada",
            mensagem="O atendimento foi finalizado com sucesso e seus dados foram desconectados com segurança.",
            on_close=encerrar
        )

    def _abrir_cadastro_titular(self):
        if not self.caixa.logado:
            self.navegar_para("cadastro_inicial")
            return

        def salvar(nome, ag, ct, tipo):
            self.caixa.atualizar_dados_titular(nome, ag, ct, tipo)
            if self.tela_atual == "inicio":
                self.navegar_para("inicio")
            elif self.tela_atual == "extrato":
                self.navegar_para("extrato")
            ModalCustomizado(self, tipo="cancelado", titulo_janela="Caixa Eletrônico - Sucesso", titulo="Dados Atualizados!", mensagem=f"Titular atualizado para {nome} (Ag: {ag} | Ct: {ct}).")

        ModalCadastroTitular(self, self.caixa.usuario_principal, salvar)

    def _atualizar_relogio(self):
        if hasattr(self, 'lbl_data_hora') and self.lbl_data_hora.winfo_exists():
            self.lbl_data_hora.configure(text=datetime.now().strftime("%d/%m/%Y\n%H:%M"))
        self.after(30000, self._atualizar_relogio)

# ======================================================================================
# 6. INICIALIZAÇÃO
# ======================================================================================
def main():
    app = CaixaEletronicoApp()
    app.mainloop()

if __name__ == "__main__":
    main()
