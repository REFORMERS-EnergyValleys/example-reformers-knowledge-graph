# Example knowledge graph for the REFORMERS Digital Twin

## About

This example shows how to set up and use a graph database, providing a knowlege graph for the REFORMERS Digital Twin.
A [Jupyter notebook](https://docs.jupyter.org/en/latest/#what-is-a-notebook) shows how to retrieve data from the graph database.

## Requirements

The following software needs to be installed to run the prototype:

+ [Docker](https://docs.docker.com/get-started/get-docker/) (incl. [Docker Compose](https://docs.docker.com/compose/)): used to run the graph database
+ [Python](https://www.python.org/): for running the interactive [Jupyter notebook](https://docs.jupyter.org/en/latest/#what-is-a-notebook) that shows how to retrieve data from the graph database

All Python packages required for running the Jupyter notebook are listed in file [`notebooks/requirements.txt`](./notebooks/requirements.txt).
*NOTE*: [This guide](https://realpython.com/what-is-pip/) explains how to use `pip` and requirement files for installing Python packages.

## Usage

Start the graph database:
``` bash
docker compose up -d
```

After successful start-up, the graph database will be accessible at http://localhost:7200

Run [`notebooks/retrieve_data.ipynb`](./notebooks/retrieve_data.ipynb) to retrieve data from the knowledge graph.

## Funding acknowledgement

<img alt="European Flag" src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Flag_of_Europe.svg/330px-Flag_of_Europe.svg.png" align="left" style="margin-right: 10px" height="57"/> This development has been supported by the [REFORMERS] project of the European Union’s research and innovation programme Horizon Europe under the grant agreement No.101136211.

[REFORMERS]: https://reformers-energyvalleys.eu/
