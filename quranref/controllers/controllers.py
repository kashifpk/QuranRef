from pyramid.view import view_config

@view_config(route_name='home', renderer='home.mako')
def homepage(request):
    return {}
