
# Loss Intelligence Online

Aplicação Streamlit pronta para rodar localmente ou publicar no Streamlit Community Cloud.

## Rodar no computador

1. Instale Python 3.11 ou 3.12.
2. Abra o terminal nesta pasta.
3. Execute:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publicar online

1. Crie um repositório no GitHub.
2. Envie todos os arquivos desta pasta para o repositório.
3. Entre no Streamlit Community Cloud.
4. Selecione o repositório, a branch e o arquivo `app.py`.
5. Clique em Deploy.

O arquivo `data.csv` é a base padrão. Dentro do aplicativo, o usuário também pode carregar outro CSV para a sessão atual.

## Arquivos

- `app.py`: aplicação
- `data.csv`: base padrão
- `requirements.txt`: dependências
- `.streamlit/config.toml`: tema e configuração
