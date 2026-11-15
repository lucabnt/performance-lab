import {useState, type ReactNode} from 'react';
import {Menu} from 'lucide-react';
import {Dialog} from './Dialog';
import {tr} from './i18n';

/** Product menu content composed with the suite's controls and modal semantics. */
export function AndroidNavigation({
  society,
  sections,
  language,
  onNavigate,
  onManage,
  context
}: {
  society: (manage: () => void) => ReactNode;
  sections: (navigate: (page: string) => void) => ReactNode;
  language: ReactNode;
  onNavigate: (page: string) => void;
  onManage: () => void;
  context?: ReactNode;
}) {
  const [open, setOpen] = useState(false);
  const navigate = (page: string) => {
    setOpen(false);
    onNavigate(page);
  };
  return (
    <>
      <button
        type="button"
        aria-label={tr('Apri menu')}
        aria-haspopup="dialog"
        aria-expanded={open}
        onClick={() => setOpen(true)}
      >
        <Menu size={22} />
      </button>
      <div className="brand brand-end">
        <div>
          Fuorigiri<small>PERFORMANCE LAB</small>
        </div>
        <img className="brand-icon" src="/branding/fuorigiri.svg" alt="" />
      </div>
      {context && (
        <div className="suite-context" role="status" aria-live="polite">
          {context}
        </div>
      )}
      {open && (
        <Dialog title={tr('Menu')} wide={false} onClose={() => setOpen(false)}>
          <div onChange={() => setOpen(false)}>
            {society(() => {
              setOpen(false);
              onManage();
            })}
          </div>
          <nav aria-label={tr('Sezioni')} style={{flexDirection: 'column', overflow: 'visible'}}>
            {sections(navigate)}
          </nav>
          <hr />
          {language}
        </Dialog>
      )}
    </>
  );
}
