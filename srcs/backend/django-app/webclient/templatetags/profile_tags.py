from django import template
from django.db.models import F
from tpong.models import PongMatch, PongStats
from api.models import User
from datetime import datetime, timezone, timedelta
from django.core.paginator import Paginator
from api.TwoFacAuth import TwoFacAuth
import logging

logger = logging.getLogger(__name__)
register = template.Library()

@register.inclusion_tag("webclient/snippets/match-history.html", takes_context=True)
def display_match_history(context):
    request = context.get("request")
    try:
        args = request.data.get("args")
        page = args.get("matchHistoryPage")
    except:
        page = 1
    matches = PongMatch.objects.filter(stats__user=request.user, status="finished").exclude(type="tournamentMatch").distinct().order_by('-created_at')
    paginator = Paginator(matches, 10)
    return {
        "request": request,
        "matches": paginator.get_page(page),
    }

@register.inclusion_tag("webclient/snippets/player-stats.html", takes_context=True)
def display_player_stats(context):
    request = context.get("request")
    allMatches = PongStats.objects.filter(
        user=request.user,
        pongmatch__status="finished"
    ).exclude(pongmatch__type='local')
    tournaments = allMatches.filter(pongmatch__type='tournament')
    gamesWon = allMatches.filter(score__gte=F('pongmatch__maxScore'))
    tournamentsWon = gamesWon.filter(pongmatch__type='tournament')

    gamesPlayedNum = allMatches.count()
    gamesWonNum = gamesWon.count()
    tournamentsPlayedNum = tournaments.count()
    tournamentsWonNum = tournamentsWon.count()
    try:
        matchWl = int(round(gamesWonNum/ gamesPlayedNum , 2) * 100)
    except:
        matchWl = "0"
    try:
        tournamentWl = int(round(tournamentsWonNum / tournamentsPlayedNum, 2) * 100)
    except:
        tournamentWl = "0"
    return {
        "request": request,
        "playerStats": [
            {
                "tag": "Total Matches Played:",
                "value": gamesPlayedNum
            },
            {
                "tag": "Matches Won:",
                "value": gamesWonNum
            },
            {
                "tag": "Matches Lost:",
                "value": gamesPlayedNum - gamesWonNum
            },
            {
                "tag": "Match Winrate:",
                "value": f"{matchWl}%"
            },
            {
                "tag": "Tournaments Played:",
                "value": tournamentsPlayedNum
            },
             {
                "tag": "Tournaments Won:",
                "value": tournamentsWonNum
            },
            {
                "tag": "Tournament Winrate:",
                "value": f"{tournamentWl}%"
            },
        ]
    }


@register.inclusion_tag("webclient/snippets/profile-info.html", takes_context=True)
def display_player_profile(context):
    userInfo = []
    request = context.get("request")
    try:
        args = request.data.get("args")
        userId = args["profileUserId"]
        user = User.objects.get(pk=userId)
        public= True
    except:
        user = request.user
        public=False
    twoFA = TwoFacAuth.enabledForUser(user)
    userInfo.append({
            "tag": "Username",
            "value": user.username,
        })
    userInfo.append({
            "tag": "Player Name",
            "value": user.nickname,
        })
    if not public:
        userInfo.append({
                "tag": "Email",
                "value": user.email,
            })
    userInfo.append({
            "tag": "Date Joined",
            "value": format_date_time(user.date_joined),
        })
    if not public:
        userInfo.append({
                "tag": "2FA ",
                "value": "Enabled" if twoFA else "Disabled"
            })
    return {
        "request": request,
        "userInfo": userInfo
    }

@register.inclusion_tag("webclient/snippets/profile-settings.html", takes_context=True)
def display_profile_settings(context):
    request = context.get("request")
    twoFA = TwoFacAuth.enabledForUser(request.user)
    return {
        "request": request,
        "twoFA": twoFA
    }


@register.filter
def format_date_time(value):
    now = datetime.now(timezone.utc)
    diff = now - value
    if diff < timedelta(seconds=90):
        return f"a moment ago"
    elif diff < timedelta(hours=1):
        return f"{diff.seconds // 60} min ago"
    elif diff < timedelta(days=1):
        return f"{diff.seconds // 3600} h ago"
    else:
        return value.strftime('%d/%m/%y')
    
@register.filter 
def times(number, maxNum = 0):
    if maxNum:
        return range(min(int(number), int(maxNum)))
    return range(number)
