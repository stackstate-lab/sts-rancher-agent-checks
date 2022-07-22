import json
from json import JSONDecodeError

from typing import List, Dict, Any

from sts_rancher_impl.model.instance import InstanceInfo
from sts_rancher_impl.client import RancherClient
from rancher import RancherCheck

from stackstate_checks.stubs import topology, health, aggregator
import yaml
import logging
import requests_mock

logging.basicConfig()
logger = logging.getLogger("stackstate_checks.base.checks.base.ranchercheck")
logger.setLevel(logging.INFO)


@requests_mock.Mocker(kw="m")
def test_check(m: requests_mock.Mocker = None):
    topology.reset()
    instance_dict = setup_test_instance()
    instance = InstanceInfo(instance_dict)
    instance.validate()
    check = RancherCheck("rancher", {}, {}, instances=[instance_dict])
    check._init_health_api()

    _setup_request_mocks(instance, m)

    check.check(instance)
    stream = {"urn": "urn:health:rancher:rancher_health", "sub_stream": ""}
    health_snapshot = health._snapshots[json.dumps(stream)]
    health_check_states = health_snapshot["check_states"]
    metric_names = aggregator.metric_names
    snapshot = topology.get_snapshot("")
    components = snapshot["components"]
    relations = snapshot["relations"]
    assert len(components) == 78, "Number of Components does not match"
    assert len(relations) == 67, "Number of Relations does not match"
    assert len(health_check_states) == 71, "Number of Health does not match"
    assert len(metric_names) == 0, "Number of Metrics does not match"

    # host_uid = "urn:host:/karbon-stackstate-c9a026-k8s-master-0"
    # k8s_cluster_uid = "urn:cluster:/kubernetes:stackstate"
    # k8s_cluster_uid = "urn:cluster:/kubernetes:stackstate"
    # host_component = assert_component(components, host_uid)
    # assert_component(components, k8s_cluster_uid)
    # assert_relation(relations, k8s_cluster_uid, host_uid)
    #
    # assert host_component["data"]["custom_properties"]["ipv4_address"] == "10.55.90.119"


def _setup_request_mocks(instance, m):
    def response(file_name):
        with open(f"tests/resources/responses/{file_name}.json") as f:
            try:
                return json.load(f)
            except JSONDecodeError as e:
                print(f"Failed to load 'tests/resources/responses/{file_name}.json'")
                raise e

    rancher = RancherClient(instance.rancher, logger)

    def register(method, uri, data):
        url = rancher.get_url(uri)
        m.register_uri(method, url, json=response(data))

    endpoints = [
        ("GET", "projects", "projects"),
        ("GET", "projects/1a17/hosts", "sts_hosts"),
        ("GET", "projects/1a5/hosts", "default_hosts"),
        ("GET", "projects/1a17/containers", "sts_containers"),
        ("GET", "projects/1a5/containers", "default_containers"),
        ("GET", "projects/1a5/stacks", "default_stacks"),
        ("GET", "projects/1a17/stacks", "sts_stacks"),
        ("GET", "projects/1a17/services", "sts_service"),
        ("GET", "projects/1a5/services", "default_service"),
        ("GET", "projects/1a5/volumes", "default_volumes"),
        ("GET", "projects/1a17/volumes", "sts_volumes"),
        ("GET", "projects/1a17/networks", "sts_networks"),
        ("GET", "projects/1a5/networks", "default_networks"),
        ("GET", "projects/1a5/subnets", "default_subnets"),
        ("GET", "projects/1a17/subnets", "sts_subnets"),
    ]

    for endpoint in endpoints:
        register(*endpoint)


def setup_test_instance() -> Dict[str, Any]:
    with open("tests/resources/conf.d/rancher.d/conf.yaml.example") as f:
        config = yaml.load(f)
        instance_dict = config["instances"][0]
    return instance_dict


def assert_component(components: List[dict], cid: str) -> Dict[str, Any]:
    component = next(iter(filter(lambda item: (item["id"] == cid), components)), None)
    assert component is not None, f"Expected to find component {cid}"
    return component


def assert_relation(relations: List[dict], sid: str, tid: str) -> Dict[str, Any]:
    relation = next(
        iter(
            filter(
                # fmt: off
                lambda item: item["source_id"] == sid and item["target_id"] == tid,
                # fmt: on
                relations,
            )
        ),
        None,
    )
    assert relation is not None, f"Expected to find relation {sid}->{tid}"
    return relation
