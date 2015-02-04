<%!
skip_dojo = True

def arabic_numerals(number):
    n = str(number)
    ret = ''
    for i in n:
        ret += chr(0x06f0+int(i))
    
    return ret

%>

<%inherit file="base.mako"/>

<%def name="title()">
Quran Reference - ${surah_info['arabic_name']} - ${surah_info['english_name']} - ${surah_info['translated_name']} -
Aya ${request.matchdict['aya'].replace(',', '-')}
</%def>

<%def name="header()"> 
</%def>

<%def name="footer()"></%def>
<%def name="body_class()"></%def>

<%def name="extra_head()">
</%def>


<% tr_class = "" %>
%if translation and translation.startswith("ur."):
   <% tr_class = "ur" %>
%endif

<table class="table">
%for aya in ayas:
  <tr>
    
    <!--<td>(${aya.aya_number})</td>-->
    %if translation:
    
    <td class="${tr_class}">${aya.get_translation(translation)}</td>
    %endif
    <td class="ar">${aya.arabic_text}</td>
    <td class="num">(${arabic_numerals(aya.aya_number)})</td>
  </tr>
  
%endfor
</table>