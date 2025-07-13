export interface ChatMessage {
  role: string;
  content: string;
  timestamp: string | Date;
  isTemp?: boolean
}

export interface ChatSession {
  session_id: string;
  created_at: string;
  title: string;
  messages: ChatMessage[];
}
// export interface ChatMessage {
//   id: string;
//   content: string;
//   sender: 'user' | 'bot';
//   timestamp: Date;
// }

// export interface ChatSession {
//   id: string;
//   title: string;
//   lastMessage: string;
//   updatedAt: Date;
//   messages: ChatMessage[];
// }