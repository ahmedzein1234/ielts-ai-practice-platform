'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { useToast } from '@/hooks/use-toast';

interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

interface UseWebSocketOptions {
  url: string;
  onMessage?: (message: WebSocketMessage) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export function useWebSocket({
  url,
  onMessage,
  onOpen,
  onClose,
  onError,
  reconnectInterval = 3000,
  maxReconnectAttempts = 5,
}: UseWebSocketOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const { toast } = useToast();

  const connect = useCallback(() => {
    if (isConnecting || isConnected) return;

    setIsConnecting(true);
    
    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setIsConnecting(false);
        setReconnectAttempts(0);
        onOpen?.();
        
        toast({
          title: 'Connected',
          description: 'Real-time connection established',
          duration: 2000,
        });
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          onMessage?.(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onclose = (event) => {
        setIsConnected(false);
        setIsConnecting(false);
        onClose?.();

        // Attempt to reconnect if not a clean close
        if (!event.wasClean && reconnectAttempts < maxReconnectAttempts) {
          const nextAttempt = reconnectAttempts + 1;
          setReconnectAttempts(nextAttempt);
          
          toast({
            title: 'Connection Lost',
            description: `Reconnecting... (${nextAttempt}/${maxReconnectAttempts})`,
            duration: 3000,
          });

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        } else if (reconnectAttempts >= maxReconnectAttempts) {
          toast({
            title: 'Connection Failed',
            description: 'Unable to establish connection. Please refresh the page.',
            variant: 'destructive',
          });
        }
      };

      ws.onerror = (error) => {
        setIsConnecting(false);
        onError?.(error);
        console.error('WebSocket error:', error);
      };
    } catch (error) {
      setIsConnecting(false);
      console.error('Failed to create WebSocket connection:', error);
    }
  }, [url, isConnecting, isConnected, reconnectAttempts, maxReconnectAttempts, reconnectInterval, onOpen, onClose, onError, onMessage, toast]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'User disconnected');
      wsRef.current = null;
    }

    setIsConnected(false);
    setIsConnecting(false);
    setReconnectAttempts(0);
  }, []);

  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (wsRef.current && isConnected) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, [isConnected]);

  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    isConnecting,
    reconnectAttempts,
    sendMessage,
    connect,
    disconnect,
  };
}

// Specialized hook for IELTS scoring
export function useIELTSScoring() {
  const [scoringStatus, setScoringStatus] = useState<'idle' | 'processing' | 'completed' | 'error'>('idle');
  const [score, setScore] = useState<number | null>(null);
  const [feedback, setFeedback] = useState<any>(null);

  const { isConnected, sendMessage } = useWebSocket({
    url: process.env.NEXT_PUBLIC_WS_URL || 'wss://ielts-api-gateway-production.up.railway.app/ws',
    onMessage: (message) => {
      switch (message.type) {
        case 'scoring_started':
          setScoringStatus('processing');
          break;
        case 'scoring_completed':
          setScoringStatus('completed');
          setScore(message.data.score);
          setFeedback(message.data.feedback);
          break;
        case 'scoring_error':
          setScoringStatus('error');
          break;
      }
    },
  });

  const submitForScoring = useCallback((data: { type: 'speaking' | 'writing'; content: string; audioUrl?: string }) => {
    sendMessage({
      type: 'submit_scoring',
      data,
      timestamp: new Date().toISOString(),
    });
  }, [sendMessage]);

  return {
    isConnected,
    scoringStatus,
    score,
    feedback,
    submitForScoring,
  };
}
