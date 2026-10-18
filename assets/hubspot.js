// Public form identifiers supplied by Paper Trail. No account credentials are used.
// Field names verified against the published HubSpot form on October 10, 2026.
export const hubspotEndpoint = 'https://api.hsforms.com/submissions/v3/integration/submit/247103073/a625ce56-9bc6-41c4-b5c0-745d600cdc21';
export const intakeLabels = {
  language:'Conversation language', state:'State', scope:'Additional service scope', meetingTime:'Meeting time', timeZone:'Time zone',
  issue:'What needs attention', period:'Scope or period', software:'Current system',
  businessType:'Type of business', business:'Company name', timing:'Start timing',
  meeting:'Meeting preference', availability:'Availability', name:'Name', email:'Email', phone:'Phone number'
};
export function validateContact(details) {
  if (!details.name?.trim() || !details.business?.trim() || !details.issue?.trim()) return 'Please include your name, company name and what needs attention.';
  if (!/^\S+@\S+\.\S+$/.test(details.email || '')) return 'Please include a valid email address.';
  const phone = details.phone || '';
  const digits = phone.split(/\s*(?:ext\.?|x)\s*/i)[0].replace(/\D/g,'');
  if (!/^[+\d().\s-]+(?:\s*(?:x|ext\.?)\s*\d{1,6})?$/i.test(phone) || !(digits.length===10 || (digits.length===11 && digits.startsWith('1')))) return 'Please include a ten digit phone number, including the area code.';
  return '';
}
export function hubspotPayload(details, topic, pageUri) {
  const names = details.name.trim().split(/\s+/);
  const values = {
    firstname:names.shift(), lastname:names.join(' '), email:details.email,
    phone:details.phone, company:details.business,
    message:'Paper Trail inquiry\nTopic: '+topic+'\n\n'+Object.entries(intakeLabels).filter(([key])=>details[key]).map(([key,label])=>label+': '+(details[key]||'')).join('\n')+(details.originalAnswers?'\n\nOriginal visitor answers:\n'+Object.entries(details.originalAnswers).filter(([key,value])=>Object.hasOwn(intakeLabels,key)&&typeof value==='string').map(([key,value])=>intakeLabels[key]+': '+value).join('\n'):'')
  };
  return {
    fields:Object.entries(values).filter(([,value])=>value).map(([name,value])=>({objectTypeId:'0-1',name,value})),
    context:{pageName:topic+' | Paper Trail',pageUri}
  };
}
export async function deliverToHubSpot(details, topic, pageUri) {
  const invalid = validateContact(details);
  if (invalid) throw new Error(invalid);
  let response;
  try {
    response = await fetch(hubspotEndpoint, {
      method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify(hubspotPayload(details,topic,pageUri)),
      signal:AbortSignal.timeout(18000)
    });
  } catch {
    throw new Error('We could not confirm delivery. Your note is still here. Please try again in a moment.');
  }
  if (!response.ok) throw new Error(response.status===429
    ? 'Please give it a moment before sending your note again.'
    : 'Your note was not accepted. Please check your contact details and try again.');
}
