// Lightweight UI helpers: toasts, ajax submit, theme init
(function () {
    function createToast(message, type='success', timeout=4000) {
        let container = document.querySelector('.ui-toasts');
        if(!container){ container = document.createElement('div'); container.className='ui-toasts'; document.body.appendChild(container) }

        const t = document.createElement('div');
        t.className = 'ui-toast ' + (type==='success'? 'success' : 'error');
        t.innerHTML = `<div class="flex-grow-1">${message}</div><button class="btn-close" aria-label="Close"></button>`;
        container.appendChild(t);

        t.querySelector('.btn-close').addEventListener('click', ()=> t.remove());
        setTimeout(()=> { if(t.parentNode) t.remove() }, timeout);
        return t;
    }

    async function ajaxSubmit(form, onSuccess, onError) {
        const url = form.action || window.location.href;
        const data = new FormData(form);
        try {
            const resp = await fetch(url, { method: form.method|| 'POST', body: data, headers: { 'X-Requested-With':'XMLHttpRequest' } });
            const contentType = resp.headers.get('content-type')||'';
            let json = null;
            if(contentType.includes('application/json')) json = await resp.json();
            if(resp.ok){ if(onSuccess) onSuccess(json, resp); } else { if(onError) onError(json, resp); else createToast('Request failed', 'error') }
        } catch(err){ if(onError) onError(null, err); else createToast('Network error', 'error') }
    }

    function initTheme() {
        try{
            const saved = localStorage.getItem('theme');
            if(saved) document.documentElement.setAttribute('data-bs-theme', saved);
        }catch(e){}
    }

    // Public API
    window.UI = {
        toast: createToast,
        ajaxSubmit: ajaxSubmit,
        init: function(){ initTheme() }
    };

    document.addEventListener('DOMContentLoaded', ()=>{
        UI.init();
        // auto-bind forms with data-ajax
        document.querySelectorAll('form[data-ajax="true"]').forEach(f=>{
            f.addEventListener('submit', function(e){ e.preventDefault(); UI.ajaxSubmit(this, (j)=>{ UI.toast('Saved', 'success') }, (j)=>{ UI.toast('Save failed', 'error') }) })
        });
        // Debounced navbar search: delay submit while typing
        document.querySelectorAll('.nav-search input[type="search"]').forEach(input=>{
            let timer = null;
            const form = input.closest('form');
            input.addEventListener('input', function(){
                if(timer) clearTimeout(timer);
                timer = setTimeout(()=>{ if(form) form.submit(); }, 650);
            });
        });

        // Dropdown small animation hooks
        document.querySelectorAll('.dropdown').forEach(dd=>{
            dd.addEventListener('show.bs.dropdown', ()=>{
                const menu = dd.querySelector('.dropdown-menu'); if(menu) { menu.style.opacity = 0; menu.style.transform = 'translateY(6px)'; setTimeout(()=>{ menu.style.transition = 'all .18s ease'; menu.style.opacity = 1; menu.style.transform='translateY(0)' }, 10) }
            });
            dd.addEventListener('hide.bs.dropdown', ()=>{
                const menu = dd.querySelector('.dropdown-menu'); if(menu) { menu.style.opacity = 0; menu.style.transform = 'translateY(6px)' }
            });
        });
    });

})();
