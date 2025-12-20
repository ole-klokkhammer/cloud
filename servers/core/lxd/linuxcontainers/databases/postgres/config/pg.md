# postgres

- docker run -i --rm postgres cat /usr/share/postgresql/postgresql.conf.sample > postgres.conf
- kubectl create namespace postgres
- kubectl create secret generic -n postgres postgres-secrets --from-env-file=.env
- kubectl create configmap postgres-config --from-file=main-config=postgres.conf -n postgres
- kubectl apply -f service.yaml
- kubectl apply -f deployment.yaml

## timescale
* https://www.timescale.com/ai/solutions/agentic-applications?bb=220956

## extensions

### Vector extension
SELECT * FROM pg_available_extensions WHERE name = 'vector'; 
* vector
CREATE EXTENSION IF NOT EXISTS vector;

### VectorCord
https://docs.vectorchord.ai/vectorchord/getting-started/installation.html

* ssh to machine: https://github.com/tensorchord/VectorChord/releases/tag/0.4.2 
* cd into postgres-config volume, create a folder: extensions/pg<version>/vchord
* wget https://github.com/tensorchord/VectorChord/releases/download/0.4.2/postgresql-17-vchord_0.4.2_x86_64-linux-gnu.zip
* unzip ...
* make sure the postgres version etc is correct
* mount files as such for v0.4.2 (check that i.e. immich supports it):

- name: postgres-config
    subPath: extensions/pg17/vchord-0.4.2/pkglibdir/vchord.so
    mountPath: /usr/lib/postgresql/17/lib/vchord.so
- name: postgres-config
    subPath: extensions/pg17/vchord-0.4.2/sharedir/extension/vchord--0.1.0--0.2.0.sql
    mountPath: /usr/share/postgresql/17/extension/vchord--0.1.0--0.2.0.sql
- name: postgres-config
    subPath: extensions/pg17/vchord-0.4.2/sharedir/extension/vchord--0.2.0--0.2.1.sql
    mountPath: /usr/share/postgresql/17/extension/vchord--0.2.0--0.2.1.sql
- name: postgres-config
    subPath: extensions/pg17/vchord-0.4.2/sharedir/extension/vchord--0.2.1--0.2.2.sql
    mountPath: /usr/share/postgresql/17/extension/vchord--0.2.1--0.2.2.sql
- name: postgres-config
    subPath: extensions/pg17/vchord-0.4.2/sharedir/extension/vchord--0.2.2--0.3.0.sql
    mountPath: /usr/share/postgresql/17/extension/vchord--0.2.2--0.3.0.sql
- name: postgres-config
    subPath: extensions/pg17/vchord-0.4.2/sharedir/extension/vchord--0.3.0--0.4.0.sql
    mountPath: /usr/share/postgresql/17/extension/vchord--0.3.0--0.4.0.sql
- name: postgres-config
    subPath: extensions/pg17/vchord-0.4.2/sharedir/extension/vchord--0.4.0--0.4.1.sql
    mountPath: /usr/share/postgresql/17/extension/vchord--0.4.0--0.4.1.sql
- name: postgres-config
    subPath: extensions/pg17/vchord-0.4.2/sharedir/extension/vchord--0.4.1--0.4.2.sql
    mountPath: /usr/share/postgresql/17/extension/vchord--0.4.1--0.4.2.sql
- name: postgres-config
    subPath: extensions/pg17/vchord-0.4.2/sharedir/extension/vchord--0.4.2.sql
    mountPath: /usr/share/postgresql/17/extension/vchord--0.4.2.sql
- name: postgres-config
    subPath: extensions/pg17/vchord-0.4.2/sharedir/extension/vchord.control
    mountPath: /usr/share/postgresql/17/extension/vchord.control

* Configure your PostgreSQL by modifying the shared_preload_libraries to include the extension.
psql -U postgres -c 'ALTER SYSTEM SET shared_preload_libraries = "vchord.so"'
* CREATE EXTENSION IF NOT EXISTS vchord CASCADE;