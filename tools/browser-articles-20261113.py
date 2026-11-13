"""Disposable browser checks; all output stays outside the repository."""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
import json, tempfile, sys
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
A=json.loads((ROOT/'verification/articles-20261113/approved-content.json').read_text(encoding='utf8'))
out=Path(tempfile.mkdtemp(prefix='paper-trail-articles-20261113-'))
class Handler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
results=[]
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
        context=browser.new_context()
        context.route('https://**/*',lambda route:route.abort())
        page=context.new_page()
        langs=['','es','fa','hy','zh-CN','ko','tl','te','ru','ar'] if '--all-languages' in sys.argv else ['']
        routes=[(lang+'/' if lang else '')+a['slug'] for lang in langs for a in A]
        routes += [(lang+'/' if lang else '')+'blog.html' for lang in langs]
        routes += ['business-loan-proceeds-nobody-can-show-where-money-went.html']
        for width in [390,834,1440]:
            page.set_viewport_size({'width':width,'height':1000})
            for route in routes:
                page.goto(f'http://127.0.0.1:{server.server_port}/{route}',wait_until='networkidle')
                page.evaluate('document.fonts.ready')
                state=page.evaluate('''() => ({overflow:document.documentElement.scrollWidth>innerWidth+2,brokenImages:[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.getAttribute('src')),title:document.querySelector('h1')?.textContent,hero:document.querySelector('.reading-masthead img')?.getBoundingClientRect().toJSON()})''')
                results.append({'route':route,'width':width,**state})
                assert not state['overflow'] and not state['brokenImages'],results[-1]
                if route.startswith(('ar/','fa/')) and not route.endswith('/blog.html'):
                    assert page.locator('.reading-spread p').first.evaluate('(e)=>getComputedStyle(e).direction')=='rtl',route
                if route in [A[0]['slug'],'blog.html','business-loan-proceeds-nobody-can-show-where-money-went.html']:
                    page.screenshot(path=str(out/(route+f'-{width}.png')),full_page=False)
        switches=0
        if '--all-languages' in sys.argv:
            for a in A:
                for lang in langs[1:]:
                    page.goto(f'http://127.0.0.1:{server.server_port}/'+a['slug'],wait_until='networkidle')
                    page.select_option('#language',lang)
                    page.wait_for_url('**/'+lang+'/'+a['slug'])
                    switches+=1
            for lang in langs[1:]:
                page.goto(f'http://127.0.0.1:{server.server_port}/'+lang+'/blog.html',wait_until='networkidle')
                page.locator('.blog-story a').first.click()
                page.wait_for_url('**/'+lang+'/'+A[0]['slug'])
                switches+=1
        browser.close()
finally:server.shutdown()
(out/'results.json').write_text(json.dumps(results,indent=2),encoding='utf8')
report={'checks':len(results),'language_and_archive_navigation_checks':switches,'errors':0,'output':str(out)}
(ROOT/'verification/articles-20261113/browser-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,indent=2))
