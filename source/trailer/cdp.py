"""Tiny helper: talk to the local headless Edge started with --remote-debugging-port=9333."""
import sys, json, urllib.request
S = 'C:/Users/toont/AppData/Local/Temp/claude/2adc7078fe966463/ae6463b0-0602-40b5-a822-8d90e035db45/scratchpad'
sys.path.insert(0, S + '/pylib')
import websocket

class Page:
    def __init__(self, port=9333, match=None):
        tabs = json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % port))
        tabs = [t for t in tabs if t['type'] == 'page' and (match is None or match in t['url'])]
        self.ws = websocket.create_connection(tabs[0]['webSocketDebuggerUrl'], max_size=None, timeout=600)
        self.n = 0

    def cmd(self, method, **params):
        self.n += 1
        self.ws.send(json.dumps({'id': self.n, 'method': method, 'params': params}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get('id') == self.n:
                if 'error' in m: raise RuntimeError(m['error'])
                return m['result']

    def js(self, expr):
        r = self.cmd('Runtime.evaluate', expression=expr, awaitPromise=True, returnByValue=True)
        if 'exceptionDetails' in r:
            raise RuntimeError(json.dumps(r['exceptionDetails'])[:1500])
        return r['result'].get('value')

    def goto(self, url):
        self.cmd('Page.navigate', url=url)
