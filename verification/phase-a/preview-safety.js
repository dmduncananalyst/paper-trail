/* This local visual review preserves guided intake but never sends an inquiry. */
(() => { const originalFetch=window.fetch.bind(window); window.fetch=(url,options={})=>{ if((options.method||'GET').toUpperCase()!=='GET')return Promise.reject(new Error('Design preview: your note has not been sent. Sending is disabled here.'));return originalFetch(url,options); }; })();
