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
      
      <th>SNo.</th>
      <th>Surah Name</th>
      <th>Translated Name (EN)</th>
      <th>Ayas</th>
      <th>Rukus</th>
      <th>Nuzool order / location</th>
      <th>Arabic Name</th>
    </tr>
  %for idx, surah in enumerate(surah_info):
    %if surah:
    <%
    aya_str = "1," + str(surah['total_ayas'])
    %>
    <tr>
      <td>
        <%
        base_link = request.route_url('qref', surah=idx,aya=aya_str)
        %>
        
        <a href="${base_link}">${idx}</a>
        <br />
        %for tr in translations:
          <a href="${base_link}?tr=${tr}"><span class="label label-success" style="font-size: smaller;">${tr.upper()}</span></a>
        %endfor
      
      </td>
      <td>
        <%
        base_link = request.route_url('qref', surah=surah['english_name'],aya=aya_str)
        %>
        
        <a href="${base_link}">${surah['english_name']}</a>
        <br />
        %for tr in translations:
          <a href="${base_link}?tr=${tr}"><span class="label label-success" style="font-size: smaller;">${tr.upper()}</span></a>
        %endfor
        
      </td>
      <td>${surah['translated_name']}</td>
      <td>${surah['total_ayas']}</td>
      <td>${surah['rukus']}</td>
      <td>${surah['nuzool_order']} (${surah['nuzool_location']})</td>
      <td class="ar">
        <%
        base_link = request.route_url('qref', surah=surah['arabic_name'],aya=aya_str)
        %>
        
        <a href="${base_link}">${surah['arabic_name']}</a>
        <br />
        %for tr in translations:
          <a href="${base_link}?tr=${tr}"><span class="label label-success" style="font-size: smaller;">${tr.upper()}</span></a>
        %endfor
        
      </td>
    </tr>
    %endif
  %endfor
  </table>
</div>  
