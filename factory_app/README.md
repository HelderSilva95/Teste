# Factory Work Tracking System

Sistema de Registo de Trabalho e Produção para Fábrica - Gestão de Ordens de Trabalho, Produção, Inventário e Não-Conformidades.

## Características

- **Gestão de Ordens de Trabalho**: Criação e acompanhamento de ordens de produção
- **Registo de Produção**: Início, pausa e conclusão de processos produtivos
- **Inventário com QR Codes**: Gestão de chapas e maciços de pedra natural
- **Não-Conformidades**: Registo e acompanhamento de problemas
- **Autenticação**: Sistema de login com 3 níveis (Operador, Supervisor, Gestor)
- **Dashboard**: Visão geral em tempo real da operação
- **Interface Responsiva**: Suporta ecrãs tácteis e mouse/teclado

## Requisitos

- **Python 3.9+**
- **SQL Server** (ou compatível)
- **Windows** (recomendado, mas funciona em Linux/macOS)

## Instalação

### 1. Clonar/Copiar o Projeto

```bash
cd /caminho/para/factory_app
```

### 2. Criar Ambiente Virtual

```bash
python -m venv venv
```

### 3. Ativar Ambiente Virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### 4. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 5. Configurar Base de Dados

1. Copie o arquivo `.env.example` para `.env`:
```bash
copy .env.example .env
```

2. Edite o arquivo `.env` e configure as credenciais do SQL Server:

```ini
DB_SERVER=localhost
DB_PORT=1433
DB_NAME=factory_db
DB_USER=sa
DB_PASSWORD=sua_senha_aqui
SECRET_KEY=sua_chave_secreta_aqui
```

### 6. Criar Base de Dados

Crie a base de dados no SQL Server:

```sql
CREATE DATABASE factory_db;
```

### 7. Inicializar com Dados de Exemplo

```bash
python init_database.py
```

Este comando irá:
- Criar todas as tabelas
- Criar utilizadores de exemplo
- Criar máquinas de exemplo
- Criar ordens de trabalho de exemplo
- Criar itens de inventário de exemplo

## Como Executar

### Iniciar Aplicação

```bash
python run.py
```

A aplicação estará disponível em: **http://localhost:8080**

## Credenciais Padrão

Após executar `init_database.py`:

| Perfil | Utilizador | Senha |
|--------|-----------|--------|
| Gestor | admin | admin123 |
| Supervisor | supervisor | super123 |
| Operador | operador1 | oper123 |

**⚠️ IMPORTANTE: Altere estas senhas em produção!**

## Estrutura do Projeto

```
factory_app/
├── app/
│   ├── models/          # Modelos de base de dados
│   ├── routes/          # Rotas da API
│   ├── templates/       # Templates HTML
│   ├── static/          # CSS, JS, imagens
│   └── main.py          # Aplicação FastAPI principal
├── config/
│   ├── settings.py      # Configurações
│   └── database.py      # Configuração BD
├── utils/
│   ├── security.py      # Autenticação
│   └── qr_generator.py  # Geração de QR codes
├── run.py               # Script de inicialização
├── init_database.py     # Script de inicialização BD
├── requirements.txt     # Dependências
└── README.md           # Esta documentação
```

## Funcionalidades por Módulo

### Dashboard
- Visão geral de estatísticas
- Produções ativas
- Ordens prioritárias
- Não-conformidades recentes

### Ordens de Trabalho
- Criar novas ordens (Supervisor/Gestor)
- Listar e filtrar ordens
- Ver detalhes de cada ordem
- Atualizar status

### Produção
- Iniciar produção em ordem de trabalho
- Pausar/Retomar produção
- Registar quantidades entrada/saída
- Associar operadores (1 ou 2)
- Definir tempo de setup

### Inventário
- Registar chapas e maciços
- Gerar QR codes automaticamente
- Imprimir etiquetas com QR
- Consultar por leitura de QR
- Atualizar status de material

### Não-Conformidades
- Registar problemas
- Classificar por tipo e severidade
- Atribuir responsáveis
- Registar ações corretivas
- Acompanhar resolução

## Configuração Avançada

### Alterar Porta

Edite o arquivo `.env`:

```ini
APP_PORT=8080  # Altere para a porta desejada (não use 5000 ou 7082)
```

### Configurar para Produção

1. Altere o ambiente no `.env`:

```ini
ENVIRONMENT=production
```

2. Gere uma chave secreta forte:

```python
import secrets
print(secrets.token_urlsafe(32))
```

3. Use essa chave no `.env`:

```ini
SECRET_KEY=sua_chave_gerada_aqui
```

### Driver ODBC SQL Server

Verifique qual driver ODBC está instalado:

```bash
# Windows
odbcad32
```

Atualize no `.env` se necessário:

```ini
DB_DRIVER=ODBC Driver 17 for SQL Server
# ou
DB_DRIVER=ODBC Driver 18 for SQL Server
```

## Resolução de Problemas

### Erro de Conexão com SQL Server

1. Verifique se o SQL Server está a correr
2. Confirme que TCP/IP está ativado
3. Verifique firewall
4. Teste conexão:

```bash
sqlcmd -S localhost -U sa -P sua_senha
```

### Erro de Import

Se encontrar erros de import, reinstale as dependências:

```bash
pip install --upgrade --force-reinstall -r requirements.txt
```

### Porta em Uso

Se a porta 8080 já estiver em uso, altere no `.env` para outra porta disponível.

## Suporte

Para problemas ou dúvidas:
1. Verifique a documentação acima
2. Revise os logs da aplicação
3. Verifique as configurações no `.env`

## Licença

Propriedade privada - Uso interno apenas.

---

**Factory Work Tracking System v1.0**
Sistema desenvolvido para gestão de produção em fábrica de transformação de pedra natural.
