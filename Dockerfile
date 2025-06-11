# Usa uma imagem oficial do Python
FROM python:3.10

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos de dependências
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o restante do código para dentro do container
COPY . .

# Expõe a porta usada pelo Uvicorn
EXPOSE 8000

# Comando para rodar a aplicação 
CMD ["python", "run.py"]