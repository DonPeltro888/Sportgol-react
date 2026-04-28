import React from 'react';
import { ShieldCheck, Lock, BadgeCheck } from 'lucide-react';

/**
 * Trust badges con loghi pagamenti per rassicurare l'utente prima dell'acquisto.
 */
const TrustBadges = () => {
  return (
    <div
      className="bg-gray-50 border border-gray-200 rounded-xl p-4"
      data-testid="trust-badges"
    >
      <div className="flex items-center gap-2 text-[#2D3436] font-semibold text-sm mb-3">
        <ShieldCheck className="w-5 h-5 text-green-600" />
        Acquisto 100% sicuro
      </div>

      {/* Trust points */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 mb-4 text-xs text-gray-600">
        <div className="flex items-center gap-1.5">
          <Lock className="w-3.5 h-3.5 text-green-600 flex-shrink-0" />
          <span>Pagamento crittografato SSL</span>
        </div>
        <div className="flex items-center gap-1.5">
          <BadgeCheck className="w-3.5 h-3.5 text-green-600 flex-shrink-0" />
          <span>Biglietti garantiti al 100%</span>
        </div>
        <div className="flex items-center gap-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-green-600 flex-shrink-0" />
          <span>Supporto 7/7 italiano</span>
        </div>
      </div>

      {/* Payment logos */}
      <div className="flex items-center justify-center flex-wrap gap-3 pt-3 border-t border-gray-200">
        {/* Visa */}
        <div className="bg-white border border-gray-200 rounded px-2.5 py-1.5 shadow-sm">
          <svg width="36" height="14" viewBox="0 0 36 14" fill="none" xmlns="http://www.w3.org/2000/svg" aria-label="Visa">
            <text x="0" y="11" fontFamily="Arial, sans-serif" fontWeight="900" fontSize="11" fill="#1A1F71" fontStyle="italic">VISA</text>
          </svg>
        </div>
        {/* Mastercard */}
        <div className="bg-white border border-gray-200 rounded px-2.5 py-1.5 shadow-sm flex items-center gap-0.5">
          <span className="block w-4 h-4 rounded-full bg-[#EB001B]"></span>
          <span className="block w-4 h-4 rounded-full bg-[#F79E1B] -ml-2 mix-blend-multiply"></span>
        </div>
        {/* PayPal */}
        <div className="bg-white border border-gray-200 rounded px-2.5 py-1.5 shadow-sm">
          <svg width="42" height="14" viewBox="0 0 42 14" xmlns="http://www.w3.org/2000/svg" aria-label="PayPal">
            <text x="0" y="11" fontFamily="Arial, sans-serif" fontWeight="900" fontSize="10" fill="#003087" fontStyle="italic">Pay</text>
            <text x="17" y="11" fontFamily="Arial, sans-serif" fontWeight="900" fontSize="10" fill="#009CDE" fontStyle="italic">Pal</text>
          </svg>
        </div>
        {/* Apple Pay */}
        <div className="bg-black text-white rounded px-2.5 py-1.5 shadow-sm">
          <svg width="36" height="14" viewBox="0 0 36 14" xmlns="http://www.w3.org/2000/svg" aria-label="Apple Pay">
            <text x="0" y="11" fontFamily="-apple-system, sans-serif" fontWeight="600" fontSize="10" fill="white">Pay</text>
          </svg>
        </div>
        {/* Stripe / Card */}
        <div className="bg-white border border-gray-200 rounded px-2.5 py-1.5 shadow-sm">
          <svg width="36" height="14" viewBox="0 0 36 14" xmlns="http://www.w3.org/2000/svg" aria-label="Stripe">
            <text x="0" y="11" fontFamily="Arial, sans-serif" fontWeight="700" fontSize="10" fill="#635BFF" fontStyle="italic">stripe</text>
          </svg>
        </div>
      </div>
    </div>
  );
};

export default TrustBadges;
