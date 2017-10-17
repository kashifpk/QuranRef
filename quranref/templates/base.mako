<%!
# from quranref.auth import is_allowed

skip_dojo = False

auth_links = [('home', 'Home'), ('contact', 'Contact Us'),
              ('admin.admin_index', 'Admin Section'), ('pyckauth_manager', 'Auth Manager')]

%>

<!DOCTYPE html>
<html>
<head>
  
  <title>${self.title()}</title>
  ${self.meta()}
  
  <meta name="viewport" content="width=device-width, user-scalable=no">
  <link rel="icon" href="${request.route_url('favicon')}" />
  <link rel="shortcut icon" href="${request.route_url('favicon')}" />

  <!-- Bootstrap -->
  
  <link rel="stylesheet" href="${request.static_url('quranref:static/bootstrap/css/bootstrap.min.css')}">
  <link rel="stylesheet" href="${request.static_url('quranref:static/bootstrap/css/bootstrap-theme.min.css')}">
  <script src="${request.static_url('quranref:static/jquery.min.js')}"></script>
  <script src="${request.static_url('quranref:static/bootstrap/js/bootstrap.min.js')}"></script>
  
  <!-- Custom CSS -->
  <link rel="stylesheet" href="${request.static_url('quranref:static/pyck.css')}" type="text/css" media="screen" charset="utf-8" />
  <link rel="stylesheet" href="${request.static_url('quranref:static/quranref.css')}" type="text/css" media="screen" charset="utf-8" />
  
  
  <!-- Dojo -->
  %if not self.attr.skip_dojo:
  <link rel="stylesheet" href="http://ajax.googleapis.com/ajax/libs/dojo/1.10.1/dojo/resources/dojo.css" type="text/css" charset="utf-8" />
  <link rel="stylesheet" href="http://ajax.googleapis.com/ajax/libs/dojo/1.10.1/dijit/themes/claro/claro.css" type="text/css" charset="utf-8" />
  <script src="//ajax.googleapis.com/ajax/libs/dojo/1.10.1/dojo/dojo.js" data-dojo-config="isDebug: true, async: true"></script>
  <script type="text/javascript">
        require(['dojo/parser', 'dojo/domReady'],function(parser,ready){ready(function(){
          parser.parse();
          });});
  </script>
  %endif
  
  ${self.extra_head()}
</head>

<%def name="extra_head()">
</%def>

<body class="${self.body_class()}" ${self.body_attrs()}>
   <div class="container">
	
	${self.header()}
	
    ${self.content_wrapper()}
	
	${self.footer()}
  </div>
</body>
</html>

<%def name="title()">The PyCK Web Application Development Framework</%def>

<%def name="meta()">
  <meta http-equiv="Content-Type" content="text/html;charset=UTF-8"/>
  <meta name="keywords" content="python web application" />
  <meta name="description" content="PyCK web application" />
</%def>

<%def name="body_class()">
claro
</%def>

<%def name="body_attrs()">
</%def>

<%def name="header()">
  <div class="row">
	<div class="col-md-12">
	  ${self.main_menu()}
	</div>
  </div>
</%def>
  
<%def name="content_wrapper()">
    
    <% flash_msgs = request.session.pop_flash() %>
    
    %for flash_msg in flash_msgs:
      <div class="alert alert-info">
        ${flash_msg}
      </div>
    %endfor
    
  ${self.body()}
</%def>
    
<%def name="main_menu()">

<nav class="navbar navbar-default" role="navigation" style="height: 120px;">
  <div class="container-fluid">
    
    <!-- Brand and toggle get grouped for better mobile display -->
    <div class="navbar-header">
      <a class="pull-left navbar-brand" href="${request.route_url('home')}"><img src="${request.static_url('quranref:static/logo.png')}"  alt="Quran Reference Home" /></a>  
      <button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1">
        <span class="sr-only">Toggle navigation</span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
      </button>
      
    </div>

    <div class="ar text-success" style="font-size: larger; font-weight: bold;">وَلَقَدْ يَسَّرْنَا ٱلْقُرْءَانَ لِلذِّكْرِ فَهَلْ مِن مُّدَّكِر</div>
    <div class="ur text-primary hidden-xs">ہم نے اِس قرآن کو نصیحت کے لیے آسان ذریعہ بنا دیا ہے، پھر کیا ہے کوئی نصیحت قبول کرنے والا؟
	  <br />
	  We have made the Qur'an easy to derive lessons from. Is there, then, any who will take heed?
	</div>
    
    <!-- Collect the nav links, forms, and other content for toggling -->
    <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
      <form class="navbar-form navbar-right" role="search">
        <div class="form-group">
          <input type="text" class="form-control" placeholder="Search">
        </div>
        <button type="submit" class="btn btn-default">Submit</button>
    </form>
	  
	  
	  
      
    </div><!-- /.navbar-collapse -->
  </div><!-- /.container-fluid -->
</nav>

  
  
  
  
  

</%def>
<%def name="footer()">
  <div class="row">
	<div class="well col-md-12" style="text-align: center">
      <div class="ar text-danger" style="text-align: center; font-weight: bold; font-size: 18pt;">رَبَّنَا تَقَبَّلْ مِنَّآ</div>
      <div style="font-size: 8pt;">QuranRef - Arabic text and translations courtesy of <a href="http://tanzil.net">Tanzil.net</a></div>
	</div>
  </div>
</%def>

