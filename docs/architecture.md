# Arquitetura do Confera

## Visão geral
A interface web conversa somente com o API Gateway (porta 8000). O Gateway encaminha as requisições para três serviços independentes:
- Event Service (8001): cadastro e consulta de eventos.
- Participant Service (8002): cadastro e consulta de participantes.
- Registration Service (8003): criação, consulta e cancelamento de inscrições. Impede inscrição duplicada ativa (HTTP 409).

O gateway também expõe `GET /services`, que consulta o `/health` de cada serviço e alimenta o painel "Microsserviços em execução" da interface.

Cada serviço é responsável por seu próprio banco SQLite. O serviço de inscrições consulta eventos e participantes antes de criar uma inscrição.

## Framework e reúso
O pacote `framework` reúne interfaces, componentes e a classe abstrata `EventFramework`. O método `create_event()` é o Template Method e fixa a sequência: validar, configurar, aplicar regras e construir.

- **Frozen spots:** `create_event()` (a sequência), `validate()` (campos obrigatórios) e a criação do evento pelo componente.
- **Hotspot 1, `configure()`:** abstrato, obrigatório. Define a categoria.
- **Hotspot 2, `check_rules()`:** hook opcional. Por padrão não faz nada; uma aplicação pode sobrescrevê-lo para impor regra própria.

`Secomp` implementa só o hotspot 1. `Symposium` implementa os dois (exige descrição de pelo menos 20 caracteres). O Event Service escolhe a aplicação pelo campo `application` usando o registro `examples.APPLICATIONS`.

## Componentes
- `EventComponent`: cria o objeto de evento.
- `ParticipantComponent`: valida nome e e-mail.
- `RegistrationComponent`: valida e normaliza identificadores.

As interfaces `EventInterface`, `ParticipantInterface` e `RegistrationInterface` estabelecem os contratos mínimos.

## Limitações
Os bancos são separados. Inscrições guardam IDs sem foreign keys entre bancos. A consulta prévia reduz referências inválidas, mas não elimina condições de corrida nem falhas entre chamadas. Não há transação distribuída. O sistema é uma demonstração acadêmica, não uma solução pronta para produção.
