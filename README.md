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
curl -L https://github.com/stackstate-lab/sts-rancher-agent-checks/releases/download/v0.1.0/sts_rancher-0.1.0.zip -o sts_rancher.zip
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

See [Instance Model](./src/sts_rancher/sts_rancher_impl/model/instance.py) for complete options.

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
| [rancher](./src/sts_rancher/sts_rancher_impl/templates/010_default.yaml)   | sts_rancher_impl.client   | [RancherClient](src/sts_rancher/sts_rancher_impl/client/rancher_client.py)  | enables rest calls to rancher  api |


### Template Mappings

| Name                                                                                                                | Type                | 4T        | rancher Api                                                                                  | Description |
|---------------------------------------------------------------------------------------------------------------------|---------------------|-----------|----------------------------------------------------------------------------------------------|-------------|
| [rancher_host_template](./src/sts_rancher/sts_rancher_impl/templates/020_rancher_hosts.yaml)                        | rancher-host        | Component | [v2-beta/projects/{project}/hosts](./tests/resources/responses/sts_hosts.json)               |             |
| [rancher_public_endpoint_template](./src/sts_rancher/sts_rancher_impl/templates/020_rancher_hosts.yaml)             | rancher-endpoint    | Component | [v2-beta/projects/{project}/hosts](./tests/resources/responses/sts_hosts.json)               |             |
| [rancher_host_status_template](./src/sts_rancher/sts_rancher_impl/templates/020_rancher_hosts.yaml)                 | rancher-host        | Health    | [v2-beta/projects/{project}/hosts](./tests/resources/responses/sts_hosts.json)               |             |
| [rancher_service_template](./src/sts_rancher/sts_rancher_impl/templates/020_rancher_services.yaml)                  | rancher-service     | Component | [v2-beta/projects/{project}/services](./tests/resources/responses/sts_services.json)         |             |
| [rancher_service_status_template](./src/sts_rancher/sts_rancher_impl/templates/020_rancher_services.yaml)           | rancher-service     | Health    | [v2-beta/projects/{project}/services](./tests/resources/responses/sts_services.json)         |             |
| [rancher_stack_template](./src/sts_rancher/sts_rancher_impl/templates/040_rancher_stacks.yaml)                      | rancher-stack       | Component | [v2-beta/projects/{project}/stacks](./tests/resources/responses/sts_stacks.json)             |             |
| [rancher_stack_status_template](./src/sts_rancher/sts_rancher_impl/templates/040_rancher_stacks.yaml)               | rancher-stack       | Health    | [v2-beta/projects/{project}/stacks](./tests/resources/responses/sts_stacks.json)             |             |
| [rancher_container_template](./src/sts_rancher/sts_rancher_impl/templates/050_rancher_containers.yaml)              | rancher-container   | Component | [v2-beta/projects/{project}/containers](./tests/resources/responses/sts_containers.json)     |             |
| [rancher_container_status_template](./src/sts_rancher/sts_rancher_impl/templates/050_rancher_containers.yaml)       | rancher-container   | Health    | [v2-beta/projects/{project}/containers](./tests/resources/responses/sts_containers.json)     |             |
| [rancher_volume_template](./src/sts_rancher/sts_rancher_impl/templates/060_rancher_volumes.yaml)                    | rancher-volume      | Component | [v2-beta/projects/{project}/volumes](./tests/resources/responses/sts_volumes.json)           |             |
| [rancher_volume_status_template](./src/sts_rancher/sts_rancher_impl/templates/060_rancher_volumes.yaml)             | rancher-volume      | Health    | [v2-beta/projects/{project}/volumes](./tests/resources/responses/sts_volumes.json)           |             |
| [rancher_storage_pool_template](./src/sts_rancher/sts_rancher_impl/templates/062_rancher_storage_pools.yaml)        | rancher-storagepool | Component | [v2-beta/projects/{project}/storagepools](./tests/resources/responses/sts_storagepools.json) |             |
| [rancher_storage_pool_status_template](./src/sts_rancher/sts_rancher_impl/templates/062_rancher_storage_pools.yaml) | rancher-storagepool | Health    | [v2-beta/projects/{project}/storagepools](./tests/resources/responses/sts_storagepools.json) |             |
| [rancher_network_template](./src/sts_rancher/sts_rancher_impl/templates/070_rancher_networks.yaml)                  | rancher-network     | Component | [v2-beta/projects/{project}/networks](./tests/resources/responses/sts_networks.json)         |             |
| [rancher_network_status_template](./src/sts_rancher/sts_rancher_impl/templates/070_rancher_networks.yaml)           | rancher-network     | Health    | [v2-beta/projects/{project}/networks](./tests/resources/responses/sts_networks.json)         |             |


## Development

StackState Rancher Agent Check is developed in Python 3, and is transpiled to Python 2.7 during build.

---
### Prerequisites:

- Python v.3.7+. See [Python installation guide](https://docs.python-guide.org/starting/installation/)
- [Poetry](https://python-poetry.org/docs/#installation)
- [Docker](https://www.docker.com/get-started)
- [Custom Synchronization StackPack](https://docs.stackstate.com/stackpacks/integrations/customsync)
---

### Setup local code repository


The poetry install command creates a virtual environment and downloads the required dependencies.

Install the [stsdev](https://github.com/stackstate-lab/stslab-dev) tool into the virtual environment.

```bash 
python -m pip install https://github.com/stackstate-lab/stslab-dev/releases/download/v0.0.7/stslab_dev-0.0.7-py3-none-any.whl
```

Finalize the downloading of the StackState Agent dependencies using `stsdev`

```bash
stsdev update
```
### Prepare local `.env` file

The `.env` file is used by `stsdev` to prepare and run the StackState Agent Docker image. Remember to change the
StackState url and api key for your environment.

```bash

cat <<EOF > ./.env
STSDEV_IMAGE_EXT=tests/resources/docker/agent_dockerfile
STS_URL=https://xxx.stackstate.io/receiver/stsAgent
STS_API_KEY=xxx
STSDEV_ADDITIONAL_COMMANDS=/etc/stackstate-agent/share/install.sh
STSDEV_ADDITIONAL_COMMANDS_FG=true
EXCLUDE_LIBS=charset-normalizer,stackstate-etl,stackstate-etl-agent-check
EOF
```
### Preparing Agent check conf.yaml

```
cp ./tests/resources/conf.d/rancher.d/conf.yaml.example ./tests/resources/conf.d/rancher.d/conf.yaml
```
---

### Running in Intellij

Setup the module sdk to point to the virtual python environment created by Poetry.
Default on macos is `~/Library/Caches/pypoetry/virtualenvs`

Create a python test run config for `tests/test_rancher_check.py`

You can now run the integration from the test.

---
### Running using `stsdev`

```bash

stsdev agent check rancher 
```

### Running StackState Agent to send data to StackState

```bash

stsdev agent run
```

---

## Quick-Start for `stsdev`

`stsdev` is a tool to aid with the development StackState Agent integrations.

### Managing dependencies

[Poetry](https://python-poetry.org/) is used as the packaging and dependency management system.

Dependencies for your project can be managed through `poetry add` or `poetry add -D` for development dependency.

```console
$ poetry add PyYAML
```
### Code styling and linting

```console
$ stsdev code-style
```

### Build the project
To build the project,
```console
$ stsdev build --no-run-tests
```
This will automatically run code formatting, linting, tests and finally the build.

### Unit Testing
To run tests in the project,
```console
$ stsdev test
```
This will automatically run code formatting, linting, and tests.

### Dry-run a check

A check can be dry-run inside the StackState Agent by running

```console
$ stsdev agent check rancher
```
Before running the command, remember to copy the example conf `tests/resources/conf.d/rancher.d/conf.yaml.example` to
`tests/resources/conf.d/rancher.d/conf.yaml`.


### Running checks in the Agent

Starts the StackState Agent in the foreground using the test configuration `tests/resources/conf.d`

```console
$ stsdev agent run
```

### Packaging checks

```console
$  stsdev package --no-run-tests
```
This will automatically run code formatting, linting, tests and finally the packaging.
A zip file is created in the `dist` directory.  Copy this to the host running the agent and unzip it.
Run the `install.sh`.

