import jwt

from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, F
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from core.utils import save_encoded_link
from core.models import Link, LinkTracking
from core.forms import GetTokenForm, CreateLinkForm, AnalyticForm
from service.settings import JWT_SECRET, JWT_ALGORITHM, JWT_EXP_DELTA_SECONDS


def get_token(request):
    token_form = GetTokenForm(request.POST)

    if not token_form.is_valid():
        return JsonResponse({'message': token_form.errors}, status=400)

    try:
        user = User.objects.get(email=token_form.data['email'])
        assert user.check_password(token_form.data['password'])
    except (ObjectDoesNotExist, AssertionError):
        return JsonResponse({'message': 'Wrong user credentials'}, status=400)

    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)}

    jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)

    return JsonResponse({'token': jwt_token.decode('utf-8')})


@login_required()
def set_link(request):
    link_form = CreateLinkForm(request.POST)

    if not link_form.is_valid():
        return JsonResponse({'message': link_form.errors}, status=400)

    link = Link.objects.filter(long_link=link_form.data['link'])

    if link.exists():
        return JsonResponse({'message': 'Shortcut for provided link already exists'}, status=409)

    saved_link = save_encoded_link(link_form.data['link'], request.user)

    return JsonResponse({'generated_link': saved_link}, status=200)


@login_required
def redirect_link(request, short_url):
    original_link = get_object_or_404(Link, short_link=short_url, deleted_at__isnull=True)

    if request.method == 'DELETE':
        if original_link.owner == request.user:
            original_link.delete()
            return JsonResponse({'message': 'Link was successfully deleted '}, status=204)
        else:
            return HttpResponse('Access denied', status=403)

    LinkTracking.objects.create(user=request.user, link=original_link)
    return redirect(original_link.long_link)


@login_required
def get_analytic(request):
    analytic_form = AnalyticForm(request.POST)

    if not analytic_form.is_valid():
        return JsonResponse({'message': analytic_form.errors}, status=400)

    qs = LinkTracking.objects.filter(date__range=[analytic_form.data['date_from'], analytic_form.data['date_to']]) \
                             .select_related('link') \
                             .values('link__short_link', 'link__long_link')\
                             .annotate(visits=Count('link'))

    if analytic_form.data['order_by']:
        order_field = 'visits'

        if analytic_form.data['order_by'] == 'DESC':
            order_field = '-' + order_field

        qs = qs.order_by(order_field)

    return JsonResponse(list(qs), safe=False)


@login_required
def get_top_analytic(request):
    if not request.user.is_superuser:
        return HttpResponse('Access denied', status=403)

    analytic_form = AnalyticForm(request.POST)

    if not analytic_form.is_valid():
        return JsonResponse({'message': analytic_form.errors}, status=400)

    qs = LinkTracking.objects.filter(date__range=[analytic_form.data['date_from'], analytic_form.data['date_to']])

    qs_redirects = qs.values(username=F('user__username'))\
                     .annotate(redirects=Count('user')) \
                     .order_by('-redirects')

    for item in qs_redirects:
        most_visited_links = qs_redirects.filter(user__username=item['username']) \
                                         .values(short_link=F('link__short_link')) \
                                         .annotate(visits=Count('short_link')) \
                                         .order_by('-visits') \
                                         .values('short_link', 'visits')[:5]

        item['links'] = list(most_visited_links)

    return JsonResponse(list(qs_redirects), safe=False)
