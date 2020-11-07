import json
import requests
from flask import Flask
from flask_restful import Api, Resource, request, reqparse
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath

app = Flask(__name__)
api = Api(app)


github_api_url_base = 'https://api.github.com/'
bitbucket_api_url_base = 'https://api.bitbucket.org/2.0/'
github_headers = {'Accept': 'application/vnd.github.v3+json'}

# fetch github repos
def get_github_info(repo):

    github_api_url = '{}orgs/{}/repos'.format(github_api_url_base, repo)

    response = requests.get(github_api_url)

    if response.status_code == 200:
        return json.loads(response.content)
    else:
        return None


# fetch github watchers
def get_github_watcher_info(name):

    github_api_watcher_url = '{}repos/{}/subscribers'.format(github_api_url_base, name)

    response = requests.get(github_api_watcher_url, headers=github_headers)

    if response.status_code == 200:
        return json.loads(response.content)
    else:
        return None


# fetch bitbucket watchers
def get_bitbucket_watcher_info(url):

    bitbucket_api_watcher_url = url

    response = requests.get(bitbucket_api_watcher_url)

    if response.status_code == 200:
        return json.loads(response.content)
    else:
        return None


# fetch bitbucket repos
def get_bitbucket_info(repo):

    bitbucket_api_url = '{}repositories/{}/'.format(bitbucket_api_url_base, repo)

    response = requests.get(bitbucket_api_url)

    if response.status_code == 200:
        return json.loads(response.content)
    else:
        return None


repo_post_arg = reqparse.RequestParser()
repo_post_arg.add_argument("github", type=str, help="Github repo is required", required=True)
repo_post_arg.add_argument("bitbucket", type=str, help="Bitbucket repo is required", required=True)


# class to get all repos information and merge
class Repos(Resource):

    """
    Endpoint to merge repos 
    """

    def post(self):
        args = repo_post_arg.parse_args()
        github = PurePosixPath(unquote(urlparse(args['github']).path)).parts[1]
        bitbucket = PurePosixPath(unquote(urlparse(args['bitbucket']).path)).parts[1]
        github_account = get_github_info(github)
        bitbucket_account = get_bitbucket_info(bitbucket)

        github_pub_arr = []
        bitbucket_pub_arr = []
        github_desc = []
        bitbucket_desc = []
        github_watcher_arr = []
        bitbucket_watcher_arr = []
        all_languages = []
        all_desc = []

        # get all public github repos(excluding forks), languages, and descriptions
        # would want to unit test
        if github_account is not None:
            languages = []
            for k in github_account:
                if not k['private'] and not k['fork']:
                    github_pub_arr.append(k)
                    github_desc.append(k['description'])
                    if k['language'] != "none":
                        languages.append(k['language'])

            all_languages = list(dict.fromkeys(languages))
            all_desc = list(dict.fromkeys(github_desc))
        else:
            print('[!] Request Failed')

        # get all public bitbucket repos(excluding forks), languages, and descriptions
        # would want to unit test
        if bitbucket_account is not None:
            languages = []
            for k in bitbucket_account['values']:
                if not k['is_private']:
                    bitbucket_pub_arr.append(k)
                    bitbucket_desc.append(k['description'])
                    languages.append(k['language'])

            all_languages = list(dict.fromkeys(languages))
            all_desc = list(dict.fromkeys(bitbucket_desc))
        else:
            print('[!] Request Failed')

        # get watchers for all public github repos(excluding forks)
        # would want to unit test
        for k in github_pub_arr:
            github_watcher = get_github_watcher_info(k['full_name'])
            for i in github_watcher:
                github_watcher_arr.append(i)

        # get watchers for all public bitbucket repos(excluding forks)
        # would want to unit test
        for k in bitbucket_pub_arr:
            bitbucket_watcher = get_bitbucket_watcher_info(k['links']['watchers']['href'])
            for i in bitbucket_watcher:
                bitbucket_watcher_arr.append(i)

        total_pub_repos = len(github_pub_arr) + len(bitbucket_pub_arr)
        watcher_count = len(github_watcher_arr) + len(bitbucket_watcher_arr)
        lang_count = len(all_languages)
        desc_count = len(all_desc)

        repos = {"repos": total_pub_repos,
                 "watchers": watcher_count,
                 "languages": {"number": lang_count, "list": all_languages},
                 "descriptions": {"number": desc_count, "list": all_desc}
                 }

        return repos


api.add_resource(Repos, "/repos")


if __name__ == "__main__":
    app.run()
