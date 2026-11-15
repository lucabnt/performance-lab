// One scheduler per open workspace. All times are milliseconds.
export class AutomaticSync {
  next: number;
  dirty: number | null = null;
  retryAt = 0;
  failures = 0;
  busy = false;
  constructor(now: number) {
    this.next = now;
  }
  changed(now: number) {
    this.dirty = now + 10_000;
  }
  due(now: number) {
    return (
      !this.busy && now >= this.retryAt && now >= (this.dirty === null ? this.next : Math.min(this.next, this.dirty))
    );
  }
  started() {
    this.busy = true;
    this.dirty = null;
  }
  finished(now: number, success: boolean) {
    this.busy = false;
    this.next = now + 300_000;
    this.failures = success ? 0 : this.failures + 1;
    this.retryAt = success ? 0 : now + Math.min(30_000 * 2 ** Math.min(this.failures - 1, 6), 1_800_000);
    if (!success) this.next = this.retryAt;
  }
}

export function isArchiveWrite(path: string, method: string) {
  return (
    !['GET', 'HEAD'].includes(method) &&
    !/^(sync|device|workspaces)(\/|$)/.test(path) &&
    !/(\/preview|\/template)(\?|$)/.test(path) &&
    /^(athletes|organizations|groups|memberships|measurements|protocols|tests|manual-tests|anaerobic|custom|import|records|conflicts|workspace\/invite|workspace\/revoke|default-profiles)(\/|\?|$)/.test(
      path
    )
  );
}
