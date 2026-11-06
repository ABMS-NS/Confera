# Arquitetura do Confera

## Visão geral
A interface web conversa somente com o API Gateway (porta 8000). O Gateway encaminha as requisições para três serviços independentes:
- Event Service (8001): cadastro e consulta de eventos.
- Participant Service (8002): cadastro e consulta de participantes.
- Registration Service (8003): criação, consulta e cancelamento de inscrições.

Cada serviço é responsável por seu próprio banco SQLite. O serviço de inscrições consulta eventos e participantes antes de criar uma inscrição.

## Framework e reúso
O pacote `framework` reúne interfaces, componentes e a classe abstrata `EventFramework`. O método `create_event()` é o Template Method e fixa a sequência validar, configurar e construir. A validação e a sequência são frozen spots; `configure()` é o hotspot abstrato.

As classes `Secomp` e `Symposium` especializam o framework e definem a categoria. A lógica comum permanece no framework e cada aplicação implementa apenas sua variação.

## Componentes
- `EventComponent`: cria o objeto de evento.
- `ParticipantComponent`: valida nome e e-mail.
- `RegistrationComponent`: valida e normaliza identificadores.

As interfaces `EventInterface`, `ParticipantInterface` e `RegistrationInterface` estabelecem os contratos mínimos.

## Limitações
Os bancos são separados. Inscrições guardam IDs sem foreign keys entre bancos. A consulta prévia reduz referências inválidas, mas não elimina condições de corrida nem falhas entre chamadas. Não há transação distribuída. O sistema é uma demonstração acadêmica, não uma solução pronta para produção.
