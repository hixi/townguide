<?php
  $title       = $_REQUEST['title'] ;
  $lat         = $_REQUEST['lat'] ;
  $lon         = $_REQUEST['lon'] ;
  $nx          = $_REQUEST['nx'] ;
  $ny          = $_REQUEST['ny'] ;
  $format      = $_REQUEST['format'];
  $papersize   = $_REQUEST['papersize'];
  $streetIndex = $_REQUEST['streetIndex'] ;
  $featureList = $_REQUEST['featureList'] ;
  $pubs        = $_REQUEST['pubs'] ;
  $restaurants = $_REQUEST['restaurants'] ;
  $fastfood    = $_REQUEST['fastfood'] ;
  $hotels      = $_REQUEST['hotels'] ;
  $tourism     = $_REQUEST['tourism'] ;
  $leisure     = $_REQUEST['leisure'] ;
  $shopping    = $_REQUEST['shopping'] ;
  $banking     = $_REQUEST['banking'] ;
  $oscale      = $_REQUEST['oscale'];

  $nowStr = gmDate("Y-m-d H:i:s");

  $xmlStr="<xml>\n";
  $xmlStr.="<title>".$title."</title>\n";
  $xmlStr.="<format>".$format."</format>\n";
  $xmlStr.="<pagesize>".$papersize."</pagesize>\n";

  if ($streetIndex=='on') {
     $xmlStr.="<streetIndex>True</streetIndex>\n";
  } else {	
     $xmlStr.="<streetIndex>False</streetIndex>\n";
  }
  if ($featureList=='on') {
     $xmlStr.="<featureList>True</featureList>\n";
  } else {	
     $xmlStr.="<featureList>False</featureList>\n";
  }

  $featureStr = "";
  if ($pubs=='on') {
    if ($featureStr!="")
        $featureStr=$featureStr.',';
    $featureStr = $featureStr."Pubs:amenity='pub'"; 
  } 
  if ($restaurants=='on') {
    if ($featureStr!="")
        $featureStr=$featureStr.',';
    $featureStr = $featureStr."Restaurants:amenity='restaurant'"; 
  } 
  if ($fastfood=='on') {
    if ($featureStr!="")
        $featureStr=$featureStr.',';
    $featureStr = $featureStr."Fast Food:amenity='fast_food'"; 
  } 
  if ($hotels=='on') {
    if ($featureStr!="")
        $featureStr=$featureStr.',';
    $featureStr = $featureStr."Hotels / Guest Houses:tourism='hotel'|'motel'|'guest_house'"; 
  } 
  if ($tourism=='on') {
    if ($featureStr!="")
        $featureStr=$featureStr.',';
    $featureStr = $featureStr."Tourism:tourism='attraction'"; 
  } 
  if ($leisure=='on') {
    if ($featureStr!="")
        $featureStr=$featureStr.',';
    $featureStr = $featureStr."Leisure:leisure='golf'|'sports_centre'|'stadium'|'pitch'|'track'"; 
  } 
  if ($shopping=='on') {
    if ($featureStr!="")
        $featureStr=$featureStr.',';
    $featureStr = $featureStr."Shopping:shop='mall'|'supermarket'|'convenience'"; 
  } 
  if ($banking=='on') {
    if ($featureStr!="")
        $featureStr=$featureStr.',';
    $featureStr = $featureStr."Leisure:amenity='bank'|'atm'"; 
  } 

  if ($featureStr=="") {
        $featureStr="None:amenity='none'";
  } 

  $xmlStr.="<features>\n".$featureStr."</features>\n";

  $xmlStr.="<mapvfrac>75</mapvfrac>\n";
  $xmlStr.="<datadir>/home/graham/townguide/src</datadir>\n";
  $xmlStr.="<outdir>/home/graham/townguide/src/www/output</outdir>\n";
  $xmlStr.="<mapfile>/home/graham/mapnik_osm/osm.xml</mapfile>\n";
  $xmlStr.="<origin>".$lat.",".$lon."</origin>\n";
  $xmlStr.="<mapsize>".$nx.",".$ny."</mapsize>\n";
  $xmlStr.="<uname>www</uname>\n";
  $xmlStr.="<password>1234</password>\n";
  $xmlStr.="<download>True</download>\n";
  $xmlStr.="</xml>\n";

  $xmlStrSafe = str_replace("'","\'",$xmlStr);
  
  #print "<pre>".$xmlStr."</pre>";
  #print "<pre>".$xmlStrSafe."</pre>";
  


  $dbconn = pg_connect("host=localhost dbname=townguide user=www password=1234")
    or die('Could not connect: ' . pg_last_error());



  $query  = "insert into queue (status, title, originlat, originlon,"
  	  . "subdate, statusdate, xml) values "
  	  . "( 0, "."'".$title."'" 
	  . ", ".$lat.", ".$lon.", "
	  . "timestamp '".$nowStr."', timestamp '".$nowStr."',"
	  . " '".$xmlStrSafe."') returning jobno;";
       
  $result = pg_query($query) or die('Query failed: ' . pg_last_error());
  $line = pg_fetch_array($result);
  $jobNo=$line['jobno'];	

  mkdir ("/home/disk2/www/townguide/www/output/".$jobNo,0777);
  chmod ("/home/disk2/www/townguide/www/output/".$jobNo,0777);
   
  print "<h1>Job Submitted</h1>";
  print "<p>Your Job Number is ".$jobNo."</p>";
  print "<p>Your output will appear <a href='output/".$jobNo."'>"
  . "Here</a>.";
  print "<p><a href='listQueue.php'>List Job Rendering Queue</a></p>";



	

?>
