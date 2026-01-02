# Sistema de Controle de TVs Samsung - Arquitetura

## 📁 Estrutura de Pastas

```
AppTvs/
│
├── app_new.py              # Aplicação principal refatorada (NOVA)
├── app.py                  # Aplicação antiga (manter como backup)
├── config.py               # Configurações centralizadas
├── requirements.txt        # Dependências Python
│
├── controllers/            # Camada de Controle - Integração com SmartThings
│   ├── __init__.py
│   ├── smartthings.py      # Cliente API SmartThings
│   └── tv_control.py       # Comandos básicos (enter, setas, etc)
│
├── services/               # Camada de Serviços - Lógica de Negócio (NOVO)
│   ├── __init__.py
│   ├── tv_service.py       # Gerenciamento de TVs
│   ├── tv_controller.py    # Controle de operações (ligar/desligar)
│   ├── webhook_service.py  # Integração com webhooks
│   ├── sequence_mapper.py  # Mapeamento TV -> Sequência
│   └── scheduler_service.py# Tarefas agendadas
│
├── sequences/              # Sequências de Inicialização
│   ├── __init__.py
│   └── tv_sequences.py     # Sequências específicas por TV
│
├── routes/                 # Camada de Apresentação - Rotas HTTP (NOVO)
│   ├── __init__.py
│   ├── api_routes.py       # Endpoints da API REST
│   └── web_routes.py       # Páginas HTML
│
├── utils/                  # Utilitários
│   ├── __init__.py
│   ├── logger.py           # Sistema de logs
│   ├── renovador_token.py  # Renovação automática de token
│   └── listar_tvs.py       # Script auxiliar
│
├── static/                 # Arquivos estáticos (CSS, JS)
│   ├── style.css
│   └── script.js
│
└── templates/              # Templates HTML
    └── index.html
```

## 🏗️ Arquitetura em Camadas

### 1. **Camada de Apresentação (Routes)**
- **Responsabilidade**: Receber requisições HTTP e retornar respostas
- **Arquivos**: `routes/api_routes.py`, `routes/web_routes.py`
- **Funções**:
  - Validação de entrada
  - Serialização de respostas (JSON)
  - Renderização de templates

### 2. **Camada de Serviços (Services)**
- **Responsabilidade**: Lógica de negócio da aplicação
- **Componentes**:

#### `TVService`
- Carrega TVs da API SmartThings
- Mantém cache de TVs
- Agrupa TVs por setor
- Obtém status de TVs

#### `TVController`
- Controla operações de ligar/desligar
- Executa sequências de inicialização
- Gerencia reconexões

#### `WebhookService`
- Envia comandos para máquinas virtuais
- Mapeia TVs para IDs numéricos
- Formata payload do webhook

#### `SequenceMapper`
- Mapeia nome da TV para sua sequência
- Executa a sequência correta

#### `SchedulerService`
- Gerencia tarefas agendadas
- Renovação automática de token
- Keep-alive periódico

### 3. **Camada de Controle (Controllers)**
- **Responsabilidade**: Integração com APIs externas
- **Componentes**:
  - `SmartThingsTV`: Cliente da API SmartThings
  - `tv_control`: Comandos básicos de controle remoto

### 4. **Camada de Dados (Config)**
- **Responsabilidade**: Configurações centralizadas
- **Conteúdo**:
  - Token de acesso
  - Lista de TVs e setores
  - URLs de webhooks
  - Configurações de servidor

## 🔄 Fluxo de Execução

### Ligar uma TV (Toggle):
```
1. Usuário → GET/POST /api/executar/<tv_nome>
2. api_routes.py → Valida e chama tv_controller.toggle_tv()
3. TVController → Verifica status atual via TVService
4. TVController → Se desligada:
   4.1. WebhookService.enviar_comando_ligar()
   4.2. SequenceMapper.executar_sequencia()
5. SequenceMapper → Identifica e executa sequência específica
6. Sequência → Usa controllers/tv_control para comandos
7. Resposta → Retorna sucesso ao usuário
```

### Keep Alive:
```
1. SchedulerService → Executa a cada X minutos
2. Para cada TV elegível:
   2.1. Verifica se está ligada (TVService)
   2.2. Se ligada: Enter + 10s + Enter
3. Processa em lotes de 2 TVs por vez
```

### Renovação de Token:
```
1. SchedulerService → Executa diariamente no horário configurado
2. RenovadorTokenSmartThings → Acessa portal e renova
3. Atualiza config.py com novo token
4. TVService.recarregar_token() → Atualiza token em memória
```

## 🔌 Separação de Responsabilidades

### ✅ Princípios Aplicados:

1. **Single Responsibility**: Cada classe tem uma responsabilidade única
2. **Dependency Injection**: Services são injetados via construtor
3. **Separation of Concerns**: Routes não conhecem detalhes de negócio
4. **Service Layer**: Toda lógica de negócio centralizada
5. **Factory Pattern**: `create_app()` para construir aplicação

### ❌ Problemas Resolvidos:

- **Antes**: Tudo em `app.py` (722 linhas)
- **Depois**: Distribuído em módulos especializados

- **Antes**: Rotas misturadas com lógica de negócio
- **Depois**: Rotas apenas delegam para services

- **Antes**: Mapeamento hardcoded em múltiplos lugares
- **Depois**: Centralizado em `SequenceMapper` e `WebhookService`

## 🚀 Como Usar

### Executar aplicação NOVA (refatorada):
```bash
python app_new.py
```

### Executar aplicação ANTIGA (backup):
```bash
python app.py
```

## 📝 Vantagens da Nova Arquitetura

1. **Testabilidade**: Services podem ser testados isoladamente
2. **Manutenibilidade**: Mudanças afetam apenas módulos específicos
3. **Escalabilidade**: Fácil adicionar novos services ou rotas
4. **Legibilidade**: Código organizado e documentado
5. **Reutilização**: Services podem ser usados em outros contextos
6. **Debugging**: Fácil identificar onde está o problema

## 🔧 Próximos Passos (Sugestões)

1. **Adicionar testes unitários** para cada service
2. **Implementar logging estruturado** (com níveis)
3. **Adicionar validação de schemas** (Pydantic/Marshmallow)
4. **Implementar rate limiting** nas rotas
5. **Adicionar autenticação** (se necessário)
6. **Criar documentação OpenAPI** (Swagger)
7. **Implementar retry policies** nos webhooks
8. **Adicionar health check endpoint**
