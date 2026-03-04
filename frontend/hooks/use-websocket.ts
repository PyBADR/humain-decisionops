"use client";

import { useEffect, useRef, useState, useCallback } from "react";

interface WebSocketMessage {
  type: string;
  payload: any;
  timestamp: string;
}

interface UseWebSocketOptions {
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  reconnectAttempts?: number;
  reconnectInterval?: number;
}

export function useWebSocket(url: string | null, options: UseWebSocketOptions = {}) {
  const {
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    reconnectAttempts = 5,
    reconnectInterval = 3000,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCountRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (!url) return;

    try {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        setIsConnected(true);
        reconnectCountRef.current = 0;
        onConnect?.();
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(message);
          onMessage?.(message);
        } catch (error) {
          console.error("Failed to parse WebSocket message:", error);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        onDisconnect?.();

        // Attempt to reconnect
        if (reconnectCountRef.current < reconnectAttempts) {
          reconnectCountRef.current += 1;
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };

      ws.onerror = (error) => {
        onError?.(error);
      };

      wsRef.current = ws;
    } catch (error) {
      console.error("WebSocket connection error:", error);
    }
  }, [url, onMessage, onConnect, onDisconnect, onError, reconnectAttempts, reconnectInterval]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return {
    isConnected,
    lastMessage,
    sendMessage,
    disconnect,
    reconnect: connect,
  };
}

// Hook for subscribing to claim updates
export function useClaimUpdates(claimId: string | null) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const wsUrl = claimId ? `${apiUrl.replace("http", "ws")}/ws/claims/${claimId}` : null;

  const [claimStatus, setClaimStatus] = useState<string | null>(null);
  const [pipelineProgress, setPipelineProgress] = useState<{
    currentNode: string;
    progress: number;
  } | null>(null);

  const { isConnected, lastMessage } = useWebSocket(wsUrl, {
    onMessage: (message) => {
      switch (message.type) {
        case "status_update":
          setClaimStatus(message.payload.status);
          break;
        case "pipeline_progress":
          setPipelineProgress({
            currentNode: message.payload.node,
            progress: message.payload.progress,
          });
          break;
      }
    },
  });

  return {
    isConnected,
    claimStatus,
    pipelineProgress,
    lastMessage,
  };
}

// Hook for subscribing to global updates (new claims, decisions, etc.)
export function useGlobalUpdates() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const wsUrl = `${apiUrl.replace("http", "ws")}/ws/updates`;

  const [newClaims, setNewClaims] = useState<any[]>([]);
  const [newDecisions, setNewDecisions] = useState<any[]>([]);

  const { isConnected, lastMessage } = useWebSocket(wsUrl, {
    onMessage: (message) => {
      switch (message.type) {
        case "new_claim":
          setNewClaims((prev) => [message.payload, ...prev].slice(0, 10));
          break;
        case "new_decision":
          setNewDecisions((prev) => [message.payload, ...prev].slice(0, 10));
          break;
      }
    },
  });

  const clearNewClaims = useCallback(() => setNewClaims([]), []);
  const clearNewDecisions = useCallback(() => setNewDecisions([]), []);

  return {
    isConnected,
    newClaims,
    newDecisions,
    clearNewClaims,
    clearNewDecisions,
    lastMessage,
  };
}
