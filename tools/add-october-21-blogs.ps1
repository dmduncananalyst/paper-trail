$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$out=Join-Path $root 'verification/approved-blogs-20261021'
$utf8=[Text.UTF8Encoding]::new($false)
function WriteUtf8($path,$text){[IO.File]::WriteAllText((Join-Path $root $path),$text,$utf8)}
function Esc($text){[Net.WebUtility]::HtmlEncode([string]$text)}
$raw=Get-Content (Join-Path $out 'pdf-streams.txt') -Raw -Encoding UTF8
function Blocks($n){
 $stream=[regex]::Match($raw,'(?s)STREAM '+$n+'\r?\n(.*?)(?=STREAM |\z)').Groups[1].Value
 foreach($b in [regex]::Matches($stream,'(?s)BT\b(.*?)\bET')){
  $parts=@([regex]::Matches($b.Groups[1].Value,'\(((?:\\.|[^\\)])*)\)\s*Tj')|ForEach-Object {
   [regex]::Replace($_.Groups[1].Value,'\\([0-7]{1,3}|.)',{param($m) if($m.Groups[1].Value -match '^[0-7]{1,3}$'){[Text.Encoding]::GetEncoding(1252).GetString([byte[]]@([Convert]::ToInt32($m.Groups[1].Value,8)))}else{$m.Groups[1].Value}})
  })
  if($parts.Count){$text=($parts -join ' ') -replace " ' s\b","'s"; [pscustomobject]@{text=$text;heading=($b.Groups[1].Value -match '/F2 12\.5 Tf')}}
 }
}
$assignments=@(
 @{streams=@(12,17,19);slug='the-receipts-that-disappear-before-the-year-ends.html';photo='End-of-Year Receipt Chaos.png';alt='Scattered receipts beside a laptop, calculator, and receipt box in a contractor workspace';service='year-end-bookkeeping.html';label='Year End Bookkeeping'},
 @{streams=@(21,23);slug='when-personal-and-business-spending-become-one.html';photo='Sorting Receipts in a Cozy Home Office.png';alt='Business owner sorting receipts and paperwork beside file boxes in a home office';service='transaction-categorization.html';label='Transaction Categorization'},
 @{streams=@(25,27,29);slug='the-contractor-records-that-make-january-difficult.html';photo='Contractor Reviewing Receipts at Work Van.png';alt='Contractor reviewing receipts and folders at the open back of a work van';service='tax-ready-bookkeeping.html';label='Tax Ready Bookkeeping'}
)
$template=Get-Content (Join-Path $root 'the-real-cost-of-monthly-bookkeeping-for-small-businesses.html') -Raw -Encoding UTF8
$archive=Get-Content (Join-Path $root 'blog.html') -Raw -Encoding UTF8
$sitemap=Get-Content (Join-Path $root 'sitemap.xml') -Raw -Encoding UTF8
$origin='https://www.papertrailusa.com/'
foreach($a in $assignments){
 $archive=[regex]::Replace($archive,'(?s)<article class="blog-story approved-blog-card">(?:(?!</article>).)*href="'+[regex]::Escape($a.slug)+'"(?:(?!</article>).)*</article>','')
 $sitemap=[regex]::Replace($sitemap,'\s*<url><loc>'+[regex]::Escape($origin+$a.slug)+'</loc>.*?</url>','')
}
$manifest=@();$cards='';$entries=''
foreach($a in $assignments){
 $all=[Collections.Generic.List[object]]::new()
 foreach($n in $a.streams){
  $page=@(Blocks $n)
  if($all.Count -and !$page[0].heading -and !$all[$all.Count-1].heading -and !$page[0].text.StartsWith('https://')){$all[$all.Count-1].text+=' '+$page[0].text;$page=@($page|Select-Object -Skip 1)}
  foreach($b in $page){$all.Add($b)}
 }
 $title=$all[0].text;$description=$all[2].text -replace '^SEO description: ',''
 if($all[1].text -cne 'October 21, 2026'){throw 'Publication date mismatch'}
 $refsAt=3;while($all[$refsAt].text -ne 'Sources and references'){$refsAt++}
 $article=@($all.GetRange(3,$refsAt-3))
 # The disclaimer and opening paragraph are split across PDF text blocks.
 $article[0].text+=' '+$article[1].text;$article=@($article[0])+@($article|Select-Object -Skip 2)
 $refs=@($all.GetRange($refsAt+1,$all.Count-$refsAt-1)|ForEach-Object {@{label=($_.text -replace '(Internal|Milestone)$','');url=($_.text -replace '(Internal|Milestone)$','')}})
 $source=Join-Path 'C:\Users\Owner\OneDrive\Desktop' $a.photo
 Copy-Item -LiteralPath $source -Destination (Join-Path $root ('assets/photos/'+$a.photo))
 $bytes=[IO.File]::ReadAllBytes($source)
 $width=($bytes[16]*16777216+$bytes[17]*65536+$bytes[18]*256+$bytes[19]);$height=($bytes[20]*16777216+$bytes[21]*65536+$bytes[22]*256+$bytes[23])
 $src='assets/photos/'+$a.photo;$imageUrl=$origin+'assets/photos/'+[uri]::EscapeDataString($a.photo)
 $image='<img fetchpriority="high" height="'+$height+'" width="'+$width+'" src="'+(Esc $src)+'" alt="'+(Esc $a.alt)+'" loading="eager">'
 $body='';$inSection=$false
 foreach($b in $article){if($b.heading){if($inSection){$body+='</div></section>'};$body+='<section class="story-section"><h2>'+(Esc $b.text)+'</h2><div class="section-copy">';$inSection=$true}else{$body+='<p>'+(Esc $b.text)+'</p>'}}
 if($inSection){$body+='</div></section>'}
 $body+='<section class="reference-list"><h2>Sources and references</h2><ol>'
 foreach($r in $refs){$body+='<li><a href="'+(Esc $r.url)+'" target="_blank" rel="noopener">'+(Esc $r.label)+'</a></li>'};$body+='</ol></section>'
 $content='<article class="reading-feature approved-blog"><header class="reading-masthead">'+$image+'<h1>'+(Esc $title)+'</h1></header><div class="reading-column"><p class="publication-date">Published <time datetime="2026-10-21">10/21/2026</time></p><div class="reading-spread">'+$body+'</div></div></article><div class="reading-actions"><a class="action" href="'+$a.service+'">'+$a.label+'</a><a class="action quiet" href="blog.html">Blog</a></div>'
 $page=$template.Replace('the-real-cost-of-monthly-bookkeeping-for-small-businesses.html',$a.slug)
 $page=[regex]::Replace($page,'<title>.*?</title>',{param($m) '<title>'+(Esc $title)+'</title>'})
 foreach($m in @(@('name','description',$description),@('property','og:title',$title),@('property','og:description',$description),@('property','og:url',($origin+$a.slug)),@('property','og:image',$imageUrl))){
  $value=$m[2];$page=[regex]::Replace($page,'(<meta '+$m[0]+'="'+$m[1]+'" content=")[^"]*(")',{param($match) $match.Groups[1].Value+(Esc $value)+$match.Groups[2].Value})
 }
 $page=$page.Replace('property="og:type" content="website"','property="og:type" content="article"')
 $page=[regex]::Replace($page,'(?s)(<main\b[^>]*>).*?(<dialog\b)',{param($m) $m.Groups[1].Value+$content+$m.Groups[2].Value},1)
 $schema=@{'@context'='https://schema.org';'@type'='BlogPosting';'@id'=($origin+$a.slug+'#article');url=($origin+$a.slug);mainEntityOfPage=($origin+$a.slug);headline=$title;description=$description;image=$imageUrl;datePublished='2026-10-21';dateModified='2026-10-21';inLanguage='en-US';author=@{'@type'='Organization';name='Paper Trail';url=$origin};publisher=@{'@type'='Organization';name='Paper Trail';logo=@{'@type'='ImageObject';url=($origin+'assets/images/paper-trail-logo.png')}};citation=@($refs|ForEach-Object url);articleBody=(($article|ForEach-Object text)-join "`n`n")}
 $json=$schema|ConvertTo-Json -Depth 15 -Compress
 $page=[regex]::Replace($page,'(?s)<script type="application/ld\+json">.*?</script>',{param($m) '<script type="application/ld+json">'+$json+'</script>'},1)
 WriteUtf8 $a.slug $page
 $cards+='<article class="blog-story approved-blog-card">'+$image+'<div><h2>'+(Esc $title)+'</h2><p class="publication-date">Published <time datetime="2026-10-21">10/21/2026</time></p><p class="blog-preview">'+(Esc $description)+'</p><a class="action" data-i18n="readNote" href="'+$a.slug+'">Read</a></div></article>'
 $entries+='  <url><loc>'+$origin+$a.slug+'</loc><lastmod>2026-10-21</lastmod><image:image><image:loc>'+$imageUrl+'</image:loc></image:image></url>'+"`n"
 $manifest+=@{title=$title;slug=$a.slug;description=$description;photo=$a.photo;article=$article;references=$refs;width=$width;height=$height;service=$a.service}
}
$archive=$archive.Replace('<div class="blog-story-list">','<div class="blog-story-list">'+$cards)
$archive=[regex]::Replace($archive,'(?s)<script type="application/ld\+json">(.*?)</script>',{param($m)
 $data=$m.Groups[1].Value|ConvertFrom-Json
 foreach($node in $data.'@graph'){if($node.'@type' -eq 'ItemList'){$old=@($node.itemListElement|Where-Object {$_.url -notin @($manifest|ForEach-Object {$origin+$_.slug})});$position=3;foreach($item in $old){$position++;$item.position=$position};$new=@();$i=0;foreach($a in $manifest){$i++;$new+=@{'@type'='ListItem';position=$i;name=$a.title;url=($origin+$a.slug)}};$node.itemListElement=$new+$old}}
 '<script type="application/ld+json">'+($data|ConvertTo-Json -Depth 20 -Compress)+'</script>'
})
WriteUtf8 'blog.html' $archive
WriteUtf8 'sitemap.xml' ($sitemap.Replace('</urlset>',$entries+'</urlset>'))
WriteUtf8 'verification/approved-blogs-20261021/approved-content.json' ($manifest|ConvertTo-Json -Depth 15)
$manifest|Select-Object title,photo
