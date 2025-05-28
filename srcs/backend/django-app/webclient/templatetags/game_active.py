from django import template
from tpong.game.networking.lobby.PongLobbyManager import lobbyManagerInstance
from tpong.models import PongStats
from django.db.models import F
import logging

logger = logging.getLogger(__name__)
register = template.Library()

@register.inclusion_tag("webclient/snippets/tournament-lobby-profiles.html", takes_context=True)
def display_tournament_profiles(context):
    request = context.get("request")
    lobby = lobbyManagerInstance.getLobbyFromUser(request.user, "tournament")
    if not lobby:
        return { "success": False }
    users = []
    for connection in lobby.playerConnections:
        users.append(connection.user)
    return {
        "request": request,
        "users": users,
    }

@register.inclusion_tag("webclient/snippets/tournament-lobby-head.html", takes_context=True)
def display_tournament_lobby_head(context):
    request = context.get("request")
    lobby = lobbyManagerInstance.getLobbyFromUser(request.user, "tournament")
    if not lobby:
        return { "success": False }
    return {
        "request": request,
        "numVoted": len(lobby.votedForStart),
        "lobbySize": len(lobby.playerConnections),
        "hasVoted": request.user in lobby.votedForStart
    }

@register.inclusion_tag("webclient/snippets/tournament-midround-stats.html", takes_context=True)
def display_tournament_midround_stats(context):
    request = context.get("request")
    lobby = lobbyManagerInstance.getLobbyFromUser(request.user, "tournament")
    if not lobby:
        return { "success": False }
    users = []
    for connection in lobby.playerConnections:
        users.append(connection.user)
    return {
        "request": request,
        "lobbySize": len(lobby.playerConnections),
    }

@register.inclusion_tag("webclient/snippets/tournament-midround-ranks.html", takes_context=True)
def display_tournament_midround_ranks(context):
    request = context.get("request")
    lobby = lobbyManagerInstance.getLobbyFromUser(request.user, "tournament")
    if not lobby:
        return { "success": False }
    stats = lobby.tournament.lobbyMatch.stats.all().order_by('-score')
    if not stats:
        return { "success": False }
    winpusers = []
    for userstats in stats:
        allMatches = PongStats.objects.filter(user=userstats.user, pongmatch__status="finished").exclude(pongmatch__type='local')
        tournaments = allMatches.filter(pongmatch__type='tournament')
        tournamentsWon = allMatches.filter(score__gte=F('pongmatch__maxScore')).filter(pongmatch__type='tournament')
        if not lobby:
            return { "success": False }
        try:
            tournamentWl = int((tournamentsWon.count() / tournaments.count()) * 100)
        except:
            tournamentWl = "0"
        winpusers.append({"stats": userstats,"wr":tournamentWl})

    return {
        "request": request,
        "userstats": winpusers,
    }
