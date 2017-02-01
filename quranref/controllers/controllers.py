from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from ..models import db, Aya, Translation
from ..forms import ContactForm
from ..lib.surah_info import surah_info
from ..lib import get_surah_number_by_name, translation_aliases


@view_config(route_name='home', renderer='home.mako')
def homepage(request):
    return {'surah_info': surah_info, 'translations': translation_aliases.keys()}


@view_config(route_name='qref', renderer='qref.mako')
@view_config(route_name='qref_trans', renderer='qref.mako')
def qref(request):
    
    aya_num_start = None
    aya_num_end = None
    surah_num = None
    
    surah = request.matchdict['surah']
    if surah.isdigit():
        surah_num = int(surah)
    else:
        surah_num = get_surah_number_by_name(surah)
    
    
    translation = request.matchdict.get('translation', None)
    if translation in translation_aliases:
        translation = translation_aliases[translation]
    
    if ',' in request.matchdict['aya']:
        aya_num_start, aya_num_end = request.matchdict['aya'].split(',')
    
    else:
        aya_num_start = int(request.matchdict['aya'])
        aya_num_end = aya_num_start
	
    s_info = surah_info[surah_num]
    
    ayas = db.query(Aya).filter_by(surah=surah_num).filter(Aya.aya_number.between(aya_num_start, aya_num_end)).order_by(Aya.aya_number) 
    
        
    return dict(surah_info=s_info, ayas=ayas, translation=translation, surah=surah_num)
  
@view_config(route_name='contact', renderer="contact.mako")
def contact_form(request):

    f = ContactForm(request.POST)   # empty form initializes if not a POST request

    if 'POST' == request.method and 'form.submitted' in request.params:
        if f.validate():
            #TODO: Do email sending here.

            request.session.flash("Your message has been sent!")
            return HTTPFound(location=request.route_url('home'))

    return {'contact_form': f}
