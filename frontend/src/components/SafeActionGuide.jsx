import React from 'react';
import {
  PhoneCall,
  ShieldCheck,
  ExternalLink,
  AlertOctagon,
  Clock,
  Search,
  CheckCircle,
  Lock
} from 'lucide-react';

export default function SafeActionGuide({ language = 'en', safeSteps = [] }) {
  const defaultSteps = [
    {
      step: 1,
      title: 'Pause Before Transferring Any Money',
      title_hi: 'Paisa transfer karne se pehle thode der rukein',
      description: 'Never send money under time pressure or artificial countdowns.',
      description_hi: 'Kisi ke dabav ya jaldi offer khatam hone ke daawe mein aakar turant paise na bhejein.'
    },
    {
      step: 2,
      title: 'Verify Organization via Official Directory',
      title_hi: 'Company ko official Regulatory Authorities directory mein check karein',
      description: 'Search the intermediary on official-registry.gov.in or sachet.rbi.org.in. Do not use phone numbers printed on the document.',
      description_hi: 'Document par likhe number par bharosa na karein. Official website official-registry.gov.in par jakar registration verify karein.'
    },
    {
      step: 3,
      title: 'Inspect Bank & UPI Payee Name',
      title_hi: 'UPI payee ka asli naam verify karein',
      description: 'Legitimate investment firms receive funds in corporate escrow accounts, never personal UPI handles.',
      description_hi: 'Investment ka paisa kabhi kisi vyakti ke personal UPI ya aam bank account mein nahi jata.'
    },
    {
      step: 4,
      title: 'Preserve Document & Report Suspicious Activity',
      title_hi: 'Document sambhal kar rakhein aur helpline par report karein',
      description: 'Save original screenshots and chat exports. If defrauded, immediately dial the National Cybercrime Helpline at 1930.',
      description_hi: 'Original file aur chat ka screenshot rakhein. Dhokha hone par turant Cybercrime Helpline 1930 par call karein.'
    }
  ];

  const stepsToRender = safeSteps.length > 0 ? safeSteps : defaultSteps;

  const emergencyHelplines = [
    {
      name: 'National Cyber Crime Helpline',
      name_hi: 'Rashtriya Cyber Crime Helpline',
      contact: '1930',
      actionType: 'tel',
      desc: 'Immediate reporting of unauthorized financial transactions & UPI fraud.',
      desc_hi: 'UPI ya online banking dhokhadhadi ki turant shikayat ke liye dial karein.'
    },
    {
      name: 'Regulatory Authority SCORES Grievance Portal',
      name_hi: 'Regulatory Authority SCORES Portal',
      contact: 'scores.gov.in',
      actionType: 'web',
      url: 'https://scores.gov.in',
      desc: 'Official investor grievance redressal portal against securities intermediaries.',
      desc_hi: 'Share market brokers aur investment advisors ke khilaf official complaint portal.'
    },
    {
      name: 'RBI Sachet Portal',
      name_hi: 'RBI Sachet Portal',
      contact: 'sachet.rbi.org.in',
      actionType: 'web',
      url: 'https://sachet.rbi.org.in',
      desc: 'Check authorized deposit-taking NBFCs and report illegal investment pools.',
      desc_hi: 'Gair-kanuni deposit aur Ponzi schemes ki jaanch aur complaint ke liye.'
    },
    {
      name: 'National Cyber Crime Portal',
      name_hi: 'National Cyber Crime Reporting',
      contact: 'cybercrime.gov.in',
      actionType: 'web',
      url: 'https://cybercrime.gov.in',
      desc: 'File comprehensive cyber fraud complaints with police cyber cells.',
      desc_hi: 'Police Cyber Cell mein formal FIR aur complaint darj karne ke liye.'
    }
  ];

  return (
    <div className="space-y-6">
      {/* HEADER BANNER */}
      <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 flex items-start gap-3">
        <AlertOctagon className="h-5 w-5 text-amber-600 shrink-0 mt-0.5" />
        <div>
          <h4 className="text-xs font-bold uppercase tracking-wider mb-0.5">
            {language === 'hi' ? 'Kavita aur Naye Niveshakon ke liye Suraksha Niyam' : 'Safety Action Protocol'}
          </h4>
          <p className="text-xs text-amber-800 leading-relaxed m-0">
            {language === 'hi'
              ? 'Proofly stock recommendations ya financial salah nahi deta. Yeh niyam aapke paise ko anjaan haathon mein jaane se bachane ke liye hain.'
              : 'Proofly provides forensic and text inspection, not investment advice. Follow these steps to verify before taking financial action.'}
          </p>
        </div>
      </div>

      {/* 4-STEP ACTION ROADMAP */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {stepsToRender.map((s, idx) => (
          <div
            key={idx}
            className="p-4 rounded-xl bg-white border border-slate-200/90 shadow-2xs space-y-2 flex flex-col justify-between"
          >
            <div className="flex items-center gap-3">
              <div className="h-7 w-7 rounded-full bg-blue-50 text-blue-700 font-bold text-xs flex items-center justify-center shrink-0 border border-blue-100">
                {s.step || idx + 1}
              </div>
              <h4 className="text-xs font-bold text-slate-900 m-0">
                {language === 'hi' ? (s.title_hi || s.title) : s.title}
              </h4>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed m-0 pl-10">
              {language === 'hi' ? (s.description_hi || s.description) : s.description}
            </p>
          </div>
        ))}
      </div>

      {/* OFFICIAL STATUTORY HELPLINES & PORTALS */}
      <div>
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-3 flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-emerald-600" />
          <span>
            {language === 'hi' ? 'Sarkari Sahayata aur Shikayat Kendro (Official Portals):' : 'Official Investor Redressal & Support Channels:'}
          </span>
        </h4>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {emergencyHelplines.map((h, i) => (
            <div
              key={i}
              className="p-3.5 rounded-xl bg-slate-50/70 border border-slate-200/80 hover:bg-white hover:border-blue-300 hover:shadow-xs transition flex flex-col justify-between"
            >
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  {h.actionType === 'tel' ? 'Helpline 24x7' : 'Statutory Portal'}
                </span>
                <h5 className="text-xs font-bold text-slate-900 mt-1 m-0">
                  {language === 'hi' ? h.name_hi : h.name}
                </h5>
                <p className="text-[11px] text-slate-500 mt-1 leading-relaxed m-0">
                  {language === 'hi' ? h.desc_hi : h.desc}
                </p>
              </div>

              <div className="mt-3 pt-2 border-t border-slate-200/60">
                {h.actionType === 'tel' ? (
                  <a
                    href={`tel:${h.contact}`}
                    className="flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold shadow-xs transition"
                  >
                    <PhoneCall className="h-3.5 w-3.5" />
                    <span>Dial {h.contact}</span>
                  </a>
                ) : (
                  <a
                    href={h.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-lg bg-white hover:bg-slate-100 text-blue-600 text-xs font-semibold border border-slate-200 transition"
                  >
                    <span>{h.contact}</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
