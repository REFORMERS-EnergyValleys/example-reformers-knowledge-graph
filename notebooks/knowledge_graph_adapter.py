import json
from collections import defaultdict
from typing import Any
from SPARQLWrapper import SPARQLWrapper, JSON, POST

class KnowledgeGraphAdapter:

    # Query template for selecting attributes associated to windparks
    SELECT_WINDPARK_ATTRIBUTES = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dici_core: <urn:digicities:core#>
    PREFIX dici_reformers: <urn:digicities:reformers#>
    SELECT ?windpark_name ?attr_name ?attr WHERE {{
        ?scenario a dici_core:Scenario ;
            rdfs:label "{scenario}" .
        ?windpark a dici_reformers:GlobalWindAtlasSite ;
            rdfs:label "{global_wind_atlas_site}" ;
            rdfs:label ?windpark_name .
        ?windpark dici_reformers:hasGlobalWindAtlasSiteAttribute ?attr .
        ?attr a ?attr_type .
        ?attr_type rdfs:subClassOf dici_reformers:GlobalWindAtlasSiteAttribute ;
            rdfs:label ?attr_name .
    }}
    """

    # Query template for selecting attributes associated to wind turbines
    SELECT_WIND_TURBINE_ATTRIBUTES = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dici_core: <urn:digicities:core#>
    PREFIX dici_reformers: <urn:digicities:reformers#>
    SELECT ?turbine_name ?attr_name ?attr WHERE {{
        ?scenario a dici_core:Scenario ;
            rdfs:label "{scenario}" .
        ?windpark a dici_reformers:GlobalWindAtlasSite ;
            rdfs:label "{global_wind_atlas_site}" .
        ?turbine a dici_reformers:WindTurbine ;
            rdfs:label ?turbine_name .
        ?turbine dici_reformers:hasWindTurbineAttribute ?attr .
        ?attr a ?attr_type .
        ?attr_type rdfs:subClassOf dici_reformers:WindTurbineAttribute ;
            rdfs:label ?attr_name .
        ?turbine dici_core:usedInScenario ?scenario .
        ?link a dici_core:ComponentLink ;
            dici_core:hasInputEntity ?windpark ;
            dici_core:linksInputyEntityTo ?turbine ;
            dici_core:usedInScenario ?scenario .
    }}
    """

    # Query template for selecting attributes associated to wind turbine types
    SELECT_WIND_TURBINE_TYPE_ATTRIBUTES = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dici_core: <urn:digicities:core#>
    PREFIX dici_reformers: <urn:digicities:reformers#>
    SELECT DISTINCT ?type_name ?type_attr_name ?type_attr WHERE {{
        ?scenario a dici_core:Scenario ;
            rdfs:label "{scenario}" .
        ?windpark a dici_reformers:GlobalWindAtlasSite ;
            rdfs:label "{global_wind_atlas_site}" .
        ?turbine a dici_reformers:WindTurbine .
        ?turbine dici_reformers:hasWindTurbineWindTurbineTypeAttribute ?type .
    	?type dici_reformers:hasWindTurbineTypeAttribute ?type_attr ;
            rdfs:label ?type_name .
    	?type_attr a ?type_attr_class .
        ?type_attr_class rdfs:subClassOf dici_reformers:WindTurbineTypeAttribute ;
            rdfs:label ?type_attr_name .
        ?turbine dici_core:usedInScenario ?scenario .
        ?link a dici_core:ComponentLink ;
            dici_core:hasInputEntity ?windpark ;
            dici_core:linksInputyEntityTo ?turbine ;
            dici_core:usedInScenario ?scenario .
    }}
    """

    # Query template for retrieving attribute values
    SELECT_ATTRIBUTE_VALUE = """
        PREFIX qudt: <http://qudt.org/schema/qudt/>
        SELECT ?value WHERE {{
            <{urn}> qudt:value ?value .
        }}
        """

    # Query template for retrieving attribute labels
    SELECT_ATTRIBUTE_LABEL = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?label WHERE {{
            <{urn}> rdfs:label ?label .
        }}
        """

    # Query template for retrieving attribute unit
    SELECT_ATTRIBUTE_UNIT = """
        PREFIX dici_core: <urn:digicities:core#>
        SELECT ?unit WHERE {{
            {{
                <{urn}> (dici_core:hasUnit | dici_core:hasUnit/dici_core:xUnit | dici_core:hasUnit/dici_core:yUnit) ?unit .
            }} UNION {{
                FILTER NOT EXISTS {{ <{urn}> dici_core:hasUnit ?any }}
                <{urn}> a ?type .
                ?type (dici_core:hasDefaultUnit | dici_core:hasDefaultUnit/dici_core:xUnit | dici_core:hasDefaultUnit/dici_core:yUnit) ?unit .
            }}
        }}
        """

    def __init__(
            self,
            endpoint: str
        ) -> None:
        self.db_connect = SPARQLWrapper(endpoint)
        self.db_connect.setMethod(POST)
        self.db_connect.setReturnFormat(JSON)

    def retrieve_windpark_info(
            self,
            scenario: str,
            global_wind_atlas_site: str
        ) -> dict:
        """
        Retrieve all information related to the wind turbines of a specific scenario
        """
        # Retrieve list of attributes
        query_windpark_attributes = self.SELECT_WINDPARK_ATTRIBUTES.format(
            scenario=scenario, global_wind_atlas_site=global_wind_atlas_site
            )
        windpark_attributes = self._retrieve_from_db(query_windpark_attributes)

        # Retrieve attribute values, convert list to nested dict, and return.
        return self._collect_in_dict(windpark_attributes)

    def retrieve_turbine_info(
            self,
            scenario: str,
            global_wind_atlas_site: str
        ) -> dict:
        """
        Retrieve all information related to the wind turbines of a specific scenario
        """
        # Retrieve list of attributes
        query_turbine_attributes = self.SELECT_WIND_TURBINE_ATTRIBUTES.format(
            scenario=scenario, global_wind_atlas_site=global_wind_atlas_site
            )
        turbine_attributes = self._retrieve_from_db(query_turbine_attributes)

        # Retrieve attribute values, convert list to nested dict, and return.
        return self._collect_in_dict(turbine_attributes)

    def retrieve_turbine_types(
            self,
            scenario: str,
            global_wind_atlas_site: str
        ) -> dict:
        """
        Retrieve all information related to the wind turbines of a specific scenario
        """
        # Retrieve list of type attributes
        query_turbine_type_attributes = self.SELECT_WIND_TURBINE_TYPE_ATTRIBUTES.format(
            scenario=scenario, global_wind_atlas_site=global_wind_atlas_site
            )
        turbine_type_attributes = self._retrieve_from_db(query_turbine_type_attributes)

        # Retrieve attribute values, convert list to nested dict, and return.
        return self._collect_in_dict(turbine_type_attributes)

    def _collect_in_dict(self, attributes: list) -> dict:
        """
        Retrieve attribute values and convert list to nested dict
        """
        out = defaultdict(dict)
        for entity, name, urn in attributes:
            query_attribute_value = self.SELECT_ATTRIBUTE_VALUE.format(urn=urn)
            value = self._retrieve_from_db(query_attribute_value)
            if value:
                query_attribute_unit = self.SELECT_ATTRIBUTE_UNIT.format(urn=urn)
                unit = self._retrieve_from_db(query_attribute_unit)
                if 1 == len(unit):
                    out[entity][name] = dict(value=value[0][0], unit=unit[0][0])
                else:
                    out[entity][name] = dict(value=value[0][0], unit=[u[0] for u in unit if not u[0][0] == '_'])
            else:
                query_attribute_label = self.SELECT_ATTRIBUTE_LABEL.format(urn=urn)
                label = self._retrieve_from_db(query_attribute_label)
                out[entity][name] = dict(value=label[0][0])
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
                type = data.get('type')
                match type:
                    case 'bnode':
                        return '_:' + entry[var]['value']
                    case _:
                        return entry[var]['value']
