from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.core.serializers import serialize
import json
from time import sleep
from datetime import datetime

from notification.utils import LazyNotificationEncoder
from notification.models import Notification

DEFAULT_NOTIFICATION_PAGE_SIZE = 15


def refresh_notifications(request, *args, **kwargs):
	"""
	Used to refresh the currently visible notifications and append any new ones.
	"""
	payload = {}

	user = request.user
	if user.is_authenticated:
		# FORMAT: 2020-08-27 19:39:13.011835+00:00
		timestamp = request.GET.get("oldest_timestamp")
		timestamp = timestamp[0:timestamp.find("+")] # remove timezone because who cares
		timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
		notifications = Notification.objects.filter(target=user, timestamp__gte=timestamp).order_by('-timestamp')

		s = LazyNotificationEncoder()
		payload['notifications'] = s.serialize(notifications)
	else:
		payload['notifications'] = None
	return HttpResponse(json.dumps(payload), content_type="application/json")


def get_notifications(request, *args, **kwargs):
	"""
	Get Notifications with Pagination (next page of results).
	This is for appending to the bottom of the notifications list.
	"""
	payload = {}

	user = request.user
	if user.is_authenticated:
		notifications = Notification.objects.filter(target=user).order_by('-timestamp')
		page_number = request.GET.get("page_number")
		p = Paginator(notifications, DEFAULT_NOTIFICATION_PAGE_SIZE)

		# sleep 1s for testing
		# sleep(1)	

		if len(notifications) > 0:
			new_page_number = int(page_number)
			print("new page number: " + str(new_page_number))
			print("num pages: " + str(p.num_pages))
			if new_page_number <= p.num_pages:
				new_page_number = new_page_number + 1
				s = LazyNotificationEncoder()
				payload['notifications'] = s.serialize(p.page(page_number).object_list)
			else:
				payload['notifications'] = None
			payload['page_number'] = new_page_number
		else:
			payload['notifications'] = None
	else:
		payload['notifications'] = None


	return HttpResponse(json.dumps(payload), content_type="application/json")
