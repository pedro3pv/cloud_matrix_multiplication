```markdown
# TRABALHO COMPUTAÇÃO PARALELA CONCORRENTE – AV3
## Multiplicação de Matrizes Distribuída

Este repositório contém a solução para a Avaliação 3 (AV3) da disciplina de Computação Paralela Concorrente, focada na implementação de um sistema de multiplicação de matrizes distribuída. O trabalho é dividido em duas partes principais: uma atividade teórica e uma atividade prática.

**Autores:**
*   Pedro Augusto de Oliveira Neto - 2224213
*   Francisco Dantas da Silva Neto - 2223879

**Disciplina:** Computação Paralela Concorrente
**Professor:** Carlos E. B. Duarte

---

## Estrutura do Repositório

*   `atividade_teorica/`: Contém o documento LaTeX (`trabalho_teorico.tex`) e o PDF gerado (`trabalho_teorico.pdf`) referente à parte teórica do trabalho.
*   `atividade_pratica/`: Contém os arquivos da implementação da multiplicação de matrizes distribuída.
    *   `servidor/app.py`: Código do servidor Flask com SocketIO que gerencia os workers e distribui as tarefas de multiplicação.
    *   `worker/worker.py`: Código do cliente (worker) que se conecta ao servidor, recebe sub-tarefas de multiplicação e as executa.
    *   `templates/home.html`: Uma interface web simples (opcional) para interagir com o servidor e iniciar a multiplicação (se implementado).
    *   `requirements.txt` (sugestão): Lista de dependências Python para fácil instalação.

---

## 📚 Atividade Teórica

O documento teórico (`atividade_teorica/trabalho_teorico.pdf`) aborda os seguintes conceitos fundamentais:

1.  **Concorrência:** Exploração da execução disputada de tarefas independentes e o papel dos escalonadores.
2.  **Paralelismo:** Discussão sobre a execução simultânea de tarefas, a relação com a concorrência e o uso de múltiplos núcleos.
3.  **Metodologia de Foster (PCAM):** Detalhamento das quatro etapas (Decomposição, Comunicação, Aglomeração, Mapeamento) para o desenvolvimento de programas paralelos.
4.  **Computação Distribuída:** Conceitos, vantagens, casos de uso, arquiteturas (cliente-servidor, 3-camadas, multicamadas, P2P) e funcionamento (acoplamento fraco/forte).
5.  **Multiplicação de Matrizes:** Análise da operação, desafios de performance e abordagens de otimização via computação paralela (máquina única) e distribuída (múltiplas máquinas).

### Para Compilar o Documento Teórico (LaTeX)

Se desejar compilar o arquivo `.tex` manualmente:
1.  Certifique-se de ter uma distribuição LaTeX instalada (como MiKTeX, TeX Live ou Overleaf).
2.  Navegue até o diretório `atividade_teorica/`.
3.  Compile o arquivo `trabalho_teorico.tex` (geralmente usando `pdflatex trabalho_teorico.tex`). Pode ser necessário compilar duas vezes para que as referências e o sumário sejam gerados corretamente.

---

## 💻 Atividade Prática: Multiplicação de Matrizes Distribuída

A atividade prática consiste em um sistema cliente-servidor para realizar a multiplicação de matrizes de forma distribuída.

### Arquitetura

*   **Servidor (`servidor/app.py`):**
    *   Implementado em Flask e Flask-SocketIO.
    *   Recebe requisições para multiplicar duas matrizes (A e B).
    *   Divide a matriz A em blocos (chunks de linhas).
    *   Distribui esses blocos, juntamente com a matriz B inteira, para os workers conectados via WebSocket.
    *   Gerencia a conexão dos workers, o estado das tarefas e a agregação dos resultados parciais.
    *   Fornece um endpoint `/status` para monitorar os workers e tarefas.
*   **Worker (`worker/worker.py`):**
    *   Implementado com a biblioteca `python-socketio`.
    *   Conecta-se ao servidor via WebSocket e se registra.
    *   Recebe sub-tarefas (um bloco da matriz A e a matriz B completa).
    *   Realiza a multiplicação do bloco recebido. Utiliza `concurrent.futures.ThreadPoolExecutor` para paralelizar o cálculo dos elementos da matriz resultante dentro do worker.
    *   Envia o resultado parcial de volta para o servidor.
    *   Possui lógica de reconexão em caso de desconexão.

### Funcionalidades Principais

*   **Distribuição de Tarefas:** O servidor divide a carga de trabalho entre os workers disponíveis.
*   **Paralelismo no Worker:** Cada worker utiliza múltiplas threads para acelerar o cálculo da sua sub-tarefa.
*   **Gerenciamento de Conexão:** Workers podem se conectar e desconectar dinamicamente.
*   **Agregação de Resultados:** O servidor consolida os resultados parciais para formar a matriz final.
*   **Validação:** Inclui validações básicas para as matrizes de entrada e durante o processamento.
*   **Monitoramento (Básico):** Endpoint `/status` no servidor.

### Como Executar

**Pré-requisitos:**
*   Python 3.7+
*   Pip (gerenciador de pacotes Python)

**1. Configurar o Ambiente e Instalar Dependências:**

```bash
# Clone o repositório (se ainda não o fez)
# git clone <url-do-repositorio>
# cd <nome-do-repositorio>

# Crie e ative um ambiente virtual (recomendado)
python -m venv venv
# No Windows:
# venv\Scripts\activate
# No macOS/Linux:
# source venv/bin/activate

# Instale as dependências
pip install Flask Flask-SocketIO python-socketio eventlet # Adicione 'eventlet' ou 'gevent' para o servidor SocketIO
```
*(Nota: `eventlet` ou `gevent` são recomendados para o servidor Flask-SocketIO em produção ou para melhor performance. Para desenvolvimento simples, o servidor Werkzeug padrão pode funcionar, mas `allow_unsafe_werkzeug=True` foi usado no código, o que não é ideal para produção.)*

**2. Iniciar o Servidor:**

Navegue até o diretório `atividade_pratica/servidor/` e execute:
```bash
python app.py
```
O servidor estará rodando em `http://localhost:5000` e esperando conexões de workers em `ws://localhost:5000`.

**3. Iniciar um ou Mais Workers:**

Abra um novo terminal para cada worker que deseja iniciar.
Navegue até o diretório `atividade_pratica/worker/` e execute:
```bash
python worker.py
```
Você pode iniciar múltiplos workers. Cada um se conectará ao servidor.

Para especificar a URL do servidor ou um ID de worker diferente:
```bash
python worker.py <server_url> <worker_id>
# Exemplo:
# python worker.py http://localhost:5000 meu_worker_especial
```

**4. Enviar Tarefas de Multiplicação (Exemplo usando `curl` ou um cliente HTTP):**

Você pode usar uma ferramenta como `curl` ou Postman para enviar uma requisição POST para o endpoint `/api/multiply-matrices` do servidor.

Exemplo com `curl`:
```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "matrixA": [[1, 2, 3], [4, 5, 6]],
  "matrixB": [[7, 8], [9, 10], [11, 12]]
}' http://localhost:5000/api/multiply-matrices
```

A resposta conterá a matriz resultante, o tempo de execução e outras informações.

**5. Verificar o Status (Opcional):**

Acesse `http://localhost:5000/status` em um navegador ou via `curl` para ver o status dos workers conectados e das tarefas.

---

## Considerações Finais e Melhorias Futuras

*   **Interface Web:** Uma interface web mais robusta poderia ser desenvolvida para facilitar o envio de matrizes e a visualização dos resultados e status.
*   **Tolerância a Falhas:** Melhorar a robustez do sistema para lidar com falhas de workers durante a execução de tarefas (ex: reatribuir tarefas).
*   **Balanceamento de Carga:** Implementar estratégias de balanceamento de carga mais sofisticadas, considerando a capacidade de cada worker.
*   **Segurança:** Adicionar mecanismos de autenticação e autorização se o sistema fosse exposto publicamente.
*   **Empacotamento e Deploy:** Utilizar ferramentas como Docker para facilitar o deploy do servidor e dos workers.

---
