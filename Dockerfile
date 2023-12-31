# Use uma imagem base que inclua o Python, por exemplo:
FROM python:3.11

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie os arquivos do seu backend Flask para o contêiner
COPY . .

# Instale as dependências Python (você pode ter um arquivo requirements.txt)
RUN pip install -r requirements.txt

# Exponha a porta em que seu servidor Flask estará em execução (porta padrão 5000)
EXPOSE 5000

# Comando para iniciar seu servidor Flask quando o contêiner for iniciado
CMD ["python", "app.py"]

# Defina variáveis de ambiente para o PostgreSQL (se necessário)
ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD admin@admin
ENV POSTGRES_DB pegga

# Exponha a porta padrão do PostgreSQL (5432)
EXPOSE 5432