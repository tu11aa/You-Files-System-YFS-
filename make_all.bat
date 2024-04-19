call docker compose up --build --detach

@REM set services=yfs1 yfs2 yfs3 yfs4 yfs5
set services=yfs1 yfs2 yfs3

for %%s in (%services%) do (
    start cmd /k "docker-compose exec %%s bash"
)