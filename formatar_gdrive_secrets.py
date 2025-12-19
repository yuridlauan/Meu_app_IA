import argparse
import json
from typing import Any, Dict


def _carrega_credenciais(path: str | None, conteudo_json: str | None) -> Dict[str, Any]:
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    if conteudo_json:
        return json.loads(conteudo_json)

    raise SystemExit("Informe --input caminho_do_json ou --json '...'.")


def _toml_block(data: Dict[str, Any]) -> str:
    linhas = ["[gdrive_credenciais]"]
    for chave in sorted(data.keys()):
        valor = data[chave]
        linhas.append(f"{chave} = {json.dumps(valor, ensure_ascii=False)}")
    return "\n".join(linhas)


def _json_line(data: Dict[str, Any]) -> str:
    json_string = json.dumps(data, ensure_ascii=False)
    return f"gdrive_credenciais = '{json_string}'"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Formata credenciais de service account para Streamlit secrets."
    )
    parser.add_argument("--input", help="Caminho do arquivo JSON da credencial.")
    parser.add_argument("--json", help="Conteúdo JSON da credencial (string).")
    args = parser.parse_args()

    cred = _carrega_credenciais(args.input, args.json)

    print("\n### Bloco TOML (cole em secrets.toml ou no painel de secrets):\n")
    print(_toml_block(cred))

    print("\n### Linha única (string JSON) para secrets:\n")
    print(_json_line(cred))


if __name__ == "__main__":
    main()