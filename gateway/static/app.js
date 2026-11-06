const $ = (selector) => document.querySelector(selector);
const formData = (form) => Object.fromEntries(new FormData(form).entries());
async function request(path,options={}) {
  const response = await fetch(path,{headers:{"Content-Type":"application/json"},...options});
  const data = await response.json().catch(()=>({}));
  if (!response.ok) throw new Error(data.detail || "Não foi possível concluir a operação.");
  return data;
}
function message(selector,text) { $(selector).textContent=text; }
async function loadAll() {
  const [events,participants,registrations]=await Promise.all([request("/events"),request("/participants"),request("/registrations")]);
  $("#events").innerHTML=events.length?events.map(e=>`<div class="item"><div><strong>${e.name}</strong><small>${e.category} · ${e.date} · ${e.location}</small></div><button data-delete-event="${e.id}">Excluir</button></div>`).join(""):'<p class="empty">Nenhum evento cadastrado.</p>';
  $("#participants").innerHTML=participants.length?participants.map(p=>`<div class="item"><div><strong>${p.name}</strong><small>${p.email}</small></div><button data-delete-participant="${p.id}">Excluir</button></div>`).join(""):'<p class="empty">Nenhum participante cadastrado.</p>';
  $("#registrations").innerHTML=registrations.length?registrations.map(r=>`<div class="item"><div><strong>Inscrição #${r.id}</strong><small>Evento #${r.event_id} · Participante #${r.participant_id} · ${r.status}</small></div>${r.status==="active"?`<button data-cancel="${r.id}">Cancelar</button>`:""}</div>`).join(""):'<p class="empty">Nenhuma inscrição cadastrada.</p>';
  $("#event-select").innerHTML=events.map(e=>`<option value="${e.id}">${e.name}</option>`).join("");
  $("#participant-select").innerHTML=participants.map(p=>`<option value="${p.id}">${p.name}</option>`).join("");
}
$("#event-form").addEventListener("submit",async e=>{e.preventDefault();try{await request("/events",{method:"POST",body:JSON.stringify(formData(e.target))});e.target.reset();message("#event-message","Evento cadastrado.");await loadAll();}catch(err){message("#event-message",err.message);}});
$("#participant-form").addEventListener("submit",async e=>{e.preventDefault();try{await request("/participants",{method:"POST",body:JSON.stringify(formData(e.target))});e.target.reset();message("#participant-message","Participante cadastrado.");await loadAll();}catch(err){message("#participant-message",err.message);}});
$("#registration-form").addEventListener("submit",async e=>{e.preventDefault();try{await request("/registrations",{method:"POST",body:JSON.stringify({event_id:Number($("#event-select").value),participant_id:Number($("#participant-select").value)})});message("#registration-message","Inscrição realizada.");await loadAll();}catch(err){message("#registration-message",err.message);}});
document.addEventListener("click",async e=>{const t=e.target;try{if(t.dataset.deleteEvent)await request("/events/"+t.dataset.deleteEvent,{method:"DELETE"});if(t.dataset.deleteParticipant)await request("/participants/"+t.dataset.deleteParticipant,{method:"DELETE"});if(t.dataset.cancel)await request("/registrations/"+t.dataset.cancel+"/cancel",{method:"PATCH"});await loadAll();}catch(err){alert(err.message);}});
loadAll().catch(err=>console.error(err));
