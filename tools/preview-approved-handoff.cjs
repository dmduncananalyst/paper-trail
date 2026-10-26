/* Local-only public build and preview, using the existing public build allowlist.
 * Runs with Node 22+; does not execute PowerShell scripts or alter execution policy.
 */
'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),http=require('node:http');
const root=path.resolve(__dirname,'..');
const args=process.argv.slice(2),port=Number(args.find(x=>/^--port=/.test(x))?.split('=')[1]||8787);
const output=args.find(x=>/^--output=/.test(x))?.slice(9)||fs.mkdtempSync(path.join(os.tmpdir(),'paper-trail-review-'));
const destination=path.resolve(output);
if(destination===root||destination.startsWith(root+path.sep))throw Error('Review output must be outside the repository.');
fs.mkdirSync(destination,{recursive:true});
if(fs.readdirSync(destination).length&&!args.includes('--refresh'))throw Error('Use an empty review output directory, or --refresh for an existing local review build.');
if(args.includes('--refresh')&&!fs.existsSync(path.join(destination,'.nojekyll')))throw Error('Refresh requires an existing review build.');
function needsCopy(source,target){if(fs.statSync(source).isDirectory())return true;if(!fs.existsSync(target))return true;const a=fs.statSync(source),b=fs.statSync(target);return a.size!==b.size||a.mtimeMs>b.mtimeMs;}
for(const item of fs.readdirSync(root,{withFileTypes:true})){
  if(item.isFile()&&(/\.(html|svg)$/.test(item.name)||['CNAME','robots.txt','sitemap.xml','sitemap-translations.xml'].includes(item.name)))fs.copyFileSync(path.join(root,item.name),path.join(destination,item.name));
}
for(const folder of ['assets','state-records','ar','es','fa','hy','ko','ru','te','tl','zh-CN'])fs.cpSync(path.join(root,folder),path.join(destination,folder),{recursive:true,dereference:false,filter:needsCopy});
const allowed=new Set(['.html','.svg','.css','.js','.json','.png','.jpg','.jpeg','.webp','.gif','.ico','.woff','.woff2','.ttf','.otf','.mp4','.webm','.xml','.txt']);
const pages=[];
function walk(dir){for(const item of fs.readdirSync(dir,{withFileTypes:true})){
 const file=path.join(dir,item.name);if(item.isSymbolicLink())throw Error('Symbolic link in public assets.');
 if(item.isDirectory())walk(file);else{if(!allowed.has(path.extname(file))&&!['CNAME','.nojekyll'].includes(item.name))throw Error('Unexpected public asset type: '+path.relative(destination,file));if(item.name.endsWith('.html'))pages.push(file);}
}}
walk(destination);
// Same analytics insertion as build-public-site.ps1. Local review blocks third-party traffic.
const analytics='<!-- Google tag (gtag.js) -->\n<script async src="https://www.googletagmanager.com/gtag/js?id=G-2SZSN9XXJZ"></script>\n<script>\n  window.dataLayer = window.dataLayer || [];\n  function gtag(){dataLayer.push(arguments);}\n  gtag(\'js\', new Date());\n\n  gtag(\'config\', \'G-2SZSN9XXJZ\');\n</script>';
for(const file of pages){let html=fs.readFileSync(file,'utf8');if(!html.includes('</head>'))throw Error('Missing head: '+path.relative(destination,file));if(!html.includes(analytics))fs.writeFileSync(file,html.replace('</head>','\n'+analytics+'\n</head>'));}
fs.writeFileSync(path.join(destination,'.nojekyll'),'');
for(const privatePath of ['tools','verification','.git','AGENTS.md','Paper-Trail-Master-Website-Instructions.md'])if(fs.existsSync(path.join(destination,privatePath)))throw Error('Private development content entered build.');
console.log(JSON.stringify({build:'passed',pages:pages.length,output:destination,preview:'http://127.0.0.1:'+port+'/packages.html'}));
if(args.includes('--build-only'))process.exit(0);
const types={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json','.svg':'image/svg+xml','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg','.mp4':'video/mp4','.woff2':'font/woff2','.ttf':'font/ttf','.xml':'application/xml'};
http.createServer((req,res)=>{
 let route;try{route=decodeURIComponent(new URL(req.url,'http://localhost').pathname)}catch{res.writeHead(400);return res.end()}
 const file=path.resolve(destination,'.'+(route==='/'?'/index.html':route));
 if(req.method!=='GET'&&req.method!=='HEAD'){res.writeHead(405);return res.end('Local review does not accept submissions.');}
 if(!file.startsWith(destination+path.sep)||!fs.existsSync(file)||!fs.statSync(file).isFile()){res.writeHead(404);return res.end('Not found');}
 // Prevent this local preview from contacting analytics, HubSpot or paid services.
 res.setHeader('Content-Security-Policy',"default-src 'self' data: blob:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data: blob:; frame-src 'none'; form-action 'none'; object-src 'none'; base-uri 'self'");
 res.setHeader('Cache-Control','no-store');res.setHeader('X-Content-Type-Options','nosniff');res.setHeader('Content-Type',types[path.extname(file)]||'application/octet-stream');
 if(req.method==='HEAD')return res.end();fs.createReadStream(file).pipe(res);
}).listen(port,'127.0.0.1',()=>console.log('Local preview ready on http://127.0.0.1:'+port));
