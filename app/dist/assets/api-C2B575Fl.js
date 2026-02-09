import{m as s,a as r,b as a,c as d}from"./mockData-DkSx-qKd.js";const o=e=>new Promise(t=>setTimeout(t,e)),p={getAll:async()=>(await o(300),[...s]),getById:async e=>(await o(200),s.find(t=>t.id===e)||null),create:async e=>{await o(500);const t={...e,id:`webapp-${Date.now()}`,userId:"user-1",createdAt:new Date().toISOString(),updatedAt:new Date().toISOString()};return s.push(t),t},update:async(e,t)=>{await o(400);const n=s.findIndex(i=>i.id===e);if(n===-1)throw new Error("Web app not found");return s[n]={...s[n],...t,updatedAt:new Date().toISOString()},s[n]},delete:async e=>{await o(300);const t=s.findIndex(n=>n.id===e);t!==-1&&s.splice(t,1)}},w={getAll:async()=>(await o(300),[...r]),getByPlatform:async e=>(await o(200),r.find(t=>t.platform===e)||null),connect:async(e,t)=>{await o(1e3);const n={id:`conn-${Date.now()}`,userId:"user-1",platform:e,accountName:t,accountId:`${e}-${Math.random().toString(36).substr(2,9)}`,isActive:!0,connectedAt:new Date().toISOString()};return r.push(n),n},disconnect:async e=>{await o(500);const t=r.findIndex(n=>n.platform===e);t!==-1&&r.splice(t,1)}},h={getAll:async e=>(await o(300),e?a.filter(t=>t.status===e):[...a]),getPending:async()=>(await o(300),a.filter(e=>e.status==="pending")),getById:async e=>(await o(200),a.find(t=>t.id===e)||null),approve:async e=>{await o(400);const t=a.findIndex(n=>n.id===e);if(t===-1)throw new Error("Content not found");return a[t]={...a[t],status:"approved",updatedAt:new Date().toISOString()},a[t]},reject:async e=>{await o(400);const t=a.findIndex(n=>n.id===e);if(t===-1)throw new Error("Content not found");return a[t]={...a[t],status:"rejected",updatedAt:new Date().toISOString()},a[t]},approveAll:async e=>{await o(600),e.forEach(t=>{const n=a.findIndex(i=>i.id===t);n!==-1&&(a[n]={...a[n],status:"approved",updatedAt:new Date().toISOString()})})},updateCaption:async(e,t)=>{await o(300);const n=a.findIndex(i=>i.id===e);if(n===-1)throw new Error("Content not found");return a[n]={...a[n],caption:t,updatedAt:new Date().toISOString()},a[n]},generate:async(e,t)=>{await o(2e3);const i={youtube:{title:"How to Boost Productivity with AI Tools",caption:`Discover the AI tools that are transforming how teams work! 🚀

In this video, we break down the top strategies for leveraging AI in your daily workflow.

#Productivity #AI #TeamWork #Innovation`,hashtags:["Productivity","AI","TeamWork","Innovation"]},tiktok:{title:"POV: AI Does Your Work",caption:`When AI handles the boring stuff so you can focus on what matters 😎

#AITools #WorkLife #ProductivityHacks`,hashtags:["AITools","WorkLife","ProductivityHacks"]},instagram:{title:"Morning Routine of Successful Teams",caption:`The best teams start their day with these 3 habits ☀️

Save this for later!

#MorningRoutine #TeamSuccess #Productivity`,hashtags:["MorningRoutine","TeamSuccess","Productivity"]},facebook:{title:"Why Smart Teams Choose AI",caption:"AI isn't just a buzzword—it's a competitive advantage. Here's why leading teams are adopting AI tools in 2024.",hashtags:["AI","BusinessGrowth","Innovation"]},twitter:{title:"Quick Tip",caption:`💡 The teams that will win in 2024 are the ones that embrace AI not as a replacement, but as an amplifier of human creativity.

What's your take on AI in the workplace?`,hashtags:["AI","FutureOfWork","TeamBuilding"]},linkedin:{title:"The ROI of AI-Powered Teams",caption:`New research shows that teams using AI tools report:

✅ 40% faster project completion
✅ 35% reduction in meeting time
✅ 50% increase in creative output

The question isn't whether to adopt AI—it's how quickly you can integrate it into your workflow.

What's your organization's approach to AI adoption?`,hashtags:["Leadership","AI","BusinessStrategy","Innovation"]}}[t],c={id:`content-${Date.now()}`,userId:"user-1",webappId:e,platform:t,type:t==="youtube"||t==="tiktok"?"video":"image",status:"pending",title:i.title||"Generated Content",caption:i.caption||"Check out this amazing tool!",hashtags:i.hashtags||["Innovation","Tech"],mediaUrls:[`https://images.unsplash.com/photo-${Math.random().toString(36).substr(2,10)}?w=800`],createdAt:new Date().toISOString(),updatedAt:new Date().toISOString()};return a.push(c),c}},l={getSummary:async()=>(await o(400),d),getPlatformStats:async e=>(await o(300),d.platformBreakdown[e])};export{l as a,h as c,w as p,p as w};
//# sourceMappingURL=api-C2B575Fl.js.map
