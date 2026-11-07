// Interface do Confera. Conversa SOMENTE com o API Gateway (mesma origem).
const $ = (selector) => document.querySelector(selector);
const formData = (form) => Object.fromEntries(new FormData(form).entries());

// Escapa HTML para que textos digitados pelo usuário nunca virem código (evita XSS).
const esc = (value) => String(value).replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

async function request(path, options = {}) {
  const response = await fetch(path, { headers: { "Content-Type": "application/json" }, ...options });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "Não foi possível concluir a operação.");
  return data;
}

function message(selector, text) { $(selector).textContent = text; }

// Painel "Microsserviços em execução": nome, porta e status de cada serviço.
async function loadServices() {
  const services = await request("/services");
  $("#services").innerHTML = services.map((s) =>
    `<div class="item"><div><strong>${esc(s.name)}</strong>` +
    `<small>${esc(s.role)} · porta <span class="port">${s.port}</span></small></div>` +
    `<span class="badge ${s.status}">${s.status}</span></div>`).join("");
}

const emptyMsg = (text) => `<p class="empty">${text}</p>`;

async function loadAll() {
  const [events, participants, registrations] = await Promise.all([
    request("/events"), request("/participants"), request("/registrations")]);

  $("#events").innerHTML = events.length ? events.map((e) =>
    `<div class="item"><div><strong>${esc(e.name)}</strong>` +
    `<small>${esc(e.category)} · ${esc(e.date)} · ${esc(e.location)}</small></div>` +
    `<button data-delete-event="${e.id}">Excluir</button></div>`).join("") : emptyMsg("Nenhum evento cadastrado.");

  $("#participants").innerHTML = participants.length ? participants.map((p) =>
    `<div class="item"><div><strong>${esc(p.name)}</strong><small>${esc(p.email)}</small></div>` +
    `<button data-delete-participant="${p.id}">Excluir</button></div>`).join("") : emptyMsg("Nenhum participante cadastrado.");

  $("#registrations").innerHTML = registrations.length ? registrations.map((r) =>
    `<div class="item"><div><strong>Inscrição #${r.id}</strong>` +
    `<small>Evento #${r.event_id} · Participante #${r.participant_id} · ${esc(r.status)}</small></div>` +
    (r.status === "active" ? `<button data-cancel="${r.id}">Cancelar</button>` : "") + `</div>`).join("") : emptyMsg("Nenhuma inscrição cadastrada.");

  $("#event-select").innerHTML = events.map((e) => `<option value="${e.id}">${esc(e.name)}</option>`).join("");
  $("#participant-select").innerHTML = participants.map((p) => `<option value="${p.id}">${esc(p.name)}</option>`).join("");
}

// Envia um formulário, mostra a mensagem de sucesso/erro e recarrega as listas.
function bindForm(formSelector, path, messageSelector, okText, buildBody = formData) {
  $(formSelector).addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      await request(path, { method: "POST", body: JSON.stringify(buildBody(e.target)) });
      e.target.reset();
      message(messageSelector, okText);
      await loadAll();
    } catch (err) { message(messageSelector, err.message); }
  });
}

bindForm("#event-form", "/events", "#event-message", "Evento cadastrado.");
bindForm("#participant-form", "/participants", "#participant-message", "Participante cadastrado.");
bindForm("#registration-form", "/registrations", "#registration-message", "Inscrição realizada.",
  () => ({ event_id: Number($("#event-select").value), participant_id: Number($("#participant-select").value) }));

document.addEventListener("click", async (e) => {
  const t = e.target;
  try {
    if (t.dataset.deleteEvent) await request("/events/" + t.dataset.deleteEvent, { method: "DELETE" });
    if (t.dataset.deleteParticipant) await request("/participants/" + t.dataset.deleteParticipant, { method: "DELETE" });
    if (t.dataset.cancel) await request("/registrations/" + t.dataset.cancel + "/cancel", { method: "PATCH" });
    if (t.id === "refresh-services") await loadServices();
    if (t.dataset.deleteEvent || t.dataset.deleteParticipant || t.dataset.cancel) await loadAll();
  } catch (err) { alert(err.message); }
});

loadServices().catch(console.error);
loadAll().catch(console.error);
