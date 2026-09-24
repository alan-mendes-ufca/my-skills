#!/usr/bin/env bash
# Instala links locais por skill para Codex/Gemini CLI e Claude Code.
set -euo pipefail

usage() {
  cat <<'EOF'
Uso: scripts/install-local.sh --check|--install

  --check    Confere se todos os links apontam para este repositório.
  --install  Cria somente links ausentes; recusa qualquer colisão.
EOF
}

if [[ $# -ne 1 ]]; then
  usage >&2
  exit 64
fi

case "$1" in
  --check|--install) mode="$1" ;;
  -h|--help) usage; exit 0 ;;
  *) usage >&2; exit 64 ;;
esac

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
repo_dir="$(cd -- "$script_dir/.." && pwd -P)"
skills=(
  humanizer simplify verification-planning post-refactor security-audit
  cost-aware-delegation
  antigravity-reviewer antigravity-debugger antigravity-security antigravity-architect
)
destinations=("$HOME/.agents/skills" "$HOME/.claude/skills")

failures=0
missing=0

link_is_correct() {
  local link="$1" source="$2"
  [[ -L "$link" ]] && [[ "$(readlink -f -- "$link")" == "$source" ]]
}

for skill in "${skills[@]}"; do
  if [[ ! -f "$repo_dir/$skill/SKILL.md" ]]; then
    printf 'ERRO: skill ausente ou inválida: %s\n' "$repo_dir/$skill" >&2
    failures=1
  fi
done

if (( failures )); then
  exit 1
fi

# Preflight: não cria nenhum link se houver uma colisão em qualquer destino.
for destination in "${destinations[@]}"; do
  for skill in "${skills[@]}"; do
    source="$repo_dir/$skill"
    target="$destination/$skill"
    if link_is_correct "$target" "$source"; then
      :
    elif [[ -e "$target" || -L "$target" ]]; then
      printf 'COLISÃO: %s já existe e não aponta para %s\n' "$target" "$source" >&2
      failures=1
    else
      missing=1
    fi
  done
done

if (( failures )); then
  printf 'Nenhum link foi criado. Resolva as colisões manualmente.\n' >&2
  exit 1
fi

if [[ "$mode" == "--check" ]]; then
  if (( missing )); then
    printf 'PENDENTE: links ainda não instalados. Execute: %s --install\n' "$0"
    exit 1
  fi
  printf 'OK: os 20 links locais estão corretos.\n'
  exit 0
fi

for destination in "${destinations[@]}"; do
  mkdir -p -- "$destination"
  for skill in "${skills[@]}"; do
    source="$repo_dir/$skill"
    target="$destination/$skill"
    if link_is_correct "$target" "$source"; then
      printf 'OK: %s\n' "$target"
    else
      ln -s -- "$source" "$target"
      printf 'CRIADO: %s -> %s\n' "$target" "$source"
    fi
  done
done

printf 'Concluído. Reinicie ou recarregue o agente para redescobrir as skills.\n'
