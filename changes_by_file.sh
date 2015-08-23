git log --pretty=format:%H $1..$2 | xargs -i git diff-tree --no-commit-id --name-only -r {} | sort | uniq -c
