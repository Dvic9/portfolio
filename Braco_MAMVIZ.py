import os
import win32com.client
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import customtkinter as ctk
import sys
import subprocess


def conectar_inventor():
    try:
        inventor = win32com.client.Dispatch("Inventor.Application")
        return inventor
    except Exception as e:
        print("Erro ao conectar com o Inventor:", e)
        return None
    
def extrair_linhas_bom(bom_rows, dados):
    for linha in bom_rows:
        try:
            if hasattr(linha, "ComponentDefinitions") and linha.ComponentDefinitions and linha.ComponentDefinitions.Count > 0:
                props = linha.ComponentDefinitions(1).Document.PropertySets
                num_estoque = props("Design Tracking Properties").Item("Stock Number").Value
                num_peca = props("Design Tracking Properties").Item("Part Number").Value
            else:
                num_estoque = "N/A"
                num_peca = "N/A"

            unidade = getattr(linha.UnitOfMeasure, "Value", "N/A") if hasattr(linha, "UnitOfMeasure") else "N/A"
            qtde = linha.ItemQuantity if hasattr(linha, 'ItemQuantity') else "N/A"

            print(f"{num_peca} | Unidade: {unidade} | QTDE: {qtde}")
            dados.append([num_estoque, num_peca, unidade, qtde])
        except Exception as e:
            print(f"⚠️ Erro ao processar linha: {e}")
            dados.append(["N/A", "N/A", "N/A", "N/A"])

        if hasattr(linha, "ChildRows") and linha.ChildRows and linha.ChildRows.Count > 0:
            extrair_linhas_bom(linha.ChildRows, dados)
            
def extrair_bom(inventor, caminho_iam):
    try:
        pasta_iam = os.path.dirname(caminho_iam)
        nome_base = os.path.splitext(os.path.basename(caminho_iam))[0]
        pasta_destino = os.path.join(pasta_iam, nome_base)
        os.makedirs(pasta_destino, exist_ok=True)

        caminho_excel = os.path.join(pasta_destino, "planilha_original.xlsx")
        caminho_log_txt = os.path.join(pasta_destino, "caminho_original.txt")

        with open(caminho_log_txt, "w", encoding="utf-8") as log:
            log.write(caminho_excel)
        print(f"📝 Caminho da planilha registrado em: {caminho_log_txt}")

        # Abre a montagem no Inventor
        doc = inventor.Documents.Open(caminho_iam)
        bom = doc.ComponentDefinition.BOM

        # Ativa somente a visualização "Somente peças"
        bom.StructuredViewEnabled = False
        bom.PartsOnlyViewEnabled = True

        # Tenta pegar a vista pelo nome (PT-BR ou EN-US)
        try:
            parts_only_view = bom.BOMViews.Item("Somente peças")
        except:
            parts_only_view = bom.BOMViews.Item("Parts Only")

        # Extrai dados da vista "Somente peças"
        dados = []
        extrair_linhas_bom(parts_only_view.BOMRows, dados)

        # Salva no Excel
        df = pd.DataFrame(dados, columns=["Número de estoque", "Nº da peça", "Unidade da QTDE", "QTDE"])
        df.to_excel(caminho_excel, index=False)
        doc.Close()

        print("✅ Planilha salva em:", caminho_excel)

    except Exception as e:
        print("Erro ao extrair BOM:", e)

    return caminho_iam

def executar_processo():
    Tk().withdraw()
    inventor = conectar_inventor()
    if inventor:
        caminho_iam = askopenfilename(
            title="Selecione o arquivo de montagem (.iam)",
            filetypes=[("Montagem do Inventor", "*.iam")]
        )
        if caminho_iam:
            extrair_bom(inventor, caminho_iam)
            inventor.Quit()
            return caminho_iam  # 🔥 Adicionado aqui!
    return None  # Também útil se nada for selecionado

def confirmar_salvamento_outra_maquina():
    janela = ctk.CTk()
    janela.title("💾 Confirmação de Salvamento")

    largura, altura = 480, 200
    pos_x = (janela.winfo_screenwidth() // 2) - (largura // 2)
    pos_y = (janela.winfo_screenheight() // 2) - (altura // 2)
    janela.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

    resposta = ctk.BooleanVar(value=False)
    frame = ctk.CTkFrame(janela)
    frame.pack(expand=True, pady=20, padx=20)

    mensagem = (
        "Você deseja salvar o arquivo original\n"
        "de outra máquina neste momento?\n\n"
        "Essa ação irá repetir o processo completo de exportação."
    )
    ctk.CTkLabel(frame, text=mensagem, font=("Bahnschrift", 14), wraplength=420, justify="center").pack(pady=10)

    def confirmar():
        resposta.set(True)
        janela.quit()
        janela.destroy()

    def cancelar():
        resposta.set(False)
        janela.quit()
        janela.destroy()

    botoes = ctk.CTkFrame(frame)
    botoes.pack(pady=10)
    ctk.CTkButton(botoes, text="✅ Sim!", command=confirmar).pack(side="left", padx=15)
    ctk.CTkButton(botoes, text="❌ Não, encerrar!", command=cancelar).pack(side="left", padx=15)

    janela.mainloop()
    return resposta.get()

caminho_iam = executar_processo()

if confirmar_salvamento_outra_maquina():
    os.system(f'python "{sys.argv[0]}"')
    sys.exit()