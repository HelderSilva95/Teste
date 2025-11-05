# 🔍 Análise de Melhorias e Inconsistências - Factory App

**Data**: 05/11/2025
**Status**: Pré-deployment em Produção (192.168.11.74:8080)

---

## 📊 Resumo Executivo

Encontradas **26 inconsistências** e **15 melhorias recomendadas** distribuídas em:
- 🔴 **8 Críticas** (bloquear produção)
- 🟠 **11 Importantes** (corrigir antes de usar intensivamente)
- 🟡 **12 Moderadas** (melhorar usabilidade)
- 🟢 **10 Opcionais** (funcionalidades futuras)

---

## 🔴 CRÍTICAS - Corrigir ANTES de produção

### 1. **Falta Validação de Permissões em Produção**
**Ficheiro**: `app/routes/production.py:107-108`
**Problema**: Formulário de início de produção mostra TODAS as máquinas e operadores, sem verificar se o utilizador tem permissão para operá-las.

```python
# ATUAL (ERRADO):
machines = db.query(Machine).filter(Machine.is_active == True).all()
operators = db.query(User).filter(User.is_active == True).all()

# DEVERIA SER:
machines = user.machines  # Apenas máquinas que o user pode operar
operators = db.query(User).filter(
    User.is_active == True,
    User.role == UserRole.OPERADOR
).all()
```

**Impacto**: Qualquer utilizador pode iniciar produção em qualquer máquina, mesmo que não esteja associado a ela.
**Correção**: Filtrar máquinas e operadores baseado em `user.machines` e `user.sectors`.

---

### 2. **Token Não Verifica is_active**
**Ficheiro**: `app/routes/auth.py:76-95`
**Problema**: Após login, o token JWT não é revalidado. Se um utilizador for desativado (`is_active=False`), ele continua com acesso até o token expirar (8 horas).

```python
# ATUAL (ERRADO):
def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    # ... obtém user do DB ...
    return user  # Não verifica is_active!

# DEVERIA VERIFICAR:
user = db.query(User).filter(User.username == username).first()
if not user or not user.is_active:
    return None
```

**Impacto**: Utilizadores desativados continuam com acesso.
**Correção**: Adicionar verificação `if not user.is_active: return None` em `get_current_user()`.

---

### 3. **Inconsistência Modelo Inventory vs SQL**
**Ficheiro**: `app/models/inventory.py` vs `create_tables.sql:183-208`

| Campo | Modelo Python | SQL Script |
|-------|---------------|------------|
| `finish` | ✅ Existe | ❌ Não existe |
| `length` | ✅ Existe | ❌ Não existe (tem `dimensions` TEXT) |
| `width` | ✅ Existe | ❌ Não existe |
| `thickness` | ✅ Ambos | ✅ Ambos |
| `batch_number` | ✅ Existe | ❌ Não existe |
| `received_date` | ✅ Existe | ❌ Não existe (tem `entry_date`) |
| `last_used_date` | ✅ Existe | ❌ Não existe |
| `dimensions` | ❌ Não existe | ✅ Existe (NVARCHAR) |

**Impacto**: Aplicação vai crashar ao tentar gravar/ler inventário.
**Correção Urgente**: Alinhar modelo Python com SQL (escolher uma versão e aplicar em ambos).

---

### 4. **Falta Criar Utilizador Admin Inicial**
**Ficheiro**: N/A
**Problema**: Não existe forma de criar primeiro utilizador admin. Não há seed script ou comando CLI.

**Impacto**: Após criar base de dados, não há forma de fazer login.
**Correção**: Criar script `create_admin.py` ou adicionar ao `init_db()`.

---

### 5. **Máquina Pode Ter Múltiplas Produções Simultâneas**
**Ficheiro**: `app/routes/production.py:127-179`
**Problema**: Não há validação se a máquina já está a ser usada noutra produção ativa.

```python
# FALTA ESTA VALIDAÇÃO:
existing_production = db.query(ProductionLog).filter(
    ProductionLog.machine_id == machine_id,
    ProductionLog.status.in_([ProductionStatus.IN_PROGRESS, ProductionStatus.PAUSED])
).first()

if existing_production:
    raise HTTPException(400, "Máquina já está em uso")
```

**Impacto**: Dados inconsistentes, duas produções na mesma máquina ao mesmo tempo.
**Correção**: Adicionar validação antes de criar `ProductionLog`.

---

### 6. **Falta Validação de operator2_id ≠ operator1_id**
**Ficheiro**: `app/routes/production.py:132`
**Problema**: Permite selecionar o mesmo operador para operator1 e operator2.

**Impacto**: Dados incorretos, operador "duplicado" na produção.
**Correção**:
```python
if operator2_id and operator2_id == operator1_id:
    raise HTTPException(400, "Operador 2 deve ser diferente do Operador 1")
```

---

### 7. **Inconsistência Enums SQL vs Python (non_compliance)**
**Ficheiro**: `create_tables.sql:237` vs `app/models/non_compliance.py:11-32`

| Enum | Modelo Python | SQL Script |
|------|---------------|------------|
| `nc_type` | `quality`, `safety`, `process`... | `qualidade`, `processo`... (PT) |
| `severity` | `low`, `medium`, `high`, `critical` | `baixa`, `media`, `alta`, `critica` (PT) |
| `status` | `open`, `in_analysis`... | `aberta`, `em_analise`... (PT) |

**Impacto**: Aplicação vai crashar ao tentar gravar não-conformidades.
**Correção**: Escolher um idioma (inglês ou português) e usar em ambos.

---

### 8. **Campos SQL Não Existem no Modelo NonCompliance**
**Ficheiro**: `create_tables.sql:243-248` vs `app/models/non_compliance.py`

| Campo | SQL | Modelo Python |
|-------|-----|---------------|
| `detected_date` | ✅ Existe | ❌ Não existe (tem `occurred_at` e `reported_at`) |
| `resolved_by_id` | ✅ Existe | ❌ Não existe (tem `assigned_to_id`) |
| `resolved_date` | ✅ Existe | ✅ Existe (`resolved_at`) |

**Impacto**: Erros ao gravar/ler não-conformidades.
**Correção**: Alinhar campos entre SQL e modelo Python.

---

## 🟠 IMPORTANTES - Corrigir antes de uso intensivo

### 9. **Falta Paginação em Vários Módulos**
**Ficheiro**: `app/routes/production.py`, `inventory.py`, `non_compliance.py`
**Problema**: Apenas `work_orders.py` tem paginação. Outros módulos carregam TODOS os registros.

```python
# Produção (linha 32):
active_productions = db.query(ProductionLog).filter(...).all()  # SEM LIMITE!

# Inventário:
items = db.query(InventoryItem).all()  # TODOS!
```

**Impacto**: Performance degrada com muitos registros (> 1000).
**Correção**: Aplicar paginação (`utils/pagination.py`) em todos os listagens.

---

### 10. **Falta Filtros Avançados**
**Módulos**: Produção, Inventário, Não-Conformidades
**Problema**: Listas não têm filtros por data, estado, máquina, setor, etc.

**Impacto**: Difícil encontrar registros específicos com muitos dados.
**Correção**: Adicionar formulários de filtro nos templates de lista.

---

### 11. **Falta Validação de Datas**
**Ficheiro**: Vários (work_orders, production)
**Problema**: Não valida se `planned_end > planned_start`, `end_time > start_time`, etc.

**Exemplo**:
```python
# work_orders.py - criar ordem
if planned_end and planned_start and planned_end < planned_start:
    raise HTTPException(400, "Data fim deve ser posterior à data início")
```

**Impacto**: Dados inconsistentes, datas ilógicas.
**Correção**: Validar datas em todas as operações de criação/edição.

---

### 12. **Falta Confirmação de Eliminações**
**Ficheiro**: Templates admin (sectors.html, machines.html, users.html)
**Problema**: Modais de confirmação existem mas não impedem eliminações acidentais críticas.

**Sugestão**: Adicionar input "digite DELETE para confirmar" em eliminações de:
- Setores com máquinas
- Máquinas com produções ativas
- Utilizadores com produções ativas

---

### 13. **Produção Não Verifica Work Order Completed**
**Ficheiro**: `app/routes/production.py:140`
**Problema**: Pode iniciar produção em Work Order já completa.

```python
work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
if work_order.status == "completed":
    raise HTTPException(400, "Ordem de trabalho já está completa")
```

**Impacto**: Produção extra em orders já finalizadas.

---

### 14. **Falta Histórico de Alterações**
**Módulos**: Todos
**Problema**: Não há auditoria de quem alterou o quê e quando (além de logs).

**Sugestão**: Criar tabela `audit_log` para registrar:
- Tabela alterada
- ID do registo
- Campos alterados (JSON)
- User que fez a alteração
- Timestamp

---

### 15. **Pausas Não Têm Limite de Tempo**
**Ficheiro**: `app/routes/production.py` - função pause
**Problema**: Operador pode pausar e esquecer. Produção fica em pausa indefinidamente.

**Sugestão**:
- Alert se pausa > 2 horas
- Botão "Retomar Todas Pausas" para supervisores
- Dashboard mostrando pausas ativas > X tempo

---

### 16. **Falta Exportação de Dados**
**Módulos**: Todos
**Problema**: Não há forma de exportar dados para Excel/PDF para análise externa.

**Sugestão**: Adicionar botões "Exportar para Excel" em listas principais.

---

### 17. **Dashboard Não Filtra por Setor**
**Ficheiro**: `app/routes/dashboard.py`
**Problema**: Supervisores vêem estatísticas de TODA a fábrica, não apenas do seu setor.

**Sugestão**: Filtrar estatísticas baseado em `user.sectors`.

---

### 18. **Falta Notificações**
**Problema**: Não há sistema de notificações para:
- Produções pausadas > 30 min
- Não-conformidades críticas
- Work orders atrasadas

**Sugestão**: Criar módulo de notificações (badges no navbar).

---

### 19. **Campos Obrigatórios Não Marcados Claramente**
**Ficheiro**: Vários templates
**Problema**: Apenas alguns formulários têm `<span class="text-danger">*</span>` para obrigatórios.

**Correção**: Padronizar todos os formulários.

---

## 🟡 MODERADAS - Melhorar usabilidade

### 20. **Breadcrumbs Ausentes**
**Templates**: Todos
**Problema**: Não há breadcrumbs para navegação (ex: Admin > Setores > Editar).

---

### 21. **Falta Search Global**
**Problema**: Não há barra de pesquisa para procurar orders, produções, items rapidamente.

---

### 22. **Mobile Responsiveness Limitada**
**Templates**: Alguns
**Problema**: Tabelas grandes não são scrollable horizontalmente no mobile.

**Correção**: Adicionar `.table-responsive` em TODAS as tabelas.

---

### 23. **Ícones Inconsistentes**
**Templates**: Vários
**Problema**: Alguns botões têm ícones, outros não. Cores inconsistentes.

---

### 24. **Falta Tooltips**
**Templates**: Vários
**Problema**: Botões de ação (editar, eliminar) não têm tooltips explicativos.

---

### 25. **Campos de Data Sem Datepicker**
**Templates**: work_orders/form.html, etc.
**Problema**: Input de data é texto simples, não há calendário.

**Sugestão**: Usar Bootstrap Datepicker ou HTML5 `type="datetime-local"`.

---

### 26. **Loading States Ausentes**
**Templates**: Todos formulários
**Problema**: Sem feedback visual durante submit (botão não fica disabled, sem spinner).

**Sugestão**: JavaScript para disable button e mostrar spinner ao submeter.

---

### 27. **Mensagens de Erro Genéricas**
**Problema**: Errors 500 não são user-friendly.

**Sugestão**: Melhorar mensagens de erro em português claro.

---

### 28. **Falta Validação Client-Side**
**Templates**: Formulários
**Problema**: Validação apenas no backend, UX lenta.

**Sugestão**: Adicionar `required`, `min`, `max` nos inputs HTML5.

---

### 29. **Timer de Produção Não Persiste com Refresh**
**Template**: `production/detail.html`
**Problema**: Se utilizador faz refresh, timer JavaScript reinicia.

**Sugestão**: Recalcular tempo baseado em `start_time` do servidor.

---

### 30. **QR Scanner Não Tem Feedback de Erro**
**Template**: Inventário
**Problema**: Se câmera falhar, não há mensagem clara.

---

### 31. **Falta Dark Mode**
**Sugestão**: Para ambientes de fábrica com iluminação reduzida.

---

## 🟢 OPCIONAIS - Funcionalidades futuras

### 32. **Dashboard com Gráficos**
**Sugestão**: Chart.js para gráficos de produção, eficiência, etc.

---

### 33. **Relatórios Automáticos**
**Sugestão**: Gerar relatórios diários/semanais em PDF e enviar por email.

---

### 34. **API REST Documentada**
**Sugestão**: FastAPI já tem Swagger, mas falta documentar endpoints para integrações.

---

### 35. **Multi-idioma (i18n)**
**Sugestão**: Suporte para inglês/português configurável.

---

### 36. **Backup Automático**
**Sugestão**: Script para backup SQL automático.

---

### 37. **Logs de Acesso**
**Sugestão**: Registrar IPs, dispositivos, horários de login.

---

### 38. **Two-Factor Authentication (2FA)**
**Sugestão**: Para utilizadores admin.

---

### 39. **Manutenção Preventiva**
**Sugestão**: Módulo para agendar manutenções de máquinas.

---

### 40. **Integração com WhatsApp/Email**
**Sugestão**: Notificações por WhatsApp para não-conformidades críticas.

---

### 41. **App Mobile Nativa**
**Sugestão**: App Flutter/React Native para operadores no chão de fábrica.

---

## 📝 Plano de Ação Recomendado

### Fase 1 - PRÉ-PRODUÇÃO (OBRIGATÓRIO) ⚠️
**Prazo**: 1-2 dias
**Bloqueia deployment**

1. ✅ Alinhar modelos Python com SQL (Inventory, NonCompliance)
2. ✅ Adicionar validação de permissões em produção (user.machines)
3. ✅ Verificar is_active em get_current_user()
4. ✅ Criar script para admin inicial
5. ✅ Validar máquina não está em uso
6. ✅ Validar operator1 ≠ operator2
7. ✅ Testar fluxo completo: criar setor → máquina → user → produção

### Fase 2 - PÓS-DEPLOYMENT IMEDIATO
**Prazo**: 1 semana
**Usar aplicação com cuidado**

8. ✅ Adicionar paginação em produção/inventário/NC
9. ✅ Validações de datas
10. ✅ Filtros básicos (data, estado)
11. ✅ Confirmação de eliminações críticas
12. ✅ Exportação Excel básica

### Fase 3 - MELHORIAS DE USABILIDADE
**Prazo**: 2-4 semanas
**Aplicação já usável**

13. Breadcrumbs
14. Search global
15. Mobile responsiveness
16. Datepickers
17. Loading states
18. Notificações básicas

### Fase 4 - FUNCIONALIDADES AVANÇADAS
**Prazo**: 1-3 meses
**Opcional**

19. Dashboard com gráficos
20. Relatórios automáticos
21. Auditoria completa
22. Integração WhatsApp
23. Dark mode

---

## 🎯 Prioridades por Impacto

| Prioridade | Item | Esforço | Impacto |
|------------|------|---------|---------|
| 🔴 P0 | Alinhar SQL vs Models | 2h | ALTO |
| 🔴 P0 | Validar permissões produção | 1h | ALTO |
| 🔴 P0 | Verificar is_active | 15min | MÉDIO |
| 🔴 P0 | Admin inicial | 30min | ALTO |
| 🔴 P0 | Máquina única | 30min | ALTO |
| 🟠 P1 | Paginação | 2h | MÉDIO |
| 🟠 P1 | Validação datas | 1h | MÉDIO |
| 🟠 P1 | Filtros | 3h | MÉDIO |
| 🟡 P2 | Exportação | 4h | MÉDIO |
| 🟡 P2 | Breadcrumbs | 2h | BAIXO |
| 🟢 P3 | Gráficos | 8h | BAIXO |

---

## 📞 Recomendações Finais

### ✅ PODE USAR EM PRODUÇÃO SE:
1. Corrigir todas as **8 críticas** (Fase 1)
2. Testar manualmente cada fluxo
3. Ter plano de backup SQL
4. Treinar utilizadores nos fluxos corretos

### ⚠️ USAR COM CUIDADO:
- Limitar a 2-3 utilizadores inicialmente
- Não usar para dados críticos nos primeiros dias
- Monitorar logs ativamente

### ❌ NÃO USAR ATÉ:
- Alinhar modelos com SQL (crashs garantidos)
- Criar utilizador admin inicial (não consegue login)

---

**Revisão**: Claude Code
**Próxima Revisão**: Após correções Fase 1
