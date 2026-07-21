Loss Intelligence Online
Aplicação Streamlit pronta para rodar localmente ou publicar no Streamlit Community Cloud.
Rodar no computador
Instale Python 3.11 ou 3.12.
Abra o terminal nesta pasta.
Execute:
```bash
pip install -r requirements.txt
streamlit run app.py
```
Publicar online
Crie um repositório no GitHub.
Envie todos os arquivos desta pasta para o repositório.
Entre no Streamlit Community Cloud.
Selecione o repositório, a branch e o arquivo `app.py`.
Clique em Deploy.
O arquivo `data.csv` é a base padrão. Dentro do aplicativo, o usuário também pode carregar outro CSV para a sessão atual.
Arquivos
`app.py`: aplicação
`data.csv`: base padrão
`requirements.txt`: dependências
`.streamlit/config.toml`: tema e configuração

Versão 2 — Drill-down clicável
Os gráficos de macrotema, área, tema específico, NR e 5S agora aceitam clique.
Ao selecionar uma barra, a aplicação mostra:
tipos específicos;
áreas;
responsáveis;
datas de abertura;
indicadores do recorte;
ações individuais;
download do detalhamento em CSV.
Para atualizar o site já publicado, substitua os arquivos do repositório pelos desta versão e faça um novo commit. O Streamlit redesenha a aplicação automaticamente.
