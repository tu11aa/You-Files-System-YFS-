call docker compose stop
call docker compose up --build --detach

set services=yfs1 yfs2 yfs3 yfs4 yfs5

for %%s in (%services%) do (
    start cmd /k "docker-compose exec %%s bash"
)