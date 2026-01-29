# Pipelines Base dos Dados

<p align="center">
    <a href="https://basedosdados.org">
        <img src="https://storage.googleapis.com/basedosdados-website/logos/bd_minilogo.png" width="340" alt="Base dos Dados">
    </a>
</p>

<p align="center">
    <em>Universalizando o acesso a dados de qualidade.</em>
</p>

[![Discord](https://img.shields.io/badge/Discord-Comunidade-blue?style=for-the-badge&logo=Discord)](https://discord.com/invite/huKWpsVYx4)
[![Twitter](https://img.shields.io/badge/Fique%20por%20dentro-blue?style=for-the-badge&logo=x)](https://twitter.com/basedosdados)
[![YouTube](https://img.shields.io/badge/Youtube-Assista-red?style=for-the-badge&logo=youtube)](https://www.youtube.com/c/BasedosDados)
[![LinkedIn](https://img.shields.io/badge/Linkedin-Acesse-blue?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/company/base-dos-dados)

---

## 📋 Pré-requisitos para Windows

Este guia fornece instruções completas para configurar o ambiente de desenvolvimento no Windows.

### 🔧 Requisitos de Sistema

- **Sistema Operacional**: Windows 10/11 (64-bit)
- **Processador**: Intel/AMD x64
- **Memória RAM**: Mínimo 8GB (recomendado 16GB+)
- **Espaço em Disco**: Mínimo 10GB de espaço livre
- **Conexão com Internet**: Para downloads e acesso aos serviços cloud

### 🐍 1. Instalação do Python

#### Opção 1: Python Oficial (Recomendado)
1. Baixe o Python 3.10.x (não 3.11+) do site oficial:
   - Acesse: https://www.python.org/downloads/
   - Baixe: `Python 3.10.x Windows installer (64-bit)`

2. Execute o instalador como administrador
3. **IMPORTANTE**: Marque as opções:
   - ✅ `Add Python to PATH`
   - ✅ `Install launcher for all users`
   - ✅ `Precompile standard library`

4. Verifique a instalação:
```powershell
python --version
pip --version
```

#### Opção 2: Anaconda/Miniconda
1. Baixe o Miniconda do site oficial:
   - Acesse: https://docs.conda.io/en/latest/miniconda.html
   - Baixe: `Miniconda3 Windows 64-bit`

2. Execute o instalador
3. Reinicie o terminal/PowerShell
4. Crie um ambiente conda:
```powershell
conda create -n basedosdados python=3.10
conda activate basedosdados
```

### � 2. Compiladores C++ e R

#### Por que são necessários?
O projeto utiliza várias bibliotecas Python que requerem compilação de código C/C++:
- **NumPy, Pandas, GeoPandas**: Bibliotecas científicas que precisam de compiladores
- **CFFI, cryptography**: Para interfaces de função estrangeira e criptografia
- **OpenCV, Pillow**: Para processamento de imagens
- **RPy2**: Interface entre Python e R

#### Instalação do Visual Studio Build Tools (Recomendado)
1. Baixe o Visual Studio Build Tools:
   - Acesse: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Baixe: `Build Tools for Visual Studio 2022`

2. Execute o instalador
3. Selecione a workload: **"Desktop development with C++"**
4. Marque os componentes individuais:
   - ✅ MSVC v143 - VS 2022 C++ x64/x86 build tools
   - ✅ Windows 11 SDK (ou versão mais recente)
   - ✅ C++ CMake tools for Windows
   - ✅ Testing tools core features

#### Instalação do R (R Statistical Computing)
1. Baixe o R do site oficial:
   - Acesse: https://cran.r-project.org/bin/windows/base/
   - Baixe: `R-4.x.x-win.exe` (versão mais recente)

2. Execute o instalador
3. Aceite as configurações padrão
4. Verifique a instalação:
```powershell
R --version
```

#### Verificação dos Compiladores
```powershell
# Verificar se cl.exe (compilador Microsoft) está disponível
where cl

# Verificar R
R --version

# Testar compilação Python (opcional)
python -c "import numpy; print('NumPy OK')"
```

### 🗄️ 3. Instalação do PostgreSQL

#### Opção 1: PostgreSQL Completo (Recomendado)
1. Baixe o PostgreSQL do site oficial:
   - Acesse: https://www.postgresql.org/download/windows/
   - Baixe: `PostgreSQL 15.x.x` (ou versão mais recente)

2. Execute o instalador
3. Configure:
   - **Porta**: 5432 (padrão)
   - **Senha**: Defina uma senha segura para o usuário `postgres`
   - **Locale**: Portuguese (Brazil)

4. Instale o pgAdmin junto (recomendado)

#### Opção 2: PostgreSQL via Chocolatey
```powershell
# Instalar Chocolatey (se não tiver)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Instalar PostgreSQL
choco install postgresql15
```

#### Verificação da Instalação
```powershell
# Verificar se o serviço está rodando
Get-Service postgresql*

# Conectar ao banco
psql -U postgres -h localhost
```

### ☁️ 4. Configuração do Google Cloud Platform (GCP)

#### 4.1 Criar Conta e Projeto
1. Acesse: https://console.cloud.google.com/
2. Crie uma conta Google Cloud (se não tiver)
3. Crie um novo projeto ou use um existente

#### 4.2 Habilitar APIs Necessárias
No Google Cloud Console, habilite as seguintes APIs:
- BigQuery API
- BigQuery Storage API
- Google Cloud Storage JSON API
- Google Analytics Data API

#### 4.3 Criar Service Account
1. No GCP Console, vá para "IAM & Admin" > "Service Accounts"
2. Clique em "Create Service Account"
3. Configure:
   - **Name**: `basedosdados-dev`
   - **Role**: `BigQuery Admin` (ou roles apropriadas)
4. Crie e baixe a chave JSON
5. Salve o arquivo como `dev.json` em uma pasta segura

#### 4.4 Instalar Google Cloud SDK
```powershell
# Baixar e instalar gcloud CLI
# Acesse: https://cloud.google.com/sdk/docs/install#windows
# Ou via Chocolatey:
choco install gcloudsdk

# Inicializar
gcloud init

# Autenticar
gcloud auth application-default login
```

### 🛠️ 5. Configuração do Ambiente de Desenvolvimento

#### 5.1 Clonar o Repositório
```powershell
# Instalar Git (se não tiver)
winget install --id Git.Git -e --source winget

# Clonar o repositório
git clone https://github.com/basedosdados/pipelines.git
cd pipelines
```

#### 5.2 Criar Ambiente Virtual
```powershell
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
.\.venv\Scripts\activate
```

#### 5.3 Instalar Dependências
```powershell
# Atualizar pip
python -m pip install --upgrade pip

# Instalar o projeto em modo de desenvolvimento
pip install -e .

# Instalar dependências adicionais que podem estar faltando
pip install sqlalchemy psycopg2-binary
```

#### 5.4 Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:
```env
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=basedosdados
POSTGRES_USER=postgres
POSTGRES_PASSWORD=sua_senha_aqui

# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=C:\caminho\para\sua\dev.json
BD_SERVICE_ACCOUNT_DEV=C:\caminho\para\sua\dev.json

# Outras configurações
BD_PROJECT_ID=your-gcp-project-id
```

### 🗂️ 6. Configuração do Banco de Dados

#### 6.1 Criar Banco de Dados PostgreSQL
```sql
-- Conectar como postgres
psql -U postgres

-- Criar banco de dados
CREATE DATABASE basedosdados;

-- Criar usuário (opcional)
CREATE USER basedosdados_user WITH PASSWORD 'sua_senha';
GRANT ALL PRIVILEGES ON DATABASE basedosdados TO basedosdados_user;

-- Criar schema público (se necessário)
\c basedosdados
CREATE SCHEMA IF NOT EXISTS public;
```

#### 6.2 Configurar Conexão no Código

Verifique o arquivo `pipelines/utils/tasks_postgres.py` e ajuste as configurações de conexão se necessário.

### 🚀 7. Executando os Pipelines

#### 7.1 Teste Básico
```powershell
# Ativar ambiente virtual
.\.venv\Scripts\activate

# Testar importações
python -c "import sqlalchemy; print('SQLAlchemy OK')"
python -c "from pipelines.utils.tasks_postgres import load_data_to_postgres; print('Tasks OK')"
```

#### 7.2 Executar Pipeline de Exemplo
```powershell
# Executar pipeline de CNPJ
python run_br_me_cnpj_postgres.py
```

#### 7.3 Executar Pipelines Individuais
```powershell
# Usar o manage.py para criar novos pipelines
python manage.py --help

# Listar pipelines existentes
python manage.py list
```

### 🔧 8. Solução de Problemas Comuns

#### 8.1 Erro: "ModuleNotFoundError: No module named 'sqlalchemy'"
```powershell
pip install sqlalchemy
```

#### 8.2 Erro: "Could not infer an active Flow context"
- Este erro ocorre quando tarefas Prefect são chamadas incorretamente
- Solução: Use `.run()` para tarefas fora de um contexto Flow
- Exemplo: `task.run()` ao invés de `task()`

#### 8.3 Erro de Conexão PostgreSQL
```powershell
# Verificar se o serviço está rodando
Get-Service postgresql*

# Reiniciar serviço
Restart-Service postgresql*

# Testar conexão
psql -U postgres -h localhost -d basedosdados
```

#### 8.4 Erro de Autenticação GCP
```powershell
# Verificar credenciais
gcloud auth list

# Reautenticar se necessário
gcloud auth application-default login

# Verificar variável de ambiente
echo $env:GOOGLE_APPLICATION_CREDENTIALS
```

#### 8.5 Problemas com Dependências
```powershell
# Limpar cache e reinstalar
pip cache purge
pip uninstall -y pipelines
pip install -e .

# Ou usar requirements.txt se disponível
pip install -r requirements.txt
```

#### 8.6 Erro: "'sh' não é reconhecido"
- Este é um aviso inofensivo relacionado a ferramentas Unix
- O pipeline continuará funcionando normalmente

### 📁 9. Estrutura do Projeto

```
pipelines/
├── datasets/           # Pipelines de dados individuais
│   ├── br_me_cnpj/    # Pipeline de CNPJ brasileiro
│   └── ...
├── utils/             # Utilitários
│   ├── tasks_postgres.py  # Funções para PostgreSQL
│   └── ...
├── macros/            # Macros DBT
├── models/            # Modelos DBT
├── tests-dbt/         # Testes DBT
├── run_br_me_cnpj_postgres.py  # Script de exemplo
├── pyproject.toml     # Configuração do projeto
├── profiles.yml       # Configuração DBT
└── dbt_project.yml    # Configuração DBT
```

### 📚 10. Recursos Adicionais

- [Documentação Base dos Dados](https://basedosdados.org)
- [Documentação Prefect](https://docs.prefect.io/)
- [Documentação DBT](https://docs.getdbt.com/)
- [Documentação Google Cloud](https://cloud.google.com/docs)
- [Documentação PostgreSQL](https://www.postgresql.org/docs/)

### 🤝 11. Como Contribuir

1. Leia nosso [guia de contribuição](./CONTRIBUTING.md)
2. Faça um fork do repositório
3. Crie uma branch para sua feature
4. Faça commit das suas mudanças
5. Abra um Pull Request

### 📞 12. Suporte

- **Discord**: [Comunidade Base dos Dados](https://discord.com/invite/huKWpsVYx4)
- **GitHub Issues**: Para reportar bugs
- **Documentação**: Para dúvidas sobre uso

---

**Nota**: Este projeto requer conhecimento intermediário de Python, bancos de dados e Google Cloud Platform. Se você é novo nestas tecnologias, recomendamos começar com os tutoriais oficiais antes de contribuir.
