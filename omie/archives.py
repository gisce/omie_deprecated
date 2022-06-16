# -*- coding: utf-8 -*-
from datetime import datetime
from libsaas import http, parsers, port
from libsaas.services import base

from omie.utils import translate_param, serialize_param


def parser_none(body, code, headers):
    return body


class Archive(base.RESTResource):
    path = 'archives'

    def get_filename(self):
        return self.__class__.__name__

    @base.apimethod
    def get(self, start_date, end_date, taxonomy_terms=None):
        assert isinstance(start_date, datetime)
        assert isinstance(end_date, datetime)
        if taxonomy_terms is None:
            taxonomy_terms = []
        assert isinstance(taxonomy_terms, (list, tuple))

        date_type = 'datos'
        start_date = start_date.isoformat()
        end_date = end_date.isoformat()
        locale = 'en'
        param_list = ('locale', 'start_date', 'end_date', 'date_type')
        if taxonomy_terms:
            param_list += ('taxonomy_terms',)
        params = base.get_params(
            param_list,
            locals(),
            translate_param=translate_param,
            serialize_param=serialize_param,
        )
        request = http.Request('GET', self.get_url(), params)

        return request, parsers.parse_json

    @base.apimethod
    def download(self, start_date, end_date, taxonomy_terms=None):
        """
        Download the best file version for a range of dates and the desired taxonomy terms
        """
        assert isinstance(start_date, datetime)
        assert isinstance(end_date, datetime)
        if taxonomy_terms is None:
            taxonomy_terms = []
        assert isinstance(taxonomy_terms, (list, tuple))
        # gets filename from class name
        filename = self.get_filename()

        body = self.get(start_date, end_date, taxonomy_terms)
        regs = [a for a in body['archives'] if filename in a['name']]

        url = regs[0]['download']['url']

        request = http.Request('GET', self.parent.get_url() + url)
        return request, parser_none


class MAJ(Archive):

    def get_filename(self):
        return super(MAJ, self).get_filename().lower()

    def get(self, start_date, end_date, taxonomy_terms=None):
        if taxonomy_terms is None:
            taxonomy_terms = []
        taxonomy_terms.append('Schedules')
        return super(MAJ, self).get(start_date, end_date, taxonomy_terms)
