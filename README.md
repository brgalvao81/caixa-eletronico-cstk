# 🏧 Caixa Eletrônico Desktop - CustomTkinter

> Interface bancária moderna desenvolvida em Python com **CustomTkinter** e **Pillow**, com fidelidade visual ao design de caixa eletrônico e arquitetura segura.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-1f538d?logo=tkinter&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📌 Sobre o Projeto

Este projeto é uma aplicação desktop de **Caixa Eletrônico (ATM)** que simula com realismo as operações bancárias essenciais:
- Identificação e cadastro do titular (sessão iniciada do zero a cada execução).
- Visualização de saldo com recurso de privacidade (`👁 Ver / Ocultar`).
- Realização de depósitos (para própria conta ou terceiros).
- Realização de saques com validação rigorosa de saldo insuficiente.
- Extrato bancário interativo com filtros e badges por tipo de movimentação.
- Emissão de comprovantes textuais com código de autenticação bancária.
- Modais personalizados de aviso, erro e cancelamento.

---

## 🛠️ Tecnologias Utilizadas

- **[Python](https://www.python.org/)**: Linguagem principal do projeto.
- **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)**: Biblioteca para interface gráfica moderna com cantos arredondados e suporte a temas.
- **[Pillow (PIL)](https://python-pillow.org/)**: Renderização vetorial e anti-aliasing dos ícones da aplicação.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
- Python 3.10 ou superior instalado.

### 1. Clonar o repositório
```bash
git clone https://github.com/SEU_USUARIO/caixa-eletronico-cstk.git
cd caixa-eletronico-cstk
```

### 2. Criar e ativar o ambiente virtual (Recomendado)
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar as dependências
```bash
pip install -r requirements.txt
```

### 4. Executar a aplicação
```bash
python main.py
```

---

## 📦 Como Gerar o Executável (.exe)

Caso deseje compilar o projeto em um executável autônomo de arquivo único para Windows (sem necessidade de Python instalado):

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --collect-all customtkinter --icon app_icon.ico --name "CaixaEletronico" main.py
```
O executável final será gerado dentro da pasta `dist/`.

---

## 📁 Estrutura do Repositório

```text
├── main.py              # Código-fonte principal da aplicação
├── requirements.txt     # Dependências do projeto
├── app_icon.ico         # Ícone do aplicativo
├── .gitignore           # Arquivos e pastas ignorados pelo Git
└── README.md            # Documentação do projeto
```

---

## 📄 Licença

Distribuído sob a licença MIT. Consulte `LICENSE` para mais informações.
