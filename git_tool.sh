DIR=$(dirname "${BASH_SOURCE[0]}")
git fetch --all && git log --pretty=format:%H,%s,%ae $1..$2 | grep -v "Merge pull request" | python $DIR/email_stakeholders.py

# I think this should also just clone and update the repos it's supposed to monitor for the purposes of sending the notification,
# rather than trying to get all the relative pathing right.

# * Send the list of commits by committer
# * Also break it down by number of commits per file
# * Whether or not there are database migrations
# * A clean way of sending the date and region
