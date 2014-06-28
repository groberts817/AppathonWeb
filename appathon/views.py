from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from push_notifications.models import APNSDevice, GCMDevice
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import SiteProfileNotAvailable, User

@csrf_exempt
@require_POST
@login_required
def register_device(request, device_type):
    if request.method == 'POST':
        json_data = simplejson.loads(request.body)
        if device_type == 'gcm':
            existingDevices = GCMDevice.objects.filter(registration_id=json_data['registration_id'])
            if existingDevices:
                device = existingDevices[0]
            else:
                device = GCMDevice()
        elif device_type == 'apns':
            existingDevices = APNSDevice.objects.filter(registration_id=json_data['registration_id'])
            if existingDevices:
                device = existingDevices[0]
            else:
                device = APNSDevice()
        else:
            return HttpResponseBadRequest('Invalid device type')
        device.name = request.user.username
        device.user = request.user
        device.registration_id = json_data['registration_id']
        device.save()

    return HttpResponse("OK")