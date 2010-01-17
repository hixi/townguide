<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html><head>



  <title>Free Town Guide Generator</title>
  <meta name="GENERATOR" content="Quanta Plus">
  <meta name="AUTHOR" content="Graham Jones">
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <meta name="KEYWORDS" content="OpenStreetMap, TownGuide">


<script type="text/javascript">
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
</script><script src="index_files/ga.js" type="text/javascript"></script>
<script type="text/javascript">
try {
var pageTracker = _gat._getTracker("UA-7615786-8");
pageTracker._trackPageview();
} catch(err) {}</script>

</head>
<body>
<?php include("header.php");?>
<h1>Free Town Guide Generator</h1>
<h2>Introduction</h2>
The Free Town Guide Generator will generate simple PDF posters which
are guides to a particular area. The poster contains a map, and a
selectable set of features (a street index, or lists of pubs,
restaurants, shops, banks etc.).
The Data is derived from the <a href="http://www.openstreetmap.org/" name="OpenStreetMap"></a> project, which is a freely available map dataset, that can be edited by anyone.

Examples of the town guide generator output can be seen by clicking on the following images:
<table align="center">
<tbody><tr>
  <td><a href="example1_hartlepool.pdf">Hartlepool Pub Guide</a></td>
  <td><a href="example2_london.pdf">Central London Tourist Guide</a></td>
</tr>
<tr>
  <td>
    <a href="example1_hartlepool.pdf">
      <img src="example1_hartlepool.png" alt="example1_hartlepool.png">
      </a>
  </td>
  <td>
    <a href="example2_london.pdf">
      <img src="example2_london.png" alt="example2_london.png">
    </a>
  </td>
</tr>
</tbody></table>

<h2>Generate a Town Guide</h2>
<h3>Request Generation of a Town Guide</h3>
<p>To generate a town guide you need to know the latitude and longitude of
the bottom left corner of the area you are interested in. You also
specify the size of the area to be mapped in 1km units.</p>
<p>You can try the generator <a href="submitForm.php" name="here">here</a>.
Reliability is not promised at the moment though - this is very much work in
progress!</p>

<h3>View Job Queue</h3>
You can view the job request queue <a href="listQueue.php">here</a>.


<h3>Source Code</h3>
The source code for the townguide generator is at <a href="http://code.google.com/p/townguide">http://code.google.com/p/townguide</a>.

<h2>Contact</h2>
If you have any comments on the program or its output, please email me
on grahamjones139 at googlemail.com and/or raise an issue on the
project web page at <a href="http://code.google.com/p/townguide/issues">http://code.google.com/p/townguide/issues</a>. 

<h2>Alternatives</h2>
<a href="http://www.maposmatic.org/">www.maposmatic.org</a> provide a similar
service, producing printable maps with street indices (indexes?).
</body></html>