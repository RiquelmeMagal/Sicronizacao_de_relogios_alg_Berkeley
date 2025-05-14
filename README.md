# Sicronização de Relógios - Algoritmo de Berkeley

![Python](https://img.shields.io/badge/python-3.7%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green)

Este projeto implementa o **Algoritmo de Berkeley** para sincronização de relógios distribuídos em Python.

---

## 🚀 Clonando o Repositório

Você pode clonar via HTTP ou SSH:

```bash
# Via HTTP
git clone https://github.com/RiquelmeMagal/Sicronizacao_de_relogios_alg_Berkeley.git

# Via SSH
git clone git@github.com:RiquelmeMagal/Sicronizacao_de_relogios_alg_Berkeley.git
```

---

## 🛠️ Configuração do Ambiente Virtual

> **Importante:** execute estes passos antes de qualquer comando de execução.

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows (PowerShell)

```powershell
python -m venv venv
.env\Scripts\Activate.ps1
```

### Windows (CMD)

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### Instalação de Dependências

Com o ambiente virtual ativo, instale os pacotes:

```bash
pip install -r requirements.txt
```

---

## ▶️ Como Executar

Certifique-se de estar na **pasta raiz do projeto** e com o ambiente virtual ativo.

### 1. Modo Automático (um único terminal)

Este modo inicializa automaticamente o coordenador e **4 clientes** de uma só vez:

```bash
python3 src/main.py --auto
```

- As portas `5000–5004` serão liberadas (caso já estejam em uso).
- Será iniciado:
  - **Coordenador** na porta `5000`
  - **Clientes** nas portas `5001`, `5002`, `5003` e `5004`
- Após a sincronização, pressione **Enter** para encerrar todos os nós.

### 2. Modo Manual (múltiplos terminais)

Você pode controlar cada nó individualmente em terminais separados:

#### Terminal 1 – Coordenador

```bash
python3 src/node.py \
  --role coordenador \
  --port 5000 \
  --clients localhost:5001 localhost:5002 localhost:5003 localhost:5004
```

> Após iniciar, este terminal exibirá a hora inicial e aguardará o comando de sincronização.

#### Terminais 2 a 5 – Clientes

Em cada terminal, execute um dos comandos abaixo (substitua a porta conforme indicado):

```bash
# Cliente na porta 5001
python3 src/node.py --role cliente --port 5001 --coordinator localhost:5000

# Cliente na porta 5002
python3 src/node.py --role cliente --port 5002 --coordinator localhost:5000

# Cliente na porta 5003
python3 src/node.py --role cliente --port 5003 --coordinator localhost:5000

# Cliente na porta 5004
python3 src/node.py --role cliente --port 5004 --coordinator localhost:5000
```

> Cada terminal de cliente exibirá sua hora inicial.

#### Iniciando a Sincronização

- No **terminal do coordenador**, pressione **Enter** para disparar o processo de sincronização.
- Observe os ajustes de relógio sendo enviados a cada cliente.
- Para encerrar, use **Ctrl+C** em cada terminal.

---

## 📁 Estrutura de Diretórios

```
/
├── src
│   ├── main.py        # Script que gerencia modo automático
│   └── node.py        # Implementação de Node, Coordinator e Client
└── requirements.txt   # Dependências do projeto
```

---

## 🤖 Funcionamento Interno

- **Node**: servidor TCP e relógio local (incrementa 1 por segundo).
- **Coordinator**: coleta horários, calcula média e envia ajustes.
- **Client**: responde ao pedido de tempo e aplica ajustes recebidos.

### Comandos Via Socket

- `GET_TIME` → retorna o tempo atual do nó.
- `ADJUST <delta>` → aplica ajuste de `<delta>` segundos.
- `STOP` → finaliza o servidor do nó.

---

## 📜 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
