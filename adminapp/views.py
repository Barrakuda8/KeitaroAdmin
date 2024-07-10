import random
import string
from datetime import datetime, timedelta
from pprint import pprint

import pytz
import requests
from django.contrib.auth.decorators import user_passes_test
from django.core import serializers
from django.core.management import call_command
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

import config
from adminapp.forms import AccountEditForm, CabinetEditForm
from adminapp.models import Cost, Revenue, Account, Cabinet, Update, Campaign, AdSet, Ad, Action
from authapp.forms import TeamEditForm, UserEditForm, UserCreateForm, SupportCreateForm, SupportEditForm
from authapp.models import User, Team


@user_passes_test(lambda u: not u.support_id)
def stats(request):

    costs = Cost.objects.filter(date=datetime.today())
    revenues = Revenue.objects.filter(datetime__contains=datetime.today().date())
    buyers = []

    if request.user.is_superuser:
        buyers = User.objects.filter(buyer_id__isnull=False)
    elif request.user.lead:
        team = request.user.team.pk
        costs = costs.filter(ad__adset__campaign__cabinet__account__buyer__team__pk=team)
        revenues = revenues.filter(buyer__team__pk=team)
        buyers = User.objects.filter(team__pk=team)
    else:
        costs = costs.filter(ad__adset__campaign__cabinet__account__buyer__pk=request.user.pk)
        revenues = revenues.filter(buyer__pk=request.user.pk)

    context = {
        'title': 'Статистика',
        'costs': serializers.serialize("json", costs, use_natural_foreign_keys=True),
        'revenues': serializers.serialize("json", revenues, use_natural_foreign_keys=True),
        'buyers': buyers,
        'today': datetime.today().strftime("%Y-%m-%d"),
        'yesterday': (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d"),
        'last_update_revenues': Update.objects.filter(type='revenues').order_by('datetime').last(),
        'last_update_costs': Update.objects.filter(type='costs').order_by('datetime').last(),
    }

    return render(request, 'adminapp/stats.html', context=context)


@user_passes_test(lambda u: not u.support_id)
def filter_by_date(request):
    start = request.GET.get('start_date')
    end = request.GET.get('end_date')

    costs = Cost.objects.filter(date__gte=start, date__lte=end)
    revenues = Revenue.objects.filter(datetime__gte=(datetime.strptime(start + ' 00:00:00', '%Y-%m-%d %H:%M:%S')),
                                      datetime__lte=(datetime.strptime(end + ' 23:59:59', '%Y-%m-%d %H:%M:%S')))

    if request.user.is_superuser:
        pass
    elif request.user.lead:
        team = request.user.team.pk
        costs = costs.filter(ad__adset__campaign__cabinet__account__buyer__team__pk=team)
        revenues = revenues.filter(buyer__team__pk=team)
    else:
        costs = costs.filter(ad__adset__campaign__cabinet__account__buyer__pk=request.user.pk)
        revenues = revenues.filter(buyer__pk=request.user.pk)

    costs = serializers.serialize("json", costs, use_natural_foreign_keys=True)
    revenues = serializers.serialize("json", revenues, use_natural_foreign_keys=True)

    return JsonResponse({"costs": costs, "revenues": revenues})


@user_passes_test(lambda u: u.is_superuser)
def change_password(request):
    password = ''.join(random.sample(list(string.ascii_letters) +
                                     list(map(lambda x: str(x), range(0, 10))) +
                                     ['!', '#', '$', '%', '&', '*', '/', ':', ';', '<', '>', '?', '@', '^', '~'], 10))

    user_id = request.POST.get('user_id')
    user = User.objects.get(pk=int(user_id))
    user.set_password(password)
    user.save()

    return JsonResponse({'result': password})


@user_passes_test(lambda u: u.is_superuser)
def get_costs(request):
    call_command('get_costs')
    costs = Cost.objects.filter(date=datetime.today())
    return JsonResponse({'result': 'ok',
                         'costs': serializers.serialize("json", costs, use_natural_foreign_keys=True),
                         'update': Update.objects.filter(type='costs').order_by('datetime').last().datetime})


@user_passes_test(lambda u: u.is_superuser)
def get_revenues(request):
    call_command('get_revenues')
    revenues = Revenue.objects.filter(datetime__contains=datetime.today().date())
    return JsonResponse({'result': 'ok',
                         'revenues': serializers.serialize("json", revenues, use_natural_foreign_keys=True),
                         'update': Update.objects.filter(type='revenues').order_by('datetime').last().datetime})


@user_passes_test(lambda u: u.is_superuser)
def get_cabinet_costs(request):
    cabinet_pk = int(request.POST.get('cabinet'))
    cabinet = Cabinet.objects.get(pk=cabinet_pk)
    date = datetime.now(pytz.timezone(cabinet.timezone)).date()
    cabinet.update_costs(date_start=date, date_stop=date)

    return JsonResponse({'result': 'ok'})


class HeadAccessMixin:

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    

class SupportAccessMixin:

    @method_decorator(user_passes_test(lambda u: u.is_superuser or u.support_id))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class AccessMixin:

    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class UserCreateView(HeadAccessMixin, CreateView):
    model = User
    template_name = 'adminapp/edit_user.html'
    success_url = reverse_lazy('adminapp:teams')
    form_class = UserCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление баера'

        return context


class UserEditView(HeadAccessMixin, UpdateView):
    model = User
    template_name = 'adminapp/edit_user.html'
    success_url = reverse_lazy('adminapp:teams')
    form_class = UserEditForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование баера'

        return context


class UserDeleteView(HeadAccessMixin, DeleteView):
    model = User
    template_name = 'adminapp/delete_user.html'
    success_url = reverse_lazy('adminapp:teams')
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Удаление пользователя'

        return context
    

class SupportCreateView(HeadAccessMixin, CreateView):
    model = User
    template_name = 'adminapp/edit_support.html'
    success_url = reverse_lazy('adminapp:teams')
    form_class = SupportCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление саппорта'

        return context


class SupportEditView(HeadAccessMixin, UpdateView):
    model = User
    template_name = 'adminapp/edit_support.html'
    success_url = reverse_lazy('adminapp:teams')
    form_class = SupportEditForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование саппорта'

        return context


class TeamListView(SupportAccessMixin, ListView):
    model = Team
    template_name = 'adminapp/teams.html'
    # paginate_by = 9

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Баеры'
        context['teamless'] = User.objects.filter(team__isnull=True, buyer_id__isnull=False, support_id__isnull=True)
        context['supports'] = User.objects.filter(support_id__isnull=False)

        return context

    def get_queryset(self):
        return Team.objects.all().order_by('name')


class TeamCreateView(HeadAccessMixin, CreateView):
    model = Team
    template_name = 'adminapp/edit_team.html'
    success_url = reverse_lazy('adminapp:teams')
    form_class = TeamEditForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание команды'

        return context


class TeamEditView(HeadAccessMixin, UpdateView):
    model = Team
    template_name = 'adminapp/edit_team.html'
    success_url = reverse_lazy('adminapp:teams')
    form_class = TeamEditForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование команды'

        return context


class TeamDeleteView(HeadAccessMixin, DeleteView):
    model = Team
    template_name = 'adminapp/delete_team.html'
    success_url = reverse_lazy('adminapp:teams')
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Удаление команды'

        return context


class AccountListView(AccessMixin, ListView):
    model = Account
    template_name = 'adminapp/accounts.html'
    # paginate_by = 9

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Аккаунты'

        return context

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.support_id:
            accounts = Account.objects.all()
        elif self.request.user.lead:
            accounts = Account.objects.filter(buyer__team__pk=self.request.user.team.pk)
        else:
            accounts = Account.objects.filter(buyer__pk=self.request.user.pk)
        return accounts.order_by('buyer__id').order_by('pk')


class AccountCreateView(AccessMixin, CreateView):
    model = Account
    template_name = 'adminapp/edit_account.html'
    success_url = reverse_lazy('adminapp:accounts')
    form_class = AccountEditForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление аккаунта'

        return context

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(AccountCreateView, self).get_form_kwargs()
        kwargs['user_id'] = self.request.user.pk
        return kwargs


class AccountEditView(AccessMixin, UpdateView):
    model = Account
    template_name = 'adminapp/edit_account.html'
    success_url = reverse_lazy('adminapp:accounts')
    form_class = AccountEditForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование аккаунта'

        return context

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(AccountEditView, self).get_form_kwargs()
        kwargs['user_id'] = self.request.user.pk
        return kwargs


class AccountDeleteView(AccessMixin, DeleteView):
    model = Account
    template_name = 'adminapp/delete_account.html'
    success_url = reverse_lazy('adminapp:accounts')
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Удаление аккаунта'

        return context


class CabinetCreateView(AccessMixin, CreateView):
    model = Cabinet
    template_name = 'adminapp/edit_cabinet.html'
    success_url = reverse_lazy('adminapp:accounts')
    form_class = CabinetEditForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление кабинета'

        return context

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(CabinetCreateView, self).get_form_kwargs()
        kwargs['user_id'] = self.request.user.pk
        return kwargs


class CabinetEditView(AccessMixin, UpdateView):
    model = Cabinet
    template_name = 'adminapp/edit_cabinet.html'
    success_url = reverse_lazy('adminapp:accounts')
    form_class = CabinetEditForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование кабинета'

        return context

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(CabinetEditView, self).get_form_kwargs()
        kwargs['user_id'] = self.request.user.pk
        return kwargs


class CabinetDeleteView(AccessMixin, DeleteView):
    model = Cabinet
    template_name = 'adminapp/delete_cabinet.html'
    success_url = reverse_lazy('adminapp:accounts')
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Удаление кабинета'

        return context

