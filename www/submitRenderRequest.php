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

  $fname = "/home/disk2/www/townguide/www/output/townguide.xml";
  $fh = fopen($fname,'w') or die("failed to open file ".$fname);
  
  fwrite($fh,"<xml>\n");
  fwrite($fh,"<title>".$title."</title>\n");
  fwrite($fh,"<format>".$format."</format>\n");
  fwrite($fh,"<pagesize>".$papersize."</pagesize>\n");

  if ($streetIndex=='on') {
     fwrite($fh,"<streetIndex>True</streetIndex>\n");
  } else {	
     fwrite($fh,"<streetIndex>False</streetIndex>\n");
  }
  if ($featureList=='on') {
     fwrite($fh,"<featureList>True</featureList>\n");
  } else {	
     fwrite($fh,"<featureList>False</featureList>\n");
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

  fwrite($fh,"<features>\n".$featureStr."</features>\n");

  fwrite($fh,"<mapvfrac>75</mapvfrac>\n");
  fwrite($fh,"<datadir>/home/disk2/www/townguide</datadir>\n");
  fwrite($fh,"<outdir>/home/disk2/www/townguide/www/output</outdir>\n");
  fwrite($fh,"<mapfile>/home/disk2/www/townguide/osm.xml</mapfile>\n");
  fwrite($fh,"<origin>".$lat.",".$lon."</origin>\n");
  fwrite($fh,"<mapsize>".$nx.",".$ny."</mapsize>\n");
  fwrite($fh,"<uname>www</uname>\n");
  fwrite($fh,"<download>True</download>\n");
  fwrite($fh,"</xml>\n");
  fclose($fh);

  $output = null;

  $cmdstr = "/home/disk2/www/townguide/townguide.py ".$fname." 2>&1";
  exec($cmdstr, $output);

  print "<a href='output'>Click here to see your output</a>";

  print "<pre>" . var_export($output,TRUE) . "</pre>\n";

?>

