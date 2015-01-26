import datetime
import itertools

from django.utils.safestring import mark_safe
from django.db.models import Count

from smartmin.views import *
from rapidsms.models import Backend
from rapidsms_httprouter.models import Message
from rapidsms_httprouter.router import get_router


class MessageTesterForm(forms.Form):
    backend = forms.CharField(max_length=20, initial='tester')
    sender = forms.CharField(max_length=20, initial="12065551212")
    text = forms.CharField(max_length=160, label="Message", widget=forms.TextInput(attrs={'size':'60'}))

class MessageCRUDL(SmartCRUDL):
    actions = ('list', 'csv', 'monthly', 'status')
    model = Message
    permissions = True

    class Csv(SmartCsvView):
        fields = ('date', 'direction', 'number', 'text')

        def get_number(self, obj):
            return obj.connection.identity

        def derive_queryset(self, **kwargs):
            # get our parent queryset
            queryset = super(MessageCRUDL.Csv, self).derive_queryset(**kwargs)

            # return our queryset
            return queryset.select_related(depth=1)

    class Status(SmartListView):
        permission = None

        def get_context_data(self, *args, **kwargs):
            context = super(MessageCRUDL.Status, self).get_context_data(*args, **kwargs)

            # get all messages that are unset for more than 30 seconds
            thirty_seconds_ago = datetime.datetime.now() - datetime.timedelta(seconds=30)
            context['unsent'] = Message.objects.filter(date__lte=thirty_seconds_ago, status='Q').count()
            context['error'] = Message.objects.filter(date__lte=thirty_seconds_ago, status='E').count()

            return context

    class Monthly(SmartListView):
        title = "Monthly Message Volume"

        def get_context_data(self, **kwargs):
            context = super(MessageCRUDL.Monthly, self).get_context_data(**kwargs)
            
            # get our queryset
            queryset = self.derive_queryset()

            backend_id = context['backend_id'] = int(self.request.REQUEST.get('backend_id', 0))
            search = context['search'] = self.request.REQUEST.get('search', '')

            if backend_id:
                queryset = queryset.filter(connection__backend__id=backend_id)

            if search:
                print 'yeah'
                queryset = queryset.filter(
                    Q(text__search=search) | Q(connection__identity__startswith=search))

            counts = queryset.filter(direction__in=('I', 'O')).order_by('direction', 'date').extra(
                {'month': "month(date)", 'year': "year(date)"}).values(
                'direction', 'month', 'year').annotate(message_count=Count('id'))

            # create iterator that returns incoming/outgoing counts per month,
            # or if one of both doesn't exist an empty fillvalue
            iter = itertools.izip_longest(
                filter(lambda x: x['direction'] == 'I', counts),
                filter(lambda x: x['direction'] == 'O', counts),
                fillvalue={'message_count': 0})

            total_counts = []
            for ic, oc in iter:
                ref = ic if 'month' in ic else oc
                total_counts.append({
                    'created': datetime.datetime(day=1, month=ref['month'], year=ref['year']),
                    'incoming': ic['message_count'],
                    'outgoing': oc['message_count'],
                    'total': ic['message_count'] + oc['message_count']
                })

            context['counts'] = total_counts
            context['backends'] = Backend.objects.all()

            return context

    class List(SmartListView, SmartFormMixin):
        title = "Message Console"

        fields = ('direction', 'number', 'text', 'date')
        default_order = '-date'
        search_fields = ('text__icontains', 'connection__identity__icontains')
        field_config = { 'direction': dict(label=" ") }

        refresh = 5000

        def derive_queryset(self, *args, **kwargs):
            queryset = super(MessageCRUDL.List, self).derive_queryset(*args, **kwargs)

            backend_id = int(self.request.REQUEST.get('backend_id', 0))
            if backend_id:
                queryset = queryset.filter(connection__backend=backend_id)

            return queryset

        def post(self, *args, **kwargs):
            # valid form, then process the message
            form = MessageTesterForm(self.request.POST)
            if form.is_valid():
                message = get_router().handle_incoming(form.cleaned_data.get('backend', 'tester'),
                                                       form.cleaned_data['sender'],
                                                       form.cleaned_data['text'])                

                # and off we go
                return HttpResponseRedirect(reverse('console.message_list') + "?backend_id=%d" % message.connection.backend.id)

            return self.get(*args, **kwargs)

        def build_daily_counts(self, objects, **filters):
            counts = objects.filter(**filters).order_by('date').extra({'created':"date(date)"}).values('created').annotate(created_on_count=Count('id'))
            
            for count in counts:
                created_str = count['created']
                if not hasattr(created_str, 'year'):
                    count['created'] = datetime.datetime.strptime(created_str, "%Y-%m-%d")

            return counts
        
        def get_context_data(self, **kwargs):
            context = super(MessageCRUDL.List, self).get_context_data(**kwargs)
            
            # get our queryset
            objects = self.derive_queryset()
            one_month = datetime.datetime.now() - datetime.timedelta(days=30)

            # break it up by date counts
            context['incoming_counts'] = self.build_daily_counts(objects, direction='I', date__gte=one_month)
            context['outgoing_counts'] = self.build_daily_counts(objects, direction='O', date__gte=one_month)

            context['backends'] = Backend.objects.all()

            context['backend_id'] = int(self.request.REQUEST.get('backend_id', 0))

            tester_backend = 'tester'
            backend_id = int(self.request.REQUEST.get('backend_id', 0))
            if backend_id:
                backend = Backend.objects.get(id=backend_id)
                if backend.name.find('tester') < 0:
                    tester_backend = "%s_tester" % backend.name
                else:
                    tester_backend = backend.name

            context['backend_id'] = int(self.request.REQUEST.get('backend_id', 0))
            context['tester_backend'] = tester_backend

            if self.request.method == 'POST':
                context['form'] = MessageTesterForm(self.request.POST)
            else:
                context['form'] = MessageTesterForm()

            return context
        
        def get_number(self, obj):
            return obj.connection.identity

        def get_direction(self, obj):
            is_test = obj.connection.backend.name.find('tester') >= 0 or obj.connection.backend.name == 'console'

            if obj.direction == 'I':
                if is_test:
                    style = 'cin'
                else:
                    style = 'in'
            else:
                if is_test:
                    style = 'cout'
                elif obj.status == 'D':
                    style = 'delivered'
                elif obj.status == 'S' or is_test:
                    style = 'sent'
                else:
                    style = 'queued'

            return mark_safe('<div class="%s"> </div>' % style)
                
