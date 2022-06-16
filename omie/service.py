# -*- coding: utf-8 -*-
import json

from libsaas import http
from libsaas.services import base

from omie import archives


class Omie(base.Resource):
    """
    OMIE Service API.
    """
    def __init__(self, token):
        # TODO Add OMIE apiroot
        # TODO Add OMIE apiversion
        self.token = token
        self.apiroot = 'https://'
        self.version = 'v2'
        self.add_filter(self.use_json)
        self.add_filter(self.accepted_version)
        self.add_filter(self.add_token)

    def use_json(self, request):
        if request.method.upper() not in http.URLENCODE_METHODS:
            request.headers['Content-Type'] = 'application/json'
            request.params = json.dumps(request.params)

    def add_token(self, request):
        request.headers['Authorization'] = 'Token token="{0}"'.format(self.token)

    def accepted_version(self, request):
        # TODO add OMIE API version check
        request.headers['Accept'] = 'application/json; application/vnd.esios-api-{0}+json'.format(self.version)

    def get_url(self):
        return self.apiroot

    @base.resource(archives.MAJ)
    def maj(self):
        """Get the MAJ file
        """
        return archives.MAJ(self)
