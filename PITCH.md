# Roteiro de vídeo pitch (3 a 5 minutos)

**0:00–0:40 | Abertura e contexto**  
"Olá, meu nome é [NOME]. Este projeto é o Observatório Macro-Financeiro do Brasil. O objetivo é organizar indicadores públicos para observar a evolução da política monetária, inflação, câmbio e atividade econômica entre 2020 e 2023."

**0:40–1:20 | Dados e ETL**  
"Utilizei cinco séries do Sistema Gerenciador de Séries Temporais do Banco Central: Selic Meta, IPCA mensal, IPCA 12 meses, Dólar PTAX e IBC-Br. O ETL em Python extrai os dados, padroniza datas e valores, trata registros inválidos e combina as séries em uma base mensal."

**1:20–3:40 | Demonstração do aplicativo**  
"Na visão geral, apresento os principais indicadores. Na aba de política monetária, observo a Selic e a estimativa de juro real ex-post. Na aba de câmbio, comparo a PTAX com a média do período. Em atividade econômica, acompanho o IBC-Br. Por fim, a matriz de correlação mostra associações lineares entre as variáveis. Também é possível filtrar o período e exportar os dados em CSV."

**3:40–4:30 | Conclusão e limitações**  
"Os resultados devem ser interpretados como análise descritiva. Correlação não significa causalidade, a agregação mensal reduz detalhes diários e o IBC-Br é uma proxy da atividade econômica. O projeto demonstra como dados públicos podem ser transformados em informação visual para apoiar análises."

Substitua os trechos entre colchetes e mencione apenas resultados que você tenha efetivamente observado ao executar o painel.
