import test from 'node:test';
import assert from 'node:assert/strict';
import {loadArchiveSelection, rememberedSelection, saveSelection} from '../src/archiveSelection.ts';

test('remembered workspace and organization survive reload', async () => {
  let current = {workspace: 'w1', organization: 'club2'};
  const result = await loadArchiveSelection(
    async (path, _body, _method, workspace) => {
      if (path === 'workspaces') {
        assert.equal(workspace, '');
        return [{id: 'w1'}];
      }
      assert.equal(workspace, 'w1');
      return {organization: [{id: 'club1'}, {id: 'club2'}]};
    },
    () => current,
    s => {
      current = s;
    }
  );
  assert.equal(result.organization, 'club2');
  assert.equal(current.workspace, 'w1');
});
test('stale ID falls back explicitly without sending it to state endpoint', async () => {
  let current = {workspace: 'removed-demo', organization: 'old'};
  const result = await loadArchiveSelection(
    async (path, _body, _method, workspace) => {
      assert.equal(workspace, '');
      return path === 'workspaces' ? [] : {organization: [{id: 'legacy'}]};
    },
    () => current,
    s => {
      current = s;
    }
  );
  assert.equal(result.missing, true);
  assert.deepEqual(current, {workspace: '', organization: ''});
});

const storage = () => {
  const values = new Map();
  return {getItem: key => values.get(key) ?? null, setItem: (key, value) => values.set(key, value)};
};
test('Android reopens the last selected society after the process loses session storage', () => {
  const persistent = storage(),
    oldSession = storage();
  saveSelection({workspace: 'society-2', organization: 'club-2'}, oldSession, persistent);
  const newSession = storage();
  assert.deepEqual(rememberedSelection(newSession, persistent), {workspace: 'society-2', organization: 'club-2'});
  assert.deepEqual(rememberedSelection(newSession), {workspace: '', organization: ''});
});
test('malformed persistent preferences fall back to session, without inventing a society', () => {
  const persistent = storage(),
    session = storage();
  persistent.setItem('fuorigiri-android-selection-v1', 'not-json');
  assert.deepEqual(rememberedSelection(session, persistent), {workspace: '', organization: ''});
  persistent.setItem('fuorigiri-android-selection-v1', JSON.stringify({workspace: 12, organization: 'other'}));
  assert.deepEqual(rememberedSelection(session, persistent), {workspace: '', organization: ''});
});
test('late response from a previous archive never replaces the new selection', async () => {
  let current = {workspace: 'w1', organization: 'a'},
    resolveState;
  const pending = loadArchiveSelection(
    async path =>
      path === 'workspaces'
        ? [{id: 'w1'}, {id: 'w2'}]
        : await new Promise(r => {
            resolveState = r;
          }),
    () => current,
    s => {
      current = s;
    }
  );
  await new Promise(r => setImmediate(r));
  current = {workspace: 'w2', organization: 'b'};
  resolveState({organization: [{id: 'a'}]});
  assert.equal(await pending, null);
  assert.deepEqual(current, {workspace: 'w2', organization: 'b'});
});

test('superseded refresh cannot persist a selection even for the same archive', async () => {
  let written = false;
  const result = await loadArchiveSelection(
    async () => [{id: 'w1'}],
    () => ({workspace: 'w1', organization: ''}),
    () => {
      written = true;
    },
    () => false
  );
  assert.equal(result, null);
  assert.equal(written, false);
});
