# ABOUT

This project provides some simple Python 3 scripts to interface with the GitHub
API and extract information about GitHub teams, repositories (aka repos), and
members (aka users). This will be useful if you run a GitHub organization with
private repositories and need to control access over time.

The scripts described here were developed by Barton Durbin (majisto AT gmail DOT com)
at the request of David Black (david DOT black AT doulos DOT com).

# BACKGROUND

This is the result of a long learning process we went through.

Organizations using GibHub may have a lot of group teams and repositories.  Each
repository may have `-manager` and `-contributor` teams, which probably consist
of a very small number of individuals.  This allows control over each private
repository.

In the past, there was the notion of a`-observer` team per repository with many
members, but we have migrated to a single large `observer` group that covers all
the repositories. The `-observer` teams have one member that is used to monitor
changes and forward to external e-mail lists (different system). Projects often
have both a main repo and a separate `-test` or `-regressions` repo.

Observers wishing to submit changes, make a fork of the repo they are working on
and then submit a pull-request to one of the `-contributor` team members.

## THE PROBLEM

Because our organization is supposed to be restricted to authorized members only
as dictated by our by-laws, we need to know who is on each team. Typically,
members must be employees of member companies. Since we can validate corporate
e-mails with the respective companies, we can valid users if we know their
company e-mail address.

GitHub uses GitHub ids to allow access, which does not really tell us who is
behind the id. Fortunately, each user has a profile where they can choose to
reveal their e-mail address. Thus we require that each user must make their
corporate e-mail visible, and use these scripts to obtain the relationship.

Additionally, we are concerned with security of each user account since security
is tied to the weakest link. This means we want good passwords and protections
against the possibility of hackers. Fortunately, GitHub supports 2-factor
authentication. Unfortunately, not all GitHub users have realized how important
this is. That is why this script pulls that information, which allows us to
contact users and ask they either add two-factor authentication or be lose their
priviledges to use the organization's private GitHub repositories.

## THE SOLUTION

These scripts allow us to pull the GitHub userid's, associated e-mail addresses,
and authentication information. We can then use this to enforce our policies.

# Usage

In order to use these scripts, you must be an `organization administrator` to run
these scripts. This is because GitHub rightfully restricts access to information
about the repositories.

## Installation

Before running scripts for the first time, you must install the Python, some
libraries and the scripts.

### Note

If you are reading this as a text file, and not through the web browser,
please ignore the \ character as it is used to escape certain characters so it
looks nice in a Markdown interpreter.  Remove the \ whenever you see it and
condense words together.**

### Windows

1. Download and install python 3 from [https://www.python.org/](https://www.python.org "https://www.python.org")
2. Open up Windows Powershell after installing python
3. pip install pyyaml
4. pip install openpyxl
5. pip install requests

### Linux

1. **Note**:
   Most Linux distributions already have python3 and python2 installed.
   The scripts in this project require Python 3.
   You may have to install Python 3 if it is not present.
   You might have to use pip3 and python3 if you have both python 2 and 3 installed.
   Type python3 --v in terminal and see what it says.
2. Once verified you have the correct version, open terminal program
3. pip3 install pyyaml
4. pip3 install openpyxl
5. pip3 install requests
6. sudo apt-get update
7. sudo apt-get install python3-tk

### Mac OS X

1. Should be similar to Linux, but apt-get and python3-tk should not be necessary as they 
   are likely pre-installed like on Windows. If not, you may need to install it.
   MacPorts is one way to do this.
2. If it is crashing, you might need to install tkinter.
3. If it is *still* crashing, blame the ghost of Steve Jobs.

## Configuring the included settings file

The `settings.yaml` file is used to select what to extract.
You can see a sample in the `example/` directory.

1. Change username to your github username
2. Change organization to organization you are an admin of.
   **Please make sure you are an admin!**
3. Change report to following supported types:
   - org\_members: This will give a yaml file of all member of given organization.
     Included are member names, email, two factor authentication, login.  
     Output format is orgname\_org_members\_info.yaml.
   - team\_members: Outputs yaml file of all teams in organization with its repos and members.
     Output file format is orgname\_team\_members\_info.yaml.
   - team\_repos:  Outputs yaml file of all repos for one team.  The team is given by the 
     team\_name option in the settings file.  Output file format is teamname_repos.yaml 
4. Output file-name will be based on the report used.  It is usually based on the team 
   or org name plus .yaml.

## Once this is all done

### How to run **extract github info** script

In terminal or powershell, type either

`python extract\_github\_info.py SETTINGS_FILE.yaml`

  or you may use the default settings.yaml file with simply:

`python extract\_github\_info.py`

#### Notes

- Make sure you are in the same directory as the script

- You might have to preface the script name with ./ (I recommend using tab complete.

- Be sure settings file is properly setup from previous setup paragraph.

- If you do not name a settings file, you will be asked to pick one.  If you
  don't pick one, the terminal will prompt you for information and it will be
  saved as a new settings file.

- You will be prompted for your GitHub password.
  - **Important**:  If you are using two-factor authentication, your github
    password will not be sufficient!  You must create a person access token
    through GitHub's website.

    1. Log into GitHub through your web browser.
    2. Goto profile settings.
    3. Select *personal access tokens*.
    4. Select *generate new token*.
    5. For scopes, select
       - repo, 
       - read:org, 
       - user, 
       - all admin options
    6. Select *generate token*
    7. Write the token down somewhere!  You will use this as the password.
    8. If you lose the token, you can generate a new one following above
       procedures.  The script doesn't care so long as GitHub knows what it is.

- Output file will be in same directory script is located in.

- You have a limit of requests per hour from GitHub API.  It is unlikely you
  will exhaust it, but the script will warn you if it is getting low and
  will tell you when it resets (Usually within the hour).

### How to run **Yaml Parser** script

This script will create a Microsoft Excel spreadsheet summary of the
information.

- python yaml_parse.py (Name of org\_members report)
- Will ask for file if not given on command line.
- **Note**:
  - This script will take in an org_member report and output it in Excel format.
  - Do NOT feed it an output file from another report other than org_members.
    Mysteriously strange exceptions will be thrown and you will feel silly.
    Don't panic!

# Miscellaneous developer notes

Learn more about YAML
---------------------

- http://jsontoyaml.com 
- http://yamltojson.com
- http://www.yaml.org
- http://pyyaml.org

About this document's format
----------------------------

This document uses Markdown formatting (standard for README's on GitHub). See
<https://help.github.com/articles/markdown-basics/>. You might also be
interested in <https://github.com/github/markup>. You can either view it on
GitHub, obtain a Markdown viewer, or just enjoy the reasonably formatted text.

### The end
vim:syntax=markdown
