# Ingressos Online - Infraestrutura e Servicos

Este projeto e uma solucao baseada em microsservicos para venda de ingressos online. A arquitetura e distribuida, escalavel e integrada por um unico API Gateway.

## Arquitetura do Sistema

*   **API Gateway / Load Balancer (Nginx)**: Ponto de entrada unico na porta `80`. Distribui as requisicoes entre as replicas ativas usando o algoritmo Round-Robin.
*   **Servico de Autenticacao (auth)**: Gerencia o cadastro, login e autenticacao baseada em JWT.
*   **Servico de Eventos (events)**: Gerencia o cadastro e edicao de eventos, controlando o estoque de ingressos disponiveis.
*   **Servico de Pedidos (orders)**: Coordena o fluxo de compra de ingressos com base na disponibilidade do evento e executa a integracao de pagamento.
*   **Servico de Pagamentos (payments)**: Recebe e simula o processamento das transacoes (Pix, Boleto, Cartao) e notifica eventos de pagamento.
*   **Mensageria e Cache (Redis)**: Utilizado pelo servico de pagamentos para publicacao de eventos assincronos.
*   **Banco de Dados (PostgreSQL)**: Cada microsservico possui seu banco de dados isolado no mesmo cluster do Postgres.
*   **Monitoramento (Prometheus)**: Coleta dinamicamente as metricas das replicas ativas de cada microsservico na rede interna do Docker.

---

## Como Executar a Aplicacao

Certifique-se de ter o **Docker** e o **Docker Compose** instalados em sua maquina.

### 1. Iniciar toda a infraestrutura:
```bash
docker compose up --build -d
```
Este comando criara e iniciara todos os contêineres necessários (incluindo 2 replicas de cada microsservico principal).

### 2. Verificar o status dos contêineres:
```bash
docker compose ps
```

---

## Portas e Endpoints Principais

As requisicoes externas devem ser feitas atraves do Gateway (Nginx):

*   **API Gateway**: `http://localhost/` (porta `80`)
    *   Auth: `http://localhost/auth/`
    *   Events: `http://localhost/events/`
    *   Orders: `http://localhost/orders/`
    *   Payments: `http://localhost/payments/`
*   **Prometheus**: `http://localhost:9090` (porta `9090`)

---
