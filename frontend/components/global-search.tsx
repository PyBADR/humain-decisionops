"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Search, FileText, User, Play, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";

interface SearchResult {
  type: "claim" | "customer" | "run";
  id: string;
  title: string;
  subtitle: string;
}

export function GlobalSearch() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    const searchDebounce = setTimeout(async () => {
      if (query.length >= 2) {
        setIsLoading(true);
        try {
          const response = await api.search(query);
          setResults(response.results || []);
          setIsOpen(true);
        } catch (error) {
          console.error("Search error:", error);
          setResults([]);
        } finally {
          setIsLoading(false);
        }
      } else {
        setResults([]);
        setIsOpen(false);
      }
    }, 300);

    return () => clearTimeout(searchDebounce);
  }, [query]);

  const handleSelect = (result: SearchResult) => {
    setIsOpen(false);
    setQuery("");
    
    switch (result.type) {
      case "claim":
        router.push(`/claims/${result.id}`);
        break;
      case "run":
        router.push(`/runs?run_id=${result.id}`);
        break;
      case "customer":
        router.push(`/claims?customer=${encodeURIComponent(result.title)}`);
        break;
    }
  };

  const getIcon = (type: string) => {
    switch (type) {
      case "claim":
        return <FileText className="h-4 w-4 text-blue-400" />;
      case "customer":
        return <User className="h-4 w-4 text-green-400" />;
      case "run":
        return <Play className="h-4 w-4 text-purple-400" />;
      default:
        return <Search className="h-4 w-4 text-zinc-400" />;
    }
  };

  return (
    <div ref={containerRef} className="relative w-full max-w-md">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
        <Input
          ref={inputRef}
          type="text"
          placeholder="Search claims, customers, runs..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => query.length >= 2 && setIsOpen(true)}
          className="pl-10 pr-10 bg-zinc-800 border-zinc-700 text-zinc-100 placeholder:text-zinc-500 focus:border-blue-500"
        />
        {query && (
          <button
            onClick={() => {
              setQuery("");
              setResults([]);
              setIsOpen(false);
            }}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-zinc-300"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-zinc-800 border border-zinc-700 rounded-lg shadow-xl z-50 overflow-hidden">
          {isLoading ? (
            <div className="p-4 text-center text-zinc-400">
              <div className="animate-spin h-5 w-5 border-2 border-zinc-500 border-t-blue-500 rounded-full mx-auto" />
            </div>
          ) : results.length > 0 ? (
            <ul className="max-h-80 overflow-auto">
              {results.map((result, index) => (
                <li key={`${result.type}-${result.id}-${index}`}>
                  <button
                    onClick={() => handleSelect(result)}
                    className="w-full flex items-center gap-3 px-4 py-3 hover:bg-zinc-700 transition-colors text-left"
                  >
                    {getIcon(result.type)}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-zinc-100 truncate">
                        {result.title}
                      </p>
                      <p className="text-xs text-zinc-400 truncate">
                        {result.subtitle}
                      </p>
                    </div>
                    <span className="text-xs text-zinc-500 capitalize">
                      {result.type}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <div className="p-4 text-center text-zinc-400 text-sm">
              No results found for "{query}"
            </div>
          )}
        </div>
      )}
    </div>
  );
}
