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
Quran Reference - 
</%def>

<%def name="header()"> 
</%def>

<%def name="footer()"></%def>
<%def name="body_class()"></%def>

<%def name="extra_head()">
<style>
body {
  font-family: 'MeQuran';
}
</style>
</%def>

<table>
%for aya in ayas:
  <tr>
    <td> (${arabic_numerals(aya.aya_number)}) (${aya.aya_number}) &nbsp; ${aya.arabic_text} </td>
  </tr>
  
%endfor
</table>