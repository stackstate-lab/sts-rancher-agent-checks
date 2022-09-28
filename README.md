# StackState Rancher Agent Check

## Overview

A custom [StackState Agent Check](https://docs.stackstate.com/develop/developer-guides/agent_check/agent_checks) that
makes it possible to integrate [Rancher 1.6](https://rancher.com/docs/rancher/v1.6/en/).

The integration uses the [StackState ETL framework](https://stackstate-lab.github.io/stackstate-etl/) 
to define templates to map Rancher Rest Api entities to StackState Components, Relations, Events,
Metrics and Health Syncs

See [StackState ETL documentation](https://stackstate-lab.github.io/stackstate-etl/) for more information.

## Installation

From the StackState Agent 2 linux machine, run

```bash 
curl -L https://github.com/stackstate-lab/sts-rancher-agent-checks/releases/download/v0.1.1/sts_rancher-0.1.1.zip -o sts_rancher.zip
tar -xvf sts_rancher.zip
./install.sh
```

Setup `conf.yaml` on agent machine.

```bash 
cp /etc/stackstate-agent/conf.d/rancher.d/conf.yaml.example /etc/stackstate-agent/conf.d/rancher.d/conf.yaml
chown stackstate-agent:stackstate-agent /etc/stackstate-agent/conf.d/rancher.d/conf.yaml
vi conf.yaml
```

Change the properties to match your environment.

```yaml

init_config:

instances:
  - instance_url: "rancher"
    instance_type: rancher
    collection_interval: 300
    rancher:
      url: "https://10.55.90.37:9440"
      username: "admin"
      password: "nx2Tech081!"
    domain: "rancher"
    layer: "Machines"
    etl:
      refs:
        - "module_dir://sts_rancher_impl.templates"


```

See [Instance Model](sts-rancher-agent-checks/src/sts_rancher_impl/model/instance.py) for complete options.

Run the agent check to verify configured correctly.

```bash
sudo -u stackstate-agent stackstate-agent check rancher -l info
```

## ETL

APIs to syn data from, 

- [Rancher 1.6 Api](https://rancher.com/docs/rancher/v1.6/en/api/v2-beta/)
- [Filters](https://github.com/rancher/api-spec/blob/master/specification.md#filtering)

### DataSources


| Name                                                                       | Module                    | Cls                                                                         | Description                        |
|----------------------------------------------------------------------------|---------------------------|-----------------------------------------------------------------------------|------------------------------------|
| [rancher](sts-rancher-agent-checks/src/sts_rancher_impl/templates/010_default.yaml)   | sts_rancher_impl.client   | [RancherClient](sts-rancher-agent-checks/src/sts_rancher_impl/client/rancher_client.py)  | enables rest calls to rancher  api |


### Template Mappings

| Name                                                                                                                     | Type                                           | 4T        | rancher Api                                                                                  | Description |
|--------------------------------------------------------------------------------------------------------------------------|------------------------------------------------|-----------|----------------------------------------------------------------------------------------------|-------------|
| [rancher_host_template](sts-rancher-agent-checks/src/sts_rancher_impl/templates/020_rancher_hosts.yaml)                             | rancher-host                                   | Component | [v2-beta/projects/{project}/hosts](./tests/resources/responses/sts_hosts.json)               |             |
| [rancher_public_endpoint_template](sts-rancher-agent-checks/src/sts_rancher_impl/templates/020_rancher_hosts.yaml)                  | rancher-endpoint                               | Component | [v2-beta/projects/{project}/hosts](./tests/resources/responses/sts_hosts.json)               |             |
| [rancher_host_status_template](sts-rancher-agent-checks/src/sts_rancher_impl/templates/020_rancher_hosts.yaml)                      | rancher-host                                   | Health    | [v2-beta/projects/{project}/hosts](./tests/resources/responses/sts_hosts.json)               |             |
| [rancher_service_template](sts-rancher-agent-checks/src/sts_rancher_impl/templates/020_rancher_services.yaml)                       | rancher-service/rancher-loadbalancer-service   | Component | [v2-beta/projects/{project}/services](./tests/resources/responses/sts_services.json)         |             |
| [rancher_loadbalancer_service_config_template](sts-rancher-agent-checks/src/sts_rancher_impl/templates/020_rancher_services.yaml)   | rancher-loadbalancer-service                   | Relation  | [v2-beta/projects/{project}/services](./tests/resources/responses/sts_services.json)         |             |
| [rancher_service_status_template](sts-rancher-agent-checks/src/sts_rancher_impl/templates/020_rancher_services.yaml)                | rancher-service                                | Health    | [v2-beta/projects/{project}/services](./tests/resources/responses/sts_services.json)         |             |
| [rancher_stack_template](sts-rancher-agent-checks/src/sts_rancher_impl/templates/040_rancher_stacks.yaml)                           | rancher-stack                                  | Component | [v2-beta/projects/{project}/stacks](./tests/resources/responses/sts_stacks.json)             |             |
| [rancher_stack_status_template](sts-rancher-agent-checks/src/sts_rancher_impl/templates/040_rancher_stacks.yaml)                    | rancher-stack                                  | Health    | [v2-beta/projects/{project}/stacks](./tests/resources/responses/sts_stacks.json)             |             |
| [rancher_container_template](sts-rancher-agent-checks/src/sts_rancher_impl/templates/050_rancher_containers.yaml)                   | rancher-container                              | Component | [v2-beta/projects/{project}/containers](./tests/resources/responses/sts_containers.json)     |             |
| [rancher_container_status_template](sts-rancher-agent-checks/src/sts_rancher_impl/templates/050_rancher_containers.yaml)            | rancher-container                              | Health    | [v2-beta/projects/{project}/containers](./tests/resources/responses/sts_containers.json)     |             |
| [rancher_volume_template](sts-rancher-agent-checks/src/sts_rancher_impl/templates/060_rancher_volumes.yaml)                         | rancher-volume                                 | Component | [v2-beta/projects/{project}/volumes](./tests/resources/responses/sts_volumes.json)           |             |
| [rancher_volume_status_template](sts-rancher-agent-checks/src/sts_rancher_impl/templates/060_rancher_volumes.yaml)                  | rancher-volume                                 | Health    | [v2-beta/projects/{project}/volumes](./tests/resources/responses/sts_volumes.json)           |             |
| [rancher_storage_pool_template](sts-rancher-agent-checks/src/sts_rancher_impl/templates/062_rancher_storage_pools.yaml)             | rancher-storagepool                            | Component | [v2-beta/projects/{project}/storagepools](./tests/resources/responses/sts_storagepools.json) |             |
| [rancher_storage_pool_status_template](sts-rancher-agent-checks/src/sts_rancher_impl/templates/062_rancher_storage_pools.yaml)      | rancher-storagepool                            | Health    | [v2-beta/projects/{project}/storagepools](./tests/resources/responses/sts_storagepools.json) |             |
| [rancher_network_template](sts-rancher-agent-checks/src/sts_rancher_impl/templates/070_rancher_networks.yaml)                       | rancher-network                                | Component | [v2-beta/projects/{project}/networks](./tests/resources/responses/sts_networks.json)         |             |
| [rancher_network_status_template](sts-rancher-agent-checks/src/sts_rancher_impl/templates/070_rancher_networks.yaml)                | rancher-network                                | Health    | [v2-beta/projects/{project}/networks](./tests/resources/responses/sts_networks.json)         |             |


## Development

This project is generated using [Yeoman](https://yeoman.io/) and the [StackState Generator](https://github.com/stackstate-lab/generator-stackstate-lab)

StackState Rancher Agent Check is developed in Python 3, and is transpiled to Python 2.7 for deployment to the StackState Agent v2 environment.

---
### Prerequisites:

- Python v.3.9.x See [Python installation guide](https://docs.python-guide.org/starting/installation/)
- [PDM](https://pdm.fming.dev/latest/#recommended-installation-method)
- [Docker](https://www.docker.com/get-started)
- [Mockoon](https://mockoon.com/)
---

### Setup local code repository

```bash 
git clone git@github.com:stackstate-lab/sts-rancher-agent-checks.git
cd rancher
pdm install 
```
The `pdm install` command sets up all the projects required dependencies using [PEP 582](https://peps.python.org/pep-0582/) instead of virtual environments.

### Prepare local _.sts.env_ file

The `.sts.env` file is used to run the StackState Agent container. Remember to change the StackState url and api key for your environment.

```bash

cat <<EOF > ./.sts.env
STS_URL=https://xxx.stackstate.io/receiver/stsAgent
STS_API_KEY=xxx
EOF
```

### Preparing Mock Server

In Mockoon, open environment `tests/resources/mockoon/Rancher.json` and press start.

### Preparing Agent check conf.yaml

```
cp ./src/data/conf.d/rancher.d/conf.yaml.example ./src/data/conf.d/rancher.d/conf.yaml
```
---

### Code styling and linting

- [Black](https://black.readthedocs.io/en/stable/) for formatting
- [isort](https://pycqa.github.io/isort/) to sort imports
- [Flakehell](https://flakehell.readthedocs.io/) for linting
- [mypy](https://mypy.readthedocs.io/en/stable/) for static type checking

```bash
pdm format
```

### Running unit tests

```bash
pdm test
```

### Build

The build will transpile the custom agent check to Python 2.7 and creates and install shell script packaged into
the `dist/rancher-agent-check-0.1.0.zip`

```bash
pdm build
```

### Building a StackState Agent container

You have the ability to customize the StackState Agent using the [Dockerfile](sts-rancher-agent-checks/tasks/dev-agent/Dockerfile).

For installing os packages or other tools at runtime, you could define an `install.sh` file in the `tests/resources/share/` directory that is run every time the container is started.

```bash
pdm cleanAgent
pdm buildAgent
```

### Running your custom agent check

A check can be dry-run inside the StackState Agent container by running:

```bash
pdm check
```

### Starting the StackState Agent to send data to StackState server

Starts the StackState Agent in the foreground using the configuration `src/data/conf.d/` directory.

```bash
pdm serve
```
---
