__author__ = 'Majisto'
from datetime import datetime
import os
import sys
import tkinter as tk
from tkinter import filedialog

import yaml
import requests

twofactor_list = []

class Member(yaml.YAMLObject):
    yaml_tag = "Member"
    def __init__(self, login, id_number, full_name, two_factor, email):
        self.login = login
        self.full_name = full_name
        self.user_email = email
        self.number = id_number
        self.two_factor = two_factor

class Repo(yaml.YAMLObject):
    yaml_tag = "Repo"
    def __init__(self, name, number):
        self.name = name
        self.number = number
    def __str__(self):
        return "Repoistory with Name: %s and Number: %d" % (self.name, self.number)

class Settings(yaml.YAMLObject):
    yaml_tag = "Settings"
    def __init__(self, username, report, organization):
        self.username = username
        self.report = report
        self.organization = organization

def FillDictionary():
    params = {}
    username = input("Please enter your GitHub Username: ")
    organization = input("Enter the organization name: ")
    report = input("Please input name of report you want: ")
    params["username"] = username
    params["organization"] = organization
    params["report"] = report
    if input('Would you like to save these to a file?  Please enter y or n: ') == 'y' :
        SaveYamlFile(Settings(username, report, organization))
    return params

def SaveYamlFile(params):
    while True:
        file_name = input('Pleae enter a filename for settings: ')
        if not file_name.endswith(".yaml"):
            file_name += ".yaml"
        if not os.path.isfile(file_name):
            with open (file_name, 'w') as f:
                yaml.dump(params, f, default_flow_style=False, explicit_start=True)
            return
        else:
            print('File already exists. Try another name.')

def OrgRequest (params):
    r = requests.get("https://api.github.com/orgs/%s/members" % (params['organization'], ), auth=(params["username"], params["password"]))
    output_filename = GetOutputFileName(params)
    member_list =[]
    with open (output_filename, "w") as f:
        member_list = process_page(r.json(), params, member_list)
        while "next" in r.links:
            r = requests.get(r.links["next"]["url"], auth=(params["username"], params["password"]) )
            member_list = process_page(r.json(), params, member_list)
        yaml.dump(member_list, f, default_flow_style=False, explicit_start=True)

def process_page(json_text, params, member_list):
    for entry in json_text:
        login = entry["login"]
        user_info = GetUser(login, params)
        member_list.append(Member(entry["login"], entry["id"], user_info["name"], False if entry["id"] in twofactor_list else True, user_info["email"]))
    return member_list

def GetUser(username, params):
    r = requests.get('https://api.github.com/users/%s' % (username,),  auth=(params["username"], params["password"]))
    json_text = r.json()
    user_dict = {"email":json_text['email'] if json_text['email'] else "Missing", "name":json_text['name'] if json_text['name'] else "Missing"}
    return user_dict

def CheckArgs(params):
    params["2auth"] = True if any(x == "-2auth" for x in sys.argv) else False
    params["verbose"] = True if any(x == "-v" for x in sys.argv) else False
    params["team"] = True if any(x == "-team" for x in sys.argv) else False

def GetTeams(params):
    r = requests.get("https://api.github.com/orgs/%s/teams" % (params['organization'], ), auth=(params["username"], params["password"]))
    json_text = r.json()
    with open(GetOutputFileName(params), "w") as f:
        for entry in json_text:
            team_element = {"Name": entry['name'], "Number": entry["id"], "Repos": GetRepoForTeam(entry['id'], params), "_Members":GetMembersForTeam(params, entry["id"])}
            yaml.dump(team_element, f, default_flow_style=False, explicit_start=True, indent=4)
            f.write("\n")
        while "next" in r.links: #Handle possible pagination
            r = requests.get(r.links["next"]["url"], auth=(params["username"], params["password"]))
            for entry in r.json():
                team_element = {"Name": entry['name'], "Number": entry["id"], "Repos": GetRepoForTeam(entry['id'], params), "_Members":GetMembersForTeam(params, entry["id"])}
                yaml.dump(team_element, f, default_flow_style=False, explicit_start=True, indent=4)
                f.write("\n")

def GetOutputFileName(params):
    return "%s_%s_info.yaml" % (params["organization"], params["report"])

def GetTwoFactor(params):
    global twofactor_list
    r = requests.get("https://api.github.com/orgs/%s/members?filter=2fa_disabled" % (params['organization'], ), auth=(params["username"], params["password"]))
    json_text = r.json()
    assert isinstance(twofactor_list, list)
    for entry in json_text:
        twofactor_list.append(entry["id"])
    while "next" in r.links:
        r = requests.get(r.links["next"]["url"], auth=(params["username"], params["password"]) )
        for entry in r.json():
            twofactor_list.append(entry["id"])

def GetMembersForTeam(params, team_id):
    r = requests.get("https://api.github.com/teams/%d/members" % team_id, auth=(params["username"], params["password"]))
    json_text = r.json()
    member_list = []
    for entry in json_text:
        user_info = GetUser(entry["login"], params)
        member_list.append(Member(entry["login"], entry["id"], user_info["name"], False if entry["id"] in twofactor_list else True, user_info["email"]))
    while "next" in r.links:
        r = requests.get(r.links["next"]["url"], auth=(params["username"], params["password"]) )
        json_text = r.json()
        for entry in json_text:
            user_info = GetUser(entry["login"], params)
            member_list.append(Member(entry["login"], entry["id"], user_info["name"], False if entry["id"] in twofactor_list else True, user_info["email"]))
    return member_list

def GetRepoForTeam(team_id, params):
    repo_list = []
    name_list = [] #Used as set of names to prevent duplicates.
    r = requests.get("https://api.github.com/teams/%d/repos" % team_id, auth=(params["username"], params["password"]))
    json_text= r.json()
    for entry in json_text:
        if entry["name"] not in name_list:
            name_list.append(entry["name"])
            repo_list.append(Repo(entry["name"], entry["id"]))
    while "next" in r.links:
        r = requests.get(r.links["next"]["url"], auth=(params["username"], params["password"]) )
        json_text = r.json()
        for entry in json_text:
            if entry["name"] not in name_list:
                name_list.append(entry["name"])
                repo_list.append(Repo(entry["name"], entry["id"]))
    return repo_list

def GetParams():
    params = {}
    if os.path.isfile('settings.yaml'):
        with open('settings.yaml', 'r') as inf:
            try:
                params = yaml.safe_load(inf)
            except SyntaxError:
                print("Error!  Check your settings file.")
                exit(-1)
    else:
        print("Could not find settings file.  Please enter information below.")
        params = FillDictionary()
    return params

def CheckPythoVersion():
    if sys.version_info < (3,0):
        print("Please use Python 3 or greater.")
        sys.exit(-1)

def GetSettings():
    for x in sys.argv:
        if x.endswith(".yaml"):
            with open (x, "r") as inf:
                return yaml.safe_load(inf)
    result = input("No settings file given.  Input 'c' to create new one or 'l' to load existing one of your choice: ")
    if result == 'c':
        return FillDictionary()
    root = tk.Tk()
    root.withdraw()
    options = {"filetypes": [('all_files', '.yaml')]}
    file_path = tk.filedialog.askopenfilename(**options)
    try:
        with open (file_path, "r") as inf:
            params = yaml.safe_load(inf)
    except FileNotFoundError:
        print("Unable to find file specified.")
        sys.exit(-1)
    return params

def GetPassword(params):
    while True: #Loop until password is successful.
        password = input("Please enter GitHub password or personal access token if using 2-factor: ")
        r = requests.get("https://api.github.com/rate_limit", auth=(params["username"], password))
        h = r.headers
        if r.status_code == 401:
            print("Not authorized.  Try a different password.")
            continue
        else: #Password Successful
            CheckRateLimit(h)
            params["password"] = password
            break
    return params

def CheckRateLimit(headers):
    rate_limit = int(headers.get("x-ratelimit-remaining"))
    if rate_limit < 10:
        print("You have run out of requests.  It will reset at %s.  Program will terminate." % datetime.fromtimestamp(
            int(headers.get("x-ratelimit-reset"))))
        sys.exit(-1)
    elif rate_limit < 300:
        print("Warning, your request limit is low!  Report might fail.  It will reset at %s" % datetime.fromtimestamp(
            int(headers.get("x-ratelimit-reset"))))

def CheckIfAdmin(params):
    r = requests.get("https://api.github.com/user/memberships/orgs/%s" % params["organization"], auth=(params["username"], params["password"]))
    body = r.json()
    try:
        if not body["role"] == "admin":
            print("You are not an administrator of this organization.  This script will terminate.")
            sys.exit(-1)
    except KeyError:
        print("You are not part of this organization.  Script will terminate.")
        sys.exit(-1)

def ProcessTeamRepo(params):
    team_id = TeamIDFromName(params)
    if team_id == 0:
        print("Team not found for organization.")
        sys.exit(-1)
    repo_list = GetRepoForTeam(team_id, params)
    with open (params["team_name"] + "_repos.yaml", "w") as f:
        yaml.dump(repo_list, f, default_flow_style=False, explicit_start=True,)

def TeamIDFromName(params):
    r = requests.get("https://api.github.com/orgs/%s/teams" % (params['organization'], ), auth=(params["username"], params["password"]))
    goal_team_name = params["team_name"]
    for entry in r.json():
        if entry["name"] == goal_team_name:
            return entry["id"]
    while "next" in r.links:
        r = requests.get(r.links["next"]["url"], auth=(params["username"], params["password"]))
        for entry in r.json():
            if entry["name"] == goal_team_name:
                return entry["id"]
    return 0

def DetermineReportToRun(params):
    report_type = params["report"]
    if report_type == "team_members" :
        GetTeams(params)
    elif report_type == "org_members":
        OrgRequest(params)
    elif report_type == "team_repos":
        ProcessTeamRepo(params)

def main():
    CheckPythoVersion()
    params = GetSettings()
    CheckArgs(params)
    params = GetPassword(params)
    CheckIfAdmin(params)
    GetTwoFactor(params)
    DetermineReportToRun(params)

main()