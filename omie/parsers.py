# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .archives import MAJ
from datetime import datetime
from dateutil.relativedelta import relativedelta
from io import BytesIO
from lxml import etree, objectify
from lxml.etree import XMLSyntaxError
from pytz import timezone
import json
import os.path
import zipfile


_ROOT = os.path.abspath(os.path.dirname(__file__))

XSD_PATH = os.path.join(_ROOT, 'data')

MAJ_XSD = 'MAJ-OMIE.xsd'

LOCAL_TZ = timezone('Europe/Madrid')
UTC_TZ = timezone('UTC')


class MAJParser(MAJ):

    def get_filename(self):
        return 'maj'

    def config_validators(self):

        xmlschema_doc = etree.parse(os.path.join(XSD_PATH, MAJ_XSD))
        xmlschema = etree.XMLSchema(xmlschema_doc)
        self.maj_parser = objectify.makeparser(schema=xmlschema)

    def get_data_json(self, program_unit, start, end):
        res = self.download(start, end)
        return self.parse_to_json(res, program_unit)

    def get_data_json_from_file(self, program_unit, filepath):
        with open(filepath, 'rb') as filereader:
            res = filereader.read()
        return self.parse_to_json(res, program_unit)

    def parse_to_json(self, file_content, program_unit):
        """
        Returns a json from file. it may be a zip fail containing several fails
        :param file_content: the file content
        :param program_unit: The Program Unit to parse
        :return: a json list of dicts
        """
        self.config_validators()

        content = BytesIO(file_content)

        zip_filenames = []

        try:
            zf = zipfile.ZipFile(content)
            if zf.testzip() is None:
                # Multiple files in one zip
                zip_filenames = zf.namelist()
        except zipfile.BadZipfile as e:
            # single file XML
            result = self.parse_maj(file_content, program_unit)
            return json.dumps(result, default=str)

        data = []
        for filename in zip_filenames:
            content = zf.read(filename)
            data.extend(self.parse_maj(content, program_unit))
        return json.dumps(data, default=str)

    def parse_maj(self, content, program_unit):
        """
        Returns a list of registers, one per hour of the program_unit selected from de XML content.
        It validates de file previously
        :param content: XML to parse
        :param program_unit: Program unit to get
        :return: A list of registers:
        {
            "hour":             Hour in the XML field
            "up":               Program_unit: "SOMEC01",
            "value":            Float: Quantity of Energy programmed in MWh
            "magn":             Str:
                                 * ECMAJ: MAJ cost
                                 * EECMD: Energy cost
            "utc_timestamp":    UTC timestamp of the register
            "local_timestamp":  Local timestamp calculated,
        },
        """
        is_maj = self.is_maj_type(content)

        # padrsing
        xmlobj = etree.XML(content)
        # Search UP
        e = xmlobj.xpath('//*[@v="{}"]'.format(program_unit))

        # SeriesTemporales Node
        st = e[0].getparent()
        # Periodo
        periodo = st[4]
        # Curve:
        curve = []
        for e in periodo:
            if 'IntervaloTiempo' in e.tag:
                value = e.get('v')
                start_str, end_str = value.split('/')
                start = UTC_TZ.localize(datetime.strptime(start_str, '%Y-%m-%dT%H:%MZ'))
                end = UTC_TZ.localize(datetime.strptime(end_str, '%Y-%m-%dT%H:%MZ'))
            elif 'Intervalo' not in e.tag:
                continue
            else:
                hour = int(e[0].get('v'))
                value = float(e[1].get('v'))
                utc_timestamp = start + relativedelta(hours=hour)
                local_timestamp = LOCAL_TZ.normalize(utc_timestamp.astimezone(LOCAL_TZ))
                curve.append({
                    'up': program_unit,
                    'hour': hour,
                    'value': value,
                    'utc_timestamp': utc_timestamp,
                    'local_timestamp': local_timestamp,
                })

        return curve

    def is_maj_type(self, content):
        """
        MAJ informs 2 magn:
        * ECMAJ (compensation cost)
        * EECMD (energy cost)
        We only care about ECMAJ
        :param content:
        :return: True: ECMAJ , False: EECMD
        """
        try:
            objectify.fromstring(content, self.maj_parser)
            return True
        except XMLSyntaxError as e:
            return False
