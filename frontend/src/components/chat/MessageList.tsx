import { Message } from "@/types/chat";
import MessageBubble from "./MessageBubble";
import { useAutoScroll } from "@/hooks/useAutoScroll";


interface MessageListProps {
  messages: Message[];
  suggestions: string[];
  onPick: (question: string) => void;
}

// Rendering each message, no fetch, jwt, etc.
export default function MessageList({
  messages,
  suggestions,
  onPick,
}: MessageListProps) {
  const bottomRef = useAutoScroll(messages);

  return (
    <div className="chat-messages flex-1 overflow-y-auto space-y-4 p-4 sm:p-6">
      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          message={message}
        />
        )
        )
      }
      {suggestions.length > 0 && (
        <div className="flex flex-wrap gap-2 sm:pl-10">
          {suggestions.map((question) => (
            <button
              key={question}
              type="button"
              onClick={() => onPick(question)}
              className="chat-chip rounded-full px-3.5 py-2 text-sm transition"
            >
              {question}
            </button>
          ))}
        </div>
      )}
    <div ref={bottomRef} />
  </div>
);
}