from django.contrib.auth import authenticate
from api.models import TwoFactor
import pyotp

class TwoFacAuth():
	def generate2FA(user):
		if TwoFactor.objects.filter(user=user).exists():
			obj = TwoFactor.objects.get(user=user)
			if obj.verified:
				return False
			obj.delete()
		secret = pyotp.random_base32()
		pyotp_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=user.email if user.email else "Secure account", issuer_name="42 Pong")
		tfa = TwoFactor(user=user, secret=secret)
		tfa.save()
		return pyotp_uri

	def verify2FA(user, code):
		try:
			tfa = TwoFactor.objects.get(user=user)
		except TwoFactor.DoesNotExist:
			return False
		totp = pyotp.TOTP(tfa.secret)
		status = totp.verify(code)
		if status and not tfa.verified:
			tfa.verified = True
			tfa.save()
		return status

	def disable2FA(user, password):
		try:
			tfa = TwoFactor.objects.get(user=user)
		except TwoFactor.DoesNotExist:
			return False
		tfa.delete()
		return True
		user = authenticate(username=user.username, password=password)
		if user is not None:
			tfa = TwoFactor.objects.get(user=user)
			tfa.delete()
			return True
		return False

	def reconfigure2FA(user, password):
		if TwoFacAuth.disable2FA(user, password):
			return TwoFacAuth.generate2FA(user)
		return False

	def enabledForUser(user):
		try:
			tfa = TwoFactor.objects.get(user=user)
		except TwoFactor.DoesNotExist:
			return False
		if not tfa.verified:
			return False
		return True

	def verifyRequest(user, code):
		if not TwoFacAuth.enabledForUser(user):
			return True
		return TwoFacAuth.verify2FA(user, code)