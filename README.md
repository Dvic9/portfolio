# Jonas Vitor — Portfólio

Desenvolvedor Python e Flutter de Cariacica (ES). Trabalho com automação de processos, integração com ERPs (Sankhya, Nomus, Omie) e automação industrial (CLPs, IHMs e inversores).

## Projetos principais

O código destes projetos é privado: pertence às empresas ou aos clientes para quem foram feitos.

| Projeto | O que é | Tecnologias |
|---|---|---|
| **Plataforma de operações industriais** | App + API em produção usados por 9 setores de uma fábrica de equipamentos para panificação. Integra o ERP Sankhya via OAuth2 e tem cerca de 1.900 testes automatizados com CI. | Flutter, FastAPI, PostgreSQL, Alembic, GitHub Actions |
| **MAMVAS** | Sincroniza a lista de materiais do Autodesk Inventor com as fichas técnicas do Sankhya, com simulação, backup e relatório. | Python, COM (Inventor), API Sankhya, pytest |
| **Gestão de loja de varejo** | Sistema em produção de estoque, caixa, consignação e cupons. | Flutter, Next.js, FastAPI, PostgreSQL, Redis |
| **Gestão para igrejas** | API com row-level security e conformidade com a LGPD, app de membros e painel web. | FastAPI, Flutter, Next.js |
| **Moises** | Assistente de voz com IA: palavra de ativação e reconhecimento de voz no aparelho, memória com RAG. | Flutter, Supabase (pgvector), Gemini, ONNX |

## Automações neste repositório

Robôs que escrevi para tirar trabalho manual do setor de compras e fiscal, usando o ERP Nomus.

| Arquivo | O que faz |
|---|---|
| [`Automacao_entrada_NFE.py`](Automacao_entrada_NFE.py) | Entrada de NF-e: confere as notas importadas com os pedidos de compra (busca aproximada com rapidfuzz) e gera os documentos de entrada. |
| [`Ultron.py`](Ultron.py) | Automatiza cotações e pedidos de compra. |
| [`Jarvis.py`](Jarvis.py) / [`Sexta-feira.py`](Sexta-feira.py) | Pedidos de compra e solicitação de AF, com tela de login em PySide6. |
| [`MAMVIZ.py`](MAMVIZ.py) / [`Braco_MAMVIZ.py`](Braco_MAMVIZ.py) | Extraem a lista de materiais do Autodesk Inventor (COM) e cadastram os produtos no ERP. |
| [`gerar_danfe.php`](gerar_danfe.php) | Gera o DANFE em PDF a partir dos XMLs de NF-e, em lote (biblioteca sped-da). |
| [`Modelo_Uso_API_Telegram.py`](Modelo_Uso_API_Telegram.py) | Exemplo de envio de notificações por bot do Telegram. |

Também público: [bootcamp_ciencia_dados_com_python](https://github.com/Dvic9/bootcamp_ciencia_dados_com_python).

## Como rodar

```
pip install -r requirements.txt
```

Nenhuma credencial fica no código. Defina antes estas variáveis de ambiente:

| Variável | Para quê |
|---|---|
| `NOMUS_URL` | Endereço do seu ERP Nomus |
| `NOMUS_USUARIO`, `NOMUS_SENHA` | Login usado pelos robôs |
| `PASTA_TRABALHO` | Pasta dos XMLs, logs e relatórios (padrão: `dados/`) |
| `CALLMEBOT_PHONE`, `CALLMEBOT_APIKEY` | Aviso por WhatsApp no fim do MAMVIZ (opcional) |

O `gerar_danfe.php` precisa do Composer: `composer require nfephp-org/sped-da`.

## Contato

- LinkedIn: [jonas-vitor-silva-santos](https://www.linkedin.com/in/jonas-vitor-silva-santos-2728a2160/)
- E-mail: jonasvitor116@gmail.com
