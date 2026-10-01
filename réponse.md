1) le verbe a utiliser pour utiliser cette création est POST ainsi le code qui est renvoyé est 201.


2) Le code HTTP ici est le 404 en raison de la station qui est introuvable. Une réponse du type "la station n'existe pas" est donc attendue.


3) Dans l'erreur 403 le serveur comprend la requête mais décide simplement de ne pas l'executer et s'authentifier ne fera aucune différence contrairement a l'erreur 401 où l'authentification est nécessaire pour accéder à cette requête.


4) $ python -m pytest -q
........                                                                                      [100%]
========================================= warnings summary =========================================
.venv\Lib\site-packages\fastapi\testclient.py:1
  C:\Users\timur\OneDrive\Desktop\ynov\Exam-Python-Timur\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

app\main.py:33
  C:\Users\timur\OneDrive\Desktop\ynov\Exam-Python-Timur\app\main.py:33: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.13/migration/
    class StationResponse(BaseModel):

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
8 passed, 2 warnings in 0.98s
(.venv) 