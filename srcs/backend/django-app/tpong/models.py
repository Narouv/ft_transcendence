from django.db import models
from django.db.models import FilteredRelation, Q
from django.contrib.postgres.fields import ArrayField
from api.models import User
import logging

logger = logging.getLogger(__name__)

class PongStats(models.Model):
	user = models.ForeignKey(User, on_delete=models.PROTECT)
	playerName = models.CharField(max_length=25, default=0)
	score = models.IntegerField(default=0)
	side = models.CharField(max_length=15, default=0)

class PongMatch(models.Model):
	MODES = (
		("classic", "Classic"),
		("gravity", "Gravity"),
	)
	
	TYPES = (
		("local", "Local"),
		("pvp", "PvP"),
		("tournament", "Tournament"),
		("tournamentMatch", "TournamentMatch"),
	)

	STATUS = (
		("noinit", "Not intialized"),
		("running", "Running"),
		("finished", "Finished"),
	)
	
	created_at = models.DateTimeField(auto_now_add=True)
	type = models.CharField(max_length=25, choices=TYPES, default="local")
	mode = models.CharField(max_length=25, choices=MODES, default="classic")
	status = models.CharField(max_length=25, choices=STATUS, default="noinit")
	stats = models.ManyToManyField(PongStats)
	maxScore = models.IntegerField(default=3)

	def get_result(self):
		if self.type != "tournament":
			return {
				"left": self.getPlayerStatsBySide("left"),
				"right": self.getPlayerStatsBySide("right"),
			}
		return {"result": self.stats.all().order_by("-score")}



	def addPlayer(self, user):
		if self.stats.filter(user=user).exists():
			return
		side = 'left'
		if self.stats.count():
			side = 'right'
		if self.type == 'local':
			self.stats.create(user=user, side="right", playerName="Right")
		self.stats.create(user=user, side=side, playerName=side.title() if self.type == 'local' else user.getNick())

	def getPlayerStatsFromUser(self, user):
		try:
			result = self.stats.get(user=user)
		except PongStats.DoesNotExist:
			return False
		return result

	def getPlayerStatsBySide(self, side):
		result = self.stats.filter(side=side)
		if result:
			return result[0]
		return False

	def getWinner(self):
		stats = self.stats.filter(score=self.maxScore)
		if len(stats) == 1:
			return stats[0]
		return False

	def getActiveMatch(user):
		result = PongMatch.objects.filter(stats__user=user, status="active").distinct()
		if len(result) == 1:
			return result[0]
		return False

