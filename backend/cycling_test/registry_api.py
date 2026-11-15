"""Organizations, groups, athletes, memberships and measurements (registry routes)."""

from datetime import date

from pydantic import Field

from .api import (
    Athlete,
    Group,
    GroupLifecycle,
    GroupRevision,
    IntegrationSettings,
    Measurement,
    Membership,
    Model,
    Organization,
)


def install(app, store, require):
    @app.post("/api/v1/organizations")
    def organization(data: Organization):
        if hasattr(store, 'identity'):
            raise ValueError('Un workspace contiene una sola società. Creare un nuovo workspace.')
        return store.save("organization", data.model_dump())

    @app.put('/api/v1/organizations/{id}/integrations')
    def integrations(id: str, data: IntegrationSettings):
        original = require(id, 'organization')
        return store.save(
            'organization', {**original, 'intervals_icu_enabled': data.intervals_icu_enabled}, id, data.base
        )

    def validate_group(data: Group, id: str | None = None):
        require(data.organization_id, "organization")
        if data.parent_id:
            parent = require(data.parent_id, 'group')
            if (
                parent['organization_id'] != data.organization_id
                or parent.get('parent_id')
                or parent['id'] == id
                or parent.get('status') == 'deleted'
            ):
                raise ValueError('Categoria padre non valida.')
            if id and any(g.get('parent_id') == id for g in store.list('group')):
                raise ValueError('Spostare prima le stagioni figlie della categoria.')
            if not data.season.strip():
                raise ValueError('Indicare la stagione del gruppo figlio.')
            data.name = data.name.strip() or parent['name']
        elif not data.name.strip():
            raise ValueError('Indicare il nome della categoria principale.')
        data.name = data.name.strip()
        data.season = data.season.strip()

    @app.post("/api/v1/groups")
    def group(data: Group):
        validate_group(data)
        return store.save("group", data.model_dump())

    @app.put('/api/v1/groups/{id}')
    def revise_group(id: str, data: GroupRevision):
        old = require(id, 'group')
        if old['organization_id'] != data.organization_id:
            raise ValueError('Non è possibile cambiare società del gruppo.')
        if old.get('status') == 'deleted':
            raise ValueError('Ripristinare il gruppo prima di modificarlo.')
        validate_group(data, id)
        return store.save('group', {**old, **data.model_dump(exclude={'base'})}, id, data.base)

    @app.post('/api/v1/groups/{id}/lifecycle')
    def group_lifecycle(id: str, data: GroupLifecycle):
        old = require(id, 'group')
        if data.scope == 'season':
            if old.get('parent_id') or not old.get('season') or old.get('status') == 'deleted':
                raise ValueError('Stagione sulla categoria non disponibile.')
            payload = {**old, 'season_status': data.status}
        else:
            if data.status == 'deleted' and any(
                g.get('parent_id') == id and g.get('status') != 'deleted' for g in store.list('group')
            ):
                raise ValueError('Spostare o eliminare prima le stagioni attive della categoria.')
            if (
                data.status == 'active'
                and old.get('parent_id')
                and require(old['parent_id'], 'group').get('status') == 'deleted'
            ):
                raise ValueError('Ripristinare prima la categoria padre.')
            payload = {**old, 'status': data.status}
        return store.save('group', payload, id, data.base)

    @app.post("/api/v1/athletes")
    def athlete(data: Athlete):
        require(data.organization_id, "organization")
        return store.save("athlete", data.model_dump(mode='json'))

    @app.put("/api/v1/athletes/{id}")
    def edit_athlete(id: str, base: str, data: Athlete):
        original = require(id, "athlete")
        if original["organization_id"] != data.organization_id:
            raise ValueError("Trasferimento fra società non supportato da questa modifica.")
        payload = data.model_dump(mode='json')
        if 'intervals_icu_id' not in data.model_fields_set:
            payload.pop('intervals_icu_id', None)
        return store.save("athlete", {**original, **payload}, id, base)

    @app.post("/api/v1/memberships")
    def membership(data: Membership):
        a, g = require(data.athlete_id, "athlete"), require(data.group_id, "group")
        if g.get('status') == 'deleted' or g.get('season_status') == 'deleted':
            raise ValueError('Scegliere un gruppo attivo.')
        if a["organization_id"] != g["organization_id"]:
            raise ValueError("Atleta e gruppo devono appartenere alla stessa società.")
        return store.save("membership", data.model_dump(mode="json"))

    class MembershipBatch(Model):
        group_id: str
        athlete_ids: list[str] = Field(min_length=1, max_length=1000)
        start: date
        end: date | None = None
        category_year: int | None = Field(default=None, ge=1, le=20)

    @app.post('/api/v1/memberships/batch')
    def membership_batch(data: MembershipBatch):
        from uuid import uuid5, NAMESPACE_URL

        g = require(data.group_id, 'group')
        if g.get('status', 'active') != 'active' or g.get('season_status') == 'deleted':
            raise ValueError('Scegliere un gruppo attivo.')
        athletes = [require(id, 'athlete') for id in dict.fromkeys(data.athlete_ids)]
        entries = []
        skipped = []
        existing = store.list('membership')
        for a in athletes:
            if a['organization_id'] != g['organization_id']:
                raise ValueError('Atleta e gruppo devono appartenere alla stessa società.')
            if a.get('status', 'active') != 'active':
                raise ValueError('Si possono aggiungere soltanto atleti attivi.')
            payload = Membership(
                athlete_id=a['id'], group_id=g['id'], start=data.start, end=data.end, category_year=data.category_year
            ).model_dump(mode='json')
            if any(
                m['athlete_id'] == a['id']
                and m['group_id'] == g['id']
                and m.get('status') != 'deleted'
                and m['start'] <= (payload['end'] or '9999-12-31')
                and (m.get('end') or '9999-12-31') >= payload['start']
                for m in existing
            ):
                skipped.append(a['id'])
                continue
            payload['id'] = str(
                uuid5(
                    NAMESPACE_URL,
                    'membership|' + g['id'] + '|' + a['id'] + '|' + payload['start'] + '|' + str(payload['end']),
                )
            )
            entries.append(('membership', payload))
        records = store.save_batch(entries) if entries else []
        return {'added': len(records), 'skipped': len(skipped), 'memberships': records}

    @app.post("/api/v1/measurements")
    def measurement(data: Measurement):
        a = require(data.athlete_id, "athlete")
        return store.save("measurement", {**data.model_dump(mode="json"), 'organization_id': a['organization_id']})

    class MeasurementRevision(Model):
        base: str
        reason: str = Field(min_length=3, max_length=1000)
        measurement: Measurement

    @app.put('/api/v1/measurements/{id}')
    def revise_measurement(id: str, data: MeasurementRevision):
        old = require(id, 'measurement')
        if old['athlete_id'] != data.measurement.athlete_id:
            raise ValueError('Non è possibile trasferire la misura a un altro atleta.')
        a = require(old['athlete_id'], 'athlete')
        return store.save(
            'measurement',
            {
                **data.measurement.model_dump(mode='json'),
                'organization_id': a['organization_id'],
                'reason': data.reason,
            },
            id,
            data.base,
        )
