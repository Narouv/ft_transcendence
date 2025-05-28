from tpong.game.engine.PongGameHost import PongGameEngine
from tpong.game.engine.Vec2 import Vec2
from asgiref.sync import async_to_sync,sync_to_async
from tpong.models import PongMatch
from tpong.serializers import StatsSerializer
from datetime import datetime, timedelta
import logging
import random

logger = logging.getLogger(__name__)

class EventQueue():
    def __init__(self) -> None:
        self.events = []

    def add(self, delta: timedelta, callback, *args, **kwargs):
        self.events.append({
            "time": datetime.now() + delta,
            "callback": (callback, args, kwargs)
        })

    def process(self):
        toRemove = []
        for event in self.events:
            if event["time"] > datetime.now():
                continue
            toRemove.append(event)
        for event in toRemove:
            callback, args, kwargs = event["callback"]
            callback(*args, **kwargs)
            self.events.remove(event)


class PongGame(PongGameEngine):
    def __init__(self, lobby, currentMatch) -> None:
        super().__init__(lobby)
        self.gameState = "waiting"
        self.mapBorder.collisionCallback = self.onBorderCollision
        self.paddles["left"].collisionCallback = self.onPaddleCollision
        self.paddles["right"].collisionCallback = self.onPaddleCollision
        self.currentMatch = currentMatch
        self.eventQueue = EventQueue()

    def increaseScore(self, side):
        if not self.currentMatch:
            return
        playerStats = self.currentMatch.getPlayerStatsBySide(side)
        if not playerStats:
            logger.warning(f"Cant get player stats for side {side}")
            return
        playerStats.score += 1
        playerStats.save()
        self.broadcastEvent({
            "event": "score-change",
            "score": StatsSerializer(self.currentMatch.stats.all(), many=True).data
            })
        if self.currentMatch.maxScore is playerStats.score:
            self.onGameOver(playerStats)
            return
        self.endRound(playerStats)
    
    def endRound(self, winner):
        self.gameState = "prep_next_round"
        self.resetOjects()
        self.broadcastEvent({
            "event": "start-round",
            "delay": 3
            })
        self.eventQueue.add(timedelta(seconds=4), self.startRound, winner)

    def startRound(self, lastWinner):
        ballVelocity = Vec2(0.3,0)#Vec2(random.randrange(25,30) / 100, random.randrange(5, 25) / 100)
        #ballVelocity.rotate(45)
        ballVelocity.rotate(random.randrange(-45, 45))
        if lastWinner is not None:
            ballVelocity.x *=  (-1 if lastWinner.side == "right" else 1)
        elif random.randrange(0,2):
            ballVelocity.x *= -1
        self.pongBall.velocity = ballVelocity
        self.gameState = "running"

    def onBorderCollision(self, collision):
        if collision["side"].y and not collision["side"].x:
            return
        self.increaseScore("right" if collision["side"].x < 0 else "left")

    def onPaddleCollision(self, collision, side):
        if collision["side"].y:
            self.increaseScore("right" if side == "left" else "left")

    def onGameOver(self, winner):
        self.gameState = "gameover"
        self.currentMatch.status = "finished"
        self.currentMatch.save()
        self.resetOjects()
        self.broadcastEvent({ "event": "game-end" })
        self.owningLobby.onGameStateChange(self, self.gameState)

    def triggerStateChangeEvent(self):
        stateChanged = False
        for paddle in self.paddles.values():
            if paddle.stateChanged:
                stateChanged = True
                paddle.stateChanged = False
        if stateChanged:
            logger.warning("State changed")
            async_to_sync(self.syncClients())

    def gameTick(self, delta):
        self.eventQueue.process()
        if self.gameState == "running":
            #logger.warning(f"FPS: { 1.0 / delta}")
            self.simulate(delta)
            #self.triggerStateChangeEvent()

    def startGame(self):
        if not self.currentMatch:
            return False
        self.resetOjects()
        self.broadcastEvent({
            "event": "start-round",
            "delay": 4
            })
        self.currentMatch.status = "running"
        self.currentMatch.save()
        self.eventQueue.add(timedelta(seconds=5), self.startRound, None)
        return True

