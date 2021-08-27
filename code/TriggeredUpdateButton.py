import os.path
from datetime import datetime
import pytz
from github import Github
import PlotData

tz = pytz.timezone('Europe/Berlin')
now = datetime.now(tz)
weekday = now.weekday()
times = [[10, 23], [10, 23], [10, 23], [10, 23], [10, 23], [9, 22], [9, 22], [9, 22]]

if __name__ == '__main__':
    repo = Github(os.environ['GITHUB_TOKEN']).get_repo(os.environ['GITHUB_REPOSITORY'])
    issue = repo.get_issue(number=int(os.environ['ISSUE_NUMBER']))
    issue_author = '@' + issue.user.login
    repo_owner = '@' + os.environ['REPOSITORY_OWNER']
    if times[weekday][0] <= now.hour <= times[weekday][1]:
        PlotData.main('Nürnberg')
        PlotData.main('Zirndorf')
        issue.create_comment("Thanks {author} for updating this repo!".format(author=issue_author))
        issue.edit(state='closed', labels=['UpdateBock'])
    else:
        issue.create_comment(
            "Sorry {author}, but it seems that Steinbock is closed now. That's why the graphs won't update. If you "
            "think that's a bug, create an issue!".format(author=issue_author))
        issue.edit(state='closed', labels=['UpdateBock', 'ClosedBock'])
