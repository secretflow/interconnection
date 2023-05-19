#!/bin/bash

set -eux

PYTHON=../.venv/bin/python

[[ -d _build ]] && find _build -type f -not -name '*.doctree' -and -not -name '*.pickle' -delete

$PYTHON -m sphinx -T -E -b mdx -t html -t mdx -D language=en . _build/mdx/en-US
$PYTHON -m sphinx -T -E -b mdx -t html -t mdx -D language=zh_CN . _build/mdx/zh-Hans
