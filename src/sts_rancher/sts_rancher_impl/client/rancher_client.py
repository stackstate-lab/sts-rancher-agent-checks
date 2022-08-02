from logging import Logger
from typing import Any, Dict, List, Optional

import pydash.strings
import requests
from requests.adapters import HTTPAdapter
from requests.structures import CaseInsensitiveDict
from sts_rancher_impl.model.instance import RancherSpec
from urllib3.util import Retry


class RancherClient(object):
    def __init__(self, spec: RancherSpec, log: Logger):
        self.log = log
        self.spec = spec
        self.spec.url = pydash.strings.ensure_ends_with(spec.url, "/")
        self._session = self._init_session(spec)
        self._project_lookup: Dict[str, str] = {}

    def get(self, url: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        if params is None:
            params = {}
        if "limit" not in params:
            params["limit"] = "1000"
        result = self._handle_failed_call(self._session.get(url, params=params)).json()
        return result

    def get_collection(self, uri: str, params: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        paging = True
        result = []
        url = self.get_url(uri)
        while paging:
            page = self._handle_failed_call(self._session.get(url, params=params)).json()
            if page["type"] != "collection":
                raise Exception(f"Endpoint {url} expected to return collection by type was {page['type']}")
            result.extend(page["data"])
            if page["pagination"] is None:
                paging = False
            elif page["pagination"]["next"] is None:
                paging = False
            else:
                url = page["pagination"]["next"]
        return result

    def get_resource_from_all_projects(
        self, resource: str, params: Optional[Dict[str, str]] = None, exclude_projects: List[str] = None
    ) -> List[Dict[str, Any]]:
        if exclude_projects is None:
            exclude_projects = []
        self._init_project_lookup()
        results = []
        for project_id, name in self._project_lookup.items():
            if project_id in exclude_projects:
                continue
            if len(self.spec.include_environment_ids) > 0 and project_id not in self.spec.include_environment_ids:
                continue
            resources = self.get_collection(f"projects/{project_id}/{resource}", params)
            for r in resources:
                r["project_name"] = name
            results.extend(resources)
        return results

    def _init_project_lookup(self):
        if len(self._project_lookup) == 0:
            for project in self.get_collection("projects"):
                self._project_lookup[str(project["id"])] = project["name"]

    def get_url(self, uri: str) -> str:
        return f"{self.spec.url}{self.spec.api_uri}/{uri}"

    def get_project_name_using_link(self, link: str) -> str:
        self._init_project_lookup()
        project_id = self.get_project_id_from_link(link)
        return self._project_lookup[project_id]

    @staticmethod
    def get_project_id_from_link(link: str) -> str:
        # http://192.168.56.30:8080/v2-beta/projects/1a17/containers/1i23
        id_part = link.split("/projects/")[1]
        return id_part.split("/", 1)[0]

    @staticmethod
    def _init_session(spec: RancherSpec) -> requests.Session:
        retry = Retry(
            total=spec.max_request_retries,
            backoff_factor=spec.retry_backoff_seconds,
            status_forcelist=spec.retry_on_status,
        )
        session = requests.Session()
        session.verify = False
        session.auth = (spec.username, spec.password)
        session.headers = CaseInsensitiveDict(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "cache-control": "no-cache",
            }
        )
        session.mount(spec.url, HTTPAdapter(max_retries=retry))
        return session

    @staticmethod
    def _handle_failed_call(response: requests.Response) -> requests.Response:
        if not response.ok:
            msg = f"Failed to call [{response.url}]. Status code {response.status_code}. {response.text}"
            raise Exception(msg)
        return response
