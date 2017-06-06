"""
QuranRef API
============

API access to the QuranRef site

GET /api/v1/assets
__________________

Return a list of all assets of the current user. Requires user's auth token in request headers.

Example::

    curl "http://api.threatify.com/api/v1/assets" -H "Content-Type: application/json"

Returns something like::

    [
        {
            "_id": "domains/www.threatify.com",
            "verified": true,
            "value": "www.threatify.com",
            "_relations": [
                  {"has_ip": "ip_addresses/122.122.122.122"}
             ]
        },
        {
            "_id": "ip_addresses/122.122.122.122",
            "verified": false,
            "value": "122.122.122.122"
        }
    ]


GET /api/v1/assets/{asset_id}
_____________________________

Return details of given asset. Please note that asset ID is of the form
**domains/www.threatify.com**. Supports the query string parameter depth. Depth specifies how
much information is required. Default is 1 which also returns all relations and their
information. All linked documents are placed inside the _relations key.

Example::

    curl -XGET "http://api.threatify.com/api/v1/assets/domains/www.threatify.com -H "Content-Type: application/json"

Returns something like::


    {
        "_id": "domains/www.threatify.com",
        "verified": true,
        "value": "www.threatify.com",
        "_relations": [
            {
                "has_ip": {
                    "_id": "ip_addresses/122.122.122.122",
                    "verified": false,
                    "value": "122.122.122.122"
                }
            }
         ]
    }

POST /api/v1/assets
___________________

Creates a new asset for the user. Assets that the user adds using this API are automatically
marked as verified. Requires user's auth token in request headers. Requires the following info in
POST's JSON data:

* **asset_type**: Currently can be either **domain** or **ip**
* **value**: The actual domain or ip address of the asset.

Example::

    curl -XPOST "http://api.threatify.com/api/v1/assets" -H "Content-Type: application/json" \\
    -X POST -d '{"asset_type": "domain", "value": "threatify.com"}'

Returns::

    {"msg": "ok", "_id": "domains/threatify.com"}


"""

import logging


from pyramid.view import view_defaults, view_config
from .api_base import APIBase
from .exceptions import APIForbidden, APIBadRequest, APITooManyRequests

from ..graph_models.quran_graph import QuranGraph, Surah, Aya, Text
from .. import graph_models

log = logging.getLogger(__name__)


@view_defaults(route_name='api', renderer="prettyjson")
class QrefAPI(APIBase):

    _ENDPOINTS = {
        'GET': [
            ('surahs', 'surah_list'),
            ('text_types', 'get_text_types'),
            ('qref/{text_type}/{surah}', 'qref_arabic_text'),
            ('qref/{text_type}/{surah}/{aya}', 'qref_arabic_text')
        ],
        # 'POST': [
        #     ('', 'new_asset')
        # ]
    }

    @view_config(request_method=("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"))
    def request_handler(self):
        return self.handle_request()

    def surah_list(self):
        gdb = graph_models.gdb
        surahs = gdb.query(Surah).sort("surah_number").all()
        log.debug(surahs)

        return [s._dump() for s in surahs]

    def get_text_types(self):

        aql = """
        FOR doc IN aya_texts
            FILTER doc.language=='arabic'
        RETURN DISTINCT doc.text_type
        """

        gdb = graph_models.gdb
        results = [r for r in gdb._db.aql.execute(aql)]
        # log.debug(results)

        return sorted(results)

    def qref_arabic_text(self):
        surah = self.endpoint_info['surah']
        text_type = self.endpoint_info['text_type']
        aya = self.endpoint_info.get('aya', None)

        gdb = graph_models.gdb
        surah_doc = gdb.query(Surah).by_key(surah)

        assert surah_doc is not None

        qgraph = QuranGraph(connection=gdb)

        # qgraph.expand(surah_doc, depth=2)
        # log.debug(surah_doc._relations['has'][1]._next._relations)

        aql = """
        FOR v, e, p IN 1..2 OUTBOUND 'surahs/{surah}' GRAPH 'quran_graph'
            FILTER e.text_type=="{text_type}"
            SORT p['vertices'][1].aya_number
        RETURN p
        """.format(surah=surah, text_type=text_type)

        obj = qgraph.aql(aql)
        # log.debug(obj)
        # log.debug(obj._dump())
        # log.debug(obj._relations)
        ayas_arabic = [dict(aya_text=rel._next._relations['aya_texts'][0]._next.text,
                            aya_number=rel._next.aya_number)
                       for rel in obj._relations['has']]
        # log.debug(ayas_arabic)

        # log.debug(obj._relations['has'][1]._next._relations['aya_texts'][0]._next.text)

        ret_dict = surah_doc._dump()
        ret_dict['ayas'] = ayas_arabic

        return ret_dict
    # def _get_asset(self):
    # 
    #     user_id = self._get_auth_user()
    #     col_name = self.endpoint_info['asset_type']
    #     key = self.endpoint_info['asset_id']
    # 
    #     if col_name not in self.supported_collections:
    #         return APIBadRequest("ID not understood")
    # 
    #     rec = graph_models.gdb.query(self.supported_collections[col_name]).by_key(key)
    # 
    #     client_graph = ClientInfrastructureGraph(connection=graph_models.gdb)
    #     client_graph.expand(rec, depth=1, direction='any')
    # 
    #     # verify ownership
    #     assert 'owns' in rec._relations
    #     if user_id != rec._relations['owns'][0]._next._key:
    #         raise APIForbidden("You don't own this asset")
    # 
    #     rec.verified = rec._relations['owns'][0].verified
    # 
    #     # add country and city location for ip addresses
    #     if 'ip_addresses' == col_name:
    #         rec.location = geodb.simple_ip_lookup(key)
    # 
    #     return rec
    # 
    # def get_asset(self):
    # 
    #     rec = self._get_asset()
    #     return graph.convert_to_asset_dict(rec)

