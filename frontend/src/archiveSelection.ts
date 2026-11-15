type Selection = {workspace: string; organization: string};
type Row = Record<string, any>;
const rememberedKey = 'fuorigiri-android-selection-v1';
type StorageLike = Pick<Storage, 'getItem' | 'setItem'>;
/** Persistent IDs only: no archive content, access token or credentials. */
export function rememberedSelection(session: StorageLike, persistent?: StorageLike): Selection {
  if (persistent) {
    try {
      const saved = JSON.parse(persistent.getItem(rememberedKey) || 'null');
      if (saved && typeof saved.workspace === 'string' && typeof saved.organization === 'string') return saved;
    } catch {
      /* Old or malformed preferences cannot prevent opening the archive picker. */
    }
  }
  return {
    workspace: session.getItem('fuorigiri-workspace') || '',
    organization: session.getItem('fuorigiri-organization') || ''
  };
}
export function saveSelection(selection: Selection, session: StorageLike, persistent?: StorageLike) {
  session.setItem('fuorigiri-workspace', selection.workspace);
  session.setItem('fuorigiri-organization', selection.organization);
  persistent?.setItem(
    rememberedKey,
    JSON.stringify({workspace: selection.workspace, organization: selection.organization})
  );
}

/** Ignore responses from a previous selection; recover stale IDs after a demo reset. */
export async function loadArchiveSelection(
  api: any,
  read: () => Selection,
  write: (selection: Selection) => void,
  isCurrent = () => true
) {
  const requested = read();
  const unchanged = (expected: Selection) => {
    const now = read();
    return isCurrent() && now.workspace === expected.workspace && now.organization === expected.organization;
  };
  // The archive inventory must remain readable even when a remembered ID disappeared.
  const workspaces: Row[] = await api('workspaces', undefined, 'GET', '');
  if (!unchanged(requested)) return null;
  const missing = !!requested.workspace && !workspaces.some(w => w.id === requested.workspace);
  const expected = missing ? {workspace: '', organization: ''} : requested;
  if (missing) write(expected);
  const state = await api('state', undefined, 'GET', expected.workspace);
  if (!unchanged(expected)) return null;
  const organization = missing
    ? ''
    : state.organization.some((o: Row) => o.id === expected.organization)
      ? expected.organization
      : state.organization[0]?.id || '';
  write({workspace: expected.workspace, organization});
  return {workspaces, state, workspace: expected.workspace, organization, missing};
}
