#!/usr/bin/env bash
# Boot setup for a cloud agent VM.
#
# The package itself needs nothing installed: it is Python standard library only, by design,
# and that is checked by scripts/validate-package.py. This file exists for the connectors,
# which are not part of the package and do not survive a fresh VM.
#
# Firecrawl is the case that wasted real time. `firecrawl login` writes a credential on the
# machine where it runs, so a desktop authentication reaches nothing here, and the CLI is not
# present either. The reported symptom is "I authenticated it, why is it not working" and the
# cause is that it was never installed. See connectors/firecrawl.md.
set -euo pipefail

PREFIX="${HOME}/.npm-global"
BIN="${PREFIX}/bin"

echo "Installing the Firecrawl CLI to ${PREFIX}"
# A global install lands in /usr/lib/node_modules, which is not writable here, and there is no
# usable sudo. A user prefix is the working route.
npm config set prefix "${PREFIX}"
npm install -g firecrawl-cli

# So every later shell finds it, without appending a duplicate line on each rebuild.
for RC in "${HOME}/.bashrc" "${HOME}/.profile"; do
  if [ -f "${RC}" ] && ! grep -q 'npm-global/bin' "${RC}"; then
    printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> "${RC}"
  fi
done

export PATH="${BIN}:${PATH}"
firecrawl --version

# Unauthenticated scrape and search work and were verified returning real content. Only the
# authenticated capabilities need FIRECRAWL_API_KEY, and on a cloud agent that has to arrive
# through the dashboard secrets, because a desktop login does not travel.
if [ -n "${FIRECRAWL_API_KEY:-}" ]; then
  echo "FIRECRAWL_API_KEY is present, so the authenticated capabilities are available."
else
  echo "FIRECRAWL_API_KEY is absent. scrape and search still work unauthenticated."
fi

# Brand folders live outside the repository on purpose, so no brand's commercial data is ever
# committed here. This only creates the directory.
mkdir -p "${HOME}/brands"
echo "Brand folders belong in ${HOME}/brands/<brand-slug>/"

echo "Setup complete."
