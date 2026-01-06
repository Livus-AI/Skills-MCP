"use client";

import { useState } from "react";
import { 
  Search, 
  Linkedin, 
  MapPin, 
  Briefcase, 
  Building2, 
  Loader2, 
  Filter,
  Users
} from "lucide-react";
import { cn } from "@/lib/utils";

interface Lead {
  full_name?: string;
  title?: string;
  company_name?: string;
  linkedin_url?: string;
  location?: string;
}

export default function Home() {
  const [query, setQuery] = useState("");
  const [limit, setLimit] = useState(5);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState("");
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError("");
    setHasSearched(true);
    setLeads([]);

    try {
      const res = await fetch("/api/pipeline", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, limit, useApify: true }),
      });
      
      const data = await res.json();
      
      if (!data.success) {
        throw new Error(data.error || "Failed to fetch leads");
      }
      
      setLeads(data.leads || []);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full relative overflow-hidden bg-zinc-950 font-sans selection:bg-indigo-500/20">
      
      {/* Background Ambience */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[400px] bg-indigo-500/20 blur-[120px] rounded-full pointer-events-none opacity-50" />
      
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-20">
        
        {/* Header Section */}
        <div className="max-w-3xl mx-auto text-center space-y-6 mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-medium uppercase tracking-wide">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
            </span>
            AI Pipeline Active
          </div>
          
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight text-white">
            Find your next <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">ideal customer</span>
          </h1>
          
          <p className="text-lg text-zinc-400 max-w-xl mx-auto leading-relaxed">
            Enter a natural language query to discover and enrich B2B leads automatically. Powered by Apify, Clay, and OpenAI.
          </p>
        </div>

        {/* Search Interface */}
        <div className="max-w-3xl mx-auto mb-20 relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-cyan-500 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"></div>
          
          <form 
            onSubmit={handleSearch} 
            className="relative flex items-center gap-1 sm:gap-2 bg-zinc-900 border border-zinc-800 p-2 rounded-xl shadow-2xl focus-within:ring-2 focus-within:ring-indigo-500/50 focus-within:border-indigo-500/50 transition-all"
          >
            <div className="pl-3 sm:pl-4 text-zinc-500 shrink-0">
              <Search className="w-5 h-5" />
            </div>
            
            <input
              type="text"
              placeholder="e.g. Marketing Directors..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="flex-1 bg-transparent border-none text-white placeholder:text-zinc-600 focus:outline-none focus:ring-0 px-2 py-3 text-base md:text-lg min-w-0"
            />
            
            <div className="h-6 w-px bg-zinc-800 mx-1 hidden sm:block"></div>
            
            {/* Unified Custom Dropdown */}
            <div className="relative z-50 shrink-0">
              <button
                type="button"
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="flex items-center gap-2 text-zinc-400 text-sm font-medium hover:text-white transition-colors px-2 sm:px-3 py-2 rounded-lg hover:bg-zinc-800 focus:outline-none"
              >
                {/* Mobile: Filter Icon Only / Desktop: Text + Icon */}
                <span className="hidden sm:inline">{limit} results</span>
                <span className="sm:hidden">{limit}</span>
                <Filter className="w-3 h-3" />
              </button>

              {isDropdownOpen && (
                <>
                  <div 
                    className="fixed inset-0 z-40" 
                    onClick={() => setIsDropdownOpen(false)}
                  ></div>
                  <div className="absolute right-0 top-full mt-2 w-48 bg-zinc-900 border border-zinc-800 rounded-xl shadow-xl overflow-hidden z-50 animate-in fade-in zoom-in-95 duration-200">
                    {[5, 10, 20, 50].map((val) => (
                      <button
                        key={val}
                        type="button"
                        onClick={() => {
                          setLimit(val);
                          setIsDropdownOpen(false);
                        }}
                        className={cn(
                          "w-full text-left px-4 py-3 text-sm transition-colors hover:bg-zinc-800",
                          limit === val ? "text-indigo-400 bg-indigo-400/10" : "text-zinc-400"
                        )}
                      >
                        {val} results
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="bg-white text-zinc-950 hover:bg-zinc-200 disabled:opacity-50 disabled:cursor-not-allowed font-semibold py-3 px-4 sm:px-6 rounded-lg transition-all flex items-center gap-2 shadow-lg shadow-white/5 shrink-0"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <span className="hidden sm:inline">Search</span>} 
              <span className="sm:hidden">{loading ? "" : <Search className="w-4 h-4"/>}</span>
            </button>
          </form>
        </div>

        {/* Error Message */}
        {error && (
           <div className="max-w-2xl mx-auto mb-10 p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg text-sm text-center">
             {error}
           </div>
        )}

        {/* LOADING STATE - Skeleton */}
        {loading && (
          <div className="max-w-5xl mx-auto space-y-4 animate-pulse">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-20 bg-zinc-900/50 rounded-xl border border-zinc-800/50"></div>
            ))}
            <div className="text-center text-zinc-500 text-sm mt-4">
              AI Agent is analyzing query and scraping sources... (approx 30s)
            </div>
          </div>
        )}

        {/* RESULTS */}
        {!loading && hasSearched && leads.length === 0 && !error && (
            <div className="text-center py-20 text-zinc-500">
                <Users className="w-12 h-12 mx-auto mb-4 opacity-20" />
                <p>No leads found matching your criteria.</p>
            </div>
        )}

        {!loading && leads.length > 0 && (
          <div className="max-w-6xl mx-auto">
            <div className="flex items-center justify-between mb-6 px-2">
                <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                    Results <span className="text-zinc-500 text-sm font-normal">({leads.length} found)</span>
                </h2>
                <button className="text-xs font-medium text-indigo-400 hover:text-indigo-300 transition-colors">
                    Export CSV
                </button>
            </div>

            {/* Desktop View */}
            <div className="hidden md:block overflow-hidden rounded-xl border border-zinc-800 bg-zinc-900/30 backdrop-blur-sm shadow-2xl">
              <table className="w-full text-left">
                <thead className="bg-zinc-900 text-zinc-400 uppercase tracking-wider text-xs border-b border-zinc-800">
                  <tr>
                    <th className="px-6 py-4 font-medium">Professional</th>
                    <th className="px-6 py-4 font-medium">Role</th>
                    <th className="px-6 py-4 font-medium">Company</th>
                    <th className="px-6 py-4 font-medium">Location</th>
                    <th className="px-6 py-4 text-right font-medium">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800/50">
                  {leads.map((lead, idx) => (
                    <tr key={idx} className="group hover:bg-zinc-800/30 transition-colors duration-200">
                      
                      {/* Name */}
                      <td className="px-6 py-4">
                        <div className="font-medium text-white group-hover:text-indigo-300 transition-colors">
                          {lead.full_name || "Unknown"}
                        </div>
                      </td>

                      {/* Role */}
                      <td className="px-6 py-4 text-zinc-300 text-sm">
                        <div className="flex items-center gap-2">
                            <Briefcase className="w-3 h-3 text-zinc-500" />
                            <span className="truncate max-w-[200px]" title={lead.title}>{lead.title || "—"}</span>
                        </div>
                      </td>

                      {/* Company */}
                      <td className="px-6 py-4 text-zinc-300 text-sm">
                        <div className="flex items-center gap-2">
                            <Building2 className="w-3 h-3 text-zinc-500" />
                            <span className="truncate max-w-[200px]" title={lead.company_name}>{lead.company_name || "—"}</span>
                        </div>
                      </td>

                      {/* Location */}
                      <td className="px-6 py-4 text-zinc-400 text-sm">
                        <div className="flex items-center gap-2">
                            <MapPin className="w-3 h-3 text-zinc-600" />
                            {lead.location || "—"}
                        </div>
                      </td>

                      {/* Action */}
                      <td className="px-6 py-4 text-right">
                        {lead.linkedin_url ? (
                          <a 
                            href={lead.linkedin_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-zinc-800 hover:bg-blue-600 text-zinc-400 hover:text-white transition-all group-hover:scale-110"
                            title="View on LinkedIn"
                          >
                            <Linkedin className="w-4 h-4" />
                          </a>
                        ) : (
                          <span className="text-zinc-600">-</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Mobile Card View */}
            <div className="md:hidden space-y-4">
              {leads.map((lead, idx) => (
                <div key={idx} className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-5 shadow-sm space-y-4 hover:border-zinc-700 transition-colors active:scale-[0.99]">
                    <div className="flex justify-between items-start">
                        <div>
                            <h3 className="text-white font-semibold text-lg">{lead.full_name}</h3>
                            <p className="text-indigo-400 text-sm font-medium mt-0.5">{lead.title}</p>
                        </div>
                        {lead.linkedin_url && (
                            <a href={lead.linkedin_url} target="_blank" rel="noopener noreferrer" className="p-2 bg-blue-600/10 text-blue-500 rounded-full hover:bg-blue-600 hover:text-white transition-colors">
                                <Linkedin className="w-5 h-5" />
                            </a>
                        )}
                    </div>
                    
                    <div className="space-y-2 pt-2 border-t border-zinc-800/50">
                        <div className="flex items-center gap-3 text-sm text-zinc-400">
                            <Building2 className="w-4 h-4 text-zinc-600" />
                            {lead.company_name}
                        </div>
                        <div className="flex items-center gap-3 text-sm text-zinc-400">
                            <MapPin className="w-4 h-4 text-zinc-600" />
                            {lead.location}
                        </div>
                    </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
