"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut, Download } from "lucide-react";

interface PDFViewerProps {
  url: string;
  filename: string;
}

export function PDFViewer({ url, filename }: PDFViewerProps) {
  const [scale, setScale] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);
  const totalPages = 5; // Mock total pages

  const handleZoomIn = () => setScale((prev) => Math.min(prev + 0.25, 2));
  const handleZoomOut = () => setScale((prev) => Math.max(prev - 0.25, 0.5));
  const handlePrevPage = () => setCurrentPage((prev) => Math.max(prev - 1, 1));
  const handleNextPage = () => setCurrentPage((prev) => Math.min(prev + 1, totalPages));

  // For demo purposes, we show a styled placeholder
  // In production, you would use react-pdf or iframe with actual PDF
  const isValidUrl = url && url.startsWith("http");

  return (
    <div className="flex flex-col h-full bg-zinc-900 rounded-lg border border-zinc-800">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-zinc-800 bg-zinc-800/50">
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={handlePrevPage}
            disabled={currentPage === 1}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="text-sm text-zinc-400">
            Page {currentPage} of {totalPages}
          </span>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleNextPage}
            disabled={currentPage === totalPages}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" onClick={handleZoomOut}>
            <ZoomOut className="h-4 w-4" />
          </Button>
          <span className="text-sm text-zinc-400 w-16 text-center">
            {Math.round(scale * 100)}%
          </span>
          <Button variant="ghost" size="sm" onClick={handleZoomIn}>
            <ZoomIn className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm" asChild>
            <a href={url} download={filename} target="_blank" rel="noopener noreferrer">
              <Download className="h-4 w-4" />
            </a>
          </Button>
        </div>
      </div>

      {/* PDF Content */}
      <div className="flex-1 overflow-auto p-4 flex items-center justify-center">
        {isValidUrl ? (
          <iframe
            src={`${url}#page=${currentPage}`}
            className="w-full h-full rounded border border-zinc-700"
            style={{ transform: `scale(${scale})`, transformOrigin: "top center" }}
            title={filename}
          />
        ) : (
          <div
            className="bg-white rounded-lg shadow-xl flex flex-col items-center justify-center text-zinc-800 p-8"
            style={{
              width: `${595 * scale}px`,
              height: `${842 * scale}px`,
              maxWidth: "100%",
            }}
          >
            <div className="text-6xl mb-4">📄</div>
            <h3 className="text-xl font-semibold mb-2">{filename}</h3>
            <p className="text-zinc-500 text-center mb-4">
              Document Preview
            </p>
            <div className="w-full max-w-md space-y-3">
              <div className="h-4 bg-zinc-200 rounded w-full" />
              <div className="h-4 bg-zinc-200 rounded w-5/6" />
              <div className="h-4 bg-zinc-200 rounded w-4/6" />
              <div className="h-4 bg-zinc-200 rounded w-full" />
              <div className="h-4 bg-zinc-200 rounded w-3/4" />
              <div className="h-20 bg-zinc-100 rounded w-full mt-6" />
              <div className="h-4 bg-zinc-200 rounded w-full" />
              <div className="h-4 bg-zinc-200 rounded w-2/3" />
            </div>
            <p className="text-xs text-zinc-400 mt-6">
              Page {currentPage} of {totalPages}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
