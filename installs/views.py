from datetime import datetime, timedelta
import json
import random
import string
import requests
import asyncio
from kalyke import ApnsClient, ApnsConfig, Payload, PayloadAlert
from kalyke.exceptions import BadDeviceToken
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
import config
from authapp.models import User
from installs.forms import AppEditForm, StatusPushEditForm, TimedPushEditForm
from installs.models import Install, Application, Push


@csrf_exempt
def register_install(request):
    if 'externalId' in request.POST:
        external_id = request.POST.get('externalId')

        if Install.objects.filter(external_id=external_id).exists():
            return JsonResponse({'response': 'externalId already exists', 'status_code': 400})

        payload = json.dumps({
            "columns": [],
            "metrics": ["campaign_unique_clicks", "conversions", "sales", "revenue"],
            "grouping": ["datetime", "campaign", "stream", "stream_id", "sub_id", "country_flag", "language", "ip",
                         "os", "os_version", "sub_id_1", "sub_id_2", "sub_id_3", "sub_id_4", "sub_id_5", "sub_id_6",
                         "sub_id_7", "sub_id_8", "sub_id_9", "sub_id_10", "sub_id_11", "sub_id_12", "sub_id_13",
                         "sub_id_14", "sub_id_15", "sub_id_16", "sub_id_17", "sub_id_18", "sub_id_19", "sub_id_20",
                         "sub_id_21", "sub_id_22", "sub_id_23", "sub_id_24", "sub_id_25", "sub_id_26", "sub_id_27",
                         "sub_id_28", "sub_id_29", "sub_id_30", "external_id"],
            "filters": [
                {"name": "external_id", "operator": "EQUALS", "expression": external_id}
            ],
            "sort": [{"name": "sub_id_10", "order": "desc"}],
            "limit": 1,
            "summary": True,
            "offset": 0
        })

        headers = {
            'Api-Key': config.KEITARO_API_KEY,
            'Content-Type': "application/json",
        }
        response = requests.post(url=f'{config.KEITARO_API_URL}/admin_api/v1/report/build',
                                 headers=headers,
                                 data=payload)
        response_json = response.json()

        data = response_json['rows'][0] if len(response_json['rows']) == 1 else {"external_id": external_id}
        if 'sub_id_4' in data.keys():
            if data['sub_id_4']:
                buyer_check = User.objects.filter(buyer_id=data['sub_id_4'])
                if buyer_check.exists():
                    buyer = buyer_check.first()
                else:
                    password = ''.join(random.sample(list(string.ascii_letters) +
                                                     list(map(lambda x: str(x), range(0, 10))) +
                                                     ['!', '#', '$', '%', '&', '*', '/', ':', ';', '<', '>', '?', '@', '^',
                                                      '~'], 10))
                    email = password + '@not.found'
                    buyer = User.objects.create_user(username=email, email=email, password=password)
                    buyer.first_name = 'Not found'
                    buyer.buyer_id = data['sub_id_4']
                    buyer.save()
                data['buyer'] = buyer
            del data['sub_id_4']

        if 'sub_id_10' in data.keys() and data['sub_id_10']:
            app_check = Application.objects.filter(bundle=data['sub_id_10'])
            if app_check.exists():
                data['application'] = app_check.first()
            else:
                data['application'] = Application.objects.create(name='Not found', bundle=data['sub_id_10'])

        Install.objects.create(**data)

        return JsonResponse({'response': 'ok', 'status_code': 200})
    else:
        return JsonResponse({'response': 'missing params', 'status_code': 400})


@csrf_exempt
def change_install(request):
    if 'external_id' in request.POST and 'status' in request.POST:
        external_id = request.POST.get('external_id')

        install = Install.objects.filter(external_id=external_id)

        if not Install.objects.filter(external_id=external_id).exists():
            return JsonResponse({'response': 'install doesn\'t exists', 'status_code': 400})

        status = request.POST.get('status')
        install = install.first()
        now = datetime.now().replace(second=0, microsecond=0)
        if status == 'reg':
            install.registered_at = now
        elif status == 'dep':
            install.purchased_at = now
        else:
            return JsonResponse({'response': 'incorrect status', 'status_code': 400})
        install.status = status
        install.save()

        return JsonResponse({'response': 'ok', 'status_code': 200})
    else:
        return JsonResponse({'response': 'missing params', 'status_code': 400})


@user_passes_test(lambda u: u.is_authenticated and (u.is_superuser or u.app_admin or u.buyer_id) and not u.is_deleted)
def get_installs(request):
    app_pk = int(request.POST.get('id'))
    app = Application.objects.get(pk=app_pk)
    time_from = datetime.strptime(request.POST.get('date_start'), '%Y-%m-%d')
    time_to = datetime.strptime(request.POST.get('date_stop'), '%Y-%m-%d').replace(hour=23, minute=59, second=59)
    app.get_installs(time_from, time_to)
    return JsonResponse({'result': 'ok'})


@user_passes_test(lambda u: u.is_authenticated and (u.is_superuser or u.app_admin or u.buyer_id) and not u.is_deleted)
def make_push(request):
    installs = Install.objects.filter(application__isnull=False, application__is_deleted=False,
                                      application__key_id__isnull=False, application__team_id__isnull=False,
                                      application__key__isnull=False)

    if request.user.is_superuser or request.user.app_admin:
        pass
    elif request.user.lead:
        installs = Install.objects.filter(buyer__team__pk=request.user.team.pk)
    else:
        installs = Install.objects.filter(buyer__pk=request.user.pk)

    context = {
        'title': 'Отправка пуша',
        'audience': len(installs),
        'current_time': datetime.now().time().replace(microsecond=0, second=0),
        'languages': installs.filter(language__isnull=False).order_by('language').values_list('language').distinct(),
        'country_flags': installs.filter(country_flag__isnull=False).order_by('country_flag')
        .values_list('country_flag').distinct(),
        'applications': Application.objects.filter(pk__in=installs.values_list('application__pk').distinct()),
        'offers': installs.filter(Q(sub_id_2__isnull=False), ~Q(sub_id_2='')).order_by('sub_id_2').values_list('sub_id_2').distinct(),
        'statuses': installs.filter(status__isnull=False).order_by('status').values_list('status').distinct(),
        'buyers': User.objects.filter(pk__in=installs.values_list('buyer__pk').distinct())
    }

    return render(request, 'installs/make_push.html', context=context)


@user_passes_test(lambda u: u.is_authenticated and (u.is_superuser or u.app_admin) and not u.is_deleted)
def make_test_push(request):
    context = {
        'title': 'Тестовый пуш',
        'applications': Application.objects.filter(is_deleted=False, key_id__isnull=False, team_id__isnull=False,
                                                   key__isnull=False, bundle__isnull=False)
    }
    return render(request, 'installs/make_test_push.html', context=context)


@user_passes_test(lambda u: u.is_authenticated and (u.is_superuser or u.app_admin or u.buyer_id) and not u.is_deleted)
def execute_push(request):
    print(request.POST)
    type_ = request.POST.get('type')
    languages = request.POST.getlist('languages[]')
    country_flags = request.POST.getlist('country_flags[]')
    offers = request.POST.getlist('offers[]')
    applications = request.POST.getlist('applications[]')
    buyers = request.POST.getlist('buyers[]')
    statuses = request.POST.getlist('statuses[]') if type_ != 'status' else request.POST.get('statuses')
    title = request.POST.get('title')
    text = request.POST.get('text')
    launch_image = request.FILES.get('launch_image') if 'launch_image' in request.FILES.keys() else None
    days = request.POST.getlist('days[]')
    hours = request.POST.getlist('hours[]')
    timedelta_ = request.POST.get('timedelta')

    push = Push.objects.create(user=request.user, title=title, text=text, launch_image=launch_image,
                               languages=', '.join(languages),
                               country_flags=', '.join(country_flags),
                               offers=', '.join(offers),
                               applications=', '.join(applications),
                               statuses=', '.join(statuses) if type_ != 'status' else statuses,
                               buyers=', '.join(buyers),
                               type=type_)

    if type_ == 'normal':
        push.send(data={'languages': languages, 'country_flags': country_flags, 'offers': offers,
                        'applications': applications, 'statuses': statuses, 'buyers': buyers})
    elif type_ == 'timed' and days and hours:
        push.days = '|'.join(days) + '|'
        push.hours = '|'.join(hours) + '|'
        push.save()
    elif type_ == 'status' and timedelta_ and timedelta_.isdigit() and statuses:
        push.timedelta = int(timedelta_)
        push.save()
    else:
        return JsonResponse({'result': 'not ok'})

    return JsonResponse({'result': 'ok'})


@user_passes_test(lambda u: u.is_authenticated and (u.is_superuser or u.app_admin) and not u.is_deleted)
def execute_test_push(request):
    title = request.POST.get('title')
    text = request.POST.get('text')
    external_id = request.POST.get('external_id')
    sandbox = request.POST.get('sandbox') == 'true'
    application_pk = int(request.POST.get('application'))

    application = Application.objects.get(pk=application_pk)
    client = ApnsClient(
        use_sandbox=sandbox,
        team_id=application.team_id,
        auth_key_id=application.key_id,
        auth_key_filepath=application.key.path,
    )
    payload_alert = PayloadAlert(title=title, body=text)
    payload = Payload(alert=payload_alert, badge=1, sound="default")
    config_ = ApnsConfig(topic=application.bundle)

    try:
        asyncio.run(
            client.send_message(
                device_token=external_id,
                payload=payload,
                apns_config=config_,
            )
        )

        return JsonResponse({'result': 'ok'})
    except BadDeviceToken:
        return JsonResponse({'result': 'bad token'})


@user_passes_test(lambda u: u.is_authenticated and (u.is_superuser or u.app_admin or u.buyer_id) and not u.is_deleted)
def check_push_audience(request):
    languages = request.GET.getlist('languages[]')
    country_flags = request.GET.getlist('country_flags[]')
    offers = request.GET.getlist('offers[]')
    applications = request.GET.getlist('applications[]')
    buyers = request.GET.getlist('buyers[]')
    statuses = request.GET.getlist('statuses[]')

    installs = Install.objects.filter(application__isnull=False, application__is_deleted=False,
                                      application__key_id__isnull=False, application__team_id__isnull=False,
                                      application__key__isnull=False)

    if request.user.is_superuser or request.user.app_admin:
        pass
    elif request.user.lead:
        installs = installs.filter(buyer__team__pk=request.user.team.pk)
    else:
        installs = installs.filter(buyer__pk=request.user.pk)
    if languages:
        installs = installs.filter(language__in=languages)
    if country_flags:
        installs = installs.filter(country_flag__in=country_flags)
    if offers:
        installs = installs.filter(sub_id_2__in=offers)
    if applications:
        installs = installs.filter(application__pk__in=applications)
    if statuses:
        installs = installs.filter(status__in=statuses)
    if buyers:
        installs = installs.filter(buyer__pk__in=buyers)
    return JsonResponse({'result': 'ok', 'audience': len(installs)})


class PushAccessMixin:

    @method_decorator(user_passes_test(lambda u:
                                       u.is_authenticated and (u.app_admin or u.is_superuser or u.buyer_id)
                                       and not u.is_deleted))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class AppAccessMixin:

    @method_decorator(user_passes_test(lambda u:
                                       u.is_authenticated and (u.app_admin or u.is_superuser) and not u.is_deleted))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class AppListView(AppAccessMixin, ListView):
    model = Application
    template_name = 'installs/applications.html'
    # paginate_by = 9

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Приложения'
        context['deleted'] = Application.objects.filter(is_deleted=True).order_by('name')
        context['today'] = datetime.now().date()
        context['yesterday'] = context['today'] - timedelta(days=1)
        return context

    def get_queryset(self):
        return Application.objects.filter(is_deleted=False).order_by('name')


class AppCreateView(AppAccessMixin, CreateView):
    model = Application
    template_name = 'installs/edit_application.html'
    success_url = reverse_lazy('installs:applications')
    form_class = AppEditForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление приложения'

        return context


class AppEditView(AppAccessMixin, UpdateView):
    model = Application
    template_name = 'installs/edit_application.html'
    success_url = reverse_lazy('installs:applications')
    form_class = AppEditForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование приложения'

        return context


class AppDeleteView(AppAccessMixin, DeleteView):
    model = Application
    template_name = 'installs/delete_application.html'
    success_url = reverse_lazy('installs:applications')
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Удаление приложения'

        return context


class PushListView(PushAccessMixin, ListView):
    model = Push
    template_name = 'installs/pushes.html'
    # paginate_by = 9

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Пуши'
        return context

    def get_queryset(self):
        pushes = Push.objects.filter(type__in=['status', 'timed'])
        if self.request.user.is_superuser or self.request.user.app_admin:
            pass
        elif self.request.user.lead:
            pushes = pushes.filter(user__team__pk=self.request.user.team.pk)
        else:
            pushes = pushes.filter(user__pk=self.request.user.pk)
        return pushes.order_by('pk')


class PushEditView(PushAccessMixin, UpdateView):
    model = Push
    template_name = 'installs/edit_push.html'
    success_url = reverse_lazy('installs:pushes')

    def get_form_class(self):
        return StatusPushEditForm if self.get_object().type == 'status' else TimedPushEditForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование пуша'
        context['current_time'] = datetime.now().time().replace(microsecond=0, second=0)

        return context

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(PushEditView, self).get_form_kwargs()
        kwargs['user_id'] = self.get_object().user.pk
        return kwargs


class PushDeleteView(PushAccessMixin, DeleteView):
    model = Push
    template_name = 'installs/delete_push.html'
    success_url = reverse_lazy('installs:pushes')
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Удаление пуша'

        return context
