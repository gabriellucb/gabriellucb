"""Conta as contribuições do perfil (as mesmas do gráfico do GitHub, incluindo as
privadas quando "Private contributions" está ativado) desde a criação da conta
e gera dist/contribuicoes.json,
lido pelo badge do shields.io no README (https://shields.io/badges/endpoint-badge).

Uso: GITHUB_TOKEN=... python3 contribuicoes.py <usuario>
"""

import datetime as dt
import json
import os
import pathlib
import sys
import urllib.request

USUARIO = sys.argv[1]
TOKEN = os.environ["GITHUB_TOKEN"]


def graphql(query, **variaveis):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variaveis}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "User-Agent": "readme-contribuicoes"},
    )
    resposta = json.load(urllib.request.urlopen(req, timeout=30))
    if "errors" in resposta:
        raise SystemExit(resposta["errors"])
    return resposta["data"]


criado = graphql("query($u:String!){user(login:$u){createdAt}}", u=USUARIO)["user"]["createdAt"]
inicio = dt.datetime.fromisoformat(criado.replace("Z", "+00:00"))
agora = dt.datetime.now(dt.timezone.utc)

# a API só aceita intervalos de até um ano, então soma ano a ano
total = 0
for ano in range(inicio.year, agora.year + 1):
    de = max(inicio, dt.datetime(ano, 1, 1, tzinfo=dt.timezone.utc))
    ate = min(agora, dt.datetime(ano, 12, 31, 23, 59, 59, tzinfo=dt.timezone.utc))
    dados = graphql(
        "query($u:String!,$de:DateTime!,$ate:DateTime!){user(login:$u){"
        "contributionsCollection(from:$de,to:$ate){contributionCalendar{totalContributions}}}}",
        u=USUARIO, de=de.isoformat(), ate=ate.isoformat(),
    )
    total += dados["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]

mensagem = f"{total:,}".replace(",", ".")  # 1234 -> 1.234
saida = pathlib.Path("dist/contribuicoes.json")
saida.parent.mkdir(exist_ok=True)
saida.write_text(json.dumps({"schemaVersion": 1, "label": "contribuições", "message": mensagem}))
print(f"{USUARIO}: {mensagem} contribuições desde {inicio.year}")
