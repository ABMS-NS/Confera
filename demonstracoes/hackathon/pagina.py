"""Página da aplicação Hackathon (Maratona de Programação).

Interface de terminal, escura e monoespaçada. A página é só a aplicação:
títulos de seção e as partes funcionais.
"""
from string import Template


CSS = """
:root {
  --fundo: #0b0f14;
  --painel: #111820;
  --borda: #223040;
  --texto: #c9d6e2;
  --fraco: #7d8fa3;
  --acento: #7ee787;
  --alerta: #ff7b72;
}
* { box-sizing: border-box; }
html, body { margin: 0; }
body {
  background: var(--fundo);
  color: var(--texto);
  font-family: "SFMono-Regular", "JetBrains Mono", Menlo, Consolas, monospace;
  font-size: 13px;
  line-height: 1.65;
  background-image:
    linear-gradient(rgba(126, 231, 135, .035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(126, 231, 135, .035) 1px, transparent 1px);
  background-size: 28px 28px;
}
.area { width: min(940px, 94%); margin: 0 auto; }
header {
  border-bottom: 1px solid var(--borda);
  background: rgba(11, 15, 20, .88);
  padding: 26px 0 18px;
}
h1 {
  font-size: 20px;
  margin: 0;
  letter-spacing: .12em;
  text-transform: uppercase;
  color: #f0f6fc;
}
h1::after {
  content: "_";
  color: var(--acento);
  animation: piscar 1.1s steps(1) infinite;
}
@keyframes piscar { 50% { opacity: 0; } }
.tagline { color: var(--fraco); margin: 8px 0 0; }
main { padding: 26px 0 56px; }
section {
  border: 1px solid var(--borda);
  background: var(--painel);
  padding: 18px 20px;
  margin-bottom: 18px;
}
section > h2 {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: .14em;
  color: #f0f6fc;
  margin: 0 0 14px;
  font-weight: normal;
}
section > h2 .num {
  color: var(--acento);
  margin-right: 8px;
}
form { display: grid; gap: 12px; grid-template-columns: 1fr 1fr; }
.campo { display: grid; gap: 4px; }
label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: .1em;
  color: var(--fraco);
}
label::before { content: "$ "; color: var(--acento); }
input, textarea, select {
  font: inherit;
  color: var(--texto);
  background: #0b0f14;
  border: 1px solid var(--borda);
  border-radius: 0;
  padding: 8px 10px;
}
input:focus, textarea:focus, select:focus {
  outline: none;
  border-color: var(--acento);
  box-shadow: 0 0 0 1px rgba(126, 231, 135, .35);
}
textarea { min-height: 68px; resize: vertical; }
button {
  grid-column: 1 / -1;
  justify-self: start;
  font: inherit;
  text-transform: uppercase;
  letter-spacing: .1em;
  color: var(--fundo);
  background: var(--acento);
  border: 0;
  padding: 9px 18px;
  cursor: pointer;
}
button:hover { background: #a5f0ab; }
.saida { min-height: 1.3em; margin: 12px 0 0; color: var(--fraco); }
.saida::before { content: "// "; }
.saida.erro { color: var(--alerta); }
.linha {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: baseline;
  padding: 10px 0;
  border-top: 1px dashed var(--borda);
}
.linha:first-child { border-top: 0; }
.linha strong { color: #f0f6fc; font-weight: normal; }
.linha small { display: block; color: var(--fraco); }
.linha button {
  all: unset;
  cursor: pointer;
  color: var(--alerta);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: .08em;
  border-bottom: 1px dotted var(--alerta);
}
.vazio { color: var(--fraco); margin: 6px 0; }
.vazio::before { content: "// "; }
footer {
  border-top: 1px solid var(--borda);
  padding: 18px 0 42px;
  color: var(--fraco);
}
@media (max-width: 620px) {
  form { grid-template-columns: 1fr; }
}
"""

JS = """
const campo = (id) => document.getElementById(id);

function esc(valor) {
  return String(valor).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

async function api(caminho, opcoes = {}) {
  const resposta = await fetch(caminho, {
    headers: { "Content-Type": "application/json" },
    ...opcoes
  });
  const dados = await resposta.json().catch(() => ({}));
  if (!resposta.ok) throw new Error(dados.detail || "falha na requisição");
  return dados;
}

function status(id, texto, erro = false) {
  const alvo = campo(id);
  alvo.textContent = texto;
  alvo.className = erro ? "saida erro" : "saida";
}

function renderEventos(eventos) {
  campo("events").innerHTML = eventos.length
    ? eventos.map((e) =>
        `<div class="linha"><div><strong>${esc(e.name)}</strong>` +
        `<small>${esc(e.category)} / ${esc(e.date)} / ${esc(e.location)}</small></div>` +
        `<button data-remover="${e.id}">remover</button></div>`).join("")
    : `<p class="vazio">nenhum evento registrado</p>`;
}

async function sincronizar() {
  renderEventos(await api("/api/eventos"));
}

campo("event-form").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  try {
    const corpo = Object.fromEntries(new FormData(evento.target).entries());
    await api("/api/eventos", { method: "POST", body: JSON.stringify(corpo) });
    evento.target.reset();
    status("event-message", "evento criado");
    await sincronizar();
  } catch (erro) {
    status("event-message", erro.message, true);
  }
});

document.addEventListener("click", async (evento) => {
  const alvo = evento.target;
  try {
    if (alvo.dataset.remover) {
      await api("/api/eventos/" + alvo.dataset.remover, { method: "DELETE" });
      await sincronizar();
    }
  } catch (erro) {
    status("event-message", erro.message, true);
  }
});

sincronizar().catch((erro) => status("event-message", erro.message, true));
"""


HTML = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>hackathon</title>
<style>$css</style>
</head>
<body>
<header>
  <div class="area">
    <h1>hackathon</h1>
    <p class="tagline">Maratona de Programação</p>
  </div>
</header>
<main class="area">

  <section>
    <h2><span class="num">01</span> criar evento</h2>
    <form id="event-form">
      <div class="campo"><label for="event-name">nome</label><input id="event-name" name="name" required placeholder="hackathon de inovação"></div>
      <div class="campo"><label for="event-date">data</label><input id="event-date" name="date" type="date" required></div>
      <div class="campo"><label for="event-location">local</label><input id="event-location" name="location" required placeholder="auditório / remoto"></div>
      <div class="campo"><label for="event-description">tema</label><input id="event-description" name="description" placeholder="problema a ser resolvido em 24h"></div>
      <button type="submit">executar</button>
    </form>
    <p id="event-message" class="saida"></p>
  </section>

  <section>
    <h2><span class="num">02</span> eventos</h2>
    <div id="events"></div>
  </section>

</main>
<footer>
  <div class="area">hackathon</div>
</footer>
<script>$js</script>
</body>
</html>
"""


def render() -> str:
    """Renderiza a página do Hackathon."""
    return Template(HTML).substitute(css=CSS, js=JS)
