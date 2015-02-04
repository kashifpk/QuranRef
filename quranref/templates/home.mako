<%inherit file="base.mako"/>

<%def name="title()">
Quran Reference - القرِآن
</%def>

<%def name="header()">
  ${self.main_menu()}
</%def>
  
  
<div class="row">
  <table class="table table-stripped table-bordered table-hover">
    <tr class="bg-primary">
      
      <th>Surah Name</th>
      <th>Translated Name (EN)</th>
      <th>Ayas</th>
      <th>Rukus</th>
      <th>Nuzool order / location</th>
      <th>Arabic Name</th>
    </tr>
  %for surah in surah_info:
    %if surah:
    <tr>
      <td>${surah['english_name']}</td>
      <td>${surah['translated_name']}</td>
      <td>${surah['total_ayas']}</td>
      <td>${surah['rukus']}</td>
      <td>${surah['nuzool_order']} (${surah['nuzool_location']})</td>
      <td class="ar">${surah['arabic_name']}</td>
    </tr>
    %endif
  %endfor
  </table>
</div>  
