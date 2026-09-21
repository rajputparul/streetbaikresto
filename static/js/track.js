const query=new URLSearchParams(location.search).get('order');
if(query) document.querySelector('#orderId').value=query;
document.querySelector('#trackForm').onsubmit=async e=>{
  e.preventDefault();
  const id=document.querySelector('#orderId').value.trim().toUpperCase();
  const el=document.querySelector('#trackResult');
  el.innerHTML='<p class="empty">Checking order status...</p>';
  try{
    const r=await fetch('/api/orders/'+encodeURIComponent(id)+'/');
    const d=await r.json();
    if(!r.ok||!d.ok){el.innerHTML=`<div class="error-box">${d.error||'Order not found.'}</div>`;return;}
    const o=d.order;
    const active=d.statuses.indexOf(o.status);
    el.innerHTML=`<section class="track-card"><div class="track-head"><div><span class="eyebrow">ORDER ID</span><h2>${o.public_id}</h2><p>${o.customer_name} - ${o.order_type}</p></div><strong>Rs ${o.total.toFixed(0)}</strong></div><div class="timeline">${d.statuses.map((s,i)=>`<div class="step ${i<=active?'done':''} ${i===active?'current':''}"><span>${i<=active?'OK':i+1}</span><b>${s}</b></div>`).join('')}</div><div class="track-items">${o.items.map(x=>`<div><span>${x.name} x ${x.quantity}</span><b>Rs ${Number(x.line_total).toFixed(0)}</b></div>`).join('')}</div><p class="track-note">Last updated: ${o.updated_at}</p></section>`;
  }catch(error){
    console.error(error);
    el.innerHTML='<div class="error-box">Unable to check the order right now.</div>';
  }
};
