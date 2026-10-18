/* Local review never sends inquiries or paid chat requests. Public hosting retains the original submit flow. */
if(location.protocol==='file:'||['localhost','127.0.0.1','[::1]'].includes(location.hostname)){
 const nativeFetch=window.fetch.bind(window);window.fetch=(input,init={})=>{const method=String(init.method||(input&&input.method)||'GET').toUpperCase();if(!['GET','HEAD','OPTIONS'].includes(method))return Promise.reject(new Error('Local review: your message has not been sent.'));return nativeFetch(input,init)};
 document.addEventListener('submit',e=>e.preventDefault(),true);
}