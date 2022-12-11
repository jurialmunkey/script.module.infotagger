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
                'genre': {'attr': 'setGenres', 'type': list},
                'country': {'attr': 'setCountries', 'type': list},
                'year': {'attr': 'setYear', 'type': int},
                'episode': {'attr': 'setEpisode', 'type': int},
                'season': {'attr': 'setSeason', 'type': int},
                'sortepisode': {'attr': 'setSortEpisode', 'type': int},
                'sortseason': {'attr': 'setSortSeason', 'type': int},
                'episodeguide': {'attr': 'setEpisodeGuide', 'type': str},
                'showlink': {'attr': 'setShowLinks', 'type': list},
                'top250': {'attr': 'setTop250', 'type': int},
                'setid': {'attr': 'setSetId', 'type': int},
                'tracknumber': {'attr': 'setTrackNumber', 'type': int},
                'rating': {'attr': 'setRating', 'type': float},
                'userrating': {'attr': 'setUserRating', 'type': int},
                'watched': {'skip': True},  # Evaluated internally in Nexus based on playcount so skip
                'playcount': {'attr': 'setPlaycount', 'type': int},
                'overlay': {'skip': True},  # Evaluated internally in Nexus based on playcount so skip
                'cast': {'route': 'set_info_cast'},
                'castandrole': {'route': 'set_info_cast'},
                'director': {'attr': 'setDirectors', 'type': list},
                'mpaa': {'attr': 'setMpaa', 'type': str},
                'plot': {'attr': 'setPlot', 'type': str},
                'plotoutline': {'attr': 'setPlotOutline', 'type': str},
                'title': {'attr': 'setTitle', 'type': str},
                'originaltitle': {'attr': 'setOriginalTitle', 'type': str},
                'sorttitle': {'attr': 'setSortTitle', 'type': str},
                'duration': {'attr': 'setDuration', 'type': int},
                'studio': {'attr': 'setStudios', 'type': list},
                'tagline': {'attr': 'setTagLine', 'type': str},
                'writer': {'attr': 'setWriters', 'type': list},
                'tvshowtitle': {'attr': 'setTvShowTitle', 'type': str},
                'premiered': {'attr': 'setPremiered', 'type': str},
                'status': {'attr': 'setTvShowStatus', 'type': str},
                'set': {'attr': 'setSet', 'type': str},
                'setoverview': {'attr': 'setSetOverview', 'type': str},
                'tag': {'attr': 'setTags', 'type': list},
                'imdbnumber': {'attr': 'setIMDBNumber', 'type': str},
                'code': {'attr': 'setProductionCode', 'type': str},
                'aired': {'attr': 'setFirstAired', 'type': str},
                'credits': {'attr': 'setWriters', 'type': list},
                'lastplayed': {'attr': 'setLastPlayed', 'type': str},
                'album': {'attr': 'setAlbum', 'type': str},
                'artist': {'attr': 'setArtists', 'type': list},
                'votes': {'attr': 'setVotes', 'type': int},
                'path': {'attr': 'setPath', 'type': str},
                'trailer': {'attr': 'setTrailer', 'type': str},
                'dateadded': {'attr': 'setDateAdded', 'type': str},
                'mediatype': {'attr': 'setMediaType', 'type': str},
                'dbid': {'attr': 'setDbId', 'type': int},
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
                func(self._tag_attr[k]['type'](v))  # Attempt to force conversion to correct type

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
        """ Wrapper for compatibility with Matrix ListItem.addStreamInfo() method """
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
