# Copyright (c) 2012, Benjamin Vanheuverzwijn <bvanheu@gmail.com>
# All rights reserved.
#
# Thanks to Marc-Etienne M. Leveille
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import json
import urllib.request
import urllib.parse
import urllib.error
import toutv.mapper
import toutv.config
import toutv.bos as bos


class Transport:
    def __init__(self):
        pass

    def get_emissions(self):
        pass

    def get_emission_episodes(self, emission_id):
        pass

    def get_page_repertoire(self):
        pass

    def search_terms(self, query):
        pass


class JsonTransport(Transport):
    def __init__(self):
        self.json_decoder = json.JSONDecoder()
        self.mapper = toutv.mapper.JsonMapper()

    def _do_query(self, method, parameters={}):
        parameters_str = urllib.parse.urlencode(parameters)
        url = ''.join([
            toutv.config.TOUTV_JSON_URL,
            method,
            '?',
        parameters_str])
        headers = {'User-Agent': toutv.config.USER_AGENT}
        request = urllib.request.Request(url, None, headers)
        json_string = urllib.request.urlopen(request).read().decode('utf-8')
        json_decoded = self.json_decoder.decode(json_string)
        return json_decoded['d']

    def get_emissions(self):
        emissions = {}
        emissions_dto = self._do_query('GetEmissions')

        for emission_dto in emissions_dto:
            emission = self.mapper.dto_to_bo(emission_dto, bos.Emission)
            emissions[emission.Id] = emission

        return emissions

    def get_emission_episodes(self, emission_id):
        episodes = {}
        episodes_dto = self._do_query('GetEpisodesForEmission',
                                      {'emissionid': str(emission_id)})

        if episodes_dto:
            for episode_dto in episodes_dto:
                episode = self.mapper.dto_to_bo(episode_dto, bos.Episode)
                episodes[episode.Id] = episode

        return episodes

    def get_page_repertoire(self):
        repertoire = {}
        repertoire_dto = self._do_query('GetPageRepertoire')

        if repertoire_dto:
            # EmissionRepertoire
            if repertoire_dto:
                emissionrepertoires = {}
                for emissionrepertoire_dto in repertoire_dto['Emissions']:
                    er = self.mapper.dto_to_bo(emissionrepertoire_dto,
                                               bos.EmissionRepertoire)
                    emissionrepertoires[er.Id] = er
                repertoire['emissionrepertoire'] = emissionrepertoires
            # Genre
            if repertoire_dto['Genres']:
                pass
            # Country
            if repertoire_dto['Pays']:
                pass

        return repertoire

    def search(self, query):
        searchresults_dto = self._do_query('SearchTerms', {'query': query})
        searchresults = None
        searchresultdatas = []

        if searchresults_dto:
            searchresults = self.mapper.dto_to_bo(searchresults_dto,
                                                  bos.SearchResults)
            if searchresults.Results is not None:
                for searchresultdata_dto in searchresults.Results:
                    sr_bo = self.mapper.dto_to_bo(searchresultdata_dto,
                                                  bos.SearchResultData)
                    searchresultdatas.append(sr_bo)
            searchresults.Results = searchresultdatas

        return searchresults