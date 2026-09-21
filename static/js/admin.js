function csrfToken(){return document.cookie.split('; ').find(v=>v.startsWith('csrftoken='))?.split('=')[1]||''}
async function post(url,status){const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':csrfToken()},body:JSON.stringify({status})});const d=await r.json();if(!d.ok)alert(d.error||'Update failed');else location.reload()}
document.querySelectorAll('.status-row').forEach(row=>row.querySelectorAll('.status-btn').forEach(b=>b.onclick=()=>post('/staff/orders/'+row.dataset.order+'/status/',b.dataset.status)));
document.querySelectorAll('[data-res]').forEach(b=>b.onclick=()=>post('/staff/reservations/'+b.dataset.res+'/status/',b.dataset.status));
document.querySelectorAll('[data-review]').forEach(b=>b.onclick=()=>post('/staff/reviews/'+b.dataset.review+'/status/',b.dataset.status));
