/** Native transport installed only by the Android shell. Desktop uses fetch. */
type NativeWindow = Window & {
  FuorigiriNative?: {postMessage: (value: string) => void};
  fuorigiriNativeResponse?: (value: any) => void;
};
const native = window as NativeWindow;
const pending = new Map<string, {resolve: (r: Response) => void; reject: (e: Error) => void}>();
const original = window.fetch.bind(window);
let sequence = 0;
const fromBase64 = (text: string) => Uint8Array.from(atob(text), c => c.charCodeAt(0));
async function base64(blob: Blob) {
  return new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result).split(',')[1] || '');
    reader.onerror = () => reject(new Error('Lettura del file non riuscita.'));
    reader.readAsDataURL(blob);
  });
}

if (native.FuorigiriNative) {
  document.documentElement.classList.add('android');
  native.fuorigiriNativeResponse = (message: any) => {
    const request = pending.get(message.id);
    if (!request) return;
    pending.delete(message.id);
    if (message.error) {
      request.reject(new Error(message.error));
      return;
    }
    const data = message.response;
    request.resolve(
      new Response(data.status === 204 ? null : fromBase64(data.body), {status: data.status, headers: data.headers})
    );
  };
  window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
    const request = new Request(
      new URL(typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url, location.href),
      init
    );
    const url = new URL(request.url);
    if (url.origin !== location.origin || !url.pathname.startsWith('/api/v1/')) return original(input, init);
    const body = await request.blob();
    if (body.size > 80_000_000) throw new Error('Il limite per un file su Android è 80 MB.');
    const payload = {
      path: url.pathname + url.search,
      method: request.method,
      headers: Object.fromEntries(request.headers),
      body: await base64(body)
    };
    return new Promise<Response>((resolve, reject) => {
      const id = String(++sequence);
      pending.set(id, {resolve, reject});
      native.FuorigiriNative!.postMessage(JSON.stringify({id, type: 'request', payload}));
    });
  };
  // Every existing export uses a blob-backed anchor. Copy that blob through SAF;
  // do not convert a content URI into a filesystem path or require storage access.
  const exportAnchor = (anchor: HTMLAnchorElement) => {
    original(anchor.href)
      .then(r => r.blob())
      .then(async blob => {
        if (blob.size > 80_000_000) throw new Error('Export oltre il limite mobile di 80 MB.');
        native.FuorigiriNative!.postMessage(
          JSON.stringify({
            type: 'export',
            id: String(++sequence),
            name: anchor.download,
            mime: blob.type,
            body: await base64(blob)
          })
        );
      })
      .catch(error => alert(error.message));
  };
  const originalClick = HTMLAnchorElement.prototype.click;
  HTMLAnchorElement.prototype.click = function () {
    if (this.hasAttribute('download') && this.href.startsWith('blob:')) {
      exportAnchor(this);
      return;
    }
    originalClick.call(this);
  };
  document.addEventListener(
    'click',
    event => {
      const anchor = (event.target as Element)?.closest?.('a[download]') as HTMLAnchorElement | null;
      if (!anchor || !anchor.href.startsWith('blob:')) return;
      event.preventDefault();
      exportAnchor(anchor);
    },
    true
  );
}

/** Temporary orientation request owned by the chart; Android restores its previous policy. */
export function setChartLandscape(landscape: boolean) {
  native.FuorigiriNative?.postMessage(JSON.stringify({type: 'chartOrientation', landscape}));
}
