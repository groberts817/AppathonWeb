from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from push_notifications.models import APNSDevice, GCMDevice

@csrf_exempt
@require_POST
def register_device(request, device_type):
    if request.method == 'POST':
        json_data = simplejson.loads(request.body)
        if device_type == 'gcm':
            device = GCMDevice()
        elif device_type == 'apns':
            device = APNSDevice()
        else:
            return HttpResponseBadRequest('Invalid device type')
        device.name = "test"
        device.registration_id = "abcd"
        device.save()
        print 'Raw Data: "%s"' % json_data['test']

    return HttpResponse("OK")