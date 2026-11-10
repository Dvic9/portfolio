from selenium import webdriver
from selenium.webdriver.common.by import By
import customtkinter as ctk
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import xml.etree.ElementTree as ET
from rapidfuzz import process, fuzz
from tkinter import messagebox
import pandas as pd
import tkinter as tk
from tkinter import simpledialog
from selenium.webdriver.support.ui import Select
import time
import os
NOMUS_URL = os.getenv("NOMUS_URL", "https://SUA-EMPRESA.nomus.com.br/SUA-EMPRESA")  # endereço do seu ERP Nomus
import pdfplumber
import re
import logging
import threading
import speech_recognition as sr
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, ElementNotInteractableException, ElementClickInterceptedException, NoSuchElementException
import time


# PySide6
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QLineEdit,
    QPushButton, QProgressBar, QDialog, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from webdriver_manager.chrome import ChromeDriverManager
# ---------------------------
# CONFIGURAÇÕES
# ---------------------------
recognizer = sr.Recognizer()
caminho_xml = os.getenv("PASTA_TRABALHO", "dados")
logging.basicConfig(
    filename=os.path.join(os.getenv("PASTA_TRABALHO", "dados"), "fiscal.log"),
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
options = Options()
options.add_experimental_option("prefs", {
    "download.default_directory": caminho_xml,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "profile.default_content_setting_values.automatic_downloads": 1,
    "profile.default_content_setting_values.popups": 0
})
options.add_argument("--disable-gpu")   
options.add_argument("--disable-software-rasterizer")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
service = Service(ChromeDriverManager().install())
chrome = webdriver.Chrome(service=service, options=options)
chrome.maximize_window()
chrome.get(NOMUS_URL)
wait1 = WebDriverWait(chrome, 120)
# ---------------------------
# INTERFACE PySide6
# ---------------------------
class VoiceWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dvicor - Aguardando Comando")
        self.setFixedSize(350, 150)
        self.setStyleSheet("background-color: #1e1e1e; color: #00ff88;")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        label = QLabel("🎤 Pode falar agora...")
        label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # modo indeterminado
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #00ff88;
                border-radius: 8px;
                background-color: #2c2c2c;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00ff88;
                width: 20px;
            }
        """)
        layout.addWidget(self.progress)
        self.setLayout(layout)

    def center_on_screen(self):
        geo = self.frameGeometry()
        screen = QApplication.primaryScreen().availableGeometry()
        geo.moveCenter(screen.center())
        self.move(geo.topLeft())

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login Dvicor")
        self.setFixedSize(300, 200)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Usuário")
        self.user_input.setStyleSheet("background-color: #2c2c2c; border: none; padding: 8px; color: white;")
        layout.addWidget(self.user_input)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Senha")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setStyleSheet("background-color: #2c2c2c; border: none; padding: 8px; color: white;")
        layout.addWidget(self.pass_input)

        self.btn = QPushButton("Entrar")
        self.btn.setStyleSheet("background-color: #00ff88; padding: 8px; border-radius: 5px;")
        self.btn.clicked.connect(self.accept)
        layout.addWidget(self.btn)

        self.setLayout(layout)

    def get_data(self):
        return self.user_input.text(), self.pass_input.text()
# ---------------------------
# FUNÇÕES
# ---------------------------
def _record_and_recognize(result_dict, timeout=5, phrase_time_limit=7):
    """
    Função que roda em background: escuta e reconhece.
    Coloca o resultado em result_dict como {'text': ..., 'error': ...}
    """
    try:
        audio = recognizer.listen(result_dict['source'], timeout=timeout, phrase_time_limit=phrase_time_limit)
    except sr.WaitTimeoutError:
        result_dict['error'] = 'timeout'
        return

    try:
        text = recognizer.recognize_google(audio, language="pt-BR")
        result_dict['text'] = text
    except sr.UnknownValueError:
        result_dict['error'] = 'unknown'
    except sr.RequestError as e:
        result_dict['error'] = f'request_error:{e}'

def solicitar_codigo():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Código de Autenticação")

    largura_janela = 400
    altura_janela = 200
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()
    pos_x = (largura_tela // 2) - (largura_janela // 2)
    pos_y = (altura_tela // 2) - (altura_janela // 2)
    root.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

    resultado_codigo = {}

    def confirmar_codigo(event=None):
        codigo = entrada_codigo.get()
        if codigo:
            print(f"Jarvis: Código de autenticação inserido: {codigo}")
            resultado_codigo["codigo"] = codigo
            root.destroy()
        else:
            aviso_label.configure(text="Por favor, preencha o campo do código.")

    titulo = ctk.CTkLabel(root, text="Digite o código de autenticação", font=("Segoe UI", 18, "bold"))
    titulo.pack(pady=(20, 10))

    entrada_codigo = ctk.CTkEntry(root, placeholder_text="Ex: 123456", width=250)
    entrada_codigo.pack(pady=10)
    entrada_codigo.bind("<Return>", confirmar_codigo)

    botao_confirmar = ctk.CTkButton(root, text="Confirmar", command=confirmar_codigo)
    botao_confirmar.pack(pady=10)

    aviso_label = ctk.CTkLabel(root, text="", font=("Segoe UI", 12), text_color="red")
    aviso_label.pack()

    root.mainloop()
    return resultado_codigo.get("codigo")

def validacao_login(chrome):
    try:
        #encontrar elemento cujo value seja "validarCodigoAutenticacao"
        validacao = wait1.until(EC.presence_of_element_located((By.XPATH, "//input[@value='validarCodigoAutenticacao']")))
        if validacao:
            print("Jarvis: Validação de login necessária.")

            codigo = solicitar_codigo()
            campo_codigo = chrome.find_element(By.NAME, "codigoEmail")
            campo_codigo.clear()
            campo_codigo.send_keys(codigo)
            chrome.find_element(By.NAME, "validarCodigoAutenticacao").click()
            time.sleep(1)
            print("Jarvis: Código de autenticação enviado.")

    except Exception as e:
        print(f"Jarvis: Erro na validação do login: {e}")


def login(app):
    wait = WebDriverWait(chrome, 5)

    while True:
        # Abre microfone e faz ajuste de ruído primeiro
        # with sr.Microphone() as source:
        #     print("🎤 Ajustando ruído ambiente... (aguarde)")
        #     recognizer.adjust_for_ambient_noise(source, duration=4.0)
        #     print("✅ Ajuste concluído. Preparando para ouvir...")

        #     # Agora que o ajuste terminou, mostramos a janela "Pode falar agora"
        #     vw = VoiceWindow()
        #     vw.center_on_screen()
        #     vw.show()
        #     app.processEvents()

        #     # Preparamos o dicionário compartilhado e a thread de gravação+reconhecimento
        #     result = {'text': None, 'error': None, 'source': source}
        #     t = threading.Thread(target=_record_and_recognize, args=(result,), daemon=True)
        #     t.start()

        #     # Enquanto a thread está ativa, mantemos a GUI responsiva
        #     while t.is_alive():
        #         app.processEvents()
        #         time.sleep(0.05)

        #     # Thread finalizada — fechamos a janela de voz
        #     try:
        #         vw.close()
        #         app.processEvents()
        #     except Exception:
        #         pass

        # # Ao sair do with, o microfone é liberado. Agora tratamos o resultado:
        # usuario = senha = None

        # if result.get('text'):
        #     voice = result['text']
        #     print(f"Você disse: {voice}")

        #     # Checagem de comando por palavra (ajuste branco/maiusc.)
        #     if voice.strip().lower() == "id 92":
        #         usuario, senha = os.getenv("NOMUS_USUARIO"), os.getenv("NOMUS_SENHA")
        #         print("✅ Dvicor: Identificação automática reconhecida.")
        #     else:
        #         # Tratamos como não reconhecido intencionalmente (padrão anterior)
        #         print("⚠️ Voz reconhecida, mas não corresponde ao comando esperado.")
        #         result['error'] = 'unknown'  # cairá no flow abaixo

        # # Se houver erro (timeout / unknown / request_error), oferecemos opções
        # if result.get('error'):
        #     # Mensagem com opções: Tentar novamente / Digitar manualmente / Cancelar
        #     msg = QMessageBox()
        #     msg.setWindowTitle("Reconhecimento de Voz")
        #     msg.setText("Não entendi o que você disse.")
        #     msg.setInformativeText("Deseja tentar novamente ou digitar manualmente?")
        #     msg.setStandardButtons(QMessageBox.Retry | QMessageBox.Ok | QMessageBox.Cancel)
        #     # custom text
        #     retry_btn = msg.button(QMessageBox.Retry)
        #     ok_btn = msg.button(QMessageBox.Ok)
        #     cancel_btn = msg.button(QMessageBox.Cancel)
        #     if retry_btn:
        #         retry_btn.setText("🔁 Tentar novamente")
        #     if ok_btn:
        #         ok_btn.setText("⌨️ Digitar manualmente")
        #     if cancel_btn:
        #         cancel_btn.setText("❌ Cancelar")

        #     escolha = msg.exec()

        #     if escolha == QMessageBox.Retry:
        #         # volta para o início do loop e tenta de novo com microfone
        #         continue
        #     elif escolha == QMessageBox.Ok:
        #         dialog = LoginDialog()
        #         if dialog.exec():
        #             usuario, senha = dialog.get_data()
        #         else:
        #             # se o usuário fechou o diálogo, tenta de novo
        #             continue
        #     else:
        #         # Cancelado
        #         print("Login cancelado pelo usuário.")
        #         return None
        usuario, senha = "login", "Senha"
        # Se temos usuário e senha, tentamos autenticar no site
        if usuario and senha:
            print(f"Dvicor: Tentando autenticar {usuario}...")

            campo_login = wait.until(EC.presence_of_element_located((By.ID, "campologin")))
            campo_login.clear()
            campo_login.send_keys(usuario)
            chrome.find_element(By.NAME, "senha").clear()
            chrome.find_element(By.NAME, "senha").send_keys(senha)
            chrome.find_element(By.NAME, "metodo").click()

            try:
                chrome.find_element(By.CLASS_NAME, "mensagem-erro-login")
                QMessageBox.warning(None, "Erro", "Usuário ou senha inválidos. Tente novamente.")
                print("❌ Erro detectado. Tentando novamente...")
            except:
                print("✅ Identificação válida. Avançando.")
                return usuario

def registrar_log(nota, af, usuario, status):
    mensagem = f"NF: {nota} | AF: {af} | Usuário: {usuario} | Status: {status}"
    logging.info(mensagem)
# ------------------- PDF -------------------
def apenas_numeros(valor):
    if valor:
        return ''.join(filter(str.isdigit, valor))
    return None

def pegar_pdf_mais_recente(caminho_xml):
    arquivos = [f for f in os.listdir(caminho_xml) if f.lower().endswith(".pdf")]
    if not arquivos:
        return None
    arquivos.sort(key=lambda x: os.path.getmtime(os.path.join(caminho_xml, x)), reverse=True)
    return os.path.join(caminho_xml, arquivos[0])

def extrair_cnpj_cpf_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        texto_completo = ""
        for pagina in pdf.pages:
            texto_completo += pagina.extract_text() + "\n"
    match = re.search(r"CNPJ/CPF:\s*([0-9./-]+)", texto_completo)
    if match:
        return match.group(1)
    return None

def pegar_cnpj_pdf_mais_recente(caminho_xml):
    pdf_mais_recente = pegar_pdf_mais_recente(caminho_xml)
    if pdf_mais_recente:
        return extrair_cnpj_cpf_pdf(pdf_mais_recente)
    return None
# ------------------- XML -------------------
def pegar_cnpj_emitente_xml(caminho_xml):
    arquivos = [f for f in os.listdir(caminho_xml) if f.endswith(".xml")]
    if not arquivos:
        return None
    arquivos.sort(key=lambda x: os.path.getmtime(os.path.join(caminho_xml, x)), reverse=True)
    xml_mais_recente = os.path.join(caminho_xml, arquivos[0])

    tree = ET.parse(xml_mais_recente)
    root = tree.getroot()
    ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

    cnpj_emitente = root.find('.//nfe:emit/nfe:CNPJ', ns)
    if cnpj_emitente is not None:
        return cnpj_emitente.text
    return None

def comparar_cnpjs(caminho_xml, chrome):
    cnpj_pdf = apenas_numeros(pegar_cnpj_pdf_mais_recente(caminho_xml))
    cnpj_xml = apenas_numeros(pegar_cnpj_emitente_xml(caminho_xml))


    if cnpj_pdf == cnpj_xml:
        print(f"✅ CNPJs batem! ({cnpj_pdf})")
    else:
        print(f"⚠️ CNPJs NÃO batem! PDF: {cnpj_pdf} | XML: {cnpj_xml}")

        chrome.get(NOMUS_URL + "/Pessoa.do?metodo=pesquisarPaginado&qtdeRegistrosPagina=10")
        campo_CNPJ = WebDriverWait(chrome, 10).until(
            EC.presence_of_element_located((By.ID, "cnpjPesquisa"))
        )
        campo_CNPJ.clear()
        campo_CNPJ.send_keys(cnpj_pdf)
        campo_CNPJ.send_keys(Keys.RETURN)

        # Espera a tabela carregar
        time.sleep(2)  # ou usar WebDriverWait mais avançado para linhas aparecerem

        div_tabela = chrome.find_element(By.ID, "div_tabelaPessoa")
        linhas = div_tabela.find_elements(By.XPATH, ".//table//tr[position()>1]")

        codigos = []
        for linha in linhas:
            try:
                codigo = linha.find_element(By.XPATH, ".//td[4]").text.strip()
                if codigo:
                    codigos.append(codigo)
            except Exception as e:
                print("Erro ao capturar código:", e)
                continue

        print("Códigos extraídos:", codigos)
        return codigos

def perguntar_codigo_janela(descricao_item):
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal
    codigo_match = simpledialog.askstring("Código do Item",
                                    f"Nenhum match forte para:\n{descricao_item}\nDigite o código correto:")
    root.destroy()
    return codigo_match

def pegar_xml_mais_recente(caminho_xml):
    """Retorna o caminho do XML mais recente na pasta informada."""
    if not os.path.isdir(caminho_xml):
        print("❌ Caminho informado não é uma pasta.")
        return None

    arquivos = [f for f in os.listdir(caminho_xml) if f.lower().endswith(".xml")]
    if not arquivos:
        print("❌ Nenhum XML encontrado.")
        return None

    arquivos.sort(key=lambda x: os.path.getmtime(os.path.join(caminho_xml, x)), reverse=True)
    return os.path.join(caminho_xml, arquivos[0])

def contar_itens_xml(pasta_downloads):
    arquivos = [f for f in os.listdir(pasta_downloads) if f.endswith(".xml")]
    arquivos.sort(key=lambda x: os.path.getmtime(os.path.join(pasta_downloads, x)), reverse=True)
    xml_mais_recente = os.path.join(pasta_downloads, arquivos[0])

    tree = ET.parse(xml_mais_recente)
    root = tree.getroot()

    # Namespace padrão da NF-e
    ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

    # Conta os itens da nota (cada <det> é um item)
    itens = root.findall('.//nfe:det', ns)
    print(f"📄 Dvicor: XML contém {len(itens)} item(ns).")
    return len(itens)
    
def extrair_descricoes_xml(caminho_xml):
    tree = ET.parse(caminho_xml)
    root = tree.getroot()
    ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

    descricoes = []

    for det in root.findall('.//nfe:det', ns):
        prod = det.find('.//nfe:prod', ns)
        if prod is not None:
            descricao = prod.find('nfe:xProd', ns)
            quantidade = prod.find('nfe:qCom', ns)
            valor_unitario = prod.find('nfe:vUnCom', ns)

            # Formatação com limite de 6 casas decimais
            try:
                quantidade_formatada = f"{float(quantidade.text):.6f}" if quantidade is not None else "0.000000"
            except ValueError:
                quantidade_formatada = "0.000000"

            try:
                valor_formatado = f"{float(valor_unitario.text):.6f}" if valor_unitario is not None else "0.000000"
            except ValueError:
                valor_formatado = "0.000000"

            descricoes.append({
                "descricao": descricao.text.strip() if descricao is not None else "",
                "quantidade": quantidade_formatada,
                "valor_unitario": valor_formatado
            })

    return descricoes

def capturar_descricoes_e_codigos_af(chrome):
    linhas = chrome.find_elements(By.XPATH, "//table//tr[td[13]]")
    lista_af = []

    for linha in linhas:
        try:
            desc = linha.find_element(By.XPATH, ".//td[5]").text.strip()
            cod = linha.find_element(By.XPATH, ".//td[4]").text.strip()

            # Captura do atributo value com tratamento caso o input não exista
            try:
                qtd_elem = linha.find_element(By.XPATH, ".//td[6]//input")
                qtd = qtd_elem.get_attribute("value")
            except NoSuchElementException:
                qtd = "0.000000"

            try:
                preco_elem = linha.find_element(By.XPATH, ".//td[8]//input")
                preco_unit = preco_elem.get_attribute("value")
            except NoSuchElementException:
                preco_unit = "0.000000"

            # Substitui vírgula por ponto e formata
            try:
                qtd_formatada = f"{float(qtd.replace(',', '.')):.6f}"
            except ValueError:
                qtd_formatada = "0.000000"

            try:
                preco_formatado = f"{float(preco_unit.replace(',', '.')):.6f}"
            except ValueError:
                preco_formatado = "0.000000"

            print(f"Debug - Desc: {desc}, Cod: {cod}, Qtd Value: {qtd_formatada}, Preço Value: {preco_formatado}")

            if desc and cod and desc != "Descrição do produto":
                lista_af.append({
                    "descricao_af": desc,
                    "codigo_produto": cod,
                    "quantidade": qtd_formatada,
                    "preco_unitario": preco_formatado
                })

        except Exception as e:
            print(f"❌ Erro ao capturar linha: {e}")
            continue

    for item in lista_af:
        print(f"🔍 AF: {item['descricao_af']} | Código: {item['codigo_produto']} | "
              f"Qtd: {item['quantidade']} | Preço: {item['preco_unitario']}")

    return lista_af

def reconciliar_xml_com_af(xml_descricoes, lista_af):
    correspondencias = []
    af_descricoes = [item["descricao_af"] for item in lista_af]

    for i, item_xml in enumerate(xml_descricoes, start=1):
        desc_xml = item_xml["descricao"]

        melhor_match, score, idx = process.extractOne(
            desc_xml,
            af_descricoes,
            scorer=fuzz.token_sort_ratio
        )

        af_item = lista_af[idx]

        correspondencias.append({
            "item_xml": i,
            "descricao_xml": desc_xml,
            "quantidade_xml": item_xml["quantidade"],
            "valor_unitario_xml": item_xml["valor_unitario"],

            "descricao_af": melhor_match,
            "codigo_produto": af_item["codigo_produto"],
            "quantidade_af": af_item["quantidade"],
            "valor_unitario_af": af_item["preco_unitario"],

            "score": score
        })
    return correspondencias

def validar_quantidades_valores(correspondencias):
    for item in correspondencias:
        desc_xml = item["descricao_xml"]
        qtd_xml = item["quantidade_xml"]
        qtd_af = item["quantidade_af"]
        val_xml = item["valor_unitario_xml"]
        val_af = item["valor_unitario_af"]

        print(f"🔗 Item {item['item_xml']} - {desc_xml}")

        if val_xml != val_af:
            print(f"   ❌ Divergência encontrada -> XML: (Qtd={qtd_xml}, Valor={val_xml}) | AF: (Qtd={qtd_af}, Valor={val_af})")
            
            # clicar no span da descrição
            xpath = f"//span[contains(normalize-space(.), '{desc_xml}')]"
            span_desc = WebDriverWait(chrome, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", span_desc)
            span_desc.click()
            time.sleep(0.5)

            # abrir edição
            edit_item = WebDriverWait(chrome, 10).until(
                EC.element_to_be_clickable((By.ID, "itemDocumentoEntrada_itemSubMenu_selecionarItemDocumentoEntrada"))
            )
            edit_item.click()

            # atualizar quantidade
            campo_qtd = WebDriverWait(chrome, 10).until(
                EC.element_to_be_clickable((By.ID, "id_qtdeInformada"))
            )
            campo_qtd.clear()

            # tratar quantidade: se decimal = 0, envia inteiro
            try:
                qtd_float = float(qtd_af.replace(',', '.'))
                if qtd_float.is_integer():
                    qtd_final = str(int(qtd_float))
                else:
                    qtd_final = str(qtd_float)
            except ValueError:
                qtd_final = qtd_af  # fallback caso não consiga converter

            campo_qtd.send_keys(qtd_final)

            # atualizar valor
            campo_valor = WebDriverWait(chrome, 10).until(
                EC.element_to_be_clickable((By.ID, "id_precoUnitario"))
            )
            campo_valor.clear()
            campo_valor.send_keys(val_af)


            # selecionar origem
            origem = Select(chrome.find_element(By.ID, "id_origICMS"))
            origem.select_by_visible_text("0 - Nacional (exceto as indicadas nos códigos de 3 a 5)")

            time.sleep(0.5)

            # salvar
            save_item = WebDriverWait(chrome, 10).until(
                EC.element_to_be_clickable((By.ID, "botao_salvaritemdocumentoentrada"))
            )
            chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_item)
            save_item.click()

        else:
            print(f"   ✅ Quantidade e valor batem! (Qtd={qtd_xml}, Valor={val_xml})")

        print("-" * 50)

def registrar_nf_processada(nota):
    with open("log_nf.txt", "a") as log:
        log.write(f"{nota}\n")

def nota_ja_processada(nota):
    if not os.path.exists("log_nf.txt"):
        return False
    with open("log_nf.txt", "r") as log:
        notas = log.read().splitlines()
    return str(nota) in notas

def pesquisar_nota_fiscal(chrome, nota):
    # Preenche o campo de pesquisa
    pesquisa_nota = WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.NAME, "numeroPesquisa")))
    pesquisa_nota.clear()
    pesquisa_nota.send_keys(str(nota))
    qntdregistro = chrome.find_element(By.NAME, "qtdeRegistrosPagina")
    qntdregistro.clear()
    qntdregistro.send_keys("100")

    # Clica no botão "Pesquisar"
    botoes = chrome.find_elements(By.ID, "botao_pesquisarpaginado")
    botao_pesquisa_destinadas = next((btn for btn in botoes if btn.get_attribute("value") == "Pesquisar"), None)

    if botao_pesquisa_destinadas:
        botao_pesquisa_destinadas.click()
        print(f"🔍 Dvicor: Pesquisando nota {nota}...")
    else:
        print(f"⚠️ Dvicor: Botão 'Pesquisar' não encontrado para nota {nota}.")

def clicar_nota_fiscal(chrome, nota):
    xpath = f"//span[normalize-space(text())='{nota}']"
    span_nf = WebDriverWait(chrome, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", span_nf)
    span_nf.click()
    time.sleep(0.5)  # Aguarda carregamento da página

def atualizar_tipos_movimentacao_setores_estoque(chrome):
    try:
        funcoes_especiais = chrome.find_element(By.ID, "botao_Funcoes_especiais")
        chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", funcoes_especiais)
        funcoes_especiais.click()  # Clica no botão funcoes especiais
        chrome.find_element(By.ID, "botao_atualizar_tipos_movimentacao_setores_estoque_itens_documento").click()  # Clica no botão atualizar
    except Exception as e:
        print(f"⚠️ Dvicor: Erro ao atualizar tipos de movimentação e setores de estoque: {e}")
 
def save_doc_entrada(chrome):
    try:
        savedocentrada = chrome.find_element(By.ID, "botao_salvar")
        chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", savedocentrada)
        savedocentrada.click()
        print("✅ Dvicor: Documento de entrada salvo com sucesso.")
    except Exception as e:
        print(f"⚠️ Dvicor: Erro ao salvar documento de entrada: {e}")
        registrar_log("N/A", "N/A", usuario_logado, f"Erro ao salvar documento de entrada - {str(e)}")
         
def remocao_vinculo(chrome):
    try:
        # Marca a primeira checkbox e remove vínculo
        primeira_checkbox = WebDriverWait(chrome, 5).until(EC.element_to_be_clickable((By.ID, "idMarcarItensDocumentoEntrada")))
        chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", primeira_checkbox)
        primeira_checkbox.click()
        print("☑️ Dvicor: Primeira checkbox marcada com sucesso.")
        acoes = chrome.find_element(By.ID, "botao_Acoes")
        acoes.click()
        removevinculo = chrome.find_element(By.ID, "botao_remover_vinculo_com_pedido_compra")
        removevinculo.click()
        print("🧹 Dvicor: Vínculo removido. Você pode tentar novamente.")

    except Exception as e:
        print(f"❌ Dvicor: Erro ao remover vínculo: {e}")
        return
    time.sleep(0.7)  # Aguarda carregamento
    atualizar_tipos_movimentacao_setores_estoque(chrome)

def vincular_itens(chrome, AF, mapa_codigos_por_item, xml_descricoes):
    itens_processados = set()

    # === Passo 1: descobrir índice da coluna "Itens de pedido de compra" ===
    colunas = chrome.find_elements(By.XPATH, "//table[@id='tabela_itemDocumentoEntrada']//thead//th")
    indice_coluna = None
    for idx, th in enumerate(colunas, start=1):
        if th.get_attribute("title") == "Itens de pedido de compra":
            indice_coluna = idx
            break
    if indice_coluna is None:
        print("⛔ Coluna 'Itens de pedido de compra' não encontrada!")
        return False

    print("🟢 Iniciando vínculo de itens...")

    while True:
        linhas = chrome.find_elements(By.XPATH, "//table[@id='tabela_itemDocumentoEntrada']//tr[td]")
        if not linhas or all(l.find_element(By.XPATH, ".//td[5]").text.strip() in itens_processados for l in linhas[:-1]):
            print("✅ Todos os itens foram processados.")
            break

        for i in range(len(linhas) - 1):  # ignora última linha (total)
            try:
                linhas = chrome.find_elements(By.XPATH, "//table[@id='tabela_itemDocumentoEntrada']//tr[td]")
                linha = linhas[i]
                descricao_td = linha.find_element(By.XPATH, ".//td[5]").text.strip()

                if descricao_td in itens_processados:
                    continue
                itens_processados.add(descricao_td)

                # === Botão de vincular ===
                time.sleep(0.5)
                td_botao = linha.find_element(By.XPATH, f"./td[{indice_coluna}]")
                botoes = td_botao.find_elements(By.XPATH, ".//i[contains(@class, 'fa-plus')]")
                botoes_clicaveis = [b for b in botoes if b.is_displayed() and b.is_enabled()]
                if not botoes_clicaveis:
                    print(f"⚠️ Nenhum botão clicável para linha: {descricao_td}")
                    continue

                botao = botoes_clicaveis[0]
                chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao)
                WebDriverWait(chrome, 5).until(EC.element_to_be_clickable(botao))
                try:
                    botao.click()
                except (StaleElementReferenceException, ElementNotInteractableException):
                    time.sleep(0.5)
                    linha = chrome.find_elements(By.XPATH, "//table[@id='tabela_itemDocumentoEntrada']//tr[td]")[i]
                    td_botao = linha.find_element(By.XPATH, f"./td[{indice_coluna}]")
                    botao = td_botao.find_element(By.XPATH, ".//i[contains(@class, 'fa-plus')]")
                    chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao)
                    botao.click()
                print("🖱️ Botão 'Vincular' clicado.")

                # === Campo de pedido ===
                campo_pedido = WebDriverWait(chrome, 10).until(
                    EC.element_to_be_clickable((By.ID, "nomeItemPedidoCompra"))
                )
                print("⌨️ Campo de pedido encontrado.")

                # === Código do produto via mapa ou RapidFuzz ===
                codigo_produto = mapa_codigos_por_item.get(descricao_td)
                if codigo_produto:
                    print(f"🔍 Código já mapeado para '{descricao_td}': {codigo_produto}")
                else:
                    melhor_score = 0
                    melhor_item = None
                    descricao_td_str = str(descricao_td)
                    print(f"🔍 Buscando melhor match para: {descricao_td_str}")

                    for item_xml in xml_descricoes:
                        descricao_xml_str = str(item_xml['descricao'])
                        try:
                            score = fuzz.token_sort_ratio(descricao_td_str, descricao_xml_str)
                        except Exception as e:
                            print(f"⚠️ Erro ao calcular score: {e}")
                            score = 0

                        print(f"   ➡️ Comparando '{descricao_td_str}' com '{descricao_xml_str}' | Score: {score}")
                        if score > melhor_score:
                            melhor_score = score
                            melhor_item = descricao_xml_str
                            print(f"   ➡️ Novo melhor match: '{melhor_item}' | Score: {melhor_score}")

                    if melhor_score >= 56:
                        codigo_produto = mapa_codigos_por_item.get(melhor_item)
                        print(f"🔍 Match: '{melhor_item}' | Score: {melhor_score} | Código: {codigo_produto}")
                    else:
                        print(f"⚠️ Nenhum match forte para linha: {descricao_td}")
                        codigo_produto = perguntar_codigo_janela(descricao_td)

                # Garante que o campo esteja visível e com foco
                chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", campo_pedido)
                chrome.execute_script("arguments[0].focus();", campo_pedido)

                try:
                    campo_pedido.clear()
                except Exception:
                    # fallback: selecionar tudo e apagar
                    campo_pedido.send_keys(Keys.CONTROL + "a")
                    campo_pedido.send_keys(Keys.DELETE)

                print(f"⌨️ Limpando campo de pedido.")
                campo_pedido.send_keys(f"{AF}")
                print(f"⌨️ Digitando AF: {AF}")

                # === Selecionar sugestão correta ===
                WebDriverWait(chrome, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "ui-menu-item-wrapper"))
                )
                sugestoes = chrome.find_elements(By.CLASS_NAME, "ui-menu-item-wrapper")
                time.sleep(0.5)

                sugestao_encontrada = next((s for s in sugestoes if codigo_produto in s.text.strip()), None)
                if sugestao_encontrada:
                    time.sleep(0.5)
                    sugestao_encontrada.click()
                    print(f"✅ Sugestão com código '{codigo_produto}' selecionada.")
                else:
                    print(f"⚠️ Nenhuma sugestão com código '{codigo_produto}' encontrada.")
                    chrome.find_element(By.ID, "cancelar").click()
                    continue

                # === Confirmar vínculo ===
                WebDriverWait(chrome, 5).until(
                    EC.element_to_be_clickable((By.ID, "salvarVinculoItemPedidoCompra"))
                ).click()
                print(f"✅ Item '{descricao_td}' vinculado com sucesso.")
                time.sleep(0.7)

            except Exception as e:
                print(f"❌ Erro ao processar linha '{descricao_td}': {e}")
                continue

    # === Pós-processamento ===
    marcar_checkboxes(chrome)
    atualizar_tipos_movimentacao_setores_estoque(chrome)
    return True

def marcar_checkboxes(chrome):
    # Seleciona todas as checkboxes cujo id COMEÇA com "checkbox_hashEncerraItem_"
    checkboxes = chrome.find_elements(
        By.XPATH,
        "//input[starts-with(@id, 'checkbox_hashEncerraItem_') and @type='checkbox']"
    )

    if not checkboxes:
        print("⚠️ Nenhuma checkbox encontrada.")
        return

    for cb in checkboxes:
        try:
            if not cb.is_selected():
                # Scroll até a checkbox
                chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", cb)
                
                # Espera até estar clicável
                WebDriverWait(chrome, 5).until(EC.element_to_be_clickable(cb))
                
                # Tenta clicar normalmente, senão via JS
                try:
                    cb.click()
                except ElementClickInterceptedException:
                    chrome.execute_script("arguments[0].click();", cb)
                
                print(f"✅ Checkbox '{cb.get_attribute('id')}' marcada.")
        except Exception as e:
            print(f"❌ Erro ao marcar checkbox '{cb.get_attribute('id')}': {e}")
# ---------------------------
# MAIN
# ---------------------------
if __name__ == "__main__":
    app = QApplication([])

    usuario_logado = login(app)
    print("Usuário logado:", usuario_logado)
    validacao_login(chrome)

    time.sleep(15)
    # Exemplo: relatório
    relatorio = os.path.join(os.getenv("PASTA_TRABALHO", "dados"), "RELATORIO DE NFS.xlsx")
    if os.path.exists(relatorio):
        df = pd.read_excel(relatorio, usecols=[0, 1])
        df_filtrado = df[df.iloc[:, 1].apply(lambda x: isinstance(x, (int, float)))]
    else:
        print("Relatório não encontrado:", relatorio)


    
    
    
    for linha in df_filtrado.itertuples(index=False):

        nota = linha[0]

        if nota_ja_processada(nota):
            repetir = messagebox.askyesno("Dvicor", f"Já processamos a nota {nota}. Deseja continuar? Alta probabilidade de erro ao continuar.")
            if not repetir:
                print(f"⏭️ Dvicor: Pulando a nota {nota} conforme escolha do usuário.")
                continue

        inicio = time.time()  # Marca o início do processamento
        #BAIXANDO O XML
        
        chrome.get(NOMUS_URL + "/NfeDestinadaImportada.do?metodo=pesquisarPaginado")
        time.sleep(0.5)  # Aguarda carregamento da página
        pesquisa_nota = chrome.find_element(By.NAME, "numeroPesquisa") #procurando campo pesquisa nota
        nota = linha[0]  # Número da nota fiscal    
        try:
            pesquisar_nota_fiscal(chrome, nota)
            time.sleep(0.7)  # Aguarda carregamento da página
            try:
                bolinha = WebDriverWait(chrome, 5).until(EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'protip')]")))
                status = bolinha.get_attribute("data-pt-title")
                print(f"🟢 Dvicor: Status da NF-e identificado: {status}")
                if status == "NF-e não manifestada":
                    print("📌 A nota ainda não foi manifestada.")
                elif status == "NF-e manifestada. XML importado. Documento de entrada gerado.":
                    messagebox.showinfo("Dvicor", "🟢 A nota já foi totalmente processada.")
                    continue  # pula para a próxima nota
                elif status == "NF-e manifestada. XML importado.":
                    messagebox.showinfo("Dvicor", f"🔵 A Nota Fiscal {nota} já foi manifestada. Faça manualmente para evitar erro!")
                    print(f"ℹ️ Dvicor: Nota {nota} já estava manifestada.")
                    continue
                else:
                    print("⚠️ Status da NF-e não reconhecido.")
            except Exception as e:
                print(f"❌ Erro ao identificar o status da NF-e: {e}")
            clicar_nota_fiscal(chrome, nota)
            # Importa XML se possível
            try:
                WebDriverWait(chrome, 0.5).until(EC.element_to_be_clickable((By.ID, "submenu_destinada_itemSubMenu_importarXmlNfeDestinadaImportada"))).click()
                print(f"📥 Dvicor: Botão 'Importar XML' clicado com sucesso.")
                clicar_nota_fiscal(chrome, nota)
            except Exception as e:
                outrobotao = chrome.find_element(By.ID, "submenu_destinada_resumida_itemSubMenu_importarXmlNfeDestinadaImportada")
                outrobotao.click() 
                clicar_nota_fiscal(chrome, nota)
        # Aguarda o botão "Exibir XML" estar clicável
        except Exception as e:
            print(f"⚠️ Dvicor: Erro: {e}")
        verxml = WebDriverWait(chrome, 10).until(EC.element_to_be_clickable((By.ID, "submenu_destinada_xml_ok_itemSubMenu_exibirXmlNfeDestinadaImportada")))
        verxml.click()
        time.sleep(1)
        

        #ACESSANDO PEDIDO DE COMPRA
        chrome.get(NOMUS_URL + "/PedidoCompra.do?metodo=pesquisar")
        
        af_valor = linha[1]  # Segunda coluna do DataFrame
        # Verifica se está vazio ou NaN
        if pd.isna(af_valor):
            af_str = simpledialog.askstring("Dvicor", f"A nota {linha[0]} não possui número de AF. Informe manualmente:")
            AF = int(af_str)
        else:
            AF = int(af_valor)

        # Agora usa o valor de AF para pesquisar
        campo_pesquisa = chrome.find_element(By.NAME, "nomePesquisa")
        campo_pesquisa.clear()
        campo_pesquisa.send_keys(str(AF))
        campo_pesquisa.send_keys(Keys.RETURN)
        time.sleep(0.5)
        Ids = str(AF)   
        try:
            xpath_af = f"//span[contains(text(), '{Ids}') and substring(text(), string-length(text()) - string-length('{Ids}') + 1) = '{Ids}']"
            span_af = WebDriverWait(chrome, 10).until(EC.element_to_be_clickable((By.XPATH, xpath_af)))
            chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", span_af)
            span_af.click()
            baixarpdf = chrome.find_element(By.ID, "pedidoCompra_itemSubMenu_gerarPdfPedidoCompra")
            baixarpdf.click()
            time.sleep(1)  # Aguarda o download iniciar
            span_af.click()
            print(f"🖱️ Dvicor: AF {AF} localizada e clicada com sucesso.")
        except Exception as e:
            print(f"❌ Dvicor: Não foi possível localizar a AF {AF} na tela: {e}")
            registrar_log(nota, AF, usuario_logado, f"Erro - {str(e)}")

        chrome.find_element(By.ID, "pedidoCompra_itemSubMenu_editarPedidoCompra").click()  # Clica no botão de edição


        tipo_movimentacao_element = WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.ID, "id_idTipoMovimentacao")))
        tipo_movimentacao_select = Select(tipo_movimentacao_element)
        tipo_movimentacao_texto = tipo_movimentacao_select.first_selected_option.text.strip()
        print(f"📌 Dvicor: Tipo de movimentação lido da AF → {tipo_movimentacao_texto}")





        # Caminho do XML baixado

        arquivos = [f for f in os.listdir(caminho_xml) if f.endswith(".xml")]
        arquivos.sort(key=lambda x: os.path.getmtime(os.path.join(caminho_xml, x)), reverse=True)
        xml_mais_recente = os.path.join(caminho_xml, arquivos[0])
        # Extrai descrições do XML
        xml_descricoes = extrair_descricoes_xml(xml_mais_recente)
        # Captura descrições e códigos da AF
        lista_af = capturar_descricoes_e_codigos_af(chrome)
        # Faz a reconciliação
        resultado = reconciliar_xml_com_af(xml_descricoes, lista_af)
        print("📌 Dvicor: Códigos mais parecidos encontrados:")
        for item in resultado:
            print(f"🔗 Item {item['item_xml']}: Código mais parecido → {item['codigo_produto']} (Score: {item['score']})")

        # Exibe os resultados
        for item in resultado:
            print(f"🔗 Item {item['item_xml']}:")
            print(f"    XML: {item['descricao_xml']}")
            print(f"    AF : {item['descricao_af']}")
            print(f"    Código do produto: {item['codigo_produto']}")
            print(f"    Score: {item['score']}\n")
        mapa_codigos_por_item = {item["descricao_xml"]: item["codigo_produto"] for item in resultado}
        # Salva log da reconciliação
        caminho_log = os.path.join(os.getenv("PASTA_TRABALHO", "dados"), "log_reconciliacao_codigos.txt")

        with open(caminho_log, "a", encoding="utf-8") as log:
            log.write(f"\n--- Reconciliando nota {nota} com AF {AF} ---\n")
            for item in resultado:
                log.write(
                    f"Item {item['item_xml']} | XML: {item['descricao_xml']} | "
                    f"AF: {item['descricao_af']} | Código: {item['codigo_produto']} | Score: {item['score']}\n"
                )



        WebDriverWait(chrome, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//table//tr")))


        liberados = chrome.find_elements(By.XPATH, "//span[normalize-space(text())='Liberado']")   
        quantidade_liberados = len(liberados)
        itens_xml = contar_itens_xml(caminho_xml)  # ajuste o caminho

        print(f"📦 Dvicor: Pedido de compra tem {quantidade_liberados} item(ns) liberado(s).")
        if itens_xml != quantidade_liberados:
            desejacont = messagebox.askyesno("Dvicor", "A quantidade de itens liberados não confere com o XML baixado. Deseja continuar mesmo assim?")
            if not desejacont:
                messagebox.showinfo("Dvicor", "Processo cancelado. Verifique os itens manualmente.")
                continue


        cancelar = chrome.find_element(By.ID, "botao_pesquisarpaginado")
        chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", cancelar)
        cancelar.click()
        time.sleep(1)  # Aguarda carregamento da página

        codigos = comparar_cnpjs(caminho_xml, chrome)


        # #ACESSANDO NOTAS FISCAIS DESTINADAS
        chrome.get(NOMUS_URL + "/NfeDestinadaImportada.do?metodo=pesquisarPaginado")
    
        try:       
            clicar_nota_fiscal(chrome, nota)  # Chama a função para clicar na nota fiscal

            # Manifesta a operação
            manifestarxml = WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.ID, "submenu_destinada_xml_ok_itemSubMenu_manifestarOperacaoSubmenuNfeDestinadaImportada")))
            manifestarxml.click()
            time.sleep(0.5)  # Aguarda o carregamento da página
            manifestacao = chrome.find_element(By.ID, "manifestacao_id")
            selectmanifestacao = Select(manifestacao)
            selectmanifestacao.select_by_visible_text("Confirmação da Operação")
            time.sleep(0.5)  # Aguarda o carregamento da página
            savemanifestar = chrome.find_element(By.ID, "botao_salvarmanifestacaooperacao")
            savemanifestar.click()
            time.sleep(1)  # Aguarda o carregamento da página


            bolinha = WebDriverWait(chrome, 5).until(EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'protip')]")))
            status = bolinha.get_attribute("data-pt-title")
            print(f"🟢 Dvicor: Status da NF-e identificado: {status}")
            if status == "NF-e não manifestada":
                print("📌 A nota ainda não foi manifestada.")
                messagebox.showinfo("Dvicor", f"🚨 Atenção: A nota {nota} não retornou resultado. Verifique manualmente.")
                continue
            elif status == "NF-e manifestada. XML importado.":
                print(f"ℹ️ Dvicor: Nota {nota} manifestada com sucesso.")


            # Marca o checkbox da nota
            xpath_span = f"//span[normalize-space(text())='{nota}']"
            span_nota = WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.XPATH, xpath_span)))
            checkbox_xpath = f"{xpath_span}/ancestor::tr[1]//input[@type='checkbox']"
            checkbox = WebDriverWait(chrome, 10).until(EC.element_to_be_clickable((By.XPATH, checkbox_xpath)))
            chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
            checkbox.click()
            print(f"☑️ Dvicor: Checkbox da nota {nota} marcada com sucesso.")
            gerardocentrada = chrome.find_element(By.ID, "botao_gerardocumentos")
            chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", gerardocentrada)
            gerardocentrada.click()
            bolinha = WebDriverWait(chrome, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-pt-title="NF-e manifestada. XML importado. Documento de entrada gerado."]')))
            print("🟢 Dvicor: Documento de entrada gerado com sucesso.")
            if not bolinha:
                messagebox.showinfo("Dvicor", "Documento de entrada não gerado. Verifique se o processo foi concluído corretamente. Pulando para próxima nota.")
                continue                
        except Exception as e:
            print(f"⚠️ Dvicor: Erro ao processar a nota {nota}: {e}")
            registrar_log(nota, AF, usuario_logado, f"Erro - {str(e)}")
            messagebox.showinfo("Dvicor", f"Erro ao processar a nota {nota}: {e}")
            continue

        time.sleep(1)

        chrome.get(NOMUS_URL + "/DocumentoEntrada.do?metodo=pesquisarPaginado&qtdeRegistrosPagina=10")
        clicar_nota_fiscal(chrome, nota)  # Chama a função para clicar na nota fiscal
        editar_nf = chrome.find_element(By.ID, "documentoEntradaFornecedor_itemSubMenu_selecionarDocumentoEntrada")
        editar_nf.click()
        if codigos:
            codigo_fornecedor = codigos[0]
            campo_fornecedor = chrome.find_element(By.ID, "id_nomeParceiro")
            campo_fornecedor.clear()
            campo_fornecedor.send_keys(codigo_fornecedor)
            time.sleep(0.7)  # Aguarda sugestões aparecerem
            campo_fornecedor.send_keys(Keys.RETURN)
        remocao_vinculo(chrome)

        time.sleep(0.7)
        # Abre a aba de pagamento
        try:
            abapag = WebDriverWait(chrome, 10).until(
                EC.presence_of_element_located((By.ID, "ui-id-15"))
            )
            chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", abapag)
            abapag.click()
            print("✅ Aba de pagamento aberta com sucesso.")
        except StaleElementReferenceException:
            # tenta de novo se o elemento foi recarregado
            abapag = WebDriverWait(chrome, 10).until(
                EC.presence_of_element_located((By.ID, "ui-id-15"))
            )
            chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", abapag)
            abapag.click()
            print("🔄 Aba de pagamento recarregada e aberta com sucesso.")

        # === Condição de pagamento ===
        condpag = WebDriverWait(chrome, 10).until(
            EC.element_to_be_clickable((By.ID, "id_idCondicaoPagamento"))
        )
        Select(condpag).select_by_visible_text("PIX")
        time.sleep(0.5)  # Pequena pausa para garantir que a seleção foi aplicada

        formpag = WebDriverWait(chrome, 10).until(
            EC.element_to_be_clickable((By.ID, "id_idFormaPagamento"))
        )
        Select(formpag).select_by_visible_text("Pix")
        print("✅ Forma de pagamento 'Pix' selecionada com sucesso.")


        # === Prazo ===
        campo_prazo = WebDriverWait(chrome, 10).until(
            EC.element_to_be_clickable((By.ID, "id_regraGerarParcelas"))
        )
        campo_prazo.clear()
        campo_prazo.send_keys("0")

        # === Botão gerar parcelas ===
        btngerarparcelas = WebDriverWait(chrome, 10).until(
            EC.element_to_be_clickable((By.ID, "botao_gerar_parcelas"))
        )
        chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", btngerarparcelas)
        btngerarparcelas.click()
        print("✅ Parcelas geradas.")

        time.sleep(0.5)
        save_doc_entrada(chrome)
        clicar_nota_fiscal(chrome, nota)  # Chama a função para clicar na nota fiscal
        editar_nf = chrome.find_element(By.ID, "documentoEntradaFornecedor_itemSubMenu_selecionarDocumentoEntrada")
        editar_nf.click()
        
        
        try:
            select_element = WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.ID, "id_idTipoMovimentacao")))
            select = Select(select_element)
            select.select_by_visible_text(tipo_movimentacao_texto)
            print(f"✅ Dvicor: Tipo de movimentação '{tipo_movimentacao_texto}' selecionado automaticamente.")
        except Exception as e:
            print(f"⚠️ Dvicor: Erro ao aplicar tipo de movimentação no doc de entrada: {e}")
            registrar_log(nota, AF, usuario_logado, f"Erro - {str(e)}")
        time.sleep(0.5)
        if tipo_movimentacao_texto == "Compra de mercadorias para industrialização":
            try:
                select_element = WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.ID, "id_idSetorEntrada")))
                select = Select(select_element)
                setor_alvo = "Almoxarifado"

                setor_atual = select.first_selected_option.text.strip()
                if setor_atual != setor_alvo:
                    select.select_by_visible_text(setor_alvo)
                else:
                    print(f"✅ Dvicor: Setor já está como '{setor_alvo}'.")
            except Exception as e:
                print(f"⚠️ Dvicor: Erro ao verificar/selecionar setor: {e}")
                registrar_log(nota, AF, usuario_logado, f"Erro - {str(e)}")
        time.sleep(0.5)
        if tipo_movimentacao_texto == "Compra de material de uso e consumo":
            try:
                select_element = WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.ID, "id_idSetorEntrada")))
                select = Select(select_element)
                setor_alvo = "Almoxarifado"

                setor_atual = select.first_selected_option.text.strip()
                if setor_atual != setor_alvo:
                    select.select_by_visible_text(setor_alvo)
                else:
                    print(f"✅ Dvicor: Setor já está como '{setor_alvo}'.")
            except Exception as e:
                print(f"⚠️ Dvicor: Erro ao verificar/selecionar setor: {e}")
                registrar_log(nota, AF, usuario_logado, f"Erro - {str(e)}")

        # Aguarda o campo <select> aparecer
        statusdoc = WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.NAME, "statusDocumentoEntrada")))
        # Cria o objeto Select e seleciona pelo texto visível
        select_status = Select(statusdoc)
        select_status.select_by_visible_text("Concluído")
        print("✅ Dvicor: Status 'Concluído' selecionado com sucesso.")
        validar_quantidades_valores(resultado)
        time.sleep(0.5)
        vincular_itens(chrome, AF, mapa_codigos_por_item, xml_descricoes)
        time.sleep(0.5)
        try:
            abapag = WebDriverWait(chrome, 10).until(
                EC.presence_of_element_located((By.ID, "ui-id-15"))
            )
            chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", abapag)
            abapag.click()
            print("✅ Aba de pagamento aberta com sucesso.")
        except StaleElementReferenceException:
            # tenta de novo se o elemento foi recarregado
            abapag = WebDriverWait(chrome, 10).until(
                EC.presence_of_element_located((By.ID, "ui-id-15"))
            )
            chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", abapag)
            abapag.click()
            print("🔄 Aba de pagamento recarregada e aberta com sucesso.")

        condpag = WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.ID, "id_idCondicaoPagamento")))
        selectcondpag = Select(condpag)
        selectcondpag.select_by_visible_text("PIX")
        formpag = WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.ID, "id_idFormaPagamento")))
        time.sleep(0.5)  # Pequena pausa para garantir que a seleção foi aplicada
        selectformpag = Select(formpag)
        selectformpag.select_by_visible_text("Pix")
        campo_prazo = chrome.find_element(By.ID, "id_regraGerarParcelas")
        campo_prazo.clear()
        campo_prazo.send_keys("0")
        btngerarparcelas = chrome.find_element(By.ID, "botao_gerar_parcelas")
        chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", btngerarparcelas)
        btngerarparcelas.click()
        time.sleep(0.5)
        save_doc_entrada(chrome)
        time.sleep(0.5)
        fim = time.time()  # Marca o fim do processamento
        duracao = fim - inicio
        print(f"⏱️ Dvicor: Processamento da nota {nota} concluído em {duracao:.2f} segundos.")
        
        
        
        
        
        


    app.exec()