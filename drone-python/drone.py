from urllib.request import Request, urlopen, urljoin
from urllib.parse import urlencode

import json

class DroneClient(object):
    def __init__(self, server, token, csrf=None):
        self.server = server
        self.token = token
        self.csrf = csrf
    
    @staticmethod
    def from_environment():
        from os import getenv
        return DroneClient(
            getenv("DRONE_SERVER"),
            getenv("DRONE_TOKEN"),
            getenv("DRONE_CSRF"),
            )

    def get_repo_list(self, opts):
        """Returns the user repository list.
        
        Keyword arguments:
        opts -- request options.
        """
        query = self._encode_query_string(opts)
        return self._get("/api/user/repos?{}".format(query))
    
    def get_repo(self, owner, repo):
        """Returns the repository by owner and name.

        Keyword arguments:
        owner -- repository owner.
        repo -- repository name.
        """
        return self._get("/api/repos/{}/{}".format(owner, repo))

    def activate_repo(self, owner, repo):
        """Activates the repository by owner and name.

        Keyword arguments:
        owner -- repository owner.
        repo -- repository name.
        """
        return self._post("/api/repos/{}/{}".format(owner, repo))
    
    def update_repo(self, owner, repo, data):
        """Updates the repository.

        Keyword arguments:
        owner -- repository owner.
        repo -- repository name.
        data -- repository data.
        """
        return self._patch("/api/repos/{}/{}".format(owner, repo), data)
    
    def delete_repo(self, owner, repo):
        """Deletes the repository by owner and name.
        
        Keyword arguments:
        owner -- repository owner.
        repo -- repository name.
        """
        return self._delete("/api/repos/{}/{}".format(owner, repo))
    
    def get_build_list(self, owner, repo, opts):
        """Returns the build list for the given repository.

        Keyword arguments:
        owner -- repository owner.
        repo -- repository name.
        opts -- request options.
        """
        query = self._encode_query_string(opts)
        return self._get("/api/repos/{}/{}/builds?{}".format(owner, repo, query))

    def get_build(self, owner, repo, number):
        """Returns the build by number for the given repository.

        Keyword arguments:
        owner -- repository owner.
        repo -- repository name.
        number -- build number.
        """
        return self._get("/api/repos/{}/{}/builds/{}".format(owner, repo, number))

    def get_build_feed(self, opts):
        """Returns the build feed for the user account.
        
        Keyword arguments:
        opts -- request options.
        """
        query = self._encode_query_string(opts)
        return self._get("/api/user/feed?{}".format(query))

    def cancel_build(self, owner, repo, number):
        """Cancels the build by number for the given repository.

        Keyword arguments:
        owner -- repository owner.
        repo -- repository name.
        number -- build number.
        """
        return self._delete("/api/repos/{}/{}/builds/{}".format(owner, repo, number))

    def approve_build(self, owner, repo, build, stage):
        """Approves the build.

        Keyword arguments:
        owner -- repository owner.
        repo -- repository name.
        build -- build number.
        stage -- stage number.
        """
        return self._post("/api/repos/{}/{}/builds/{}/approve/{}".format(
            owner, repo, build, stage
        ))

    def decline_build(self, owner, repo, build, stage):
        """Approves the build.

        Keyword arguments:
        owner -- repository owner.
        repo -- repository name.
        build -- build number.
        stage -- stage number.
        """
        return self._post("/api/repos/{}/{}/builds/{}/decline/{}".format(
            owner, repo, build, stage
        ))

    def restart_build(self, owner, repo, build, opts):
        """Restarts the build by number for the given repository.

        Keyword arguments:
        owner -- repository owner.
        repo -- repository name.
        build -- build number.
        opts -- request options.
        """
        query = self._encode_query_string(opts)
        return self._get("/api/repos/{}/{}/builds/{}?{}".format(
            owner, repo, build, query
        ))

    def get_logs(self, owner, repo, build, stage, step):
        """Returns the build by number for the given repository.

        Keyword arguments:
        owner -- repository owner.
        repo -- repository name.
        build -- build number.
        stage -- stage number.
        step -- step number.
        """
        return self._get("/api/repos/{}/{}/builds/{}/logs/{}/{}".format(
            owner, repo, build, stage, step
        ))

    def get_secret_list(self, owner, repo):
        """Returns the repository secret list.

        Keyword arguments:
        owner -- repository owner.
        repo -- repository name.
        """
        return self._get("/api/repos/{}/{}/secrets".format(owner, repo))

    def create_secret(self, owner, repo, secret):
        """Create the named repository secret.
        
        Keyword arguments:
        owner -- repository owner.
        repo -- repository name.
        secret -- secret details.
        """
        return self._post("/api/repos/{}/{}/secrets".format(owner, repo), secret)

    def delete_secret(self, owner, repo, secret):
        """Deletes the named repository secret.

        Keyword arguments:
        owner -- repository owner.
        repo -- repository name.
        secret -- secret name.
        """
        return self._delete("/api/repos/{}/{}/secrets/{}".format(owner, repo, secret))

    def get_registry_list(self, owner, repo):
        """Returns the repository registry list.

        Keyword arguments:
        owner -- repository owner.
        repo -- repository name.
        """
        return self._get("/api/repos/{}/{}/registry".format(owner, repo))

    def create_registry(self, owner, repo, registry):
        """Create the named registry.

        Keyword arguments:
        owner -- repository owner.
        repo -- repository name.
        registry -- registry details.
        """
        return self._post("/api/repos/{}/{}/registry".format(owner, repo), registry)

    def delete_registry(self, owner, repo, address):
        """Deletes the named registry.

        Keyword arguments:
        owner -- repository owner.
        repo -- repository name.
        address -- registry address.
        """
        return self._delete("/api/repos/{}/{}/registry/{}".format(
            owner, repo, address
        ))

    def synchronize(self):
        """Synchronizes and returns the updated repository list."""
        return self._post("/api/user/repos")

    def get_self(self):
        """Returns the currently authenticated user."""
        return self._get("/api/user")
    
    def get_token(self):
        """Returns the user's personal API token."""
        return self._post("/api/user/token")

    def _get(self, path):
        return self._request("GET", path, None)

    def _post(self, path, data=None):
        return self._request("POST", path, data)

    def _patch(self, path, data=None):
        return self._request("PATCH", path, data)

    def _delete(self, path):
        return self._request("DELETE", path, None)

    def _request(self, method, path, data):
        url = urljoin(self.server, path)
        headers = {}
        if self.token:
            headers["Authorization"] = "Bearer {}".format(self.token)
        if self.csrf:
            headers["X-CSRF-TOKEN"] = self.csrf
        if data:
            headers["Content-Type"] = "application/json"
            data = json.dumps(data)
        req = Request(url, data=data, method=method, headers=headers)
        resp = urlopen(req)
        content = resp.read().decode("utf-8")
        content_type = resp.headers.get("Content-Type", "")
        if resp.code < 300:
            if content_type.startswith("application/json"):
                content = json.dumps(content)
            return content
        return {"status": resp.code, "message": content}

    def _encode_query_string(self, opts):
        """Encodes the values into url encoded form sorted by key.
        
        Keyword arguments:
        opts -- query parameters in key value object.
        """
        return urlencode(opts) if opts else ""
