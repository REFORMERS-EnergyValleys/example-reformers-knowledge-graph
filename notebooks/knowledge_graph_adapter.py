import json
from collections import defaultdict
from typing import Any
from SPARQLWrapper import SPARQLWrapper, JSON, POST

class KnowledgeGraphAdapter:

    def __init__(
            self,
            endpoint: str
        ) -> None:
        self.db_connect = SPARQLWrapper(endpoint)
        self.db_connect.setMethod(POST)
        self.db_connect.setReturnFormat(JSON)

    # Query template for selecting attributes associated to wind turbines
    SELECT_TURBINE_ATTRIBUTES = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dici_core: <urn:digicities:core#>
        PREFIX dici_reformers: <urn:digicities:reformers#>
        SELECT ?turbine_name ?attr_name ?attr WHERE {{
            ?turbine a dici_reformers:WindTurbine ;
                rdfs:label ?turbine_name .
            ?turbine dici_reformers:hasWindTurbineAttribute ?attr .
            ?attr a ?attr_type .
            ?attr_type rdfs:subClassOf dici_reformers:WindTurbineAttribute ;
                rdfs:label ?attr_name .
            ?turbine dici_core:usedInScenario ?scenario .
            ?scenario a dici_core:Scenario ;
                rdfs:label "{scenario_name}" .
        }}
        """

    # Query template for retrieving attribute values
    SELECT_ATTRIBUTE_VALUE = """
        PREFIX qudt: <http://qudt.org/schema/qudt/>
        SELECT ?value where {{
            <{urn}> qudt:value ?value .
        }}
        """

    def retrieve_turbine_info(
            self,
            scenario_name: str
        ) -> dict:
        """
        Retrieve all information related to the wind turbines of a specific scenario
        """
        # Retrieve list of attributes
        query_turbine_attributes = self.SELECT_TURBINE_ATTRIBUTES.format(scenario_name=scenario_name)
        turbine_attributes = self._retrieve_from_db(query_turbine_attributes)

        # Retrieve attribute values and convert list to nested dict
        out = defaultdict(dict)
        for turbine, name, urn in turbine_attributes:
            query_attribute_value = self.SELECT_ATTRIBUTE_VALUE.format(urn=urn)
            out[turbine][name] = self._retrieve_from_db(query_attribute_value)[0][0]
        return dict(out)

    def _retrieve_from_db(self, query: str) -> list[tuple]:
        """
        Send query to graph database and retrieve results
        """
        self.db_connect.setQuery(query)
        result : dict[str, dict] = self.db_connect.queryAndConvert()
        vars = result['head']['vars']
        bindings = result['results']['bindings']
        return [tuple(KnowledgeGraphAdapter._retrieve_variable(entry, var) for var in vars) for entry in bindings]

    @staticmethod
    def _retrieve_variable(entry: dict, var: str) -> Any:
        """
        Helper function: retrieve variable and cast to proper type
        """
        data = entry[var]
        datatype = data.get('datatype')
        match datatype:
            case 'http://www.w3.org/2001/XMLSchema#decimal':
                return float(entry[var]['value'])
            case 'https://www.w3.org/2019/wot/json-schema#Json':
                return json.loads(entry[var]['value'])
            case _:
                return entry[var]['value']
