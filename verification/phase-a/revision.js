(() => {
 const menu=document.querySelector('.pt-menu'),nav=document.querySelector('#pt-navigation'),services=document.querySelector('.pt-services-toggle'),directory=document.querySelector('#pt-directory');
 const setOpen=(button,panel,open,hidden=true)=>{button?.setAttribute('aria-expanded',String(open));if(hidden)panel.hidden=!open;else panel.classList.toggle('is-open',open);const s=button?.querySelector('span');if(s)s.textContent=open?'−':'+'};
 menu?.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';setOpen(menu,nav,open,false);if(!open)setOpen(services,directory,false)});
 services?.addEventListener('click',()=>setOpen(services,directory,services.getAttribute('aria-expanded')!=='true'));
 document.addEventListener('keydown',e=>{if(e.key!=='Escape')return;if(!directory.hidden){setOpen(services,directory,false);services.focus()}else if(nav.classList.contains('is-open')){setOpen(menu,nav,false,false);menu.focus()}});
 nav?.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{setOpen(menu,nav,false,false);setOpen(services,directory,false)}));
 if(new URLSearchParams(location.search).has('menu')){if(matchMedia('(max-width:900px)').matches)setOpen(menu,nav,true,false);setOpen(services,directory,true)}
 const dialog=document.querySelector('.email-dialog');let trigger;
 document.querySelectorAll('[data-email]').forEach(b=>b.addEventListener('click',()=>{trigger=b;dialog.querySelector('.email-status').textContent='';dialog.showModal()}));
 dialog?.querySelector('.email-close').addEventListener('click',()=>dialog.close());
 dialog?.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close()}});
 dialog?.addEventListener('close',()=>trigger?.focus());
 dialog?.querySelector('.copy-email').addEventListener('click',async()=>{const address='bookkeeping@papertrailusa.com',status=dialog.querySelector('.email-status');try{await navigator.clipboard.writeText(address);status.textContent='Email address copied.'}catch{const field=document.createElement('textarea');field.value=address;dialog.append(field);field.select();const copied=document.execCommand('copy');field.remove();status.textContent=copied?'Email address copied.':'Select and copy: '+address}});
})();
