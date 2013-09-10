# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Domain specific language of freebase app.
"""

from quepy.dsl import FixedType, FixedRelation, FixedDataRelation, HasKeyword

# Setup the Keywords for this application
HasKeyword.relation = "/type/object/name"

# Setup Fixed Type
FixedType.fixedtyperelation = "/type/object/type"


class NameOf(FixedRelation):
    relation = "/type/object/name"
    reverse = True


class HasName(FixedDataRelation):
    relation = "/type/object/name"


class GovernmentPosition(FixedDataRelation):
    relation = "/government/government_position_held/basic_title"


class GovernmentPositionJusridiction(FixedRelation):
    relation = "/government/government_position_held/jurisdiction_of_office"


class IsCountry(FixedType):
    fixedtype = "/location/country"


class HoldsGovernmentPosition(FixedRelation):
    relation = "/government/government_position_held/office_holder"
    reverse = True


class DefinitionOf(FixedRelation):
    relation = "/common/topic/description"
    reverse = True


class IsPerson(FixedType):
    fixedtype = "/people/person"
    fixedtyperelation = "/type/object/type"


class BirthDateOf(FixedRelation):
    relation = "/people/person/date_of_birth"
    reverse = True


class BirthPlaceOf(FixedRelation):
    relation = "/people/person/place_of_birth"
    reverse = True


class IsMovie(FixedType):
    fixedtype = "/film/film"


class DurationOf(FixedRelation):
    relation = "/film/film_cut/runtime"
    reverse = True

class RuntimeOf(FixedRelation):
    relation = "/film/film/runtime"
    reverse = True


class IsActor(FixedType):
    fixedtype = "Actor"
    fixedtyperelation = "/people/person/profession"


class IsDirector(FixedType):
    fixedtype = "Film Director"
    fixedtyperelation = "/people/person/profession"


class HasPerformance(FixedRelation):
    relation = "/film/film/starring"


class PerformsIn(FixedRelation):
    relation = "/film/performance/actor"
    reverse = True


class IsPerformance(FixedType):
    fixedtype = "/film/performance"


class PerformanceOfActor(FixedRelation):
    relation = "/film/performance/actor"


class PerformanceOfMovie(FixedRelation):
    relation = "/film/film/starring"
    reverse = True


class DirectorOf(FixedRelation):
    relation = "/film/film/directed_by"
    reverse = True


class DirectedBy(FixedRelation):
    relation = "/film/film/directed_by"


class ReleaseDateOf(FixedRelation):
    relation = "/film/film/initial_release_date"
    reverse = True


class IsBand(FixedType):
    fixedtype = "/music/musical_group"


class IsMusicArtist(FixedType):
    fixedtype = "/music/artist"


class IsMemberOf(FixedRelation):
    relation = "/music/group_member/membership"


class GroupOf(FixedRelation):
    relation = "/music/group_membership/group"


class ActiveYearsOf(FixedRelation):
    relation = "/music/artist/active_start"
    reverse = True


class IsMusicGenre(FixedType):
    fixedtype = "/music/genre"


class MusicGenreOf(FixedRelation):
    relation = "/music/artist/genre"
    reverse = True


class IsAlbum(FixedType):
    fixedtype = "/music/album"


class ProducedBy(FixedRelation):
    relation = "/music/artist/album"
    reverse = True


class IsCountry(FixedType):
    fixedtype = "/location/country"


class IsPresident(FixedType):
    fixedtype = "President"
    fixedtyperelation = "/government/government_position_held/basic_title"


class OfficeHolderOf(FixedRelation):
    relation = "/government/government_position_held/office_holder"
    reverse = True


class PresidentOf(FixedRelation):
    relation = "/government/government_position_held/jurisdiction_of_office"


class CapitalOf(FixedRelation):
    relation = "/location/country/capital"
    reverse = True


class LanguageOf(FixedRelation):
    relation = "/location/country/official_language"
    reverse = True


class PopulationOf(FixedRelation):
    relation = "/location/statistical_region/population"
    reverse = True


class NumberOf(FixedRelation):
    relation = "/measurement_unit/dated_integer/number"
    reverse = True


class IsTvShow(FixedType):
    fixedtype = "/tv/tv_program"


class CastOf(FixedRelation):
    relation = "/tv/tv_program/regular_cast"
    reverse = True


class IsActorOf(FixedRelation):
    relation = "/tv/regular_tv_appearance/actor"
    reverse = True


class HasActor(FixedRelation):
    relation = "/tv/regular_tv_appearance/actor"


class HasCast(FixedRelation):
    relation = "/tv/tv_program/regular_cast"


class NumberOfEpisodesIn(FixedRelation):
    relation = "/tv/tv_program/number_of_episodes"
    reverse = True


class CreatorOf(FixedRelation):
    relation = "/tv/tv_program/program_creator"
    reverse = True


class IsBook(FixedType):
    fixedtype = "/book/book"


class AuthorOf(FixedRelation):
    relation = "/book/written_work/author"
    reverse = True


class HasAuthor(FixedRelation):
    relation = "/book/written_work/author"


class LocationOf(FixedRelation):
    relation = "/location/location/containedby"
    reverse = True
