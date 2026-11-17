"""Gera a fileira de ícones da seção "ferramentas" do README.

Baixa os ícones do skillicons.dev, insere o ícone do Logisim (desenhado aqui,
no mesmo estilo) e salva tudo em assets/ferramentas-{dark,light}.svg.

Para mudar a fileira, edite ICONES e rode:  python3 assets/gerar-ferramentas.py
"""

import pathlib
import re
import urllib.request

# ordem da fileira; "logisim" é o ícone local, o resto vem do skillicons.dev
ICONES = ["c", "python", "latex", "logisim", "linux", "git", "vscode"]

FUNDO = {"dark": "#242938", "light": "#F4F2ED"}
TRACO = {"dark": "#FFFFFF", "light": "#242938"}
VERDE = "#00D200"  # cor do nível lógico 1 no Logisim

PASTA = pathlib.Path(__file__).parent


def logisim(tema):
    """Porta AND com pinos de entrada e saída, no estilo do Logisim."""
    return f"""<svg width="256" height="256" viewBox="0 0 256 256" fill="none" xmlns="http://www.w3.org/2000/svg">
<rect width="256" height="256" rx="60" fill="{FUNDO[tema]}"/>
<path d="M58 100H90M58 156H90M186 128H202" stroke="{VERDE}" stroke-width="10" stroke-linecap="round"/>
<rect x="26" y="84" width="32" height="32" rx="4" fill="{VERDE}"/>
<rect x="26" y="140" width="32" height="32" rx="4" fill="{VERDE}"/>
<path d="M90 70H128C160 70 186 96 186 128C186 160 160 186 128 186H90Z" stroke="{TRACO[tema]}" stroke-width="12" stroke-linejoin="round"/>
<circle cx="214" cy="128" r="16" fill="{VERDE}"/>
</svg>"""


def skillicon(nome, tema):
    url = f"https://skillicons.dev/icons?i={nome}&theme={tema}"
    req = urllib.request.Request(url, headers={"User-Agent": "readme-icons"})
    svg = urllib.request.urlopen(req, timeout=30).read().decode()
    # a resposta é um <svg> externo com um <g> contendo o ícone de 256x256
    interno = re.search(r"<g transform=\"translate\(0, 0\)\">(.*)</g>", svg, re.S)
    if not interno or len(svg) < 300:
        raise SystemExit(f"ícone desconhecido no skillicons: {nome}")
    return interno.group(1).strip()


def fileira(tema):
    n = len(ICONES)
    largura = 300 * n - 44  # ícones de 256 com espaço de 44, como no skillicons
    grupos = []
    for i, nome in enumerate(ICONES):
        icone = logisim(tema) if nome == "logisim" else skillicon(nome, tema)
        grupos.append(f'<g transform="translate({300 * i}, 0)">\n{icone}\n</g>')
    return (
        f'<svg width="{largura * 48 / 256:g}" height="48" viewBox="0 0 {largura} 256" '
        'fill="none" xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1">\n'
        + "\n".join(grupos)
        + "\n</svg>\n"
    )


for tema in ("dark", "light"):
    destino = PASTA / f"ferramentas-{tema}.svg"
    destino.write_text(fileira(tema))
    print("gerado", destino)
