# Observatório Macro-Financeiro do Brasil

Dashboard acadêmico de indicadores macroeconômicos brasileiros, com dados públicos do Banco Central do Brasil (SGS), Python, Pandas, Plotly e Streamlit.

## 1. Contexto e pergunta orientadora
Como a política monetária, a inflação, o câmbio e a atividade econômica se comportaram no Brasil entre 2020 e 2023? O painel organiza essas séries para apoiar uma leitura exploratória do cenário macroeconômico.

## 2. Perguntas de negócio
1. Como a Selic Meta evoluiu no ciclo 2020–2023 e em quais momentos o juro real ex-post estimado foi mais elevado?
2. Qual foi a trajetória do Dólar PTAX e em quais períodos ficou acima da média histórica do recorte?
3. Como o IBC-Br dessazonalizado se comportou durante o período?
4. Quais pares de variáveis apresentaram maiores coeficientes de correlação de Pearson?

## 3. Fontes e período
API pública do Sistema Gerenciador de Séries Temporais do Banco Central:
- SGS 432: Meta Selic (% a.a.).
- SGS 433: IPCA mensal (%).
- SGS 13522: IPCA acumulado em 12 meses (%).
- SGS 1: Dólar PTAX (R$/US$).
- SGS 24364: IBC-Br dessazonalizado.

Período de referência do projeto: 01/01/2020 a 31/12/2023. A extração ocorre via API do BCB e pode depender da disponibilidade do serviço.

## 4. Pipeline ETL
O arquivo `src/etl.py` concentra funções reutilizáveis:
- Extração das cinco séries via API SGS.
- Conversão de datas para datetime e valores para numérico.
- Remoção de nulos inválidos e duplicidades.
- Padronização mensal e combinação das séries.
- Cálculo do juro real ex-post estimado.
- Exportação para `data/raw/` e `data/processed/`.

Os caminhos são construídos com `pathlib.Path`, relativos à estrutura do repositório.

## 5. Dicionário de dados
| Campo | Tipo | Significado |
|---|---|---|
| date | datetime | Primeiro dia do mês de referência |
| selic_meta | float | Média mensal da série Meta Selic |
| ipca_mensal | float | IPCA mensal |
| ipca_12m | float | IPCA acumulado em 12 meses |
| dolar_ptax | float | Média mensal da cotação PTAX |
| ibc_br | float | Média mensal do IBC-Br dessazonalizado |
| juro_real_ex_post | float | Estimativa: ((1+Selic)/(1+IPCA 12m)-1) × 100 |

## 6. Tecnologias
Python, Pandas, Requests, Streamlit, Plotly Express/Graph Objects e Jupyter Notebook.

## 7. Visualizações e KPIs
O aplicativo contém:
- Selic Meta e IPCA 12 meses em série temporal.
- Juro real ex-post estimado.
- Dólar PTAX com linha de média do período.
- IBC-Br dessazonalizado.
- Matriz de correlação de Pearson.
- KPIs de Selic, IPCA 12m, juro real e dólar.
- Filtros de período e exportação CSV.

## 8. Resultados
**Preencher após executar o ETL e o notebook com os dados oficiais.** Registre aqui valores efetivamente calculados, datas de máximas/mínimas e correlações observadas. Não inserir números estimados ou inventados.

## 9. Limitações
A análise é descritiva. Correlação não implica causalidade. A média mensal de séries diárias reduz a granularidade. O juro real ex-post é uma aproximação calculada com Selic Meta e IPCA acumulado em 12 meses, não uma medida completa de retorno real de investimento. O IBC-Br é indicador antecedente/proxy e não substitui o PIB.

## 10. Como executar localmente
1. Instale Python 3.10 ou superior.
2. Descompacte o projeto e abra a pasta no terminal.
3. Crie ambiente virtual: `python -m venv .venv`
4. Ative o ambiente virtual.
5. Instale dependências: `pip install -r requirements.txt`
6. Execute o ETL: `python -m src.etl`
7. Execute o notebook `notebooks/eda_exploratoria.ipynb` e salve após executar todas as células.
8. Inicie o dashboard: `streamlit run app.py`

## 11. Publicação
### GitHub
Crie um repositório público e envie todos os arquivos, exceto `secrets.toml`, ambientes virtuais e caches.

### Streamlit Community Cloud
Conecte o repositório GitHub, selecione `app.py` como arquivo principal e publique. O app consulta a API pública do BCB; portanto, precisa de acesso à internet no ambiente de execução.

## 12. Trello e vídeo
- Quadro Trello público: **https://trello.com/b/wQsh4kyA/projeto-bi-observatorio-macro-financeiro**
- Captura do quadro Kanban: **<img width="872" height="462" alt="image" src="https://github.com/user-attachments/assets/9f1bf36a-61de-49e6-b5e9-5d6fe596dbd7" />
**
- Aplicação publicada: **https://observatorio-macro-financeiro-h5anmkpdqbkf7zpfx25kku.streamlit.app**

Consulte `TRELLO_CARDS.md` e `PITCH.md` para concluir essas entregas.

## 13. Autoria e referências
Autoria: **Carolina Correa**  
Curso: Visualização de Dados e Business Intelligence  
Fonte: Banco Central do Brasil — SGS: https://www3.bcb.gov.br/sgspub/

Referências técnicas:
- API SGS: https://dadosabertos.bcb.gov.br/
- Streamlit: https://docs.streamlit.io/
- Plotly: https://plotly.com/python/
- Pandas: https://pandas.pydata.org/docs/
