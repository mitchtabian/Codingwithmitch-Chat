from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.core.serializers import serialize
import json
from time import sleep

from notification.utils import LazyNotificationEncoder
from notification.models import Notification

DEFAULT_NOTIFICATION_PAGE_SIZE = 20


def get_notifications(request, *args, **kwargs):

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
