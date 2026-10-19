"""Sharing is archive-scoped: a multi-society archive must never be published."""

MESSAGE = ('Questo archivio contiene più società: sincronizzazione e inviti bloccati. '
           'Separare prima le società in archivi indipendenti; scegliere una società nel menu non filtra lo scambio.')


def check_record(record,organization):
    if not organization:
        return
    if record['kind']=='organization' and record['id']!=organization:
        raise ValueError('Record di un’altra società: scambio non consentito.')
    if record.get('organization_id') and record['organization_id']!=organization:
        raise ValueError('Lo storico contiene dati di un’altra società: separare gli archivi prima di condividere.')


def check_archive(store,changes=None):
    organizations=store.list('organization')
    if len(organizations)>1:
        raise ValueError(MESSAGE)
    identity=store.identity if hasattr(store,'identity') else {}
    organization=identity.get('organization_id') or (organizations[0]['id'] if organizations else None)
    if organizations and organization!=organizations[0]['id']:
        raise ValueError('Identità e società dell’archivio non corrispondono.')
    for event in changes or []:
        check_record(event['record'],organization)
    return organization
