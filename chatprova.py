import React, { useState, useEffect, useRef } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, onAuthStateChanged, signInWithCustomToken } from 'firebase/auth';
import { getFirestore, doc, setDoc, collection, addDoc, serverTimestamp } from 'firebase/firestore';

/* ==========================================================================
   CONFIG & ASSETS (SYNCHRONIZED WITH CUSTOM PALETTE & DEEP LINKS)
   ========================================================================== */
const TENANT = {
  name: "ProVista Hub",
  whatsapp: "918084843501",
  phone: "+91 8084843501",
  email: "provistah@gmail.com",
  address: "HiTECH City, Hyderabad, India",
  primary: "#5A7863",        // Dark Olive Green
  accent: "#90AB8B",         // Sage Green
  secondary: "#EBF4DD",      // Pale Lime/Cream
  cta: "#5A7863",            
  site: "https://provistahub.com",
  servicesUrl: "https://provistahub.com/?view=services-list",
  avatarUrl: "https://cdn-icons-png.flaticon.com/512/4712/4712109.png"
};

// Fixed: Added back the missing Audio Guide Script
const AUDIO_GUIDE_SCRIPT = `Welcome to ProVista Hub. We are your ultimate digital destination, committed to building innovative and scalable solutions. Our core expertise includes Modern Web and App Development, Human-Centered UI/UX Design, and Data-Driven Digital Marketing. We also specialize in AI Automation to streamline your workflows. Located in Hi-Tech City, Hyderabad, we are ready to be your trusted technology partner. You can ask me about any service, or use the buttons below to contact our team directly via WhatsApp or Email.`;

const SERVICES = [
  { title: "Web Development", url: "https://provistahub.com/?view=service-detail&serviceId=web-development", desc: "Modern, scalable web engineering using high-performance frameworks." },
  { title: "UI/UX Design", url: "https://provistahub.com/#ui-ux-design", desc: "Human-centered design focused on conversion and intuitive user journeys." },
  { title: "App Development", url: "https://provistahub.com/#app-development", desc: "Native and cross-platform mobile solutions for enterprise-grade performance." },
  { title: "Graphics Designer Services", url: "https://provistahub.com/?view=service-detail&serviceId=graphics-designer-services", desc: "Professional graphics, illustrations, and brand layouts." },
  { title: "Digital Marketing", url: "https://provistahub.com/?view=service-detail&serviceId=digital-marketing", desc: "Data-driven marketing strategies to expand reach and maximize ROI." },
  { title: "Branding & Strategy", url: "https://provistahub.com/#branding", desc: "Strategic identity development and brand positioning." },
  { title: "E‑commerce Solutions", url: "https://provistahub.com/#ecommerce", desc: "Full-stack online commerce architectures with optimized conversion." },
  { title: "Content Creation", url: "https://provistahub.com/?view=service-detail&serviceId=content-creation", desc: "Engaging academic notes and high-impact promotional content." },
  { title: "Catalogues", url: "https://provistahub.com/?view=service-detail&serviceId=catalogues", desc: "Professionally designed digital and printed catalogues." },
  { title: "AI & Automation", url: "https://provistahub.com/?view=service-detail&serviceId=ai-automation", desc: "Intelligent workflow automation and generative AI integration." },
  { title: "Google Ads & PPC Management", url: "https://provistahub.com/?view=service-detail&serviceId=google-ads-services", desc: "Drive immediate traffic with optimized PPC campaigns." },
  { title: "SEO Services", url: "https://provistahub.com/?view=service-detail&serviceId=seo-services", desc: "Boost online visibility and drive organic traffic." },
  { title: "ATS Free Resume Builder", url: "https://provistahub.com/?view=service-detail&serviceId=ats-resume-builder", desc: "ATS-optimized resumes designed to increase interview chances." }
];

const LANGUAGES = [
  { code: 'en', name: 'English', voice: 'Kore' },
  { code: 'hi', name: 'Hindi', voice: 'Puja' },
  { code: 'es', name: 'Spanish', voice: 'Leda' },
  { code: 'fr', name: 'French', voice: 'Fenrir' }
];

const Icons = {
  Chat: (props) => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={props.className || "w-6 h-6"} {...props}><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V3a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>,
  LayoutGrid: (props) => <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/></svg>,
  Send: () => <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>,
  Back: (props) => <svg className={props.className || "w-5 h-5"} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>,
  Speaker: () => <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M11 5L6 9H2v6h4l5 4V5z"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>,
  Sparkle: () => <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M9 2L7.1 7.1 2 9l5.1 1.9L9 16l1.9-5.1L16 9l-5.1-1.9L9 2zM19 14l-1.1 3.1L15 18l2.9 0.9L19 22l0.9-3.1L23 18l-3.1-0.9L19 14z"/></svg>,
  WhatsApp: () => <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12.04 2.02c-5.52 0-9.98 4.47-9.98 9.98 0 1.74.45 3.48 1.34 5.01l-1.35 4.92 5.04-1.32c1.46.82 3.13 1.25 4.95 1.25 5.52 0 9.98-4.47 9.98-9.98s-4.47-9.98-9.98-9.98zm0 18.26c-1.6 0-3.18-.38-4.62-1.11-.33-.2-3.42.92-3.34-3.34-.22-.34-.8-1.48-1.22-3.15-1.22-4.88 0-4.54 3.68-8.22 8.22-8.22s8.22 3.68 8.22 8.22-3.68 8.22-8.22 8.22zm4.49-5.83c-.24-12-1.45-.72-1.68-.88l-.39-.12-.55.12c-.16.24-.63.79-.78.95-.14.16-.28.18-.52.06s-1.03-.38-1.96-1.21c-.73-.64-1.22-1.43-1.36-1.67s-.03-.36.11-.48c.13-.11.28-.28.42-.42s.18-.28.27-.48.09-19.05-.35-.01-.47s-.55-1.32-.75-1.81c-.2-.48-.4-42-.55-42s-.3-01-.46-.01c-.16 0-.42.06-.63.38-.84.82-.84 2c0 1.18.86 2.32 1 2.48s1.69 2.59 4.1 3.62l.59.25 1.05.4 1.41.51.59.18 1.13.16 1.56.1.48-.07 1.45-.59 1.65-1.16.2-.56.2-1.04.14-1.16s-.24-.18-.48-.3z"/></svg>,
  Phone: (props) => <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-3.35-2.58m-.13-13a19.4 19.4 0 0 1-2.58-3.35A19.79 19.79 0 0 1 2 5.18 2 2 0 0 1 4.08 3h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>,
  Email: () => <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>,
  Arrow: () => <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7"/></svg>,
  Mic: () => <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>,
  Play: () => <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>,
  Stop: () => <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M6 6h12v12H6z"/></svg>,
  Mail: () => <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
};

// PCM to WAV Utility
function pcmToWav(pcmData, sampleRate) {
  const buffer = new ArrayBuffer(44 + pcmData.length);
  const view = new DataView(buffer);
  const writeString = (offset, string) => { for (let i = 0; i < string.length; i++) view.setUint8(offset + i, string.charCodeAt(i)); };
  writeString(0, 'RIFF'); view.setUint32(4, 32 + pcmData.length, true); writeString(8, 'WAVE'); writeString(12, 'fmt '); view.setUint32(16, 16, true); view.setUint16(20, 1, true); view.setUint16(22, 1, true); view.setUint32(24, sampleRate, true); view.setUint32(28, sampleRate * 2, true); view.setUint16(32, 2, true); view.setUint16(34, 16, true); writeString(36, 'data'); view.setUint32(40, pcmData.length, true);
  for (let i = 0; i < pcmData.length; i++) view.setUint8(44 + i, pcmData[i]);
  return new Blob([buffer], { type: 'audio/wav' });
}

/* ==========================================================================
   HELPER COMPONENTS
   ========================================================================== */

function VoiceInput({ onText, disabled }) {
  const start = () => {
    if (!('webkitSpeechRecognition' in window)) {
      console.error("Web Speech API is not supported.");
      return;
    }
    const recognition = new window.webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.onresult = (e) => {
      const transcript = e.results[0][0].transcript;
      onText(transcript);
    };
    recognition.start();
  };
  return (
    <button onClick={start} disabled={disabled} className="p-3 bg-red-500 text-white rounded-xl shadow-md hover:bg-red-600 transition duration-150 disabled:bg-gray-400">
      <Icons.Mic className="w-5 h-5" />
    </button>
  );
}

function ContactDetail({ icon, label, value, link }) {
    return (
        <div className="flex items-start space-x-3 text-left">
            <span className="text-xl">{icon}</span>
            <div>
                <p className="text-sm font-medium text-gray-500">{label}</p>
                {link ? (
                    <a href={link} className="text-slate-900 hover:text-[#5A7863] underline font-semibold transition duration-150">{value}</a>
                ) : (
                    <p className="text-gray-800 font-semibold">{value}</p>
                )}
            </div>
        </div>
    );
}

const DashboardCard = ({ title, icon, bgColor, children }) => (
    <div className="bg-white p-5 rounded-xl shadow-sharp border border-gray-100">
        <div className={`flex items-center mb-3 p-2 rounded-lg ${bgColor} bg-opacity-10`}>
            <span className={`text-2xl mr-3 ${bgColor === 'bg-provista-primary' ? 'text-provista-primary' : 'text-provista-accent'}`}>{icon}</span>
            <h3 className="text-lg font-bold text-slate-dark">{title}</h3>
        </div>
        {children}
    </div>
);

/* ==========================================================================
   VIEW COMPONENTS (DEFINED BEFORE APP)
   ========================================================================== */

const ServicesView = ({ setView }) => (
  <div className="flex-1 flex flex-col p-6 space-y-6 bg-white animate-slide-up overflow-hidden">
    <div className="flex items-center justify-between pb-2 border-b border-gray-100">
      <button onClick={() => setView('menu')} className="text-slate-500 flex items-center text-xs font-bold uppercase tracking-wider hover:text-slate-700 transition">
          <Icons.Back className="mr-1 w-4 h-4" /> Back to Menu
      </button>
    </div>
    
    <div className="text-center space-y-2">
      <h2 className="text-xl font-bold text-slate-900 tracking-tight">Technical Domain Suite</h2>
      <p style={{ color: TENANT.primary }} className="text-xs uppercase tracking-widest font-semibold">ProVista Hub Services</p>
    </div>
    <div className="flex-1 overflow-y-auto custom-scrollbar pr-1 space-y-3 pb-4">
      {SERVICES.map((s, idx) => (
        <div 
          key={idx} 
          style={{ background: `${TENANT.secondary}50`, borderColor: `${TENANT.accent}30` }}
          className="p-4 rounded-2xl border group hover:border-emerald-400 transition-all cursor-pointer shadow-sm active:scale-[0.98]" 
          onClick={() => window.open(s.url, '_blank')}
        >
          <div className="flex items-center space-x-3 mb-1">
            <div style={{ color: TENANT.primary }} className="p-2 bg-white rounded-xl shadow-sm group-hover:bg-[#5A7863] group-hover:text-white transition-colors">
              <Icons.LayoutGrid className="w-4 h-4" />
            </div>
            <h4 className="font-bold text-slate-900 text-sm">{s.title}</h4>
          </div>
          <p className="text-[11px] text-slate-500 leading-relaxed ml-11">{s.desc}</p>
        </div>
      ))}
    </div>
  </div>
);

const GetInTouchView = ({ user, db, appId, setView }) => {
  const [formData, setFormData] = useState({ name: '', email: '', message: '' });
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!user || !db) return;
    setSubmitting(true);
    try {
      const inquiryCol = collection(db, 'artifacts', appId, 'public', 'data', 'inquiries');
      await addDoc(inquiryCol, { ...formData, userId: user.uid, timestamp: serverTimestamp() });
      setSubmitted(true);
    } catch (e) { console.error(e); } finally { setSubmitting(false); }
  };

  if (submitted) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-6 text-center animate-slide-up">
        <button onClick={() => setView('menu')} className="absolute top-4 left-4 text-slate-500 flex items-center p-2 rounded-full hover:bg-gray-100 transition"><Icons.Back /></button>
        <div style={{ background: TENANT.secondary, color: TENANT.primary }} className="w-16 h-16 rounded-full flex items-center justify-center mb-2 animate-bounce">
          <Icons.LayoutGrid className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-slate-900">Inquiry Received</h2>
        <p className="text-sm text-slate-500">Nexus updated. We will reach out shortly.</p>
      </div>
    );
  }

  return (
    <div className="flex-1 p-6 space-y-6 animate-slide-up overflow-y-auto">
      <div className="flex items-center justify-between pb-2 border-b border-gray-100">
        <button onClick={() => setView('menu')} className="text-slate-500 flex items-center text-xs font-bold uppercase tracking-wider hover:text-slate-700 transition">
            <Icons.Back className="mr-1 w-4 h-4" /> Back to Menu
        </button>
      </div>

      <div className="text-center space-y-2">
        <h2 className="text-xl font-bold text-slate-900 tracking-tight">Get in Touch</h2>
        <p className="text-xs text-[#90AB8B] uppercase tracking-widest font-semibold">Technical Inquiry</p>
      </div>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input required value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-xs outline-none focus:border-[#90AB8B] shadow-inner" placeholder="Name" />
        <input required type="email" value={formData.email} onChange={(e) => setFormData({...formData, email: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-xs outline-none focus:border-[#90AB8B] shadow-inner" placeholder="Business Email" />
        <textarea required rows="4" value={formData.message} onChange={(e) => setFormData({...formData, message: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-xs outline-none focus:border-[#90AB8B] resize-none shadow-inner" placeholder="Requirements..." />
        <button disabled={submitting} type="submit" style={{ background: TENANT.primary, color: 'white' }} className="w-full py-4 rounded-2xl font-bold text-[10px] uppercase tracking-widest shadow-xl hover:opacity-90">Transmit Inquiry</button>
      </form>
    </div>
  );
};

const AboutView = ({ setView }) => (
  <div className="flex-1 p-6 space-y-6 animate-slide-up overflow-y-auto custom-scrollbar">
    <div className="flex items-center justify-between pb-2 border-b border-gray-100">
      <button onClick={() => setView('menu')} className="text-slate-500 flex items-center text-xs font-bold uppercase tracking-wider hover:text-slate-700 transition">
          <Icons.Back className="mr-1 w-4 h-4" /> Back to Menu
      </button>
    </div>

    <div className="text-center space-y-2">
      <h2 className="text-xl font-bold text-slate-900 tracking-tight">The Vision</h2>
      <p style={{ color: TENANT.primary, backgroundColor: TENANT.secondary }} className="text-[10px] uppercase tracking-widest font-bold bg-slate-100 px-2 py-1 rounded inline-block text-[#5A7863]">Innovation Protocol</p>
    </div>
    <div className="space-y-4 text-sm text-slate-600 leading-relaxed">
      <p>At <strong>{TENANT.name}</strong>, we empower businesses with future-ready digital solutions.</p>
      <div className="p-5 rounded-3xl border border-slate-200 shadow-inner" style={{ background: '#f9fafb' }}>
        <h4 className="font-bold text-slate-900 text-xs uppercase tracking-widest mb-3">Leadership</h4>
        <div className="space-y-2 text-[11px] font-semibold text-[#5A7863]">
          <p>• Harsh Vishal (Founder & CEO)</p>
          <p>• Ravi Shankar Kumar (CIO)</p>
          <p>• Samiksha Mehare (COO)</p>
          <p>• Manish Kumar Modi (CTO)</p>
        </div>
      </div>

      <div className="mt-4 text-center">
        <p className="text-xs text-slate-400">Contact Leadership</p>
        <a href={`mailto:${TENANT.email}`} style={{ color: TENANT.primary }} className="text-sm font-bold hover:underline text-[#5A7863]">{TENANT.email}</a>
      </div>
    </div>
  </div>
);

const ContactView = ({ setView }) => (
    <div className="flex-1 p-6 space-y-6 bg-provista-bg transition duration-300 animate-slide-up">
        <div className="flex items-center justify-between pb-2 border-b border-gray-100">
          <button onClick={() => setView('menu')} className="text-slate-500 flex items-center text-xs font-bold uppercase tracking-wider hover:text-slate-700 transition">
              <Icons.Back className="mr-1 w-4 h-4" /> Back to Menu
          </button>
        </div>

        <div className="text-center space-y-2">
            <h2 className="text-xl font-bold text-slate-900 tracking-tight">Direct Contact</h2>
            <p className="text-xs text-[#90AB8B] uppercase tracking-widest font-semibold">Reach Us Directly</p>
        </div>
        
        <div className="space-y-4">
            <ContactDetail icon="📞" label="Phone (India)" value={TENANT.phone} link={`tel:${TENANT.phone}`} />
            <ContactDetail icon="📧" label="Email" value={TENANT.email} link={`mailto:${TENANT.email}`} />
            <ContactDetail icon="📍" label="Address" value={TENANT.address} />
        </div>

        <div className="pt-4 border-t border-gray-200 space-y-3">
            {/* DIRECT WHATSAPP LINK */}
            <a 
                href={`https://wa.me/${TENANT.whatsapp.replace(/\+/g, '')}?text=${encodeURIComponent("Hi ProvistaHub Support, I need immediate assistance with your services and would like to chat directly.")}`}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full flex items-center justify-center p-3 bg-green-600 text-white rounded-xl shadow-lg hover:bg-green-700 transition duration-150 font-bold hover:scale-[1.02] active:scale-[0.98]"
            >
                <Icons.WhatsApp className="mr-2" />
                Chat via WhatsApp
            </a>
            <a 
                href={`mailto:${TENANT.email}`}
                className="w-full flex items-center justify-center p-3 bg-slate-700 text-white rounded-xl shadow-lg hover:bg-slate-800 transition duration-150 font-bold hover:scale-[1.02] active:scale-[0.98]"
            >
                <Icons.Mail className="mr-2" />
                Send an Email
            </a>
        </div>
    </div>
);

// Added overflow-y-auto to enable scrolling here
const ContactSupportSection = ({ setView }) => (
  <div className="flex-1 flex flex-col p-6 space-y-6 animate-slide-up overflow-y-auto custom-scrollbar">
    <div className="flex items-center justify-between pb-2 border-b border-gray-100">
      <button onClick={() => setView('menu')} className="text-slate-500 flex items-center text-xs font-bold uppercase tracking-wider hover:text-slate-700 transition">
          <Icons.Back className="mr-1 w-4 h-4" /> Back to Menu
      </button>
    </div>

    <div className="text-center space-y-2">
      <h2 className="text-xl font-bold text-slate-900 tracking-tight">Support Channels</h2>
      <p className="text-xs text-[#90AB8B] uppercase tracking-widest font-semibold">Immediate Assistance</p>
    </div>
    <div className="space-y-3">
      {/* DIRECT WHATSAPP LINK in Support Section */}
      <a 
        href={`https://wa.me/${TENANT.whatsapp.replace(/\+/g, '')}?text=${encodeURIComponent("Hi ProvistaHub Support, I have a support inquiry.")}`}
        target="_blank" 
        rel="noopener noreferrer"
        className="w-full flex items-center p-5 bg-emerald-50 border border-emerald-100 rounded-3xl hover:bg-emerald-100 transition-all group shadow-sm"
      >
        <div style={{ background: TENANT.primary, color: TENANT.secondary }} className="w-10 h-10 rounded-2xl flex items-center justify-center mr-4 shadow-lg"><Icons.WhatsApp /></div>
        <div className="text-left"><p className="font-bold text-slate-900 text-sm">Direct WhatsApp</p><p className="text-[10px] text-emerald-600 font-medium">Instant Consultation</p></div>
      </a>
      {/* FIXED: Changed text color to slate-900 for phone link number */}
      <a href={`tel:${TENANT.phone}`} style={{ background: '#f8fafc' }} className="flex items-center p-5 border border-slate-200 rounded-3xl hover:bg-slate-100 transition-all group shadow-sm">
        <div style={{ background: TENANT.primary, color: TENANT.secondary }} className="w-10 h-10 rounded-2xl flex items-center justify-center mr-4 shadow-lg"><Icons.Phone /></div>
        <div className="text-left"><p className="font-bold text-slate-900 text-sm">Phone Link</p><p className="text-[10px] font-medium text-slate-900">{TENANT.phone}</p></div>
      </a>
      {/* ADDED EMAIL BUTTON HERE AS REQUESTED */}
      <a href={`mailto:${TENANT.email}`} className="flex items-center p-5 bg-slate-50/50 border border-slate-200 rounded-3xl hover:bg-slate-50 transition-all group shadow-sm">
        <div style={{ background: TENANT.primary, color: TENANT.secondary }} className="w-10 h-10 rounded-2xl flex items-center justify-center mr-4 shadow-lg group-hover:rotate-12 transition-transform"><Icons.Email /></div>
        <div className="text-left"><p className="font-bold text-slate-900 text-sm">Official Mail</p><p style={{ color: TENANT.primary }} className="text-[10px] font-medium text-[#5A7863]">{TENANT.email}</p></div>
      </a>
    </div>
  </div>
);

// Added overflow-y-auto and custom-scrollbar class for scrolling
const MenuView = ({ setView }) => (
    <div className="flex flex-col flex-1 p-6 space-y-6 justify-center items-center text-center transition duration-300 animate-slide-up overflow-y-auto custom-scrollbar" style={{ backgroundColor: '#fdfdfd' }}>
         {/* Fixed: Added padding-top to prevent overlap with header in small height conditions */}
         <div className="space-y-2 mb-4 pt-4">
             <div className="w-16 h-16 bg-gradient-to-br from-[#5A7863] to-[#90AB8B] rounded-3xl mx-auto flex items-center justify-center shadow-lg mb-4">
                 <img src={TENANT.avatarUrl} className="w-10 h-10 filter brightness-0 invert" alt="Logo" />
             </div>
             {/* FIXED: Changed text color to text-slate-900 (Dark Slate) for visibility */}
             <h2 className="text-xl font-bold text-slate-900">Hello, I'm Prova.</h2>
             <p className="text-slate-500 text-sm max-w-[200px] mx-auto leading-relaxed">Your personal ProVista Hub assistant. How can I help?</p>
        </div>

        <div className="w-full max-w-sm space-y-3 pb-4">
            <button onClick={() => setView('chat')} className="w-full flex items-center p-4 bg-white rounded-2xl shadow-md hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200 border border-slate-50 group text-left">
                <div className="w-10 h-10 rounded-full bg-[#EBF4DD] flex items-center justify-center text-[#5A7863] mr-4 group-hover:bg-[#5A7863] group-hover:text-white transition-colors">
                    <Icons.Chat className="w-5 h-5" />
                </div>
                <div>
                    <span className="block font-bold text-slate-800 text-sm">Start a Chat</span>
                    <span className="block text-[10px] text-slate-400">AI Support Assistant</span>
                </div>
            </button>

             <button onClick={() => setView('services')} className="w-full flex items-center p-4 bg-white rounded-2xl shadow-md hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200 border border-slate-50 group text-left">
                <div className="w-10 h-10 rounded-full bg-[#EBF4DD] flex items-center justify-center text-[#5A7863] mr-4 group-hover:bg-[#5A7863] group-hover:text-white transition-colors">
                    <Icons.LayoutGrid className="w-5 h-5" />
                </div>
                <div>
                    <span className="block font-bold text-slate-800 text-sm">Our Services</span>
                    <span className="block text-[10px] text-slate-400">Explore offerings</span>
                </div>
            </button>

            <button onClick={() => setView('contact')} className="w-full flex items-center p-4 bg-white rounded-2xl shadow-md hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200 border border-slate-50 group text-left">
                <div className="w-10 h-10 rounded-full bg-[#EBF4DD] flex items-center justify-center text-[#5A7863] mr-4 group-hover:bg-[#5A7863] group-hover:text-white transition-colors">
                    <Icons.Phone className="w-5 h-5" />
                </div>
                <div>
                    <span className="block font-bold text-slate-800 text-sm">Contact Support</span>
                    <span className="block text-[10px] text-slate-400">Direct channels</span>
                </div>
            </button>
             <button onClick={() => setView('dashboard')} className="text-[10px] text-slate-300 hover:text-slate-400 pt-4">[Agent Access]</button>
        </div>
    </div>
);

const AgentDashboard = ({ setView }) => {
    const simulatedLeads = [
        { id: 101, name: "Arjun S.", phone: "+91 9901XXXXX", email: "arjun@example.com", status: "New", date: "Dec 16, 10:30 AM" },
        { id: 102, name: "Priya K.", phone: "+91 8877XXXXX", email: "priya@example.com", status: "Follow-up", date: "Dec 15, 03:15 PM" },
    ];
    return (
        <div className="flex flex-col flex-1 p-6 space-y-6 bg-slate-50 animate-slide-up">
            <div className="flex items-center justify-between pb-2 border-b border-gray-200">
                <button onClick={() => setView('menu')} className="text-slate-500 flex items-center text-xs font-bold uppercase tracking-wider hover:text-slate-700 transition">
                    <Icons.Back className="mr-1 w-4 h-4" /> Back to Menu
                </button>
            </div>
            
            <h2 className="text-xl font-bold text-slate-900">Agent Dashboard</h2>
            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                <h3 className="font-bold text-sm mb-3">Recent Leads</h3>
                {simulatedLeads.map(l => (
                    <div key={l.id} className="text-xs border-b py-2 last:border-0">
                        <span className="font-semibold">{l.name}</span> <span className="text-gray-400">({l.status})</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

/* ==========================================================================
   MAIN APP
   ========================================================================== */

const firebaseConfig = typeof __firebase_config !== 'undefined' ? JSON.parse(__firebase_config) : {};
const initialAuthToken = typeof __initial_auth_token !== 'undefined' ? __initial_auth_token : null;
const appId = typeof __app_id !== 'undefined' ? __app_id : 'provistahub-assistant-v9';

export default function App() {
  const [isOpen, setIsOpen] = useState(false);
  // DEFAULT VIEW IS NOW 'MENU' AS REQUESTED
  const [viewHistory, setViewHistory] = useState(['menu']);
  const currentView = viewHistory[viewHistory.length - 1];

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [lang, setLang] = useState(LANGUAGES[0]);
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [history, setHistory] = useState([]);
  const [user, setUser] = useState(null);
  const [isAudioGuidePlaying, setIsAudioGuidePlaying] = useState(false);
  const [leadDetected, setLeadDetected] = useState(false);
   
  const scrollRef = useRef(null);
  const audioRef = useRef(new Audio());
  const recognitionRef = useRef(null);
  const db = useRef(null);
  const auth = useRef(null);

  // 🎙️ Voice Logic
  const speakAIText = async (text) => {
    const apiKey = "";
    try {
      const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key=${apiKey}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contents: [{ parts: [{ text: `Say in ${lang.name}: ${text}` }] }], generationConfig: { responseModalities: ["AUDIO"], speechConfig: { voiceConfig: { prebuiltVoiceConfig: { voiceName: lang.voice } } } } })
      });
      const result = await res.json();
      const pcmBase64 = result.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
      if (pcmBase64) {
        const pcmData = Uint8Array.from(atob(pcmBase64), c => c.charCodeAt(0));
        const wavBlob = pcmToWav(pcmData, 24000);
        audioRef.current.src = URL.createObjectURL(wavBlob);
        audioRef.current.play();
      }
    } catch (e) { console.error(e); }
  };

  const toggleVoiceAssistant = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;
    if (isRecording) { recognitionRef.current?.stop(); return; }
    const recognition = new SpeechRecognition();
    recognition.lang = lang.code === 'hi' ? 'hi-IN' : 'en-US';
    recognition.onstart = () => setIsRecording(true);
    recognition.onend = () => setIsRecording(false);
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
      handleSend(transcript, true);
    };
    recognition.start();
    recognitionRef.current = recognition;
  };

  const systemPrompt = `Role: ${TENANT.name} Advisor. Identity: Tech Lead. Tone: Executive. Respond to digital queries.`;

  useEffect(() => {
    const app = initializeApp(firebaseConfig);
    auth.current = getAuth(app); db.current = getFirestore(app);
    const performAuth = async () => {
      if (initialAuthToken) await signInWithCustomToken(auth.current, initialAuthToken);
      else await signInAnonymously(auth.current);
    };
    performAuth().catch(console.error);
    const unsubscribe = onAuthStateChanged(auth.current, (u) => setUser(u));
    return () => unsubscribe();
  }, []);

  useEffect(() => {
    if (isOpen) {
      setMessages([{ role: 'ai', text: `Nexus Online. I am Prova, your **Voice Assistant**. Use the Mic to speak or explore our permanent sections below.`, actions: ['Play Audio Guide'] }]);
    } else {
      setMessages([]); setHistory([]); setLeadDetected(false); 
      // Reset view to menu when closed so it reopens fresh
      setViewHistory(['menu']);
      window.speechSynthesis.cancel(); audioRef.current.pause();
    }
  }, [isOpen]);

  useEffect(() => { 
      const audio = audioRef.current;
      const handleEnded = () => setIsAudioGuidePlaying(false);
      audio.addEventListener('ended', handleEnded);
      return () => audio.removeEventListener('ended', handleEnded);
  }, []);

  useEffect(() => { scrollRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, currentView]);

  const navigate = (view) => {
    if (currentView !== view) setViewHistory(prev => [...prev, view]);
  };

  const logLead = async (query) => {
    if (!user || !db.current) return;
    try {
      const leadCol = collection(db.current, 'artifacts', appId, 'public', 'data', 'leads');
      await addDoc(leadCol, { userId: user.uid, query, language: lang.code, timestamp: serverTimestamp() });
    } catch (e) { console.error(e); }
  };

  const handleSend = async (text = input, fromVoice = false) => {
    const val = text.trim(); if (!val) return;
    if (val === 'Play Audio Guide') { 
      if (isAudioGuidePlaying) {
          audioRef.current.pause();
          audioRef.current.currentTime = 0;
          setIsAudioGuidePlaying(false);
          window.speechSynthesis.cancel();
      } else {
          setIsAudioGuidePlaying(true);
          speakAIText(AUDIO_GUIDE_SCRIPT);
      }
      return; 
    }
    setMessages(prev => [...prev.filter(m => !m.actions && !m.loading), { role: 'user', text: val }, { role: 'ai', loading: true }]);
    setHistory(prev => [...prev, { role: "user", parts: [{ text: val }] }]);
    setInput(''); setLoading(true);

    if (/quote|price|contact|hire|build|service|web|seo|app|resume/.test(val.toLowerCase())) {
      setLeadDetected(true); logLead(val);
    }

    try {
      const apiKey = "";
      const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contents: [...history, { role: "user", parts: [{ text: val }] }], systemInstruction: { parts: [{ text: systemPrompt }] } })
      });
      const data = await res.json();
      const raw = data.candidates?.[0]?.content?.parts?.[0]?.text || "Resyncing...";
      setMessages(prev => [ ...prev.filter(m => !m.loading), { role: 'ai', text: raw } ]);
      setHistory(prev => [...prev, { role: "model", parts: [{ text: raw }] }]);
      if (fromVoice) speakAIText(raw);
    } catch (e) { setMessages(prev => [...prev.filter(m => !m.loading), { role: 'ai', text: "Resyncing nexus..." }]); } finally { setLoading(false); }
  };

  // --- RENDER ---
  let content = <MenuView setView={navigate} />;
  
  if (currentView === 'chat') {
      content = (
        <>
          <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar bg-white/50 backdrop-blur-sm" style={{ background: `${TENANT.secondary}30` }}>
            {messages.map((msg, i) => (
              <div key={i} className={`flex items-start ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.role === 'ai' && (
                  <div className="flex-shrink-0 mr-3 mt-1">
                    <img src={TENANT.avatarUrl} alt="Bot" className="w-8 h-8 rounded-full border border-slate-200 shadow-sm object-cover" />
                  </div>
                )}
                <div className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} max-w-[85%]`}>
                  {msg.text && (
                    <div className={`group relative px-5 py-3.5 text-sm shadow-xl shadow-emerald-200/10 whitespace-pre-wrap ${msg.role === 'user' ? 'bg-gradient-to-br from-[#90AB8B] to-[#5A7863] text-white rounded-[24px] rounded-tr-none' : 'bg-white text-slate-800 border border-slate-100 rounded-[24px] rounded-tl-none'}`}>
                      {msg.text.split('**').map((part, idx) => idx % 2 === 1 ? <strong key={idx} style={{ color: msg.role === 'user' ? '#EBF4DD' : TENANT.primary }}>{part}</strong> : part)}
                      {msg.role === 'ai' && !msg.loading && <button onClick={() => speakAIText(msg.text)} className="absolute -right-8 bottom-2 p-2 text-slate-300 hover:text-emerald-500 transition-all opacity-0 group-hover:opacity-100"><Icons.Speaker /></button>}
                    </div>
                  )}
                  {msg.actions && (
                    <div className="flex flex-wrap gap-2.5 mt-4">
                      {msg.actions.map((a, ai) => ( 
                          <button 
                            key={ai} 
                            onClick={() => handleSend(a)} 
                            style={a === 'Play Audio Guide' ? { background: TENANT.primary, color: 'white' } : { background: 'white', color: TENANT.primary, borderColor: `${TENANT.accent}50` }}
                            className={`text-[10px] font-black uppercase border px-5 py-3 rounded-2xl transition-all shadow-md flex items-center gap-2 hover:opacity-90`}
                          >
                            {a === 'Play Audio Guide' && (isAudioGuidePlaying ? <Icons.Stop /> : <Icons.Play />)}
                            {a === 'Play Audio Guide' && isAudioGuidePlaying ? 'Stop Audio' : a}
                          </button> 
                        ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {leadDetected && (
              <div style={{ background: '#f0fdf4', borderColor: '#bbf7d0' }} className="p-6 border rounded-[32px] space-y-3 animate-slide-up shadow-xl shadow-emerald-200/20">
                <p className="text-xs text-emerald-900 font-medium leading-relaxed">Strategic interest detected. Choose your communication channel:</p>
                <div className="space-y-2">
                    <button onClick={() => window.open(`https://wa.me/${TENANT.whatsapp}`, "_blank")} className="w-full py-3 bg-emerald-600 text-white text-[10px] font-black uppercase rounded-xl flex items-center justify-center space-x-2 shadow-lg hover:scale-[1.02] transition-all"><Icons.WhatsApp /> <span>WhatsApp</span></button>
                    <a href={`mailto:${TENANT.email}`} className="w-full py-3 bg-slate-700 text-white text-[10px] font-black uppercase rounded-xl flex items-center justify-center space-x-2 shadow-lg hover:scale-[1.02] transition-all decoration-0"><Icons.Mail /> <span>Email Us</span></a>
                </div>
              </div>
            )}
            <div ref={scrollRef} />
          </div>

          {/* Input Area */}
          <div className="p-6 border-t border-slate-50 bg-white">
            <div className="flex items-center group space-x-2">
              <div className="relative flex-1">
                <input value={input} onChange={(e) => setInput(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && handleSend()} placeholder="Talk to Prova..." className="w-full bg-slate-50 border border-slate-200 rounded-3xl px-6 py-4 text-xs font-medium outline-none focus:border-[#90AB8B] transition-all pr-12 shadow-inner" />
                <button onClick={toggleVoiceAssistant} className={`absolute right-4 top-1/2 -translate-y-1/2 p-2 rounded-full transition-all ${isRecording ? 'text-white bg-red-500 pulse-mic' : 'text-slate-400 hover:text-[#90AB8B]'}`}><Icons.Mic /></button>
              </div>
              <button onClick={() => handleSend()} style={{ background: TENANT.primary, color: 'white' }} className="p-4 rounded-full shadow-lg disabled:opacity-30" disabled={!input.trim()}><Icons.Send /></button>
            </div>
          </div>
        </>
      );
  } else if (currentView === 'about') content = <AboutView setView={navigate} />;
  else if (currentView === 'services') content = <ServicesView setView={navigate} />;
  else if (currentView === 'contact') content = <ContactSupportSection setView={navigate} />;
  else if (currentView === 'get-in-touch') content = <GetInTouchView user={user} db={db.current} appId={appId} setView={navigate} />;
  else if (currentView === 'dashboard') content = <AgentDashboard setView={navigate} />;

  return (
    <div className="fixed inset-0 pointer-events-none z-50 flex items-end justify-end p-6 font-sans">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
        .font-sans { font-family: 'Plus Jakarta Sans', sans-serif; pointer-events: none; }
        .interactive { pointer-events: auto; }
        .glass-hub { background: rgba(255, 255, 255, 0.98); backdrop-filter: blur(20px); border: 1px solid #f1f5f9; box-shadow: 0 40px 100px -20px rgba(15, 23, 42, 0.15); }
        .custom-scrollbar::-webkit-scrollbar { width: 3px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 20px; }
        @keyframes slide-up { from { transform: translateY(40px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
        .animate-slide-up { animation: slide-up 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
        .pulse-mic { animation: mic-pulse 1.5s infinite; background: #90AB8B; }
        @keyframes mic-pulse { 0% { box-shadow: 0 0 0 0 rgba(144, 171, 139, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(144, 171, 139, 0); } 100% { box-shadow: 0 0 0 0 rgba(144, 171, 139, 0); } }
      `}</style>

      {/* Floating Trigger Button with ANIMATION & IMAGE */}
      <button 
        onClick={() => setIsOpen(!isOpen)} 
        className="interactive fixed bottom-6 right-6 w-16 h-16 rounded-full shadow-lg bg-white flex items-center justify-center z-50 transition-transform duration-200 hover:scale-110"
      >
        <img
          src={TENANT.avatarUrl}
          alt="Chatbot"
          className="w-12 h-12"
        />
      </button>

      {isOpen && (
        <div className="interactive absolute bottom-24 right-6 w-[440px] max-w-[calc(100vw-48px)] h-[760px] max-h-[calc(100vh-140px)] flex flex-col glass-hub rounded-[40px] animate-slide-up overflow-hidden border border-slate-100 shadow-2xl">
          
          {/* Executive Header with LOGO */}
          <div style={{ background: TENANT.primary }} className="p-7 pb-4 flex flex-col relative">
            <div className="flex items-center justify-between w-full">
              <div className="flex items-center space-x-3">
                {viewHistory.length > 1 && <button onClick={() => setViewHistory(prev => prev.slice(0, -1))} className="p-2 bg-black/5 rounded-xl border border-black/10 hover:bg-black/10 transition-all"><Icons.Back className="text-slate-800" /></button>}
                <div className="flex items-center space-x-4 cursor-pointer" onClick={() => setViewHistory(['chat'])}>
                  <div className="flex items-center justify-center bg-white rounded-full w-10 h-10 overflow-hidden border border-slate-200">
                     <img src={TENANT.avatarUrl} className="w-8 h-8 object-contain" alt="Bot" />
                  </div>
                  <div><h3 className="font-extrabold text-sm tracking-tight text-slate-800">{TENANT.name} AI</h3><p className="text-[9px] opacity-60 font-bold uppercase tracking-[0.2em] text-slate-600">Partner Hub</p></div>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <select value={lang.code} onChange={(e) => setLang(LANGUAGES.find(l => l.code === e.target.value))} className="bg-white/40 text-[9px] font-black uppercase py-1.5 px-3 rounded-xl border border-black/5 cursor-pointer outline-none text-slate-800">{LANGUAGES.map(l => <option key={l.code} value={l.code} className="text-black">{l.name}</option>)}</select>
                <button onClick={() => setIsOpen(false)} className="opacity-40 hover:opacity-100 p-1 text-xl text-slate-800">×</button>
              </div>
            </div>
          </div>

          {/* Persistent Quick Access Nav */}
          <div className="flex items-center justify-around bg-slate-50 border-b border-slate-100 py-3 px-4 overflow-x-auto no-scrollbar">
            <button onClick={() => setViewHistory(['chat'])} className={`text-[9px] font-black uppercase tracking-widest px-3 py-1.5 rounded-xl transition-all ${currentView === 'chat' ? 'bg-[#90AB8B] text-white shadow-sm' : 'text-slate-400 hover:text-[#90AB8B]'}`}>Chat</button>
            <button onClick={() => navigate('about')} className={`text-[9px] font-black uppercase tracking-widest px-3 py-1.5 rounded-xl transition-all ${currentView === 'about' ? 'bg-[#90AB8B] text-white shadow-sm' : 'text-slate-400 hover:text-[#90AB8B]'}`}>About Us</button>
            <button onClick={() => navigate('services')} className={`text-[9px] font-black uppercase tracking-widest px-3 py-1.5 rounded-xl transition-all ${currentView === 'services' ? 'bg-[#90AB8B] text-white shadow-sm' : 'text-slate-400 hover:text-[#90AB8B]'}`}>Services</button>
            <button onClick={() => navigate('contact')} className={`text-[9px] font-black uppercase tracking-widest px-3 py-1.5 rounded-xl transition-all ${currentView === 'contact' ? 'bg-[#90AB8B] text-white shadow-sm' : 'text-slate-400 hover:text-[#90AB8B]'}`}>Support</button>
            <button onClick={() => navigate('get-in-touch')} className={`text-[9px] font-black uppercase tracking-widest px-3 py-1.5 rounded-xl transition-all ${currentView === 'get-in-touch' ? 'bg-[#90AB8B] text-white shadow-sm' : 'text-slate-400 hover:text-[#90AB8B]'}`}>Inquiry</button>
          </div>

          {/* Router Views */}
          {content}

          <div className="text-[8px] text-center text-slate-300 py-4 bg-white border-t uppercase font-black tracking-[0.3em]">© 2025 ProVista Hub Infrastructure</div>
        </div>
      )}
    </div>
  );
}