$ErrorActionPreference='Stop'
$matrixPath=Join-Path $PSScriptRoot '50-state-research-matrix.csv'
$rows=@(Import-Csv -LiteralPath $matrixPath)
$review=@()
foreach($row in $rows){
  $pilot=$row.state -in @('CA','TX','FL','NY','WA')
  $slug=($row.state_name.ToLowerInvariant() -replace ' ','-')
  $angles=($row.planned_distinct_angles -replace '-',' ').Split(';')
  $description=$row.state_name+' business records covering '+$angles[0].Trim().ToLowerInvariant()+' and '+$angles[1].Trim().ToLowerInvariant()+'. Review supporting documents and account reconciliations.'
  $draftStatus=if($pilot){'Local draft written; owner and individual factual quality review pending'}else{'Not drafted; await five pilot quality and design approval before drafting'}
  $next=if($pilot){'Review the local '+$row.state_name+' draft against its claim sources; check '+$angles[0].Trim().ToLowerInvariant()+'; resolve applicability and retention exceptions; visually review all three device sizes; obtain individual owner approval.'}else{'After pilot approval, independently verify '+$angles[0].Trim().ToLowerInvariant()+' and '+$angles[1].Trim().ToLowerInvariant()+'; draft substantive examples; complete individual factual and design review before seeking state approval.'}
  $add=[ordered]@{
    planned_public_url=('https://www.papertrailusa.com/state-records/'+$slug+'.html')
    planned_title=($row.state_name+' Bookkeeping And Business Records')
    planned_description=$description
    visible_card_action='Read only after approval and publication; flags currently have no links'
    quality_readiness=$draftStatus
    individual_quality_review_status='Pending; no state marked fully reviewed or approved'
    current_quality_gaps=$next
    publication_status='Not approved; not published'
    sitemap_status='Excluded; add only after individual approval and actual publication'
  }
  foreach($key in $add.Keys){$row|Add-Member -MemberType NoteProperty -Name $key -Value $add[$key] -Force}
  $review += [pscustomobject][ordered]@{
    state=$row.state
    state_name=$row.state_name
    planned_public_url=$add.planned_public_url
    local_draft_path=$(if($pilot){'verification/state-guides/'+$slug+'.html'}else{''})
    draft_status=$draftStatus
    independent_source_discovery=('Revenue: '+$row.revenue_access_result+'; Workforce: '+$row.workforce_access_result)
    factual_claim_review='Pending individual review; discovery is not a factual compliance signoff'
    applicability_and_effective_dates='Pending claim by claim verification for the relevant entity industry and tax year'
    state_specificity_review=('Pending review of '+$row.planned_distinct_angles)
    retention_review=$row.retention_verification_status
    hypothetical_examples_review='Pending individual review; examples must be labeled hypothetical and distinguish general bookkeeping from state requirements'
    duplicate_content_review='Pending individual comparison against other states; no name substitution accepted'
    title_description_review='Unique proposed title and description prepared; rendered metadata still needs individual verification'
    primary_source_link_review='Agency access results recorded; direct topic links and all cited claim destinations need individual final check'
    desktop_review='Pending rendered individual page review'
    tablet_review='Pending rendered individual page review'
    mobile_review='Pending rendered individual page review'
    accessibility_review='Pending keyboard headings contrast text size and image name checks on the actual page'
    owner_approval='Not approved'
    publication_status=$add.publication_status
    sitemap_status=$add.sitemap_status
    next_steps=$next
    review_record_date='2026-10-16'
  }
}
$rows|Export-Csv -LiteralPath $matrixPath -NoTypeInformation -Encoding UTF8
$review|Export-Csv -LiteralPath (Join-Path $PSScriptRoot 'individual-quality-review.csv') -NoTypeInformation -Encoding UTF8
[pscustomobject]@{matrix_rows=$rows.Count;review_rows=$review.Count;unique_urls=($rows.planned_public_url|Sort-Object -Unique).Count;unique_titles=($rows.planned_title|Sort-Object -Unique).Count;unique_descriptions=($rows.planned_description|Sort-Object -Unique).Count;prose_dash_matches=@($rows|Where-Object {$_.planned_title -match '-' -or $_.planned_description -match '-'}).Count}|ConvertTo-Json
