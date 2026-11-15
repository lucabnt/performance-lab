import {useEffect, useId, useMemo, useRef, useState} from 'react';
import {ChartFrame, LoadingState, FloatingPanel} from '@cycling-suite/ui';
import {Dialog} from './Dialog';
import {language, tr} from './i18n';
import {setChartLandscape} from './mobile';
import {chartTablePage, chartSummary} from './chartAccessibility';
type Row = Record<string, any>;
let engine: Promise<any> | undefined;
function loadEngine() {
  return (engine ??= import('plotly.js-dist-min')
    .then(m => m.default)
    .catch(e => {
      engine = undefined;
      throw e;
    }));
}
const touchModes = new Map<HTMLElement, () => void>();
(window as Window & {fuorigiriChartBack?: () => boolean}).fuorigiriChartBack = () => {
  const dialogs = document.querySelectorAll('dialog[open]'),
    top = dialogs[dialogs.length - 1];
  for (const [element, leave] of [...touchModes].reverse())
    if (element.isConnected && element.closest('dialog') === (top || null)) {
      leave();
      return true;
    }
  const panel = top?.querySelector<HTMLDetailsElement>('.suite-floating-panel[open]');
  if (panel) {
    panel.open = false;
    return true;
  }
  return false;
};
const mobile = () => document.documentElement.classList.contains('android');

/** Heavy engine loads only once a figure reaches the viewport; offline bundled chunk. */
export function Plot({
  data,
  layout = {},
  onPick,
  onPoint
}: {
  data: any[];
  layout?: Row;
  onPick?: (t: number) => void;
  onPoint?: (p: any) => void;
}) {
  const [wide, setWide] = useState(false);
  useEffect(() => {
    if (!wide || !mobile()) return;
    setChartLandscape(true);
    return () => setChartLandscape(false);
  }, [wide]);
  return (
    <>
      <Chart
        data={data}
        layout={layout}
        onPick={onPick}
        onPoint={onPoint}
        expand={mobile() ? () => setWide(true) : undefined}
      />
      {wide && (
        <Dialog fullscreen title={tr('Esplora grafico')} onClose={() => setWide(false)}>
          <Chart data={data} layout={layout} onPick={onPick} onPoint={onPoint} wide />
        </Dialog>
      )}
    </>
  );
}
function Chart({
  data,
  layout,
  onPick,
  onPoint,
  expand,
  wide = false
}: {
  data: Row[];
  layout: Row;
  onPick?: (t: number) => void;
  onPoint?: (p: any) => void;
  expand?: () => void;
  wide?: boolean;
}) {
  const [viewportHeight, setViewportHeight] = useState(window.innerHeight);
  useEffect(() => {
    const resized = () => setViewportHeight(window.innerHeight);
    window.addEventListener('resize', resized);
    return () => window.removeEventListener('resize', resized);
  }, []);
  const wideHeight = viewportHeight;
  const android = mobile(),
    id = useId(),
    [mode, setMode] = useState('scroll'),
    [reset, setReset] = useState(0),
    [attempt, setAttempt] = useState(0),
    [status, setStatus] = useState('waiting'),
    [page, setPage] = useState(0);
  const view = useRef<{key: string; reset: number; axes: Row} | null>(null),
    shown = useRef(false),
    ref = useRef<HTMLDivElement>(null),
    canvas = useRef<HTMLDivElement>(null),
    callback = useRef(onPick),
    pointCallback = useRef(onPoint);
  callback.current = onPick;
  pointCallback.current = onPoint;
  const plotKey = JSON.stringify({data, layout}),
    summary = useMemo(() => chartSummary(data), [plotKey]);
  const table = chartTablePage(data, page),
    interacting = !android || mode !== 'scroll';
  useEffect(() => {
    setPage(0);
  }, [plotKey]);
  useEffect(() => {
    const el = ref.current;
    if (!android || mode === 'scroll' || !el) return;
    touchModes.set(el, () => setMode('scroll'));
    return () => {
      touchModes.delete(el);
    };
  }, [mode, android]);
  useEffect(() => {
    const host = ref.current,
      el = canvas.current;
    if (!host || !el) return;
    let active = true,
      plotly: any,
      observer: IntersectionObserver | undefined,
      resize: ResizeObserver | undefined,
      rendered = false;
    const render = async () => {
      if (rendered) return;
      rendered = true;
      setStatus('loading');
      try {
        plotly = await loadEngine();
        if (!active) return;
        const configured: Row = {
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          font: {family: 'Segoe UI, sans-serif', color: '#42566f'},
          margin: {l: 48, r: 25, t: 18, b: 44},
          height: 300,
          showlegend: true,
          legend: {orientation: 'h', y: 1.16},
          xaxis: {gridcolor: '#edf0eb'},
          yaxis: {gridcolor: '#edf0eb'},
          ...layout
        };
        if (android) {
          configured.height = wide ? wideHeight : Math.min(layout.height || 300, 380);
          configured.dragmode = mode === 'scroll' ? false : mode;
          configured.margin = {...configured.margin, l: 50, r: 50, t: 55, b: 55};
          configured.legend = {...configured.legend, font: {size: 11}, orientation: 'h', y: 1.02, yanchor: 'bottom'};
          configured.uirevision = plotKey + '-' + reset;
          if (view.current?.key === plotKey && view.current.reset === reset)
            for (const [axis, range] of Object.entries(view.current.axes))
              configured[axis] = {...configured[axis], range, autorange: false};
        }
        await plotly.react(el, data, configured, {
          responsive: true,
          displaylogo: false,
          displayModeBar: android ? false : 'hover',
          scrollZoom: false,
          staticPlot: android && !interacting,
          modeBarButtonsToRemove: ['lasso2d', 'select2d']
        });
        if (!active) {
          plotly.purge(el);
          return;
        }
        setStatus('ready');
        if (wide && !shown.current) {
          shown.current = true;
          const dialog = el.closest('dialog');
          if (dialog) dialog.scrollTop = 0;
        }
        (el as any).on?.('plotly_click', (event: any) => {
          const point = event.points?.[0],
            x = point?.x;
          pointCallback.current?.(point);
          if (typeof x === 'number') callback.current?.(x * 60);
        });
        resize = new ResizeObserver(() => {
          if (active && el.isConnected && el.clientWidth && el.clientHeight)
            Promise.resolve(plotly.Plots.resize(el)).catch(() => {});
        });
        resize.observe(el);
      } catch {
        if (active) setStatus('error');
      }
    };
    observer = new IntersectionObserver(
      entries => {
        if (entries.some(e => e.isIntersecting)) {
          observer?.disconnect();
          void render();
        }
      },
      {rootMargin: '120px'}
    );
    observer.observe(host);
    return () => {
      active = false;
      observer?.disconnect();
      resize?.disconnect();
      const drawn = (el as any)._fullLayout;
      if (android && drawn)
        view.current = {
          key: plotKey,
          reset,
          axes: Object.fromEntries(
            Object.keys(drawn)
              .filter(k => /^[xy]axis\d*$/.test(k) && drawn[k].range)
              .map(k => [k, [...drawn[k].range]])
          )
        };
      if (plotly) plotly.purge(el);
    };
  }, [plotKey, mode, reset, attempt, wide, viewportHeight]);
  const label = tr('Grafico e valori'),
    format = (v: any) =>
      v == null
        ? '—'
        : typeof v === 'number'
          ? v.toLocaleString(language === 'en' ? 'en-GB' : 'it-IT', {maximumFractionDigits: 4})
          : String(v);
  const chooseMode = (next: string) => {
    setMode(next);
    const panel = canvas.current?.closest('dialog')?.querySelector<HTMLDetailsElement>('.suite-floating-panel');
    if (panel) panel.open = false;
  };
  const tools = android ? (
    <>
      <button type="button" aria-pressed={mode === 'scroll'} onClick={() => chooseMode('scroll')}>
        {tr('Scorri pagina')}
      </button>
      <button type="button" aria-pressed={mode === 'pan'} onClick={() => chooseMode('pan')}>
        {tr('Esplora')}
      </button>
      <button type="button" aria-pressed={mode === 'zoom'} onClick={() => chooseMode('zoom')}>
        {tr('Zoom')}
      </button>
      <button type="button" onClick={() => setReset(v => v + 1)}>
        {tr('Ripristina vista')}
      </button>
      {expand && (
        <button type="button" onClick={expand}>
          {tr('Vista ampia')}
        </button>
      )}
    </>
  ) : undefined;
  const help = android && (
    <p className="suite-chart-note" id={id}>
      {tr(
        interacting
          ? 'Trascina per spostare o selezionare lo zoom; tocca un punto per i valori. Torna a Scorri pagina per scorrere sul grafico.'
          : 'Scorri liberamente la pagina. Attiva Esplora per leggere i punti o Zoom per ingrandire. I valori sono disponibili anche in tabella.'
      )}
    </p>
  );
  const values = (
    <details className="suite-chart-data">
      <summary>
        {tr('Valori e riepilogo del grafico')} · {summary.length} {tr('serie')}
      </summary>
      <p className="suite-chart-note">
        {tr(
          'Valori originali disponibili, con unità nel nome della serie. I dati mancanti sono indicati con —; le righe non implicano tempi uguali tra serie diverse.'
        )}
      </p>
      <table>
        <caption>{tr('Riepilogo serie')}</caption>
        <thead>
          <tr>
            {['Serie', 'Valori', 'Minimo', 'Massimo'].map(t => (
              <th scope="col" key={t}>
                {tr(t)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {summary.map((s, i) => (
            <tr key={i}>
              <th scope="row">{s.name}</th>
              <td>{s.count}</td>
              <td>{format(s.min)}</td>
              <td>{format(s.max)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <table>
        <caption>{tr('Dati del grafico')}</caption>
        <thead>
          <tr>
            {['Serie', 'Ascissa', 'Valore'].map(t => (
              <th scope="col" key={t}>
                {tr(t)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {table.rows.map((r, i) => (
            <tr key={i}>
              <th scope="row">{r.name}</th>
              <td>{format(r.x)}</td>
              <td>{format(r.y)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {table.total > 30 && (
        <div className="suite-pagination">
          <button type="button" disabled={table.page === 0} onClick={() => setPage(table.page - 1)}>
            {tr('Precedenti')}
          </button>
          <span role="status">
            {table.page * 30 + 1}–{Math.min((table.page + 1) * 30, table.total)} / {table.total}
          </span>
          <button type="button" disabled={(table.page + 1) * 30 >= table.total} onClick={() => setPage(table.page + 1)}>
            {tr('Successivi')}
          </button>
        </div>
      )}
    </details>
  );
  return (
    <>
      <ChartFrame label={label} wide={wide} fullscreen={wide} toolsAfter tools={wide ? undefined : tools}>
        <div
          ref={ref}
          className={'suite-chart-surface ' + (!interacting ? 'is-scroll' : '')}
          style={{
            minHeight: wide ? wideHeight : Math.min(layout.height || 300, 380),
            touchAction: android && interacting ? 'none' : undefined
          }}
          aria-describedby={android ? id : undefined}
        >
          <div
            ref={canvas}
            className="plot"
            aria-label={label}
            style={!interacting ? {pointerEvents: 'none'} : undefined}
          />
          {status !== 'ready' && (
            <LoadingState
              title={tr(status === 'error' ? 'Grafico non disponibile' : 'Caricamento grafico…')}
              detail={tr(
                status === 'error'
                  ? 'I dati rimangono consultabili nella tabella. Puoi riprovare.'
                  : 'Il grafico viene preparato sul dispositivo.'
              )}
              retry={status === 'error' ? () => setAttempt(v => v + 1) : undefined}
              retryLabel={tr('Riprova')}
            />
          )}
        </div>
        {wide && (
          <FloatingPanel label={tr('Comandi grafico')}>
            <div className="suite-chart-tools">{tools}</div>
            {help}
            {values}
          </FloatingPanel>
        )}
      </ChartFrame>
      {!wide && (
        <>
          {help}
          {values}
        </>
      )}
    </>
  );
}
