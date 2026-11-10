import os
NOMUS_URL = os.getenv("NOMUS_URL", "https://SUA-EMPRESA.nomus.com.br/SUA-EMPRESA")  # endereço do seu ERP Nomus
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import customtkinter as ctk
from PySide6.QtGui import QFont, QColor, QPalette
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from math import cos, sin, radians


# Configurações do navegador
options = Options()
options.add_argument("--incognito")
service = Service(ChromeDriverManager().install())
chrome = webdriver.Chrome(service=service, options=options)
chrome.maximize_window()
chrome.get(NOMUS_URL)
wait1 = WebDriverWait(chrome, 120)

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sexta-Feira")
        self.setFixedSize(460, 560)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.central_widget = QWidget(self)
        self.central_widget.setStyleSheet("background-color: #0f0f0f; border-radius: 10px;")

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        self.central_widget.setPalette(palette)
        self.central_widget.setFont(QFont("Segoe UI", 14))

        # 🎯 Sombra com cor pulsante + rotação
        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setBlurRadius(80)
        self.shadow_effect.setColor(QColor("#00c9c9"))
        self.central_widget.setGraphicsEffect(self.shadow_effect)

        # Layouts
        layout_conteudo = QVBoxLayout(self.central_widget)
        layout_conteudo.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Sexta-Feira\n Por favor, Digite seu Login:")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #00fff7")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_conteudo.addWidget(title)
        layout_conteudo.addSpacing(40)

        # Campos
        layout_conteudo.addWidget(QLabel("Usuário", styleSheet="color: white"))
        self.username = QLineEdit()
        self.username.setStyleSheet("background-color: #1e1e1e; color: #00fff7; border-radius: 4px;")
        layout_conteudo.addWidget(self.username)

        layout_conteudo.addWidget(QLabel("Senha", styleSheet="color: white"))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setStyleSheet("background-color: #1e1e1e; color: #00fff7; border-radius: 4px;")
        layout_conteudo.addWidget(self.password)

        self.password.returnPressed.connect(self.check_login)
        layout_conteudo.addSpacing(30)

        # Botão
        login_button = QPushButton("Entrar")
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #00fff7;
                color: #0f0f0f;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00c9c9;
            }
        """)
        login_button.clicked.connect(self.check_login)
        layout_conteudo.addWidget(login_button)

        layout_conteudo.addStretch()
        footer = QLabel("© 2025 Sexta-feira")
        footer.setStyleSheet("color: #555")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_conteudo.addWidget(footer)

        layout_principal = QVBoxLayout(self)
        layout_principal.addWidget(self.central_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        layout_principal.setContentsMargins(25, 25, 25, 25)

        # 🎬 Fade-in
        self.setWindowOpacity(0)
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(800)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim.start()

        # 💡 Interpolação RGB da sombra
        self.sombra_cores = [
            QColor("#00c9c9"), QColor("#00ffa2"), QColor("#00ff4c"), QColor("#48ff00"),
            QColor("#ffd900"), QColor("#ff9900"), QColor("#ff2600"), QColor("#ff00aa"),
            QColor("#6200ff"), QColor("#001aff")
        ]
        self.sombra_index, self.next_index = 0, 1
        self.steps, self.step = 30, 0

        self.timer_cor = QTimer()
        self.timer_cor.timeout.connect(self.atualizar_sombra_cor)
        self.timer_cor.start(50)

        # 🔄 Sombra giratória
        self.angle, self.raio = 0, 15
        self.timer_giro = QTimer()
        self.timer_giro.timeout.connect(self.atualizar_sombra_offset)
        self.timer_giro.start(50)

    def atualizar_sombra_cor(self):
        cor_atual = self.sombra_cores[self.sombra_index]
        cor_proxima = self.sombra_cores[self.next_index]
        r = cor_atual.red() + (cor_proxima.red() - cor_atual.red()) * self.step / self.steps
        g = cor_atual.green() + (cor_proxima.green() - cor_atual.green()) * self.step / self.steps
        b = cor_atual.blue() + (cor_proxima.blue() - cor_atual.blue()) * self.step / self.steps
        nova_cor = QColor(int(r), int(g), int(b))
        self.shadow_effect.setColor(nova_cor)

        self.step += 1
        if self.step > self.steps:
            self.step = 0
            self.sombra_index = self.next_index
            self.next_index = (self.next_index + 1) % len(self.sombra_cores)

    def atualizar_sombra_offset(self):
        self.angle = (self.angle + 5) % 360
        rad = radians(self.angle)
        dx = int(self.raio * cos(rad))
        dy = int(self.raio * sin(rad))
        self.shadow_effect.setOffset(dx, dy)


    def check_login(self):
        self.close()
    def get_credentials(self):
        return {"usuario": self.username.text(), "senha": self.password.text()}

def login(chrome):
    wait = WebDriverWait(chrome, 5)
    autenticado = False

    # 👇 Cria o app só uma vez
    app = QApplication([])

    while not autenticado:
        janela = LoginWindow()
        janela.show()
        app.exec()  # Executa até a janela fechar

        credenciais = janela.get_credentials()
        usuario = credenciais["usuario"]
        senha = credenciais["senha"]

        print(f"Jarvis: Tentando autenticar {usuario}...")

        try:
            campo_login = wait.until(EC.presence_of_element_located((By.ID, "campologin")))
            campo_login.clear()
            campo_login.send_keys(usuario)
            chrome.find_element(By.NAME, "senha").clear()
            chrome.find_element(By.NAME, "senha").send_keys(senha)
            chrome.find_element(By.NAME, "metodo").click()
            time.sleep(2)

            erro = chrome.find_elements(By.CLASS_NAME, "mensagem-erro-login")
            if erro:
                print("Jarvis: Login falhou. Tentar novamente...")
                continue  # Reexibe janela no próximo loop
            else:
                print("Jarvis: Login bem-sucedido!")
                autenticado = True

        except Exception as e:
            print(f"Jarvis: Erro técnico: {e}")
            break

def solicitar_af():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Solicitação de AF Manual")

    # Tamanho centralizado
    largura_janela = 400
    altura_janela = 200
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()
    pos_x = (largura_tela // 2) - (largura_janela // 2)
    pos_y = (altura_tela // 2) - (altura_janela // 2)
    root.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

    resultado_af = {}

    def confirmar_af(event=None):
        af = entrada_af.get()
        if af:
            print(f"Sexta-feira: AF informada manualmente: {af}")
            resultado_af["af"] = af
            root.destroy()
            root.quit()
        else:
            aviso_label.configure(text="Por favor, preencha o campo de AF.")

    # Título
    titulo = ctk.CTkLabel(root, text="Digite o código da AF", font=("Segoe UI", 18, "bold"))
    titulo.pack(pady=(20, 10))

    entrada_af = ctk.CTkEntry(root, placeholder_text="Ex: 123456", width=250)
    entrada_af.pack(pady=10)
    entrada_af.bind("<Return>", confirmar_af)

    botao_confirmar = ctk.CTkButton(root, text="Confirmar", command=confirmar_af)
    botao_confirmar.pack(pady=10)

    aviso_label = ctk.CTkLabel(root, text="", font=("Segoe UI", 12), text_color="red")
    aviso_label.pack()

    root.mainloop()
    return resultado_af.get("af")

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



def pesquisa_af(chrome):
    af_str = solicitar_af()
    AF = int(af_str)
    campo_pesquisa = chrome.find_element(By.NAME, "nomePesquisa")
    campo_pesquisa.clear()
    campo_pesquisa.send_keys(str(AF))
    campo_pesquisa.send_keys("\n")
    time.sleep(0.5)
    Ids = str(AF)   
    try:
        xpath_af = f"//span[contains(text(), '{Ids}') and substring(text(), string-length(text()) - string-length('{Ids}') + 1) = '{Ids}']"
        span_af = WebDriverWait(chrome, 10).until(EC.element_to_be_clickable((By.XPATH, xpath_af)))
        chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", span_af)
        span_af.click()
        print(f"🖱️ Dvicor: AF {AF} localizada e clicada com sucesso.")
    except Exception as e:
        print(f"❌ Dvicor: Não foi possível localizar a AF {AF} na tela: {e}")

def remocao_ipi(chrome):
    itens_processados = set()
    i = 0

    while True:
        time.sleep(0.5)
        WebDriverWait(chrome, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//table[starts-with(@class,'tabelasDados tablesorter tablesorter-default')]//tr[td[16]]")
            )
        )

        linhas = chrome.find_elements(
            By.XPATH,
            "//table[starts-with(@class,'tabelasDados tablesorter tablesorter-default')]//tr[td[16]]"
        )
        if i >= len(linhas):
            print("✅ Todos os itens foram processados.")
            break

        try:
            print(f"🔍 Processando linha {i+1}/{len(linhas)}")
            linha = linhas[i]
            item = linha.find_element(By.XPATH, ".//td[2]")
            texto = item.text.strip()

            if texto in itens_processados:
                print(f"⚠️ Item {texto} já foi processado. Pulando...")
                i += 1
                

            chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", item)
            chrome.execute_script("arguments[0].click();", item)
            time.sleep(0.5)

            edit = WebDriverWait(chrome, 20).until(EC.element_to_be_clickable((By.ID, "pedidoCompraCriarEditar_itemSubMenu_selecionarItemPedidoCompra")))
            chrome.execute_script("arguments[0].click();", edit)
            time.sleep(0.5)

            WebDriverWait(chrome, 20).until(EC.presence_of_element_located((By.ID, "ui-id-11")))
            tributos = chrome.find_element(By.ID, "ui-id-11")
            chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", tributos)
            WebDriverWait(chrome, 20).until(EC.element_to_be_clickable(tributos)).click()
            time.sleep(0.5)

            situacao_select = Select(WebDriverWait(chrome, 20).until(EC.element_to_be_clickable((By.ID, "id_idSituacaoTributariaIPI"))))
            situacao_select.select_by_visible_text("Selecione")
            time.sleep(0.5)

            saveitem = WebDriverWait(chrome, 20).until(EC.element_to_be_clickable((By.ID, "botao_salvaritempedido")))
            chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", saveitem)
            saveitem.click()

            print(f"[{i+1}/{len(linhas)}] ✅ IPI removido corretamente no item {texto}.")
            itens_processados.add(texto)
            i += 1

        except Exception as e:
            print(f"❌ Erro no item {i+1}: {e}")
            i += 1  # Mesmo em erro, avança para o próximo

def rodape(chrome):
    vtotais = chrome.find_element(By.ID, "ui-id-12")  # localizar o elemento de valores totais
    chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", vtotais)  # rolar para o elemento
    vtotais.click()  # clicar em valores totais
    cvtotal = wait1.until(EC.element_to_be_clickable((By.ID, "botao_calcular_valores_totais")))  # localizar o botão calcular valores totais
    cvtotal.click()  # clicar no botão calcular valores totais
    #CARREGANDO CONDIÇÕES DE PAGAMENTO
    cpagamento = chrome.find_element(By.ID, "ui-id-15") # localizar o elemento de condições de pagamento
    chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", cpagamento) #rolar para o elemento
    cpagamento.click()  # clicar em condições de pagamento
    campo_parcela = chrome.find_element(By.ID, "id_regraGerarParcelas")
    campo_parcela.clear()
    campo_parcela.send_keys("1")
    gerarp = chrome.find_element(By.ID, "botao_gerar_parcelas") #encontar o botão de gerar parcelas
    gerarp.click()  # clicar no botão de gerar parcelas
    time.sleep(1)
    pag_select = Select(WebDriverWait(chrome, 10).until(EC.element_to_be_clickable((By.ID, "id_idsFormasPagamentoParcelas_0"))))
    pag_select.select_by_visible_text("Pix")
    saveaf = chrome.find_element(By.ID, "botao_salvar") # localizar o botão de salvar AF
    chrome.execute_script("arguments[0].scrollIntoView({block: 'center'});", saveaf) # rolar para o botão de salvar AF
    time.sleep(0.5)
    saveaf.click()  # clicar no botão de salvar AF

login(chrome)
validacao_login(chrome)
chrome.get(NOMUS_URL + "/PedidoCompra.do?metodo=pesquisar") 
time.sleep(1)  # aguardar o carregamento da página de pesquisa
pesquisa_af(chrome)
chrome.find_element(By.ID, "pedidoCompra_itemSubMenu_editarPedidoCompra").click()  # Clica no botão de edição
remocao_ipi(chrome)
rodape(chrome)

time.sleep(5)