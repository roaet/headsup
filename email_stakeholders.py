import sys

# Needs a generic config, something like ~/.dongploy
# Needs a match list of stakeholders, and all others will be ignored
# Also must identify migrations and email that
# What if it sent a meeting invite?
# All stakeholders in the config should get the email. This can be a clue that
#   the person SHOULD have a change and it's not in the branch
# Hard commits to ignore (the blamar commit from each branch cut)
# Also needs timestamps and regions
# Correlate ticket numbers in commits with JIRA, break them down by Bugs Fixed
#   and Features Implemented


def split_authors(stream):
    lines = stream.readlines()
    authors = {}
    for line in lines:
        line = line.replace("\n", '')
        sha, subject, email = line.split(',')
        authors.setdefault(email, [])
        authors[email].append((sha, subject))
    return authors

if __name__ == "__main__":
    authors = split_authors(sys.stdin)
    for email, commits in authors.iteritems():
        print email
        for c in commits:
            print "\t * [%s] - %s" % (c[0], c[1])


# HEY! Somehow determine whether or not there are migrations in here too!
# git log --pretty=format:%H internal/master..internal/neutron.180 | xargs -i git diff-tree --no-commit-id --name-only -r {} | sort | uniq -c
