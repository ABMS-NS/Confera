"""Página da aplicação Workshop (Oficina).

Interface editorial, em tons quentes. A página é só a aplicação: títulos de
seção e as partes funcionais.
"""
from string import Template


CSS = """
* { box-sizing: border-box; }
body {
  margin: 0;
  background: #faf6ef;
  color: #2e2a25;
  font-family: Verdana, Geneva, sans-serif;
  font-size: 15px;
  line-height: 1.6;
}
.limite { width: min(760px, 92%); margin: 0 auto; }
header { padding: 40px 0 18px; border-bottom: 1px solid #d8cfc2; }
.marca {
  color: #2e2a25;
  text-decoration: none;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 34px;
}
.marca span { color: #b5562a; }
main { padding: 10px 0 50px; }
.bloco { padding: 26px 0; border-bottom: 1px dashed #d8cfc2; }
.bloco h2 {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 22px;
  font-weight: normal;
  margin: 0 0 14px;
}
.form { display: grid; gap: 12px; }
.campo { display: grid; gap: 4px; }
.campo label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: #7a6f63;
}
input, textarea, select {
  font: inherit;
  padding: 8px;
  border: 1px solid #cbbfae;
  background: #fffdfa;
  border-radius: 2px;
}
textarea { min-height: 70px; resize: vertical; }
button {
  justify-self: start;
  border: 1px solid #8f3f1f;
  background: #b5562a;
  color: #ffffff;
  padding: 8px 16px;
  font: inherit;
  border-radius: 2px;
  cursor: pointer;
}
button:hover { background: #8f3f1f; }
.recado { min-height: 1.2em; font-size: 13px; color: #7a6f63; margin: 10px 0 0; }
.recado.erro { color: #a12f1c; }
.lista { display: grid; }
.linha {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: baseline;
  padding: 10px 0;
  border-bottom: 1px solid #e7ded2;
}
.linha:last-child { border-bottom: 0; }
.linha strong {
  font-weight: normal;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 16px;
}
.linha small { display: block; color: #7a6f63; font-size: 12px; }
.linha button {
  background: none;
  border: 0;
  color: #b5562a;
  padding: 0;
  font-size: 12px;
  text-decoration: underline;
  cursor: pointer;
}
.vazio { color: #8a7f72; font-size: 13px; margin: 8px 0; }
footer { padding: 20px 0 40px; color: #8a7f72; font-size: 12px; }
@media (max-width: 560px) {
  .linha { flex-direction: column; gap: 4px; }
}
"""

JS = """
const ler = (id) => document.getElementById(id);

function escapar(valor) {
  return String(valor).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

async function pedir(caminho, opcoes = {}) {
  const resposta = await fetch(caminho, {
    headers: { "Content-Type": "application/json" },
    ...opcoes
  });
  const dados = await resposta.json().catch(() => ({}));
  if (!resposta.ok) throw new Error(dados.detail || "Não deu para concluir.");
  return dados;
}

function recado(id, texto, erro = false) {
  const elemento = ler(id);
  elemento.textContent = texto;
  elemento.className = erro ? "recado erro" : "recado";
}

function desenharEventos(eventos) {
  ler("events").innerHTML = eventos.length
    ? eventos.map((evento) =>
        `<div class="linha"><div><strong>${escapar(evento.name)}</strong>` +
        `<small>${escapar(evento.category)} · ${escapar(evento.date)} · ${escapar(evento.location)}</small></div>` +
        `<button data-apagar-evento="${evento.id}">remover</button></div>`).join("")
    : `<p class="vazio">Nenhuma oficina cadastrada ainda.</p>`;
}

function desenharParticipantes(participantes) {
  ler("participants").innerHTML = participantes.length
    ? participantes.map((pessoa) =>
        `<div class="linha"><div><strong>${escapar(pessoa.name)}</strong>` +
        `<small>${escapar(pessoa.email)}</small></div>` +
        `<button data-apagar-participante="${pessoa.id}">remover</button></div>`).join("")
    : `<p class="vazio">Ninguém cadastrado ainda.</p>`;
}

function desenharInscricoes(inscricoes) {
  ler("registrations").innerHTML = inscricoes.length
    ? inscricoes.map((inscricao) =>
        `<div class="linha"><div><strong>Inscrição #${inscricao.id}</strong>` +
        `<small>oficina #${inscricao.event_id} · pessoa #${inscricao.participant_id} · ${escapar(inscricao.status)}</small></div>` +
        (inscricao.status === "active" ? `<button data-cancelar="${inscricao.id}">cancelar</button>` : "") +
        `</div>`).join("")
    : `<p class="vazio">Nenhuma inscrição feita ainda.</p>`;
}

function preencherSelects(eventos, participantes) {
  ler("event-select").innerHTML = eventos.map((evento) =>
    `<option value="${evento.id}">${escapar(evento.name)}</option>`).join("");
  ler("participant-select").innerHTML = participantes.map((pessoa) =>
    `<option value="${pessoa.id}">${escapar(pessoa.name)}</option>`).join("");
}

async function atualizar() {
  const eventos = await pedir("/api/eventos");
  desenharEventos(eventos);
  const [participantes, inscricoes] = await Promise.all([
    pedir("/api/participantes"), pedir("/api/inscricoes")]);
  desenharParticipantes(participantes);
  desenharInscricoes(inscricoes);
  preencherSelects(eventos, participantes);
}

function ligarFormulario(formId, caminho, recadoId, mensagemOk, corpo) {
  ler(formId).addEventListener("submit", async (evento) => {
    evento.preventDefault();
    try {
      const dados = corpo ? corpo() : Object.fromEntries(new FormData(evento.target).entries());
      await pedir(caminho, { method: "POST", body: JSON.stringify(dados) });
      evento.target.reset();
      recado(recadoId, mensagemOk);
      await atualizar();
    } catch (erro) {
      recado(recadoId, erro.message, true);
    }
  });
}

ligarFormulario("event-form", "/api/eventos", "event-message", "Oficina adicionada.");
ligarFormulario("participant-form", "/api/participantes", "participant-message", "Pessoa adicionada.");
ligarFormulario("registration-form", "/api/inscricoes", "registration-message", "Inscrição feita.",
  () => ({ event_id: Number(ler("event-select").value), participant_id: Number(ler("participant-select").value) }));

document.addEventListener("click", async (evento) => {
  const alvo = evento.target;
  try {
    if (alvo.dataset.apagarEvento) await pedir("/api/eventos/" + alvo.dataset.apagarEvento, { method: "DELETE" });
    if (alvo.dataset.apagarParticipante) await pedir("/api/participantes/" + alvo.dataset.apagarParticipante, { method: "DELETE" });
    if (alvo.dataset.cancelar) await pedir("/api/inscricoes/" + alvo.dataset.cancelar + "/cancelar", { method: "PATCH" });
    if (alvo.dataset.apagarEvento || alvo.dataset.apagarParticipante || alvo.dataset.cancelar) await atualizar();
  } catch (erro) { alert(erro.message); }
});

atualizar().catch((erro) => recado("event-message", erro.message, true));
"""


HTML = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Oficina</title>
<style>$css</style>
</head>
<body>
<header>
  <div class="limite">
    <a class="marca" href="/">Oficina<span>.</span></a>
  </div>
</header>
<main class="limite">

  <section class="bloco">
    <h2>Nova oficina</h2>
    <form id="event-form" class="form">
      <div class="campo"><label for="event-name">nome</label><input id="event-name" name="name" required placeholder="Oficina de cerâmica"></div>
      <div class="campo"><label for="event-date">data</label><input id="event-date" name="date" type="date" required></div>
      <div class="campo"><label for="event-location">local</label><input id="event-location" name="location" required placeholder="Sala 3 — bloco B"></div>
      <div class="campo"><label for="event-description">descrição</label><textarea id="event-description" name="description" placeholder="O que vai acontecer?"></textarea></div>
      <button type="submit">criar oficina</button>
    </form>
    <p id="event-message" class="recado"></p>
  </section>

  <section class="bloco">
    <h2>Oficinas</h2>
    <div id="events" class="lista"></div>
  </section>

  <section class="bloco">
    <h2>Quem vai participar</h2>
    <form id="participant-form" class="form">
      <div class="campo"><label for="person-name">nome</label><input id="person-name" name="name" required placeholder="Maria Silva"></div>
      <div class="campo"><label for="person-email">e-mail</label><input id="person-email" name="email" type="email" required placeholder="maria@exemplo.com"></div>
      <button type="submit">adicionar pessoa</button>
    </form>
    <p id="participant-message" class="recado"></p>
    <div id="participants" class="lista"></div>
  </section>

  <section class="bloco">
    <h2>Inscrições</h2>
    <form id="registration-form" class="form">
      <div class="campo"><label for="event-select">oficina</label><select id="event-select" name="event_id" required></select></div>
      <div class="campo"><label for="participant-select">pessoa</label><select id="participant-select" name="participant_id" required></select></div>
      <button type="submit">inscrever</button>
    </form>
    <p id="registration-message" class="recado"></p>
    <div id="registrations" class="lista"></div>
  </section>

</main>
<footer class="limite">
  <p>Oficina</p>
</footer>
<script>$js</script>
</body>
</html>
"""


def render() -> str:
    """Renderiza a página do Workshop."""
    return Template(HTML).substitute(css=CSS, js=JS)
