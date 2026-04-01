#!/usr/bin/env bash
# setup.sh — install dependencies for weighted_vertex_cover.py

set -e

try_install() {
    # Arguments: command1 "desc1" command2 "desc2" ...
    local i=1
    while [ $i -le $# ]; do
        CMD="${!i}"; i=$((i+1))
        DESC="${!i}"; i=$((i+1))

        echo "Trying to install $DESC..."
        if $CMD; then
            echo "$DESC installed successfully."
            return 0
        else
            echo "Failed: $DESC. Trying next option..."
        fi
    done

    echo "All installation attempts failed."
    exit 1
}

try_install \
    "pip install pulp" "PuLP (LP modelling + CBC solver)" \
    "python3 -m pip install pulp" "PuLP via python3 -m pip" \
    "python3 -m pip install --user pulp" "PuLP with --user flag"

echo "Installation complete."