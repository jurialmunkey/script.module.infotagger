# -*- coding: utf-8 -*-
# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
from xbmc import Actor, VideoStreamDetail, AudioStreamDetail, SubtitleStreamDetail, LOGINFO
from xbmc import log as kodi_log


class ListItemInfoTag():
    INFO_TAG_ATTR = {
        'video': {
            'tag_getter': 'getVideoInfoTag',
            'tag_attr': {
                'genre': {'attr': 'setGenres', 'convert': lambda x: [x], 'type': list},
                'country': {'attr': 'setCountries', 'convert': lambda x: [x], 'type': list},
                'year': {'attr': 'setYear', 'convert': int, 'type': int},
                'episode': {'attr': 'setEpisode', 'convert': int, 'type': int},
                'season': {'attr': 'setSeason', 'convert': int, 'type': int},
                'sortepisode': {'attr': 'setSortEpisode', 'convert': int, 'type': int},
                'sortseason': {'attr': 'setSortSeason', 'convert': int, 'type': int},
                'episodeguide': {'attr': 'setEpisodeGuide', 'convert': str, 'type': str},
                'showlink': {'attr': 'setShowLinks', 'convert': lambda x: [x], 'type': list},
                'top250': {'attr': 'setTop250', 'convert': int, 'type': int},
                'setid': {'attr': 'setSetId', 'convert': int, 'type': int},
                'tracknumber': {'attr': 'setTrackNumber', 'convert': int, 'type': int},
                'rating': {'attr': 'setRating', 'convert': float, 'type': float},
                'userrating': {'attr': 'setUserRating', 'convert': int, 'type': int},
                'watched': {'skip': True},  # Evaluated internally in Nexus based on playcount so skip
                'playcount': {'attr': 'setPlaycount', 'convert': int, 'type': int},
                'overlay': {'skip': True},  # Evaluated internally in Nexus based on playcount so skip
                'cast': {'route': 'set_info_cast'},
                'castandrole': {'route': 'set_info_cast'},
                'director': {'attr': 'setDirectors', 'convert': lambda x: [x], 'type': list},
                'mpaa': {'attr': 'setMpaa', 'convert': str, 'type': str},
                'plot': {'attr': 'setPlot', 'convert': str, 'type': str},
                'plotoutline': {'attr': 'setPlotOutline', 'convert': str, 'type': str},
                'title': {'attr': 'setTitle', 'convert': str, 'type': str},
                'originaltitle': {'attr': 'setOriginalTitle', 'convert': str, 'type': str},
                'sorttitle': {'attr': 'setSortTitle', 'convert': str, 'type': str},
                'duration': {'attr': 'setDuration', 'convert': int, 'type': int},
                'studio': {'attr': 'setStudios', 'convert': lambda x: [x], 'type': list},
                'tagline': {'attr': 'setTagLine', 'convert': str, 'type': str},
                'writer': {'attr': 'setWriters', 'convert': lambda x: [x], 'type': list},
                'tvshowtitle': {'attr': 'setTvShowTitle', 'convert': str, 'type': str},
                'premiered': {'attr': 'setPremiered', 'convert': str, 'type': str},
                'status': {'attr': 'setTvShowStatus', 'convert': str, 'type': str},
                'set': {'attr': 'setSet', 'convert': str, 'type': str},
                'setoverview': {'attr': 'setSetOverview', 'convert': str, 'type': str},
                'tag': {'attr': 'setTags', 'convert': lambda x: [x], 'type': list},
                'imdbnumber': {'attr': 'setIMDBNumber', 'convert': str, 'type': str},
                'code': {'attr': 'setProductionCode', 'convert': str, 'type': str},
                'aired': {'attr': 'setFirstAired', 'convert': str, 'type': str},
                'credits': {'attr': 'setWriters', 'convert': lambda x: [x], 'type': list},
                'lastplayed': {'attr': 'setLastPlayed', 'convert': str, 'type': str},
                'album': {'attr': 'setAlbum', 'convert': str, 'type': str},
                'artist': {'attr': 'setArtists', 'convert': lambda x: [x], 'type': list},
                'votes': {'attr': 'setVotes', 'convert': int, 'type': int},
                'path': {'attr': 'setPath', 'convert': str, 'type': str},
                'trailer': {'attr': 'setTrailer', 'convert': str, 'type': str},
                'dateadded': {'attr': 'setDateAdded', 'convert': str, 'type': str},
                'mediatype': {'attr': 'setMediaType', 'convert': str, 'type': str},
                'dbid': {'attr': 'setDbId', 'convert': int, 'type': int},
            }
        },
        'music': {
            'tag_getter': 'getMusicInfoTag',
            'tag_attr': {}
        },
        'pictures': {
            'tag_getter': 'getPictureInfoTag',
            'tag_attr': {}
        },
        'game': {
            'tag_getter': 'getGameInfoTag',
            'tag_attr': {}
        }
    }

    def __init__(self, listitem, tag_type: str = 'video'):
        self._listitem = listitem
        self._tag_type = tag_type
        self._tag_attr = self.INFO_TAG_ATTR[tag_type]['tag_attr']
        self._info_tag = getattr(self._listitem, self.INFO_TAG_ATTR[tag_type]['tag_getter'])()

    def set_info(self, infolabels: dict):
        """ Wrapper for compatibility with Matrix ListItem.setInfo() method """
        for k, v in infolabels.items():
            if v is None:
                continue
            try:
                func = getattr(self._info_tag, self._tag_attr[k]['attr'])
                func(v)
            except KeyError:
                if k not in self._tag_attr:
                    log_msg = f'[script.module.infotagger] set_info:\nKeyError: {k}'
                    kodi_log(log_msg, level=LOGINFO)
                    continue

                if self._tag_attr[k].get('skip'):
                    continue

                if 'route' in self._tag_attr[k]:
                    getattr(self, self._tag_attr[k]['route'])(v)
                    continue

                log_msg = self._tag_attr[k].get('log_msg') or ''
                log_msg = f'[script.module.infotagger] set_info:\nKeyError: {log_msg}'
                kodi_log(log_msg, level=LOGINFO)
                continue

            except TypeError:
                func(self._tag_attr[k]['convert'](v))  # Attempt to force conversion to correct type

    def set_info_cast(self, cast: list):
        """ Wrapper for compatibility with Matrix ListItem.setCast() method """
        def _set_cast_member(x, i):
            if not isinstance(i, tuple):
                i = (i, '',)
            return {'name': f'{i[0]}', 'role': f'{i[1]}', 'order': x, 'thumbnail': ''}

        self._info_tag.setCast([Actor(**_set_cast_member(x, i)) for x, i in enumerate(cast, start=1)])

    def set_cast(self, cast: list):
        """ Wrapper for compatibility with Matrix ListItem.setCast() method """
        self._info_tag.setCast([Actor(**i) for i in cast])

    def set_unique_ids(self, unique_ids: dict, default_id: str = None):
        """ Wrapper for compatibility with Matrix ListItem.setUniqueIDs() method """
        self._info_tag.setUniqueIDs({k: f'{v}' for k, v in unique_ids.items()}, default_id)

    def set_stream_details(self, stream_details: dict):
        """ Wrapper for compatibility with multiple ListItem.addStreamInfo() methods in one call """
        if not stream_details:
            return

        try:
            for i in stream_details['video']:
                try:
                    self._info_tag.addVideoStream(VideoStreamDetail(**i))
                except TypeError:
                    # TEMP BANDAID workaround for inconsistent key names prior to Nexus Beta changes
                    i['hdrType'] = i.pop('hdrtype', '')
                    i['stereoMode'] = i.pop('stereomode', '')
                    self._info_tag.addVideoStream(VideoStreamDetail(**i))
        except (KeyError, TypeError):
            pass

        try:
            for i in stream_details['audio']:
                self._info_tag.addAudioStream(AudioStreamDetail(**i))
        except (KeyError, TypeError):
            pass

        try:
            for i in stream_details['subtitle']:
                self._info_tag.addSubtitleStream(SubtitleStreamDetail(**i))
        except (KeyError, TypeError):
            pass

    def add_stream_info(self, stream_type, stream_values):
        """ Wrapper for compatibility with Matrix ListItem.addStreamInfo() method """
        stream_details = {'video': [], 'audio': [], 'subtitle': []}
        stream_details[stream_type] = [stream_values]
        self.set_stream_details(stream_details)
