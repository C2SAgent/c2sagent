export interface ChatMessage {
  role: string;
  content: string;
  timestamp: string | Date;
}

export interface ChatSession {
  session_id: string;
  created_at: string;
  title: string;
  messages: ChatMessage[];
}