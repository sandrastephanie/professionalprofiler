import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import Avatar from "./Avatar";

import { Message } from "@/types/chat";

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({
  message,
}: MessageBubbleProps) {
  const isUser = message.role === "user";
  const isStreaming = message.status === "streaming";
  const isTyping = isStreaming && message.content === "";

  return (
    <div
      className={`flex items-end gap-2 ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      {!isUser && (
        <div
          className={`h-8 w-8 shrink-0 rounded-full ${
            isStreaming ? "chat-avatar-glow" : ""
          }`}
        >
          <Avatar size={32} />
        </div>
      )}

      <div
        className={`max-w-[85%] rounded-[18px] px-4 py-3 text-[15px] leading-relaxed sm:max-w-[80%] ${
          isUser
            ? "chat-bubble-user rounded-br-md"
            : "chat-bubble-assistant rounded-bl-md"
        }`}
      >
        {isTyping ? (
          <div className="flex items-center gap-1 py-1">
            <span className="chat-typing-dot h-1.5 w-1.5 rounded-full bg-slate-400" />
            <span className="chat-typing-dot h-1.5 w-1.5 rounded-full bg-slate-400" />
            <span className="chat-typing-dot h-1.5 w-1.5 rounded-full bg-slate-400" />
          </div>
        ) : (
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {message.content}
          </ReactMarkdown>
        )}
      </div>
    </div>
  );
}