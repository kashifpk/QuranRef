<%!
skip_dojo = True
def arabic_numerals(number):
    n = str(number)
    ret = ''
    for i in n:
        #ret += chr(0x06f0+int(i))
	ret += chr(int(i)+1776)
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
    %if translation: 

	%if (surah!=1 and surah!=9 and aya.aya_number==1 and translation.startswith("ur.")):
	<td class="${tr_class}">${"اللہ کے نام سے جو رحمان و رحیم ہے"}</td>
	%elif (surah!=1 and surah!=9 and aya.aya_number==1 and translation.startswith("en.")):
	<td class="${tr_class}">${"In the name of Allah, the Merciful, the Compassionate"}</td>
	%else:
	<td class="${tr_class}">${aya.get_translation(translation)}</td>
	%endif
    %endif
    
    <td class="ar-num">
      
      %if aya.arabic_text.strip().endswith("۩"):
        
        ${aya.arabic_text.strip()[:-1]}
        <span class="text-danger" style="font-size: larger; text-decoration: underline;">          السجدة </span>
       
        
      %elif (surah!=1 and surah!=9 and aya.aya_number==1):
	  ${aya.arabic_text[:38]} <!--Display bismillah -->
	  
  </tr>
	<tr>
	  %if translation:
	      <td class="${tr_class}">${aya.get_translation(translation)}</td>
	      <td class="ar-num">${aya.arabic_text.strip()[38:]}${"۝"}${arabic_numerals(aya.aya_number)}</td> <!-- Display first verse -->
	 %else:
	      <td class="ar-num">${aya.arabic_text.strip()[38:]}${"۝"}${arabic_numerals(aya.aya_number)}</td>
	  %endif
	</tr>
  <tr>
  
      %else:
       ${aya.arabic_text}${"۝"}${arabic_numerals(aya.aya_number)}
      %endif
      
  </tr>
     
%endfor
</table>
    
  
