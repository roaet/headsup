"""
Thanks to JM this is irrelevant. This can all be accomplished with:

git log --pretty=format:%H-%s-%an-%ae branch_1..branch_2
"""

import os
import sys

import git


def _repo(path):
    repo = git.Repo(path)
    if repo.bare:
        print "Cannot continue on a bare repo"
        sys.exit(1)
    return repo


def list_branches(path):
    repo = _repo(path) 
    heads = [h.name for h in repo.heads]
    print "Current repo heads:", ', '.join(heads)


def diff_branches(path, left_branch, right_branch):
    """Equivalent to git-rev-parse, see man page for details"""

    repo = _repo(path)
    left_head = repo.heads[left_branch]
    right_head = repo.heads[right_branch]
    left_log = left_head.log()
    right_log = right_head.log()

    left_objects = set([c.newhexsha for c in left_log])
    right_objects = set([c.newhexsha for c in right_log])

    revision_diff = right_objects - left_objects
    for sha in revision_diff:
        obj = git.repo.fun.rev_parse(repo, sha)
        print obj, obj.author, obj.summary

if __name__ == "__main__":
    if sys.argv[1] == "list_branches":
        list_branches(sys.argv[2])
    elif sys.argv[1] == "diff":
        diff_branches(sys.argv[2], sys.argv[3], sys.argv[4])
