import { Button } from "../ui/button";

interface ChatInputProps {
  value: string;
  loading: boolean;
  onChange: (value: string) => void;
  onSend: () => void;
}

export default function ChatInput({
  value,
  loading,
  onChange,
  onSend,
}: ChatInputProps) {
  return (
    <div className="flex gap-2.5 px-4 pt-4 pb-2 sm:px-6">
      <input
        className="chat-input h-11 min-w-0 flex-1 rounded-full px-4 py-3 text-[15px] transition"
        placeholder="ask me about my work..."
        value={value}
        disabled={loading}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            onSend();
          }
        }}
      />


      <Button
        onClick={() => onSend()}
        disabled={loading}
        className="chat-send h-11 rounded-full px-5 text-[15px] transition hover:opacity-90 disabled:opacity-50"
        >
        send
      </Button>
    </div>
  );
}