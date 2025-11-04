# Guia de Início Rápido - Factory Work Tracking System

## Instalação em 5 Passos

### 1️⃣ Executar Instalação

Execute o arquivo `install.bat` (duplo clique no Windows):

```
install.bat
```

Este script irá:
- Verificar se Python está instalado
- Criar ambiente virtual
- Instalar todas as dependências

### 2️⃣ Configurar Base de Dados

1. Abra o **SQL Server Management Studio** (SSMS)
2. Execute o seguinte comando para criar a base de dados:

```sql
CREATE DATABASE factory_db;
```

3. Edite o arquivo `.env` e configure suas credenciais:

```ini
DB_SERVER=localhost
DB_USER=sa
DB_PASSWORD=SUA_SENHA_AQUI
```

### 3️⃣ Inicializar Dados

Execute o script de inicialização:

```bash
python init_database.py
```

Este comando cria:
- ✓ Todas as tabelas
- ✓ Utilizadores de exemplo
- ✓ Máquinas de exemplo
- ✓ Ordens de trabalho de exemplo
- ✓ Itens de inventário de exemplo

### 4️⃣ Iniciar Aplicação

Execute o arquivo `start.bat` (duplo clique):

```
start.bat
```

Ou manualmente:

```bash
python run.py
```

### 5️⃣ Acessar Sistema

Abra o navegador e acesse:

```
http://localhost:8080
```

## Credenciais de Acesso

| Perfil | Utilizador | Senha | Permissões |
|--------|-----------|-------|------------|
| **Gestor** | admin | admin123 | Todas |
| **Supervisor** | supervisor | super123 | Criar ordens, planeamento |
| **Operador** | operador1 | oper123 | Produção, registos |

⚠️ **Altere estas senhas após primeiro acesso!**

## Verificação Rápida

Após login, você deve ver:
- ✓ Dashboard com estatísticas
- ✓ Menu de navegação superior
- ✓ Acesso a todos os módulos

## Módulos Principais

### 📋 Ordens de Trabalho
- Criar novas ordens (Supervisor/Gestor)
- Acompanhar progresso
- Ver detalhes e histórico

### ⚙️ Produção
- Iniciar/Pausar/Completar produção
- Registar quantidades
- Associar operadores

### 📦 Inventário
- Registar chapas e maciços
- Gerar QR codes
- Consultar stock

### ⚠️ Não-Conformidades
- Registar problemas
- Atribuir responsáveis
- Acompanhar resolução

## Resolução Rápida de Problemas

### Erro: "Python não encontrado"
- Instale Python 3.9+ de python.org
- Marque a opção "Add to PATH" durante instalação

### Erro: "Não consegue conectar ao SQL Server"
1. Verifique se SQL Server está em execução
2. Confirme credenciais no arquivo `.env`
3. Teste conexão com SSMS primeiro

### Erro: "Porta 8080 em uso"
- Edite `.env` e altere `APP_PORT=8080` para outra porta
- Exemplo: `APP_PORT=8081`

### Erro ao executar scripts .bat
- Execute como Administrador
- Ou use PowerShell:
  ```powershell
  python run.py
  ```

## Suporte Adicional

Consulte o **README.md** completo para:
- Configuração avançada
- Estrutura do projeto
- Documentação detalhada de cada módulo

---

**Pronto para começar!** 🚀

Execute `start.bat` e acesse http://localhost:8080
