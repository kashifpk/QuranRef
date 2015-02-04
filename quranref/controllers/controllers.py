from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from ..models import db, Aya, Translation

from ..forms import ContactForm


@view_config(route_name='home', renderer='home.mako')
def homepage(request):
    return {'project': 'quranref'}


@view_config(route_name='qref', renderer='qref.mako')
def qref(request):
    
    aliases = {
        'ur': 'ur.maududi',
        'en': 'en.maududi',
    }
    
    aya_num_start = None
    aya_num_end = None
    
    surah_num = int(request.matchdict['surah'])
    translation = request.GET.get('tr', None)
    if translation in aliases:
        translation = aliases[translation]
    
    if ',' in request.matchdict['aya']:
        aya_num_start, aya_num_end = request.matchdict['aya'].split(',')
    
    else:
        aya_num_start = int(request.matchdict['aya'])
        aya_num_end = aya_num_start
        
    ayas = db.query(Aya).filter_by(
        surah=surah_num).filter(Aya.aya_number.between(aya_num_start, aya_num_end))
    
    
    return dict(ayas=ayas, translation=translation)


@view_config(route_name='contact', renderer="contact.mako")
def contact_form(request):

    f = ContactForm(request.POST)   # empty form initializes if not a POST request

    if 'POST' == request.method and 'form.submitted' in request.params:
        if f.validate():
            #TODO: Do email sending here.

            request.session.flash("Your message has been sent!")
            return HTTPFound(location=request.route_url('home'))

    return {'contact_form': f}
